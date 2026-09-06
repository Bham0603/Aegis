import uuid
from datetime import UTC, datetime

from app.domain.action import Action
from app.domain.context import SecurityContext
from app.domain.decision import TrustClassEnum
from app.schemas.registry import AgentResponse, ToolResponse
from app.services.trust_engine import TrustEngine


def test_trust_engine_all_trusted():
    engine = TrustEngine()
    agent_id = uuid.uuid4()

    context = SecurityContext(
        action=Action(
            action_id="1",
            correlation_id="c1",
            timestamp=datetime.now(UTC),
            session_id=str(uuid.uuid4()),
            tool_id=str(uuid.uuid4()),
            agent_id=str(agent_id),
            operation="select",
            resource="table",
        ),
        agent=AgentResponse(
            id=agent_id,
            name="TestAgent",
            trust_classification="TRUSTED",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        tool=ToolResponse(
            id=uuid.uuid4(),
            canonical_name="TestTool",
            trust_classification="TRUSTED",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    )

    result = engine.evaluate(context)
    assert result.is_trusted is True
    assert result.trust_class == TrustClassEnum.TRUSTED


def test_trust_engine_blocked():
    engine = TrustEngine()
    agent_id = uuid.uuid4()

    context = SecurityContext(
        action=Action(
            action_id="1",
            correlation_id="c1",
            timestamp=datetime.now(UTC),
            session_id=str(uuid.uuid4()),
            tool_id=str(uuid.uuid4()),
            agent_id=str(agent_id),
            operation="select",
            resource="table",
        ),
        agent=AgentResponse(
            id=agent_id,
            name="TestAgent",
            trust_classification="TRUSTED",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        tool=ToolResponse(
            id=uuid.uuid4(),
            canonical_name="TestTool",
            trust_classification="BLOCKED",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    )

    result = engine.evaluate(context)
    assert result.is_trusted is False
    assert result.trust_class == TrustClassEnum.BLOCKED


def test_trust_engine_internal():
    engine = TrustEngine()
    agent_id = uuid.uuid4()

    context = SecurityContext(
        action=Action(
            action_id="1",
            correlation_id="c1",
            timestamp=datetime.now(UTC),
            session_id=str(uuid.uuid4()),
            tool_id=str(uuid.uuid4()),
            agent_id=str(agent_id),
            operation="select",
            resource="table",
        ),
        agent=AgentResponse(
            id=agent_id,
            name="TestAgent",
            trust_classification="INTERNAL",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        tool=ToolResponse(
            id=uuid.uuid4(),
            canonical_name="TestTool",
            trust_classification="TRUSTED",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    )

    result = engine.evaluate(context)
    assert result.is_trusted is True
    assert result.trust_class == TrustClassEnum.INTERNAL


def test_trust_engine_unknown():
    engine = TrustEngine()

    context = SecurityContext(
        action=Action(
            action_id="1",
            correlation_id="c1",
            timestamp=datetime.now(UTC),
            session_id=str(uuid.uuid4()),
            tool_id=str(uuid.uuid4()),
            agent_id=str(uuid.uuid4()),
            operation="select",
            resource="table",
        ),
        # Missing agent and tool means their trust classification defaults to UNKNOWN
    )

    result = engine.evaluate(context)
    assert result.is_trusted is False
    assert result.trust_class == TrustClassEnum.UNKNOWN
