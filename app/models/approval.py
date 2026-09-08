"""
Database models for approval requests and approver identity.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class ApprovalStatusDB(str, PyEnum):
    """Database enum for approval status."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class ApprovalRequestDB(Base):
    """
    Persistent storage for approval requests.

    Security invariants enforced at the database level:
    - approval_request_id is unique and immutable
    - action_id is immutable after creation
    - action_fingerprint is immutable after creation
    - Foreign keys ensure referential integrity
    - Indexes support fast lookup by action_id and status
    """

    __tablename__ = "approval_request"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Business identifier (matches domain model approval_request_id)
    approval_request_id: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    # Action binding (immutable)
    action_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    action_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)

    # Correlation
    correlation_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)

    # Identity context
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("session.id", ondelete="CASCADE"), nullable=False
    )

    # Action context
    tool_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tool.id", ondelete="CASCADE"), nullable=False
    )
    operation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resource: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    environment: Mapped[str] = mapped_column(String(255), nullable=False)

    # Approval lifecycle
    status: Mapped[ApprovalStatusDB] = mapped_column(
        Enum(ApprovalStatusDB),
        default=ApprovalStatusDB.PENDING,
        nullable=False,
        index=True,
    )

    # Approver identity
    required_approver_role: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    approver_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Timestamps (all UTC)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Security context (from decision engine)
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    highest_threat_severity: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )

    # Explanation and resolution
    reasons: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    resolution_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Audit metadata
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class ApproverDB(Base):
    """
    Approver identity registry.

    For MVP, this is a simple table. In future phases, this will integrate
    with enterprise SSO, RBAC, and separation-of-duties policies.

    Security invariants:
    - approver_id is unique
    - An approver cannot have the same ID as an agent (enforced in application layer)
    """

    __tablename__ = "approver"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Business identifier (used in approval decisions)
    approver_id: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    # Display information
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Authorization
    roles: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
