import uuid
from datetime import UTC, datetime, timedelta

from app.domain.action import Action
from app.domain.context import SecurityContext
from app.domain.decision import PermissionStatusEnum
from app.models.agent import AgentStatus
from app.schemas.registry import (
    AgentResponse,
    AgentToolBindingResponse,
    SessionResponse,
    UserAgentDelegationResponse,
    UserResponse,
)
from app.services.permission_engine import PermissionEngine


def test_permission_engine_granted():
    engine = PermissionEngine()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()

    context = SecurityContext(
        action=Action(
            action_id="1",
            correlation_id="c1",
            timestamp=datetime.now(UTC),
            session_id=str(uuid.uuid4()),
            tool_id=str(uuid.uuid4()),
            agent_id=str(agent_id),
            user_id=str(user_id),
            operation="select",
            resource="table_a",
        ),
        agent=AgentResponse(
            id=agent_id,
            name="TestAgent",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        user=UserResponse(
            id=user_id,
            display_name="TestUser",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        session=SessionResponse(
            id=uuid.uuid4(),
            agent_id=agent_id,
            user_id=user_id,
            created_at=datetime.now(UTC),
        ),
        user_agent_delegation=UserAgentDelegationResponse(
            id=uuid.uuid4(),
            user_id=user_id,
            agent_id=agent_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        agent_tool_binding=AgentToolBindingResponse(
            id=uuid.uuid4(),
            agent_id=agent_id,
            tool_id=uuid.uuid4(),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            config_metadata={"allowed_operations": ["select"]},
        ),
    )

    result = engine.evaluate(context)
    assert result.status == PermissionStatusEnum.GRANTED


def test_permission_engine_denied_operation():
    engine = PermissionEngine()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()

    context = SecurityContext(
        action=Action(
            action_id="1",
            correlation_id="c1",
            timestamp=datetime.now(UTC),
            session_id=str(uuid.uuid4()),
            tool_id=str(uuid.uuid4()),
            agent_id=str(agent_id),
            user_id=str(user_id),
            operation="delete",
            resource="table_a",
        ),
        agent=AgentResponse(
            id=agent_id,
            name="TestAgent",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        user=UserResponse(
            id=user_id,
            display_name="TestUser",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        session=SessionResponse(
            id=uuid.uuid4(),
            agent_id=agent_id,
            user_id=user_id,
            created_at=datetime.now(UTC),
        ),
        user_agent_delegation=UserAgentDelegationResponse(
            id=uuid.uuid4(),
            user_id=user_id,
            agent_id=agent_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        agent_tool_binding=AgentToolBindingResponse(
            id=uuid.uuid4(),
            agent_id=agent_id,
            tool_id=uuid.uuid4(),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            config_metadata={"allowed_operations": ["select"]},
        ),
    )

    result = engine.evaluate(context)
    assert result.status == PermissionStatusEnum.DENIED
    assert "Operation 'delete' is not allowed" in result.reasons[0]


def test_permission_engine_denied_inactive_agent():
    engine = PermissionEngine()
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
            status=AgentStatus.DISABLED,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    )

    result = engine.evaluate(context)
    assert result.status == PermissionStatusEnum.DENIED
    assert "not ACTIVE" in result.reasons[0]


def test_permission_engine_denied_expired_delegation():
    engine = PermissionEngine()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()

    context = SecurityContext(
        action=Action(
            action_id="1",
            correlation_id="c1",
            timestamp=datetime.now(UTC),
            session_id=str(uuid.uuid4()),
            tool_id=str(uuid.uuid4()),
            agent_id=str(agent_id),
            user_id=str(user_id),
            operation="select",
            resource="table",
        ),
        agent=AgentResponse(
            id=agent_id,
            name="TestAgent",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        user=UserResponse(
            id=user_id,
            display_name="TestUser",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        user_agent_delegation=UserAgentDelegationResponse(
            id=uuid.uuid4(),
            user_id=user_id,
            agent_id=agent_id,
            expires_at=datetime.now(UTC) - timedelta(days=1),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    )

    result = engine.evaluate(context)
    assert result.status == PermissionStatusEnum.DENIED
    assert "has expired" in result.reasons[0]
