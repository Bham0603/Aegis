from app.services.audit_service import AuditService


def test_audit_redaction_simple_fields():
    payload = {
        "user_id": "usr_123",
        "password": "supersecretpassword",
        "api_key": "sk-12345",
        "normal_key": "safe_value",
    }

    redacted = AuditService.redact_parameters(payload)

    assert redacted["user_id"] == "usr_123"
    assert redacted["password"] == "[REDACTED]"
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["normal_key"] == "safe_value"


def test_audit_redaction_nested_dict():
    payload = {
        "config": {
            "token": "secret_token",
            "db_host": "localhost",
            "authorization": "Bearer token123",
        }
    }

    redacted = AuditService.redact_parameters(payload)

    assert redacted["config"]["token"] == "[REDACTED]"
    assert redacted["config"]["db_host"] == "localhost"
    assert redacted["config"]["authorization"] == "[REDACTED]"


def test_audit_redaction_nested_lists():
    payload = {
        "queries": [
            {"query": "SELECT *", "secret_token": "abc"},
            {"query": "DELETE *", "password": "def"},
        ],
        "list_of_passwords": ["p1", "p2"],
    }

    redacted = AuditService.redact_parameters(payload)

    assert redacted["queries"][0]["secret_token"] == "[REDACTED]"
    assert redacted["queries"][0]["query"] == "SELECT *"
    assert redacted["queries"][1]["password"] == "[REDACTED]"

    # "list_of_passwords" key has "password" in it, so the entire list is redacted
    assert redacted["list_of_passwords"] == "[REDACTED]"
