from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.domain.audit import AuditEvent
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("/events", response_model=list[AuditEvent])
async def list_audit_events(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    event_type: str | None = None,
    agent_id: str | None = None,
    user_id: str | None = None,
    decision: str | None = None,
):
    audit_svc = AuditService(db)
    return await audit_svc.list_events(
        limit=limit,
        offset=offset,
        event_type=event_type,
        agent_id=agent_id,
        user_id=user_id,
        decision=decision,
    )


@router.get("/events/{event_id}", response_model=AuditEvent)
async def get_audit_event(event_id: str, db: Annotated[AsyncSession, Depends(get_db)]):
    audit_svc = AuditService(db)
    event = await audit_svc.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Audit event not found")
    return event


@router.get("/actions/{action_id}", response_model=list[AuditEvent])
async def get_action_history(
    action_id: str, db: Annotated[AsyncSession, Depends(get_db)]
):
    audit_svc = AuditService(db)
    events = await audit_svc.get_action_history(action_id)
    return events


@router.get("/correlations/{correlation_id}", response_model=list[AuditEvent])
async def get_correlation_history(
    correlation_id: str, db: Annotated[AsyncSession, Depends(get_db)]
):
    audit_svc = AuditService(db)
    events = await audit_svc.get_correlation_history(correlation_id)
    return events
