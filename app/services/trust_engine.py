from app.domain.context import SecurityContext
from app.domain.decision import TrustClassEnum, TrustResult


class TrustEngine:
    def evaluate(self, context: SecurityContext) -> TrustResult:
        """
        Evaluates the trust level of the action based on the agent and tool trust classifications.
        """
        reasons = []
        is_trusted = True
        overall_trust_class = TrustClassEnum.UNKNOWN

        agent_trust = (
            context.agent.trust_classification if context.agent else None
        ) or "UNKNOWN"
        tool_trust = (
            context.tool.trust_classification if context.tool else None
        ) or "UNKNOWN"

        agent_trust = agent_trust.upper()
        tool_trust = tool_trust.upper()

        if agent_trust == "BLOCKED" or tool_trust == "BLOCKED":
            is_trusted = False
            overall_trust_class = TrustClassEnum.BLOCKED
            reasons.append("Entity trust classification is BLOCKED.")
        elif agent_trust == "UNTRUSTED" or tool_trust == "UNTRUSTED":
            is_trusted = False
            overall_trust_class = TrustClassEnum.UNTRUSTED
            reasons.append("Entity trust classification is UNTRUSTED.")
        elif agent_trust == "EXTERNAL" or tool_trust == "EXTERNAL":
            is_trusted = True
            overall_trust_class = TrustClassEnum.EXTERNAL
            reasons.append("One or more entities have EXTERNAL trust classification.")
        elif agent_trust == "INTERNAL" or tool_trust == "INTERNAL":
            is_trusted = True
            overall_trust_class = TrustClassEnum.INTERNAL
            reasons.append("One or more entities have INTERNAL trust classification.")
        elif agent_trust == "TRUSTED" and tool_trust == "TRUSTED":
            is_trusted = True
            overall_trust_class = TrustClassEnum.TRUSTED
            reasons.append("All entities are TRUSTED.")
        else:
            is_trusted = False
            overall_trust_class = TrustClassEnum.UNKNOWN
            reasons.append(
                "Could not confidently determine trust class; defaulting to UNKNOWN/Untrusted."
            )

        return TrustResult(
            is_trusted=is_trusted, trust_class=overall_trust_class, reasons=reasons
        )
