import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class PrincipalDB(Base):
    __tablename__ = "api_principals"

    id = Column(
        String(50), primary_key=True, default=lambda: f"prn_{uuid.uuid4().hex[:8]}"
    )
    name = Column(String(255), nullable=False)
    principal_type = Column(String(50), nullable=False)
    api_key_hash = Column(String(255), nullable=False, index=True)
    roles = Column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, server_default="[]"
    )  # Use JSONB for list of roles
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
