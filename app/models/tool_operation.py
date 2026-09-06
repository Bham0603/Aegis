from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.tool import Tool
import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ToolOperation(Base):
    __tablename__ = "tool_operation"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tool_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tool.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    tool: Mapped["Tool"] = relationship("Tool", back_populates="operations")

    __table_args__ = (UniqueConstraint("tool_id", "name", name="uix_tool_id_name"),)
