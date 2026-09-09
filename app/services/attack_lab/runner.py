import uuid
from datetime import UTC, datetime

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.normalization import normalize_action
from app.domain.attack_lab import AttackRunResult, AttackRunStatus
from app.models.attack_lab import AttackRunDB
from app.schemas.gateway import ActionRequest
from app.services.attack_lab.mock_environment import MockEnvironmentSeeder
from app.services.attack_lab.scenarios import SCENARIOS_REGISTRY
from app.services.evaluator import evaluate_action

logger = structlog.get_logger(__name__)


class AttackRunner:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.seeder = MockEnvironmentSeeder(db)

    async def run(self, scenario_id: str) -> AttackRunResult:
        scenario = SCENARIOS_REGISTRY.get(scenario_id)
        if not scenario:
            raise ValueError(f"Unknown scenario ID: {scenario_id}")

        run_id = f"run_{uuid.uuid4().hex}"
        correlation_id = f"corr_atk_{uuid.uuid4().hex}"
        started_at = datetime.now(UTC)

        try:
            # 1. Seed the mock environment
            await self.seeder.seed()

            # 2. Parse the Action
            action_req = ActionRequest(**scenario.synthetic_inputs)
            action = normalize_action(action_req, correlation_id)

            # 3. Evaluate the Action
            decision = await evaluate_action(action, self.db)

            # 4. Compare Actual vs Expected
            actual_outcome = decision.decision.value
            expected_outcome = scenario.expected_security_behavior

            if actual_outcome == expected_outcome:
                status = AttackRunStatus.PASS
            else:
                status = AttackRunStatus.FAIL

            # 5. Extract provenance
            # (Note: we use the fields from SecurityDecision and ThreatAssessment)
            explanation = " | ".join(decision.reasons)

            result = AttackRunResult(
                run_id=run_id,
                scenario_id=scenario_id,
                started_at=started_at,
                completed_at=datetime.now(UTC),
                correlation_id=correlation_id,
                expected_outcome=expected_outcome,
                actual_outcome=actual_outcome,
                status=status,
                permission_result=None,  # Extracted from logs or just leave None, not tightly bound in SecurityDecision response directly
                trust_result=None,
                policy_result=None,
                risk_score=decision.risk_score,
                risk_level=decision.risk_level,
                threat_severity=decision.highest_threat_severity,
                approval_result="REQUIRED" if decision.approval_required else "N/A",
                final_decision=decision.decision.value,
                triggered_detectors=decision.triggered_detectors or [],
                audit_event_ids=[
                    f"evt_{action.action_id}_recv",
                    f"evt_{action.action_id}_eval",
                ],
                explanation=explanation,
            )

        except Exception as e:  # noqa: BLE001
            logger.error("attack_run_error", error=str(e), scenario_id=scenario_id)
            result = AttackRunResult(
                run_id=run_id,
                scenario_id=scenario_id,
                started_at=started_at,
                completed_at=datetime.now(UTC),
                correlation_id=correlation_id,
                expected_outcome=scenario.expected_security_behavior,
                actual_outcome="ERROR",
                status=AttackRunStatus.ERROR,
                explanation=f"Execution error: {e!s}",
            )

        # 6. Save result to database
        try:
            run_db = AttackRunDB(
                run_id=result.run_id,
                scenario_id=result.scenario_id,
                status=result.status.value,
                expected_result=result.expected_outcome,
                actual_result=result.actual_outcome,
                correlation_id=result.correlation_id,
                started_at=result.started_at,
                completed_at=result.completed_at,
                payload=result.model_dump(mode="json"),
            )
            self.db.add(run_db)
            await self.db.commit()
        except Exception as db_err:  # noqa: BLE001
            logger.error("attack_run_persist_error", error=str(db_err))
            await self.db.rollback()

        return result
