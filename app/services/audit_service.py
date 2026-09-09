from typing import Any

import structlog
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.audit import AuditEvent
from app.models.audit import AuditEventDB

logger = structlog.get_logger(__name__)


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def redact_parameters(params: dict[str, Any]) -> dict[str, Any]:
        """
        Redacts sensitive fields based on exact match or heuristic names.
        """
        sensitive_keywords = {"password", "token", "secret", "api_key", "authorization"}
        redacted: dict[str, Any] = {}
        for k, v in params.items():
            if isinstance(v, dict):
                redacted[k] = AuditService.redact_parameters(v)
            elif isinstance(v, list):
                # We redact elements if they are dicts, otherwise leave primitive lists alone unless key matched
                if any(keyword in k.lower() for keyword in sensitive_keywords):
                    redacted[k] = "[REDACTED]"
                else:
                    redacted[k] = [
                        AuditService.redact_parameters(item)
                        if isinstance(item, dict)
                        else item
                        for item in v
                    ]
            elif any(keyword in k.lower() for keyword in sensitive_keywords):
                redacted[k] = "[REDACTED]"
            else:
                redacted[k] = v
        return redacted

    async def log_event(self, event: AuditEvent) -> None:
        """
        Safely persists the audit event. Failures are logged but not raised
        to prevent blocking the security flow.
        """
        try:
            event_db = AuditEventDB(
                event_id=event.event_id,
                event_version=event.event_version,
                event_type=event.event_type.value,
                timestamp=event.timestamp,
                correlation_id=event.correlation_id,
                action_id=event.action_id,
                user_id=event.user_id,
                agent_id=event.agent_id,
                session_id=event.session_id,
                tool_id=event.tool_id,
                operation=event.operation,
                resource=event.resource,
                environment=event.environment,
                final_decision=event.final_decision,
                payload=event.model_dump(mode="json"),
            )
            self.db.add(event_db)
            await self.db.commit()
            logger.info(
                "audit_event_created",
                event_id=event.event_id,
                event_type=event.event_type.value,
            )
        except Exception as e:  # noqa: BLE001
            logger.error(
                "audit_persistence_failed", error=str(e), event_id=event.event_id
            )
            await self.db.rollback()

    async def get_event(self, event_id: str) -> AuditEvent | None:
        stmt = select(AuditEventDB).where(AuditEventDB.event_id == event_id)
        result = await self.db.execute(stmt)
        record = result.scalars().first()
        if record:
            return AuditEvent.model_validate(record.payload)
        return None

    async def get_action_history(self, action_id: str) -> list[AuditEvent]:
        stmt = (
            select(AuditEventDB)
            .where(AuditEventDB.action_id == action_id)
            .order_by(AuditEventDB.timestamp.asc())
        )
        result = await self.db.execute(stmt)
        return [
            AuditEvent.model_validate(record.payload)
            for record in result.scalars().all()
        ]

    async def get_correlation_history(self, correlation_id: str) -> list[AuditEvent]:
        stmt = (
            select(AuditEventDB)
            .where(AuditEventDB.correlation_id == correlation_id)
            .order_by(AuditEventDB.timestamp.asc())
        )
        result = await self.db.execute(stmt)
        return [
            AuditEvent.model_validate(record.payload)
            for record in result.scalars().all()
        ]

    async def list_events(
        self,
        limit: int = 50,
        offset: int = 0,
        event_type: str | None = None,
        agent_id: str | None = None,
        user_id: str | None = None,
        decision: str | None = None,
    ) -> list[AuditEvent]:
        stmt = select(AuditEventDB).order_by(desc(AuditEventDB.timestamp))
        if event_type:
            stmt = stmt.where(AuditEventDB.event_type == event_type)
        if agent_id:
            stmt = stmt.where(AuditEventDB.agent_id == agent_id)
        if user_id:
            stmt = stmt.where(AuditEventDB.user_id == user_id)
        if decision:
            stmt = stmt.where(AuditEventDB.final_decision == decision)

        stmt = stmt.limit(min(limit, 100)).offset(offset)
        result = await self.db.execute(stmt)
        return [
            AuditEvent.model_validate(record.payload)
            for record in result.scalars().all()
        ]
