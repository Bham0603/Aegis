import structlog
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.normalization import normalize_action
from app.core.redaction import redact_parameters
from app.schemas.gateway import ActionRequest, SecurityDecision
from app.services.evaluator import evaluate_action

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post(
    "/evaluate", response_model=SecurityDecision, summary="Evaluate Agent Action"
)
async def evaluate_action_endpoint(
    request: Request, payload: ActionRequest, db: AsyncSession = Depends(get_db)
) -> SecurityDecision:
    """
    Primary interception point for all AI Agent actions.
    Normalizes the payload, redacts sensitive parameters, logs the intent securely,
    and routes the action through the Security Evaluation Pipeline.
    """
    # 1. Extract context
    correlation_id = request.state.correlation_id

    # 2. Normalize to Domain Model
    action = normalize_action(payload, correlation_id)

    # 3. Redact for safe audit logging
    safe_parameters = redact_parameters(action.parameters)
    logger.info(
        "Action intercepted",
        action_id=action.action_id,
        correlation_id=action.correlation_id,
        agent_id=action.agent_id,
        tool_id=action.tool_id,
        operation=action.operation,
        environment=action.environment,
        parameters=safe_parameters,
    )

    # 4. Evaluate Action
    decision = await evaluate_action(action, db)

    # 5. Log Decision securely
    logger.info(
        "Action evaluated",
        action_id=decision.action_id,
        correlation_id=decision.correlation_id,
        decision=decision.decision.value,
        reasons=decision.reasons,
    )

    return decision
