import structlog

from app.core.config import settings
from app.domain.action import Action
from app.domain.ai_security import AISecurityAssessment, AISecurityStatus
from app.domain.audit import AuditEvent, AuditEventType
from app.domain.context import SecurityContext
from app.services.ai_security.mock_provider import MockAISecurityProvider
from app.services.ai_security.openai_provider import OpenAIAISecurityProvider
from app.services.ai_security.provider import BaseAISecurityProvider
from app.services.audit_service import AuditService

logger = structlog.get_logger(__name__)


class AISecurityIntelligence:
    """
    Orchestrates the AI Security Intelligence layer.
    """

    def __init__(self, audit_svc: AuditService | None = None):
        self.enabled = settings.AI_SECURITY_ENABLED
        self.provider_name = settings.AI_SECURITY_PROVIDER
        self.max_input_size = settings.AI_SECURITY_MAX_INPUT_SIZE
        self.audit_svc = audit_svc

        self.provider: BaseAISecurityProvider | None = None
        if self.enabled:
            if self.provider_name == "mock":
                self.provider = MockAISecurityProvider(
                    model_name=settings.AI_SECURITY_MODEL
                )
            elif self.provider_name == "openai_compatible":
                self.provider = OpenAIAISecurityProvider(
                    model_name=settings.AI_SECURITY_MODEL,
                    base_url=settings.AI_SECURITY_BASE_URL,
                    api_key=settings.AI_SECURITY_API_KEY,
                    timeout=settings.AI_SECURITY_TIMEOUT,
                )
            else:
                logger.warning(
                    "unknown_ai_security_provider", provider=self.provider_name
                )
                self.enabled = False

    async def evaluate(
        self, action: Action, context: SecurityContext
    ) -> AISecurityAssessment | None:
        """
        Evaluates the action using AI security intelligence if enabled.
        """
        if not self.enabled or not self.provider:
            return None

        # 1. Minimize and sanitize input
        raw_params = action.parameters or {}
        sanitized_params = AuditService.redact_parameters(raw_params)

        analysis_context = {
            "operation": action.operation,
            "resource": action.resource,
            "environment": action.environment,
            "parameters": sanitized_params,
        }

        # Add safe context pieces
        if context.tool:
            analysis_context["tool_description"] = context.tool.description

        # Serialize and enforce size limits
        import json

        try:
            context_str = json.dumps(analysis_context)
            if len(context_str) > self.max_input_size:
                # Naive truncation for now, could be smarter
                logger.warning(
                    "ai_security_input_truncated",
                    correlation_id=action.correlation_id,
                    size=len(context_str),
                )
                context_str = context_str[: self.max_input_size]
                analysis_context = {"truncated_raw": context_str}
        except (TypeError, ValueError) as e:
            logger.error(
                "ai_security_serialization_failed",
                correlation_id=action.correlation_id,
                error=str(e),
            )
            return None

        # 2. Emit Diagnostic Audit Event: STARTED
        if self.audit_svc:
            await self.audit_svc.log_event(
                AuditEvent(
                    event_id=f"evt_{action.action_id}_ai_start",
                    event_type=AuditEventType.AI_SECURITY_ANALYSIS_STARTED,
                    timestamp=action.timestamp,
                    correlation_id=action.correlation_id,
                    action_id=action.action_id,
                    metadata={
                        "provider": self.provider_name,
                        "model": settings.AI_SECURITY_MODEL,
                    },
                )
            )

        # 3. Call Provider
        try:
            assessment = await self.provider.analyze_security_context(
                action.correlation_id, analysis_context
            )
        except Exception as e:
            logger.exception("ai_security_unhandled_exception", error=str(e))
            assessment = AISecurityAssessment(
                assessment_id="ai_eval_failed",
                provider=self.provider_name,
                model=settings.AI_SECURITY_MODEL,
                status=AISecurityStatus.FAILED,
                reason="Unhandled exception during provider execution.",
            )

        # 4. Emit Diagnostic Audit Event: COMPLETED/FAILED
        if self.audit_svc:
            event_type = AuditEventType.AI_SECURITY_ANALYSIS_COMPLETED
            if assessment.status != AISecurityStatus.SUCCESS:
                if assessment.status == AISecurityStatus.UNAVAILABLE:
                    event_type = AuditEventType.AI_SECURITY_ANALYSIS_UNAVAILABLE
                else:
                    event_type = AuditEventType.AI_SECURITY_ANALYSIS_FAILED

            await self.audit_svc.log_event(
                AuditEvent(
                    event_id=f"evt_{action.action_id}_ai_comp",
                    event_type=event_type,
                    timestamp=action.timestamp,
                    correlation_id=action.correlation_id,
                    action_id=action.action_id,
                    ai_provider=assessment.provider,
                    ai_model=assessment.model,
                    ai_threat_type=assessment.threat_type.value,
                    ai_severity=assessment.severity.value
                    if assessment.severity
                    else None,
                    ai_confidence=assessment.confidence,
                    ai_status=assessment.status.value,
                    metadata={
                        "reason": assessment.reason,
                        "latency_ms": assessment.latency_ms,
                    },
                )
            )

        return assessment
