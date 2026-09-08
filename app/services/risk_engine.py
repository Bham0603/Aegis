from app.domain.action import Action
from app.domain.context import SecurityContext
from app.domain.decision import TrustClassEnum, TrustResult
from app.domain.risk import (
    RiskAssessment,
    RiskFactor,
    RiskFactorCategoryEnum,
    RiskLevelEnum,
)


class RiskEngine:
    """
    Deterministic Explainable Risk Engine.
    Evaluates the security risk of an action and produces a RiskAssessment.
    """

    MODEL_VERSION = "1.0"

    def assess(
        self,
        action: Action,
        context: SecurityContext,
        trust_result: TrustResult | None = None,
    ) -> RiskAssessment:
        factors = []
        raw_score = 0

        # 1. Operation Sensitivity (Base Score)
        op_factor = self._evaluate_operation(action)
        factors.append(op_factor)
        raw_score += op_factor.contribution

        # 2. Environment Multiplier
        env_multiplier, env_factor = self._evaluate_environment(action)
        factors.append(env_factor)

        # Apply multiplier (only to base operation score so far, or to total?
        # Typically multiplier applies to base score or total raw score. Let's apply to raw_score)
        raw_score = int(raw_score * env_multiplier)

        # 3. Trust Contribution (Additive)
        if trust_result:
            trust_factor = self._evaluate_trust(trust_result)
            factors.append(trust_factor)
            raw_score += trust_factor.contribution

        # 4. External Destination Contribution (Additive)
        ext_factor = self._evaluate_external_destination(action)
        factors.append(ext_factor)
        raw_score += ext_factor.contribution

        # Clamp score between 0 and 100
        final_score = max(0, min(100, raw_score))

        # Determine risk level
        level = self._determine_risk_level(final_score)

        # Generate explanation
        explanation_lines = [
            f"Risk Score: {final_score}",
            f"Risk Level: {level.value}",
            "",
            "Factors:",
        ]
        for f in factors:
            prefix = "+" if f.contribution >= 0 else ""
            if f.category == RiskFactorCategoryEnum.ENVIRONMENT:
                # Special display for multiplier if needed, or just show the flat added contribution
                pass  # We already applied multiplier, so the "contribution" here might be misleading if we just say "multiplier".
                # Let's adjust env_factor to show its flat contribution difference, or just document the multiplier.
            explanation_lines.append(f"{prefix}{f.contribution:>3}  {f.reason}")

        explanation_lines.append("")
        explanation_lines.append(f"Total:\n{final_score}")

        explanation = "\n".join(explanation_lines)

        return RiskAssessment(
            risk_score=final_score,
            risk_level=level,
            factors=factors,
            explanation=explanation,
            model_version=self.MODEL_VERSION,
        )

    def _evaluate_operation(self, action: Action) -> RiskFactor:
        op = (action.operation or "").lower()
        if op in ["read", "search", "query", "get", "list"]:
            return RiskFactor(
                name="Read Operation",
                contribution=10,
                category=RiskFactorCategoryEnum.OPERATION_SENSITIVITY,
                reason="Read-only operation",
            )
        elif op in ["write", "update", "put", "patch", "create", "post"]:
            return RiskFactor(
                name="Write Operation",
                contribution=40,
                category=RiskFactorCategoryEnum.OPERATION_SENSITIVITY,
                reason="State-mutating operation",
            )
        elif op in ["delete", "drop", "truncate", "remove", "destroy"]:
            return RiskFactor(
                name="Destructive Operation",
                contribution=80,
                category=RiskFactorCategoryEnum.OPERATION_SENSITIVITY,
                reason="Destructive operation",
            )
        else:
            return RiskFactor(
                name="Unknown Operation",
                contribution=20,
                category=RiskFactorCategoryEnum.OPERATION_SENSITIVITY,
                reason="Unknown or unclassified operation",
            )

    def _evaluate_environment(self, action: Action) -> tuple[float, RiskFactor]:
        env = (action.environment or "").lower()
        if env in ["development", "dev", "local"]:
            return (
                0.5,
                RiskFactor(
                    name="Development Environment",
                    contribution=0,  # the multiplier handles the actual math, but we represent factor for explainability
                    category=RiskFactorCategoryEnum.ENVIRONMENT,
                    reason="Development environment (x0.5 multiplier)",
                ),
            )
        elif env in ["staging", "test", "qa"]:
            return 1.0, RiskFactor(
                name="Staging Environment",
                contribution=0,
                category=RiskFactorCategoryEnum.ENVIRONMENT,
                reason="Staging environment (x1.0 multiplier)",
            )
        elif env in ["production", "prod"]:
            return 1.5, RiskFactor(
                name="Production Environment",
                contribution=0,
                category=RiskFactorCategoryEnum.ENVIRONMENT,
                reason="Production environment (x1.5 multiplier)",
            )
        else:
            # Default to safest assumption for unknown
            return 1.5, RiskFactor(
                name="Unknown Environment",
                contribution=0,
                category=RiskFactorCategoryEnum.ENVIRONMENT,
                reason="Unknown environment (defaults to x1.5 multiplier)",
            )

    def _evaluate_trust(self, trust_result: TrustResult) -> RiskFactor:
        if trust_result.trust_class == TrustClassEnum.TRUSTED:
            return RiskFactor(
                name="Trusted Tool",
                contribution=0,
                category=RiskFactorCategoryEnum.TRUST,
                reason="Tool is trusted",
            )
        elif trust_result.trust_class == TrustClassEnum.INTERNAL:
            return RiskFactor(
                name="Internal Tool",
                contribution=5,
                category=RiskFactorCategoryEnum.TRUST,
                reason="Internal tool",
            )
        elif trust_result.trust_class == TrustClassEnum.EXTERNAL:
            return RiskFactor(
                name="External Tool",
                contribution=15,
                category=RiskFactorCategoryEnum.TRUST,
                reason="External tool",
            )
        elif trust_result.trust_class == TrustClassEnum.UNTRUSTED:
            return RiskFactor(
                name="Untrusted Tool",
                contribution=25,
                category=RiskFactorCategoryEnum.TRUST,
                reason="Untrusted or experimental tool",
            )
        else:
            # Unknown or Blocked (Blocked shouldn't reach here normally, but if it does, it's 0 contribution to risk score because it's blocked anyway, but let's give 20 for UNKNOWN)
            return RiskFactor(
                name="Unknown Trust",
                contribution=20,
                category=RiskFactorCategoryEnum.TRUST,
                reason="Unknown trust level",
            )

    def _evaluate_external_destination(self, action: Action) -> RiskFactor:
        # Heuristics: if resource contains http:// or https:// or tool is email, flag as external
        res = (action.resource or "").lower()
        tool = (action.tool_id or "").lower()
        if "http://" in res or "https://" in res or "email" in tool:
            return RiskFactor(
                name="External Destination",
                contribution=15,
                category=RiskFactorCategoryEnum.DESTINATION,
                reason="Action involves an external destination",
            )
        return RiskFactor(
            name="Internal Destination",
            contribution=0,
            category=RiskFactorCategoryEnum.DESTINATION,
            reason="Action remains internal",
        )

    def _determine_risk_level(self, score: int) -> RiskLevelEnum:
        if score <= 25:
            return RiskLevelEnum.LOW
        elif score <= 50:
            return RiskLevelEnum.MEDIUM
        elif score <= 85:
            return RiskLevelEnum.HIGH
        else:
            return RiskLevelEnum.CRITICAL
