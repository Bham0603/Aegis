import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.agent import Agent, AgentStatus
from app.models.agent_tool_binding import AgentToolBinding
from app.models.session import Session
from app.models.tool import Tool
from app.models.tool_operation import ToolOperation
from app.models.user import User, UserStatus
from app.models.user_agent_delegation import UserAgentDelegation
from app.schemas.registry import (
    AgentCreate,
    AgentToolBindingCreate,
    AgentUpdate,
    SessionCreate,
    SessionUpdate,
    ToolCreate,
    ToolUpdate,
    UserAgentDelegationCreate,
    UserCreate,
    UserUpdate,
)


class RegistryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- User Management ---
    async def create_user(self, user_in: UserCreate) -> User:
        user = User(
            ext_id=user_in.ext_id,
            display_name=user_in.display_name,
            status=user_in.status,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user(self, user_id: uuid.UUID) -> User | None:
        return await self.db.get(User, user_id)

    async def update_user(self, user_id: uuid.UUID, user_in: UserUpdate) -> User | None:
        user = await self.get_user(user_id)
        if not user:
            return None
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # --- Agent Management ---
    async def list_agents(
        self, skip: int = 0, limit: int = 100
    ) -> Sequence[Agent]:
        stmt = select(Agent).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_agent(self, agent_in: AgentCreate) -> Agent:
        agent = Agent(
            name=agent_in.name,
            description=agent_in.description,
            trust_classification=agent_in.trust_classification,
            status=agent_in.status,
        )
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def get_agent(self, agent_id: uuid.UUID) -> Agent | None:
        return await self.db.get(Agent, agent_id)

    async def update_agent(
        self, agent_id: uuid.UUID, agent_in: AgentUpdate
    ) -> Agent | None:
        agent = await self.get_agent(agent_id)
        if not agent:
            return None
        update_data = agent_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    # --- Tool Management ---
    async def list_tools(
        self, skip: int = 0, limit: int = 100
    ) -> Sequence[Tool]:
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Tool)
            .options(selectinload(Tool.operations))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_tool(self, tool_in: ToolCreate) -> Tool:
        tool = Tool(
            canonical_name=tool_in.canonical_name,
            description=tool_in.description,
            provider=tool_in.provider,
            trust_classification=tool_in.trust_classification,
            status=tool_in.status,
        )
        self.db.add(tool)
        await self.db.flush()

        for op in tool_in.operations:
            tool_op = ToolOperation(
                tool_id=tool.id,
                name=op.name,
                description=op.description,
            )
            self.db.add(tool_op)

        await self.db.commit()
        await self.db.refresh(tool, ["operations"])
        return tool

    async def get_tool(self, tool_id: uuid.UUID) -> Tool | None:
        stmt = (
            select(Tool)
            .options(selectinload(Tool.operations))
            .where(Tool.id == tool_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_tool(self, tool_id: uuid.UUID, tool_in: ToolUpdate) -> Tool | None:
        tool = await self.get_tool(tool_id)
        if not tool:
            return None
        update_data = tool_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tool, field, value)
        await self.db.commit()
        await self.db.refresh(tool, ["operations"])
        return tool

    # --- Agent-Tool Bindings ---
    async def bind_tool_to_agent(
        self, agent_id: uuid.UUID, binding_in: AgentToolBindingCreate
    ) -> AgentToolBinding:
        binding = AgentToolBinding(
            agent_id=agent_id,
            tool_id=binding_in.tool_id,
            enabled=binding_in.enabled,
            config_metadata=binding_in.config_metadata,
        )
        self.db.add(binding)
        await self.db.commit()
        await self.db.refresh(binding)
        return binding

    async def get_agent_bindings(
        self, agent_id: uuid.UUID
    ) -> Sequence[AgentToolBinding]:
        stmt = select(AgentToolBinding).where(AgentToolBinding.agent_id == agent_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # --- Session Management ---
    async def create_session(self, session_in: SessionCreate) -> Session:
        # Validate agent exists and is ACTIVE
        agent = await self.get_agent(session_in.agent_id)
        if not agent:
            raise ValueError("Agent not found")
        if agent.status != AgentStatus.ACTIVE:
            raise ValueError("Agent is not active")

        # Validate user if provided
        if session_in.user_id:
            user = await self.get_user(session_in.user_id)
            if not user:
                raise ValueError("User not found")
            if user.status != UserStatus.ACTIVE:
                raise ValueError("User is not active")

        session = Session(
            agent_id=session_in.agent_id,
            user_id=session_in.user_id,
            status=session_in.status,
            metadata_=session_in.metadata_,
            expires_at=session_in.expires_at,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session(self, session_id: uuid.UUID) -> Session | None:
        return await self.db.get(Session, session_id)

    async def update_session(
        self, session_id: uuid.UUID, session_in: SessionUpdate
    ) -> Session | None:
        session = await self.get_session(session_id)
        if not session:
            return None
        update_data = session_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(session, field, value)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    # --- User-Agent Delegation Management ---
    async def create_user_agent_delegation(
        self, delegation_in: UserAgentDelegationCreate
    ) -> UserAgentDelegation:
        delegation = UserAgentDelegation(
            user_id=delegation_in.user_id,
            agent_id=delegation_in.agent_id,
            enabled=delegation_in.enabled,
            expires_at=delegation_in.expires_at,
        )
        self.db.add(delegation)
        await self.db.commit()
        await self.db.refresh(delegation)
        return delegation

    async def get_user_agent_delegation(
        self, user_id: uuid.UUID, agent_id: uuid.UUID
    ) -> UserAgentDelegation | None:
        stmt = select(UserAgentDelegation).where(
            UserAgentDelegation.user_id == user_id,
            UserAgentDelegation.agent_id == agent_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
