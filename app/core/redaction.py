from typing import Any

SENSITIVE_KEYS = {
    "password",
    "token",
    "secret",
    "key",
    "authorization",
    "bearer",
    "access_token",
    "api_key",
    "private_key",
}


def redact_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively redact sensitive values from a dictionary.
    Keys that match our known sensitive list will have their values replaced.
    """
    if not isinstance(parameters, dict):
        return parameters

    redacted: dict[str, Any] = {}
    for k, v in parameters.items():
        if isinstance(v, dict):
            redacted[k] = redact_parameters(v)
        elif isinstance(v, list):
            redacted[k] = [
                redact_parameters(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            if any(sensitive_key in k.lower() for sensitive_key in SENSITIVE_KEYS):
                redacted[k] = "[REDACTED]"
            else:
                redacted[k] = v

    return redacted
