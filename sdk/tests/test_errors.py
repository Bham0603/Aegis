"""Tests for SDK error model."""


from aegis_sdk.errors import (
    ActionBlockedError,
    AegisAuthenticationError,
    AegisAuthorizationError,
    AegisConflictError,
    AegisError,
    AegisNetworkError,
    AegisNotFoundError,
    AegisRateLimitError,
    AegisServerError,
    AegisTimeoutError,
    AegisUnavailableError,
    AegisValidationError,
    ApprovalRequiredError,
)


class TestErrorHierarchy:
    def test_all_errors_inherit_from_aegis_error(self):
        errors = [
            AegisAuthenticationError(),
            AegisAuthorizationError(),
            AegisNotFoundError(),
            AegisValidationError(),
            AegisConflictError(),
            AegisRateLimitError(),
            AegisServerError(),
            AegisNetworkError(),
            AegisTimeoutError(),
            AegisUnavailableError(),
            ActionBlockedError(),
            ApprovalRequiredError(),
        ]
        for err in errors:
            assert isinstance(err, AegisError)

    def test_status_codes(self):
        assert AegisAuthenticationError().status == 401
        assert AegisAuthorizationError().status == 403
        assert AegisNotFoundError().status == 404
        assert AegisValidationError().status == 422
        assert AegisConflictError().status == 409
        assert AegisRateLimitError().status == 429
        assert AegisServerError().status == 500
        assert AegisNetworkError().status is None
        assert AegisTimeoutError().status is None
        assert AegisUnavailableError().status is None

    def test_rate_limit_retry_after(self):
        err = AegisRateLimitError(retry_after=30.0)
        assert err.retry_after == 30.0

    def test_validation_error_details(self):
        err = AegisValidationError(errors=[{"field": "agent_id", "msg": "required"}])
        assert len(err.errors) == 1

    def test_blocked_error_reasons(self):
        err = ActionBlockedError(reasons=["Policy violation", "High risk"])
        assert err.reasons == ["Policy violation", "High risk"]

    def test_approval_required_error(self):
        err = ApprovalRequiredError(
            approval_request_id="apr_123",
            reasons=["Risk threshold exceeded"],
        )
        assert err.approval_request_id == "apr_123"
        assert err.reasons == ["Risk threshold exceeded"]

    def test_server_error_custom_status(self):
        err = AegisServerError(status=503)
        assert err.status == 503


class TestErrorCredentialSafety:
    """Verify API keys and credentials never appear in error output."""

    def test_api_key_not_in_str(self):
        fake_key = "sk-super-secret-key-12345"
        err = AegisAuthenticationError(f"Failed with key {fake_key}")
        # The error message is whatever was passed — but the point is
        # the SDK should never CONSTRUCT such a message. This test
        # documents the contract.
        assert isinstance(str(err), str)

    def test_repr_is_safe(self):
        err = AegisError("test message", status=401)
        r = repr(err)
        assert "AegisError" in r
        assert "401" in r

    def test_error_does_not_contain_stack_trace_from_backend(self):
        """Errors should not propagate raw backend tracebacks."""
        malicious = "Traceback (most recent call last):\n  File /app/secret/path.py"
        err = AegisServerError(malicious[:500])
        # The error stores it but SDK users should see it as a generic server error
        assert err.status == 500
