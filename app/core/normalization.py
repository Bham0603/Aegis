import uuid
from datetime import UTC, datetime

from app.domain.action import Action
from app.schemas.gateway import ActionRequest


def normalize_action(request: ActionRequest, correlation_id: str) -> Action:
    """
    Normalizes an API ActionRequest into a Domain Action.
    Injects generated identity (action_id), correlation context, and timestamp.
    """
    return Action(
        action_id=f"act_{uuid.uuid4().hex}",
        correlation_id=correlation_id,
        timestamp=datetime.now(UTC),
        agent_id=request.agent_id,
        session_id=request.session_id,
        user_id=request.user_id,
        tool_id=request.tool_id,
        operation=request.operation,
        resource=request.resource,
        parameters=request.parameters,
        environment=request.environment,
        authorization_context=request.authorization_context,
    )
