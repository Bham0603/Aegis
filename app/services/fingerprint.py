"""
Action fingerprinting service for approval binding.

Generates deterministic cryptographic fingerprints of actions to ensure
approvals cannot be reused for different actions (action substitution attack).

Security Requirements:
1. Same action -> same fingerprint
2. Different security-relevant actions -> different fingerprints
3. Deterministic (no randomness, no timestamp, no ordering dependencies)
4. Canonicalization before hashing
5. Safe handling of sensitive parameters
"""

import hashlib
import json
from typing import Any

from app.domain.action import Action


def _canonicalize_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Canonicalize a dictionary for deterministic serialization.

    - Sorts keys recursively
    - Handles nested dictionaries
    - Preserves None values
    - Does not include random/variable fields

    Args:
        data: Dictionary to canonicalize

    Returns:
        Canonicalized dictionary with sorted keys
    """
    if not isinstance(data, dict):
        return data

    result: dict[str, Any] = {}
    for key in sorted(data.keys()):
        value = data[key]
        if isinstance(value, dict):
            result[key] = _canonicalize_dict(value)
        elif isinstance(value, list):
            canonicalized_list: list[Any] = [
                _canonicalize_dict(item) if isinstance(item, dict) else item
                for item in value
            ]
            result[key] = canonicalized_list
        else:
            result[key] = value

    return result


def _redact_sensitive_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
    """
    Redact known sensitive parameter values while preserving structure.

    The fingerprint must detect parameter changes without storing raw secrets.
    We hash sensitive values individually rather than including them plainly.

    Args:
        parameters: Raw parameters from the action

    Returns:
        Parameters with sensitive values hashed
    """
    if not parameters:
        return {}

    # Known sensitive parameter names
    sensitive_keys = {
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
        "api-key",
        "credential",
        "auth",
        "authorization",
        "private_key",
        "privatekey",
    }

    result: dict[str, Any] = {}
    for key, value in parameters.items():
        key_lower = key.lower().replace("_", "").replace("-", "")

        # Check if this looks like a sensitive parameter
        is_sensitive = any(sens in key_lower for sens in sensitive_keys)

        if is_sensitive and isinstance(value, str):
            # Hash the sensitive value rather than including it
            value_hash = hashlib.sha256(value.encode("utf-8")).hexdigest()
            result[key] = f"REDACTED:{value_hash[:16]}"
        elif isinstance(value, dict):
            result[key] = _redact_sensitive_parameters(value)
        else:
            result[key] = value

    return result


def generate_action_fingerprint(action: Action) -> str:
    """
    Generate a deterministic cryptographic fingerprint for an action.

    The fingerprint includes all security-relevant fields that determine
    whether two actions are "the same" for approval purposes.

    Included fields:
    - action_id: The unique action identifier
    - agent_id: Who is requesting
    - user_id: On whose behalf
    - session_id: In which session
    - tool_id: What tool
    - operation: What operation
    - resource: On what resource
    - environment: In what environment
    - parameters: With what arguments (redacted)
    - authorization_context: With what auth context

    NOT included:
    - timestamp: Actions at different times can be the same
    - correlation_id: Observability identifier, not security-relevant

    Args:
        action: The action to fingerprint

    Returns:
        SHA-256 hex digest of the canonicalized action
    """
    # Build the fingerprint payload with security-relevant fields
    payload = {
        "action_id": action.action_id,
        "agent_id": action.agent_id,
        "user_id": action.user_id,
        "session_id": action.session_id,
        "tool_id": action.tool_id,
        "operation": action.operation,
        "resource": action.resource,
        "environment": action.environment,
        "parameters": _redact_sensitive_parameters(action.parameters),
        "authorization_context": _canonicalize_dict(action.authorization_context),
    }

    # Canonicalize to ensure deterministic ordering
    canonical_payload = _canonicalize_dict(payload)

    # Serialize to JSON with sorted keys (redundant but explicit)
    json_str = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"))

    # Generate SHA-256 hash
    fingerprint = hashlib.sha256(json_str.encode("utf-8")).hexdigest()

    return fingerprint


def verify_action_fingerprint(action: Action, expected_fingerprint: str) -> bool:
    """
    Verify that an action matches an expected fingerprint.

    This is the critical security check that prevents approval reuse.

    Args:
        action: The action to verify
        expected_fingerprint: The fingerprint from the approval request

    Returns:
        True if fingerprints match, False otherwise
    """
    actual_fingerprint = generate_action_fingerprint(action)
    return actual_fingerprint == expected_fingerprint
