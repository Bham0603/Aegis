from app.core.redaction import redact_parameters


def test_redact_parameters_handles_sensitive_keys():
    payload = {
        "user_id": "123",
        "password": "supersecretpassword",
        "nested": {
            "api_key": "sk-12345",
            "normal": "value",
        },
        "list_of_secrets": [{"my_token": "abc"}],
    }

    redacted = redact_parameters(payload)

    assert redacted["user_id"] == "123"
    assert redacted["password"] == "[REDACTED]"
    assert redacted["nested"]["api_key"] == "[REDACTED]"
    assert redacted["nested"]["normal"] == "value"
    assert redacted["list_of_secrets"][0]["my_token"] == "[REDACTED]"
