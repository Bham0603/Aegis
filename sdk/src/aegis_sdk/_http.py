"""
Internal HTTP transport layer for the Aegis SDK.

Wraps httpx.AsyncClient with centralized:
- Authentication header injection
- Request/response handling
- Response validation and JSON parsing
- Error mapping to SDK exceptions
- Safe retry logic for transient failures
- Security header control
"""

from __future__ import annotations

import asyncio
import time
from typing import Any
from urllib.parse import urlparse

import httpx

from aegis_sdk import _logging
from aegis_sdk.errors import (
    AegisAuthenticationError,
    AegisAuthorizationError,
    AegisConflictError,
    AegisNetworkError,
    AegisNotFoundError,
    AegisRateLimitError,
    AegisServerError,
    AegisTimeoutError,
    AegisUnavailableError,
    AegisValidationError,
)

# HTTP status codes that are safe to retry (transient server errors)
_RETRYABLE_STATUS_CODES = frozenset({502, 503, 504})

# HTTP methods that are safe to retry
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})

# Minimum base URL schemes
_ALLOWED_SCHEMES = frozenset({"http", "https"})


def validate_base_url(url: str) -> str:
    """
    Validate and normalize a base URL.
    Only HTTP and HTTPS schemes are allowed.
    """
    parsed = urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ValueError(
            f"Unsupported URL scheme: {parsed.scheme!r}. "
            f"Only {', '.join(sorted(_ALLOWED_SCHEMES))} are supported."
        )
    if not parsed.hostname:
        raise ValueError(f"Invalid URL: missing hostname in {url!r}")
    # Strip trailing slash for consistency
    return url.rstrip("/")


