"""
Safe diagnostic logging for the Aegis SDK.

NEVER logs: API keys, bearer tokens, passwords, private keys, sensitive parameters.
DOES log: action_id, correlation_id, decision, latency_ms, http_status.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("aegis_sdk")

# Patterns that should never appear in log output
_SENSITIVE_KEYS = frozenset({
    "api_key", "apikey", "api-key",
    "token", "bearer", "secret",
    "password", "passwd", "pwd",
    "private_key", "privatekey",
    "authorization",
})


def _is_sensitive(key: str) -> bool:
    """Check if a key name looks like it could contain credentials."""
    return key.lower().replace("-", "_") in _SENSITIVE_KEYS


def safe_log_fields(**kwargs: Any) -> dict[str, Any]:
    """
    Filter a dict of log fields, redacting values for sensitive keys.
    Returns a new dict safe for logging.
    """
    result: dict[str, Any] = {}
    for key, value in kwargs.items():
        if _is_sensitive(key):
            result[key] = "***redacted***"
        else:
            result[key] = value
    return result


def log_request(method: str, url: str, *, correlation_id: str | None = None) -> None:
    """Log an outgoing SDK request (safe — no credentials)."""
    fields = safe_log_fields(method=method, url=url, correlation_id=correlation_id)
    logger.debug("aegis_sdk_request", extra=fields)


def log_response(
    status_code: int,
    *,
    latency_ms: float | None = None,
    correlation_id: str | None = None,
    action_id: str | None = None,
    decision: str | None = None,
) -> None:
    """Log a backend response (safe — no credentials)."""
    fields = safe_log_fields(
        status_code=status_code,
        latency_ms=latency_ms,
        correlation_id=correlation_id,
        action_id=action_id,
        decision=decision,
    )
    logger.debug("aegis_sdk_response", extra=fields)


def log_error(error_type: str, error_message: str, *, status_code: int | None = None) -> None:
    """Log an SDK error (safe — no credentials)."""
    fields = safe_log_fields(
        error_type=error_type,
        error_message=error_message,
        status_code=status_code,
    )
    logger.warning("aegis_sdk_error", extra=fields)
