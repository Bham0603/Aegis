from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.tool_operation import ToolOperation
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class ToolStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class Tool(Base):
    __tablename__ = "tool"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    canonical_name: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    provider: Mapped[str | None] = mapped_column(String, nullable=True)
    trust_classification: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[ToolStatus] = mapped_column(
        Enum(ToolStatus), default=ToolStatus.ACTIVE, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    operations: Mapped[list["ToolOperation"]] = relationship(
        "ToolOperation", back_populates="tool", cascade="all, delete-orphan"
    )
