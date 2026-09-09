"""
Aegis SDK exception hierarchy.

Maps HTTP status codes from the Aegis backend to typed SDK exceptions.
Never leaks API keys, credentials, backend stack traces, or internal paths.
"""

from __future__ import annotations


class AegisError(Exception):
    """Base exception for all Aegis SDK errors."""

    def __init__(self, message: str, *, status: int | None = None) -> None:
        # Scrub any accidental credential inclusion from the message
        self.status = status
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={str(self)!r}, status={self.status})"


class AegisAuthenticationError(AegisError):
    """401 — Missing or invalid API key / token."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, status=401)


class AegisAuthorizationError(AegisError):
    """403 — Authenticated but insufficient permissions."""

    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message, status=403)


class AegisNotFoundError(AegisError):
    """404 — Requested resource does not exist."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status=404)


class AegisValidationError(AegisError):
    """422 — Request payload failed validation."""

    def __init__(self, message: str = "Validation error", *, errors: list[dict] | None = None) -> None:
        self.errors = errors or []
        super().__init__(message, status=422)


class AegisConflictError(AegisError):
    """409 — Conflict (e.g. duplicate operation, state violation)."""

    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(message, status=409)


class AegisRateLimitError(AegisError):
    """429 — Rate limit exceeded."""

    def __init__(
        self, message: str = "Rate limit exceeded", *, retry_after: float | None = None
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message, status=429)


class AegisServerError(AegisError):
    """5xx — Aegis backend internal error."""

    def __init__(self, message: str = "Server error", *, status: int = 500) -> None:
        super().__init__(message, status=status)


class AegisNetworkError(AegisError):
    """Connection failure, DNS resolution, or other transport-level error."""

    def __init__(self, message: str = "Network error") -> None:
        super().__init__(message, status=None)


class AegisTimeoutError(AegisError):
    """Request exceeded the configured timeout."""

    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message, status=None)


class AegisUnavailableError(AegisError):
    """
    Aegis backend is unreachable or returned a transient failure
    after all retry attempts were exhausted.

    This is an EXPLICIT failure state — the SDK does NOT silently
    transform unavailability into ALLOW.
    """

    def __init__(self, message: str = "Aegis backend unavailable") -> None:
        super().__init__(message, status=None)


class ActionBlockedError(AegisError):
    """
    Raised by the protected tool wrapper when the backend returns BLOCK.
    The protected tool was NOT invoked.
    """

    def __init__(self, message: str = "Action blocked by Aegis", *, reasons: list[str] | None = None) -> None:
        self.reasons = reasons or []
        super().__init__(message, status=None)


class ApprovalRequiredError(AegisError):
    """
    Raised by the protected tool wrapper when the backend returns REVIEW.
    The protected tool was NOT automatically invoked — the caller must
    handle the approval workflow explicitly.
    """

    def __init__(
        self,
        message: str = "Approval required",
        *,
        approval_request_id: str | None = None,
        reasons: list[str] | None = None,
    ) -> None:
        self.approval_request_id = approval_request_id
        self.reasons = reasons or []
        super().__init__(message, status=None)
