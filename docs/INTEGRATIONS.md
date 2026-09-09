# Aegis Agent Integrations

The Aegis SDK provides out-of-the-box integrations for popular agent frameworks, making it easy to add runtime security without refactoring your existing agent logic.

## LangChain Integration

The `AegisLangChainTool` allows you to wrap existing LangChain `BaseTool` instances. It intercepts invocations, validates them against the Aegis backend, and enforces the security decision.

### Setup

```python
from langchain.tools import tool
from aegis_sdk import AegisClient
from aegis_sdk.integrations.langchain import AegisLangChainTool

# 1. Define your LangChain tool
@tool
def execute_sql(query: str) -> str:
    """Executes a SQL query against the database."""
    # ... execution logic ...
    return "Results..."

# 2. Initialize the Aegis client
client = AegisClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# 3. Wrap the tool
safe_sql_tool = AegisLangChainTool.wrap(
    client=client,
    tool=execute_sql,
    agent_id="analytics-bot"
)

# 4. Give the tool to your LangChain agent
# agent = initialize_agent(tools=[safe_sql_tool], ...)
```

### Error Handling

If Aegis blocks the action or demands human approval, the wrapper raises standard LangChain `ToolException` errors, ensuring the agent's internal loop handles the rejection gracefully (e.g., retrying with different parameters or reporting the block to the user).

- **Blocks**: Raised as a `ToolException` containing the block reasons (e.g., "SQL Injection detected").
- **Approvals**: Raised as a `ToolException` indicating an approval is pending.
- **Unavailability**: Raised as a `ToolException` if the Aegis backend is unreachable, ensuring fail-closed safety.

To enable the agent to catch these errors and continue, ensure you configure the underlying tool appropriately (e.g., `handle_tool_error=True` in standard LangChain setups).

## Model Context Protocol (MCP)

The `AegisMCPGateway` wraps the standard MCP Python SDK's `ClientSession`. By routing MCP calls through Aegis, you enforce security policies, human-in-the-loop approvals, and runtime threat detection for all tools accessed via the Model Context Protocol.

For setup and details, please refer to the dedicated [MCP Security](MCP_SECURITY.md) documentation.
