from enum import Enum

from pydantic import BaseModel, Field


class PrincipalType(str, Enum):
    HUMAN = "HUMAN"
    SERVICE = "SERVICE"
    ADMIN = "ADMIN"


class Role(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    APPROVER = "approver"
    AUDITOR = "auditor"
    AGENT = "agent"


class Principal(BaseModel):
    principal_id: str
    principal_type: PrincipalType
    roles: list[Role] = Field(default_factory=list)
    is_active: bool = True
