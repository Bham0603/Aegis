from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.domain.attack_lab import AttackRunResult, AttackScenario
from app.domain.audit import AuditEvent
from app.models.attack_lab import AttackRunDB
from app.services.attack_lab.runner import AttackRunner
from app.services.attack_lab.scenarios import SCENARIOS_REGISTRY
from app.services.audit_service import AuditService

router = APIRouter()


class RunScenarioRequest(BaseModel):
    scenario_id: str


@router.get("/scenarios", response_model=list[AttackScenario])
async def list_scenarios() -> list[AttackScenario]:
    """Returns all available attack lab scenarios."""
    return list(SCENARIOS_REGISTRY.values())


@router.get("/scenarios/{scenario_id}", response_model=AttackScenario)
async def get_scenario(scenario_id: str) -> AttackScenario:
    """Returns a specific scenario by ID."""
    scenario = SCENARIOS_REGISTRY.get(scenario_id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found"
        )
    return scenario


@router.post("/runs", response_model=AttackRunResult)
async def run_scenario(
    request: RunScenarioRequest, db: AsyncSession = Depends(get_db)
) -> AttackRunResult:
    """Executes a scenario and returns the result."""
    if request.scenario_id not in SCENARIOS_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found"
        )

    runner = AttackRunner(db)
    result = await runner.run(request.scenario_id)
    return result


@router.get("/runs/{run_id}", response_model=AttackRunResult)
async def get_run(run_id: str, db: AsyncSession = Depends(get_db)) -> AttackRunResult:
    """Retrieves the result of a specific attack run."""
    stmt = select(AttackRunDB).where(AttackRunDB.run_id == run_id)
    result = await db.execute(stmt)
    record = result.scalars().first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Run not found"
        )

    return AttackRunResult.model_validate(record.payload)


@router.get("/runs/{run_id}/events", response_model=list[AuditEvent])
async def get_run_events(
    run_id: str, db: AsyncSession = Depends(get_db)
) -> list[AuditEvent]:
    """Retrieves the audit events associated with a specific run."""
    stmt = select(AttackRunDB).where(AttackRunDB.run_id == run_id)
    result = await db.execute(stmt)
    record = result.scalars().first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Run not found"
        )

    audit_svc = AuditService(db)
    events = await audit_svc.get_correlation_history(record.correlation_id)
    return events
