import uuid
from datetime import UTC, datetime

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.action import Action
from app.domain.context import SecurityContext
from app.domain.decision import (
    DecisionEnum,
    PermissionStatusEnum,
    SecurityDecision,
    TrustClassEnum,
)
from app.schemas.registry import (
    AgentResponse,
    AgentToolBindingResponse,
    SessionResponse,
    ToolResponse,
    UserAgentDelegationResponse,
    UserResponse,
)
from app.services.permission_engine import PermissionEngine
from app.services.policy_engine import PolicyEngine
from app.services.policy_service import PolicyService
from app.services.registry_service import RegistryService
from app.services.trust_engine import TrustEngine

logger = structlog.get_logger(__name__)


async def evaluate_action(action: Action, db: AsyncSession) -> SecurityDecision:
    """
    Evaluates the action through the Permission Engine, Trust Engine, and Policy Engine (Phase 5).
    Implements strict precedence and fail-closed behavior.
    """
    try:
        registry_svc = RegistryService(db)

        # 1. Fetch Context Entities
        agent_resp = None
        user_resp = None
        session_resp = None
        tool_resp = None
        binding_resp = None
        delegation_resp = None

        if action.agent_id:
            try:
                agent = await registry_svc.get_agent(uuid.UUID(action.agent_id))
                if agent:
                    agent_resp = AgentResponse.model_validate(agent)
            except ValueError:
                pass

        if action.user_id:
            try:
                user = await registry_svc.get_user(uuid.UUID(action.user_id))
                if user:
                    user_resp = UserResponse.model_validate(user)
            except ValueError:
                pass

        if action.session_id:
            try:
                session = await registry_svc.get_session(uuid.UUID(action.session_id))
                if session:
                    session_resp = SessionResponse.model_validate(session)
            except ValueError:
                pass

        if action.tool_id:
            try:
                tool = await registry_svc.get_tool(uuid.UUID(action.tool_id))
                if tool:
                    tool_resp = ToolResponse.model_validate(tool)
            except ValueError:
                pass

        if agent_resp and tool_resp:
            bindings = await registry_svc.get_agent_bindings(agent_resp.id)
            for b in bindings:
                if str(b.tool_id) == str(tool_resp.id):
                    binding_resp = AgentToolBindingResponse.model_validate(b)
                    break

        if agent_resp and user_resp:
            delegation = await registry_svc.get_user_agent_delegation(
                user_resp.id, agent_resp.id
            )
            if delegation:
                delegation_resp = UserAgentDelegationResponse.model_validate(delegation)

        # Build Context
        _context = SecurityContext(
            action=action,
            agent=agent_resp,
            user=user_resp,
            session=session_resp,
            tool=tool_resp,
            agent_tool_binding=binding_resp,
            user_agent_delegation=delegation_resp,
        )

        # 2. Evaluate Permissions
        permission_engine = PermissionEngine()
        permission_result = permission_engine.evaluate(_context)

        if permission_result.status == PermissionStatusEnum.DENIED:
            return SecurityDecision(
                action_id=action.action_id,
                correlation_id=action.correlation_id,
                timestamp=action.timestamp,
                decision=DecisionEnum.BLOCK,
                reasons=["Permission DENIED: " + " | ".join(permission_result.reasons)],
            )

        # 3. Evaluate Trust
        trust_engine = TrustEngine()
        trust_result = trust_engine.evaluate(_context)

        if trust_result.trust_class == TrustClassEnum.BLOCKED:
            return SecurityDecision(
                action_id=action.action_id,
                correlation_id=action.correlation_id,
                timestamp=action.timestamp,
                decision=DecisionEnum.BLOCK,
                reasons=["Trust Engine BLOCKED: " + " | ".join(trust_result.reasons)],
            )

        # 4. Fetch active policies
        policy_svc = PolicyService(db)
        policies = await policy_svc.get_active_policies()

        # 5. Evaluate using PolicyEngine
        # Inject trust_class into the context for Policy Engine
        eval_context = {
            "environment": action.environment,
            "trust_class": trust_result.trust_class.value,
        }

        eval_result = PolicyEngine.evaluate(
            action=action,
            policies=policies,  # type: ignore
            context=eval_context,
        )

        final_effect = eval_result["final_effect"]
        matched_rules = eval_result["matched_rules"]
        reasons = []

        if eval_result["default_deny"]:
            reasons.append("Default Deny: No matching policy found.")
        else:
            for match in matched_rules:
                reasons.append(
                    f"Matched Policy '{match['policy_name']}' (Priority {match['priority']}) -> {match['effect']}"
                )

        # Include trust reason info
        reasons.extend(trust_result.reasons)

        # 6. Evaluate Risk
        from app.services.risk_engine import RiskEngine

        risk_engine = RiskEngine()
        risk_assessment = risk_engine.assess(action, _context, trust_result)

        # 7. Evaluate Threat
        from app.domain.threat import ThreatSeverity
        from app.services.threat.engine import ThreatEngine

        threat_engine = ThreatEngine()
        threat_assessment = threat_engine.evaluate(action, _context)

        # 7.5. Evaluate AI Security Intelligence
        from app.domain.ai_security import AISecurityStatus
        from app.services.ai_security.engine import AISecurityIntelligence

        # We pass audit_svc below, but we haven't initialized it yet, let's initialize audit_svc early
        from app.services.audit_service import AuditService

        audit_svc = AuditService(db)

        ai_engine = AISecurityIntelligence(audit_svc=audit_svc)
        ai_assessment = await ai_engine.evaluate(action, _context)

        # Map PolicyEffect to DecisionEnum
        decision_val = DecisionEnum.BLOCK
        if final_effect == "ALLOW":
            decision_val = DecisionEnum.ALLOW
        elif final_effect == "REVIEW":
            decision_val = DecisionEnum.REVIEW
        elif final_effect == "BLOCK":
            decision_val = DecisionEnum.BLOCK

        # 8. Apply Risk and Threat Thresholds (if Policy says ALLOW)
        if decision_val == DecisionEnum.ALLOW:
            # Risk thresholds
            if risk_assessment.risk_score == 100:
                decision_val = DecisionEnum.BLOCK
                reasons.append(
                    "Risk Threshold: BLOCKED due to CRITICAL risk score of 100."
                )
            elif risk_assessment.risk_score > 75:
                decision_val = DecisionEnum.REVIEW
                reasons.append(
                    f"Risk Threshold: REVIEW required due to HIGH risk score ({risk_assessment.risk_score})."
                )

            # Deterministic Threat thresholds
            if threat_assessment.overall_severity == ThreatSeverity.CRITICAL:
                decision_val = DecisionEnum.BLOCK
                reasons.append(
                    "Threat Threshold: BLOCKED due to CRITICAL threat detection."
                )
            elif (
                threat_assessment.overall_severity == ThreatSeverity.HIGH
                and decision_val != DecisionEnum.BLOCK
            ):
                decision_val = DecisionEnum.REVIEW
                reasons.append(
                    "Threat Threshold: REVIEW required due to HIGH threat detection."
                )

        # 8.5 Apply AI Security Intelligence Precedence
        if (
            ai_assessment
            and ai_assessment.status == AISecurityStatus.SUCCESS
            and ai_assessment.threat_detected
        ):
            ai_severity = ai_assessment.severity
            ai_confidence = ai_assessment.confidence or 0.0

            # Define escalation threshold logic
            if ai_severity == ThreatSeverity.CRITICAL and ai_confidence >= 0.75:
                if decision_val in [DecisionEnum.ALLOW, DecisionEnum.REVIEW]:
                    decision_val = DecisionEnum.BLOCK
                    reasons.append(
                        f"AI Security Intelligence: BLOCKED due to {ai_severity.value} AI threat assessment ({ai_assessment.threat_type.value}, confidence {ai_confidence:.2f})."
                    )
            elif (
                ai_severity == ThreatSeverity.HIGH
                and ai_confidence >= 0.75
                and decision_val == DecisionEnum.ALLOW
            ):
                decision_val = DecisionEnum.REVIEW
                reasons.append(
                    f"AI Security Intelligence: REVIEW required due to {ai_severity.value} AI threat assessment ({ai_assessment.threat_type.value}, confidence {ai_confidence:.2f})."
                )

        reasons.append(
            f"Risk Assessment: {risk_assessment.risk_level.value} ({risk_assessment.risk_score})"
        )
        if threat_assessment.overall_severity:
            reasons.append(
                f"Threat Assessment: {threat_assessment.overall_severity.value}"
            )
        else:
            reasons.append("Threat Assessment: NONE")

        if ai_assessment and ai_assessment.threat_detected:
            reasons.append(
                f"AI Security Assessment: {ai_assessment.severity.value if ai_assessment.severity else 'UNKNOWN'}"
            )
        else:
            reasons.append("AI Security Assessment: NONE")

        highest_threat = (
            threat_assessment.overall_severity.value
            if threat_assessment.overall_severity
            else None
        )

        # 9. Handle REVIEW decision - check existing approvals or create new
        approval_required = decision_val == DecisionEnum.REVIEW
        approval_request_id = None

        if approval_required:
            from app.domain.approval import ApprovalStatus
            from app.services.approval_service import ApprovalService
            from app.services.fingerprint import generate_action_fingerprint

            approval_svc = ApprovalService(db)
            action_fp = generate_action_fingerprint(action)

            existing_req = await approval_svc.get_request_by_fingerprint(action_fp)

            if existing_req:
                if existing_req.status == ApprovalStatus.APPROVED:
                    is_valid, _ = await approval_svc.verify_approval(
                        action, existing_req.approval_request_id
                    )
                    if is_valid:
                        decision_val = DecisionEnum.ALLOW
                        approval_required = False
                        reasons.append(
                            f"REVIEW bypassed: Valid APPROVED request found ({existing_req.approval_request_id})"
                        )

                elif existing_req.status == ApprovalStatus.PENDING:
                    if not existing_req.is_expired(datetime.now(UTC)):
                        approval_request_id = existing_req.approval_request_id
                        reasons.append(
                            f"Using existing PENDING request: {approval_request_id}"
                        )

            if approval_required and not approval_request_id:
                temp_dec = SecurityDecision(
                    action_id=action.action_id,
                    correlation_id=action.correlation_id,
                    timestamp=action.timestamp,
                    decision=decision_val,
                    risk_score=risk_assessment.risk_score,
                    risk_level=risk_assessment.risk_level.value,
                    highest_threat_severity=highest_threat,
                    reasons=reasons,
                )
                new_req = await approval_svc.create_request(action, _context, temp_dec)
                approval_request_id = new_req.approval_request_id

            logger.info(
                "approval_required" if approval_required else "approval_bypassed",
                action_id=action.action_id,
                correlation_id=action.correlation_id,
                decision=decision_val.value,
                approval_request_id=approval_request_id,
            )

        decision_final = SecurityDecision(
            action_id=action.action_id,
            correlation_id=action.correlation_id,
            timestamp=action.timestamp,
            decision=decision_val,
            risk_score=risk_assessment.risk_score,
            risk_level=risk_assessment.risk_level.value,
            risk_explanation=risk_assessment.explanation,
            risk_factors=[f.model_dump() for f in risk_assessment.factors],
            highest_threat_severity=highest_threat,
            threat_results=[f.model_dump() for f in threat_assessment.findings],
            triggered_detectors=[f.detector_id for f in threat_assessment.findings],
            reasons=reasons,
            approval_required=approval_required,
            approval_request_id=approval_request_id,
        )

        # Emit Audit Event
        from app.domain.audit import AuditEvent, AuditEventType

        await audit_svc.log_event(
            AuditEvent(
                event_id=f"evt_{action.action_id}_eval",
                event_type=AuditEventType.ACTION_EVALUATED,
                timestamp=datetime.now(UTC),
                correlation_id=action.correlation_id,
                action_id=action.action_id,
                agent_id=action.agent_id,
                user_id=action.user_id,
                session_id=action.session_id,
                tool_id=action.tool_id,
                operation=action.operation,
                resource=action.resource,
                environment=action.environment,
                permission_result=permission_result.status.value,
                trust_result=trust_result.trust_class.value,
                policy_result=final_effect,
                risk_score=risk_assessment.risk_score,
                risk_level=risk_assessment.risk_level.value,
                threat_severity=highest_threat,
                ai_provider=ai_assessment.provider if ai_assessment else None,
                ai_model=ai_assessment.model if ai_assessment else None,
                ai_threat_type=ai_assessment.threat_type.value
                if ai_assessment
                else None,
                ai_severity=ai_assessment.severity.value
                if ai_assessment and ai_assessment.severity
                else None,
                ai_confidence=ai_assessment.confidence if ai_assessment else None,
                ai_status=ai_assessment.status.value if ai_assessment else None,
                approval_result="REQUESTED"
                if approval_required
                else ("BYPASSED" if approval_request_id else "NONE"),
                final_decision=decision_val.value,
                decision_reasons=reasons,
                redacted_parameters=AuditService.redact_parameters(action.parameters),
            )
        )
        return decision_final

    except Exception as e:
        logger.exception(
            "Security evaluation failure", error=str(e), action_id=action.action_id
        )
        # Fail-closed
        return SecurityDecision(
            action_id=action.action_id,
            correlation_id=action.correlation_id,
            timestamp=action.timestamp,
            decision=DecisionEnum.BLOCK,
            reasons=["Security evaluation failure (Fail-Closed)"],
        )
