import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.agent import AgentStatus
from app.models.session import SessionStatus
from app.models.tool import ToolStatus
from app.models.user import UserStatus


# --- User Schemas ---
class UserBase(BaseModel):
    ext_id: str | None = None
    display_name: str
    status: UserStatus = UserStatus.ACTIVE


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    display_name: str | None = None
    status: UserStatus | None = None


class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Agent Schemas ---
class AgentBase(BaseModel):
    name: str = Field(..., description="Unique name for the agent")
    description: str | None = None
    trust_classification: str | None = None
    status: AgentStatus = AgentStatus.ACTIVE


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    description: str | None = None
    trust_classification: str | None = None
    status: AgentStatus | None = None


class AgentResponse(AgentBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Tool Operation Schemas ---
class ToolOperationBase(BaseModel):
    name: str = Field(..., description="Name of the operation (e.g., query, insert)")
    description: str | None = None


class ToolOperationCreate(ToolOperationBase):
    pass


class ToolOperationResponse(ToolOperationBase):
    id: uuid.UUID
    tool_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


# --- Tool Schemas ---
class ToolBase(BaseModel):
    canonical_name: str = Field(..., description="Unique canonical name of the tool")
    description: str | None = None
    provider: str | None = None
    trust_classification: str | None = None
    status: ToolStatus = ToolStatus.ACTIVE


class ToolCreate(ToolBase):
    operations: list[ToolOperationCreate] = Field(default_factory=list)


class ToolUpdate(BaseModel):
    description: str | None = None
    provider: str | None = None
    trust_classification: str | None = None
    status: ToolStatus | None = None


class ToolResponse(ToolBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    operations: list[ToolOperationResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Agent-Tool Binding Schemas ---
class AgentToolBindingBase(BaseModel):
    enabled: bool = True
    config_metadata: dict[str, Any] | None = None


class AgentToolBindingCreate(AgentToolBindingBase):
    tool_id: uuid.UUID


class AgentToolBindingUpdate(BaseModel):
    enabled: bool | None = None
    config_metadata: dict[str, Any] | None = None


class AgentToolBindingResponse(AgentToolBindingBase):
    id: uuid.UUID
    agent_id: uuid.UUID
    tool_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Session Schemas ---
class SessionBase(BaseModel):
    agent_id: uuid.UUID
    user_id: uuid.UUID | None = None
    status: SessionStatus = SessionStatus.ACTIVE
    metadata_: dict[str, Any] | None = None
    expires_at: datetime | None = None


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    status: SessionStatus | None = None
    expires_at: datetime | None = None
    metadata_: dict[str, Any] | None = None


class SessionResponse(SessionBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- User-Agent Delegation Schemas ---
class UserAgentDelegationBase(BaseModel):
    user_id: uuid.UUID
    agent_id: uuid.UUID
    enabled: bool = True
    expires_at: datetime | None = None


class UserAgentDelegationCreate(UserAgentDelegationBase):
    pass


class UserAgentDelegationUpdate(BaseModel):
    enabled: bool | None = None
    expires_at: datetime | None = None


class UserAgentDelegationResponse(UserAgentDelegationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
