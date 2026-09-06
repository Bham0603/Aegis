from datetime import datetime, timezone

from app.core.normalization import normalize_action
from app.schemas.gateway import ActionRequest


def test_normalize_action_generates_identities():
    request = ActionRequest(
        agent_id="agt_1",
        session_id="ses_1",
        tool_id="test.tool",
        parameters={"k": "v"},
    )
    correlation_id = "trace_abc"

    action = normalize_action(request, correlation_id)

    assert action.action_id.startswith("act_")
    assert action.correlation_id == correlation_id
    assert action.agent_id == "agt_1"
    assert action.tool_id == "test.tool"
    assert action.parameters == {"k": "v"}
    assert isinstance(action.timestamp, datetime)
    assert action.timestamp.tzinfo == timezone.utc
