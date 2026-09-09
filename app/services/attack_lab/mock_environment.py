import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent, AgentStatus
from app.models.agent_tool_binding import AgentToolBinding
from app.models.policy import Policy, PolicyStatus
from app.models.session import Session as AgentSession
from app.models.session import SessionStatus
from app.models.tool import Tool, ToolStatus
from app.models.user import User, UserStatus
from app.models.user_agent_delegation import UserAgentDelegation


class MockEnvironmentSeeder:
    """
    Seeds a deterministic, isolated mock environment for the Attack Lab.
    """

    MOCK_AGENT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
    MOCK_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
    MOCK_SESSION_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
    MOCK_TOOL_DB_QUERY_ID = uuid.UUID("00000000-0000-0000-0000-000000000004")
    MOCK_TOOL_DB_DELETE_ID = uuid.UUID("00000000-0000-0000-0000-000000000005")
    MOCK_TOOL_EXTERNAL_ID = uuid.UUID("00000000-0000-0000-0000-000000000006")
    MOCK_TOOL_POISON_ID = uuid.UUID("00000000-0000-0000-0000-000000000007")

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _clean_up(self) -> None:
        """Removes old mock entities."""
        await self.db.execute(
            delete(AgentToolBinding).where(
                AgentToolBinding.agent_id == self.MOCK_AGENT_ID
            )
        )
        await self.db.execute(
            delete(UserAgentDelegation).where(
                UserAgentDelegation.agent_id == self.MOCK_AGENT_ID
            )
        )
        await self.db.execute(
            delete(AgentSession).where(AgentSession.id == self.MOCK_SESSION_ID)
        )
        await self.db.execute(
            delete(Tool).where(
                Tool.id.in_(
                    [
                        self.MOCK_TOOL_DB_QUERY_ID,
                        self.MOCK_TOOL_DB_DELETE_ID,
                        self.MOCK_TOOL_EXTERNAL_ID,
                        self.MOCK_TOOL_POISON_ID,
                    ]
                )
            )
        )
        await self.db.execute(delete(User).where(User.id == self.MOCK_USER_ID))
        await self.db.execute(delete(Agent).where(Agent.id == self.MOCK_AGENT_ID))
        await self.db.execute(
            delete(Policy).where(Policy.name == "mock_production_policy")
        )

    async def seed(self) -> None:
        """Seeds the deterministic mock entities."""
        await self._clean_up()

        # Seed Agent
        agent = Agent(
            id=self.MOCK_AGENT_ID,
            name="mock_attack_lab_agent",
            description="Agent used for synthetic attack lab evaluations",
            status=AgentStatus.ACTIVE,
            trust_classification="LOW",
        )
        self.db.add(agent)

        # Seed User
        user = User(
            id=self.MOCK_USER_ID,
            ext_id="mock_user_123",
            display_name="Mock User",
            status=UserStatus.ACTIVE,
        )
        self.db.add(user)

        # Seed Tools
        tool_query = Tool(
            id=self.MOCK_TOOL_DB_QUERY_ID,
            canonical_name="database.query",
            description="Query the mock database",
            provider="mock_provider",
            trust_classification="MEDIUM",
            status=ToolStatus.ACTIVE,
        )
        tool_delete = Tool(
            id=self.MOCK_TOOL_DB_DELETE_ID,
            canonical_name="database.delete",
            description="Delete records from the mock database",
            provider="mock_provider",
            trust_classification="HIGH",
            status=ToolStatus.ACTIVE,
        )
        tool_external = Tool(
            id=self.MOCK_TOOL_EXTERNAL_ID,
            canonical_name="network.send",
            description="Send data to external sink",
            provider="mock_provider",
            trust_classification="LOW",
            status=ToolStatus.ACTIVE,
        )
        tool_poison = Tool(
            id=self.MOCK_TOOL_POISON_ID,
            canonical_name="tool.poisoned",
            description="A poisoned tool",
            provider="mock_provider",
            trust_classification="LOW",
            status=ToolStatus.ACTIVE,
        )
        self.db.add_all([tool_query, tool_delete, tool_external, tool_poison])

        # Bind Tools to Agent (Only query is allowed by default, delete/external not bound so permission will block)
        binding_query = AgentToolBinding(
            id=uuid.uuid4(),
            agent_id=self.MOCK_AGENT_ID,
            tool_id=self.MOCK_TOOL_DB_QUERY_ID,
            enabled=True,
            config_metadata={},
        )
        self.db.add(binding_query)

        # User-Agent Delegation
        delegation = UserAgentDelegation(
            id=uuid.uuid4(),
            user_id=self.MOCK_USER_ID,
            agent_id=self.MOCK_AGENT_ID,
            enabled=True,
        )
        self.db.add(delegation)

        # Seed Session
        session = AgentSession(
            id=self.MOCK_SESSION_ID,
            agent_id=self.MOCK_AGENT_ID,
            user_id=self.MOCK_USER_ID,
            status=SessionStatus.ACTIVE,
            metadata={},
        )
        self.db.add(session)

        # Seed Policy (Production protection policy)
        policy = Policy(
            id=uuid.uuid4(),
            name="mock_production_policy",
            description="Blocks destructive actions in production",
            version="1.0",
            status=PolicyStatus.ACTIVE,
            priority=100,
            rules=[
                {
                    "effect": "BLOCK",
                    "condition": {
                        "tool_id": {"eq": str(self.MOCK_TOOL_DB_DELETE_ID)},
                        "context.environment": {"eq": "production"},
                    },
                },
                {
                    "effect": "BLOCK",
                    "condition": {
                        "tool_id": {"eq": str(self.MOCK_TOOL_EXTERNAL_ID)},
                        "parameters.resource": {"eq": "SYNTHETIC_SECRET_001"},
                    },
                },
                {
                    "effect": "ALLOW",
                    "condition": {},
                },
            ],
        )
        self.db.add(policy)

        await self.db.commit()
