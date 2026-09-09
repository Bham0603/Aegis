from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditEventDB(Base):
    __tablename__ = "audit_events"

    event_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    event_version: Mapped[str] = mapped_column(String, nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    timestamp: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    correlation_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    action_id: Mapped[str] = mapped_column(String, nullable=True, index=True)

    # Actor Context
    user_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    agent_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    session_id: Mapped[str] = mapped_column(String, nullable=True, index=True)

    # Target Context
    tool_id: Mapped[str] = mapped_column(String, nullable=True)
    operation: Mapped[str] = mapped_column(String, nullable=True)
    resource: Mapped[str] = mapped_column(String, nullable=True)
    environment: Mapped[str] = mapped_column(String, nullable=True)

    # Provenance
    final_decision: Mapped[str] = mapped_column(String, nullable=True, index=True)

    # Detailed payload containing redacted parameters, specific reasons, sub-engine provenance
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