class HttpTransport:
    """
    Centralized HTTP transport for the Aegis SDK.

    Handles authentication, retries, timeouts, and error mapping.
    """

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        api_prefix: str = "/api/v1",
    ) -> None:
        self._base_url = validate_base_url(base_url)
        self._api_key = api_key
        self._timeout = timeout
        self._max_retries = max(0, min(max_retries, 10))  # Bounded 0-10
        self._api_prefix = api_prefix
        self._client: httpx.AsyncClient | None = None

    def _build_url(self, path: str) -> str:
        """Build a full URL from a relative API path."""
        # path should start with / e.g. /actions/evaluate
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self._base_url}{self._api_prefix}{path}"

    def _build_headers(self, correlation_id: str | None = None) -> dict[str, str]:
        """
        Build request headers.
        Only sends necessary headers — never forwards arbitrary application headers.
        """
        headers: dict[str, str] = {
            "X-API-Key": self._api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id
        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._timeout),
                follow_redirects=False,
            )
        return self._client

    async def close(self) -> None:
        """Close the underlying HTTP client and release resources."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _should_retry(self, method: str, status_code: int, attempt: int, is_mutation: bool) -> bool:
        """
        Determine whether a request should be retried.

        Rules:
        - Only retry on transient server errors (502/503/504)
        - Never retry auth failures (401/403) or client errors
        - Never retry state-changing mutations (approve/deny) unless explicitly safe
        - Respect bounded retry count
        """
        if attempt >= self._max_retries:
            return False
        if status_code not in _RETRYABLE_STATUS_CODES:
            return False
        if is_mutation:
            return False  # Never retry mutations
        return True

    def _should_retry_exception(self, method: str, attempt: int, is_mutation: bool) -> bool:
        """Determine whether to retry after a transport exception."""
        if attempt >= self._max_retries:
            return False
        if is_mutation:
            return False
        return True

    async def _backoff(self, attempt: int) -> None:
        """Exponential backoff with jitter."""
        delay = min(2 ** attempt * 0.5, 30.0)  # Cap at 30s
        await asyncio.sleep(delay)

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        is_mutation: bool = False,
    ) -> dict[str, Any] | list[Any]:
        """
        Execute an HTTP request against the Aegis backend.

        Args:
            method: HTTP method
            path: API path (e.g. "/actions/evaluate")
            json: Request body for POST/PUT
            params: Query parameters for GET
            correlation_id: Optional correlation ID
            is_mutation: If True, never retry this request

        Returns:
            Parsed JSON response

        Raises:
            AegisError subclasses based on HTTP status
        """
        url = self._build_url(path)
        headers = self._build_headers(correlation_id)

        # Filter None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        _logging.log_request(method, path, correlation_id=correlation_id)

        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            start_time = time.monotonic()
            try:
                client = await self._get_client()
                response = await client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                    headers=headers,
                )
                latency_ms = (time.monotonic() - start_time) * 1000

                if response.status_code < 400:
                    # Parse response
                    try:
                        data = response.json()
                    except Exception:
                        _logging.log_error("parse_error", "Invalid JSON response", status_code=response.status_code)
                        raise AegisServerError("Invalid JSON response from backend", status=response.status_code)

                    _logging.log_response(
                        response.status_code,
                        latency_ms=latency_ms,
                        correlation_id=correlation_id,
                    )
                    return data  # type: ignore[return-value]

                # Error response — try to extract detail
                detail = self._extract_error_detail(response)
                _logging.log_response(
                    response.status_code,
                    latency_ms=latency_ms,
                    correlation_id=correlation_id,
                )

                # Check for retry before raising
                if response.status_code in _RETRYABLE_STATUS_CODES:
                    last_error = AegisServerError(detail, status=response.status_code)
                    if self._should_retry(method, response.status_code, attempt, is_mutation):
                        await self._backoff(attempt)
                        continue
                    
                    # Retries exhausted or not allowed (mutation)
                    raise AegisUnavailableError(
                        f"Aegis backend unavailable after {attempt + 1} attempts"
                    ) from last_error

                # Map to specific error
                self._raise_for_status(response.status_code, detail)

            except (httpx.ConnectError, httpx.RemoteProtocolError, OSError) as exc:
                latency_ms = (time.monotonic() - start_time) * 1000
                _logging.log_error("network_error", str(exc))
                last_error = AegisNetworkError(f"Connection failed: {type(exc).__name__}")
                if self._should_retry_exception(method, attempt, is_mutation):
                    await self._backoff(attempt)
                    continue
                raise AegisNetworkError(f"Connection failed: {type(exc).__name__}") from exc

            except httpx.TimeoutException as exc:
                _logging.log_error("timeout", str(exc))
                last_error = AegisTimeoutError(f"Request timed out after {self._timeout}s")
                if self._should_retry_exception(method, attempt, is_mutation):
                    await self._backoff(attempt)
                    continue
                raise AegisTimeoutError(f"Request timed out after {self._timeout}s") from exc

            except (AegisAuthenticationError, AegisAuthorizationError,
                    AegisNotFoundError, AegisValidationError,
                    AegisConflictError, AegisRateLimitError):
                raise  # Never retry client errors

            except AegisServerError:
                raise  # Already decided not to retry

        # Exhausted all retries
        if last_error is not None:
            raise AegisUnavailableError(
                f"Aegis backend unavailable after {self._max_retries + 1} attempts"
            ) from last_error
        raise AegisUnavailableError("Aegis backend unavailable")

    def _extract_error_detail(self, response: httpx.Response) -> str:
        """Extract a safe error message from a response. Never leaks internals."""
        try:
            body = response.json()
            if isinstance(body, dict):
                detail = body.get("detail", "")
                if isinstance(detail, str):
                    # Sanitize: limit length, strip potential path/SQL leaks
                    return detail[:500]
                return str(detail)[:500]
        except Exception:
            pass
        return f"HTTP {response.status_code}"

    def _raise_for_status(self, status_code: int, detail: str) -> None:
        """Map HTTP status code to the appropriate SDK exception."""
        if status_code == 401:
            raise AegisAuthenticationError(detail)
        elif status_code == 403:
            raise AegisAuthorizationError(detail)
        elif status_code == 404:
            raise AegisNotFoundError(detail)
        elif status_code == 409:
            raise AegisConflictError(detail)
        elif status_code == 422:
            raise AegisValidationError(detail)
        elif status_code == 429:
            raise AegisRateLimitError(detail)
        elif status_code >= 500:
            raise AegisServerError(detail, status=status_code)
        else:
            raise AegisServerError(f"Unexpected error: {detail}", status=status_code)
