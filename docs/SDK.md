# Aegis SDK

The Aegis Python SDK is a developer-friendly client layer for integrating Aegis security and governance into your AI agents. It handles secure communication with the Aegis backend while ensuring credentials remain private and operations fail-close gracefully on error.

## Installation

```bash
pip install ./sdk
```

## Setup

The SDK requires your backend URL and an API key. You can pass them directly to the client or use environment variables.

```python
import os
from aegis_sdk import AegisClient

client = AegisClient(
    base_url=os.getenv("AEGIS_URL", "http://localhost:8000"),
    api_key=os.getenv("AEGIS_API_KEY"),
    max_retries=3  # Handles transient network errors
)
```

## Protecting Functions

The easiest way to secure a function is with the `@protect` decorator. This intercepts calls, sends the tool context and arguments to the Aegis backend, and only executes the function if Aegis replies with an `ALLOW`.

```python
from aegis_sdk import protect, ActionBlockedError, ApprovalRequiredError

@protect(client, agent_id="agent-123", tool_id="read_file")
async def read_file(filepath: str) -> str:
    with open(filepath, "r") as f:
        return f.read()

try:
    content = await read_file("/etc/passwd")
except ActionBlockedError as e:
    print(f"Action blocked by Aegis: {e.reasons}")
except ApprovalRequiredError as e:
    print(f"Human review required. Approval ID: {e.approval_request_id}")
```

For more dynamic use cases, use the `ProtectedTool` wrapper:

```python
from aegis_sdk import ProtectedTool

safe_tool = ProtectedTool(
    client=client,
    func=my_dangerous_function,
    agent_id="agent-123",
    tool_id="sql_query"
)

await safe_tool.invoke(query="DROP TABLE users;") # This will raise an ActionBlockedError
```

## MCP Integration

Aegis provides native security for the Model Context Protocol (MCP) by acting as a secure gateway for MCP Client sessions. For more details, see [MCP Security](MCP_SECURITY.md).

```python
from mcp import ClientSession
from aegis_sdk.integrations import AegisMCPGateway

# session is a standard MCP ClientSession
secure_session = AegisMCPGateway(
    session=session,
    aegis_client=client,
    agent_id="my-agent-uuid",
    session_id="my-session-uuid"
)

# Securely call tools; Aegis intercepts and validates the call.
result = await secure_session.call_tool("read_file", {"path": "/etc/passwd"})
```

## Evaluating Actions Manually

If you need full control over the evaluation flow, you can call the evaluation endpoint directly:

```python
result = await client.evaluate_action(
    agent_id="agent-123",
    tool_id="shell_exec",
    tool_args={"command": "rm -rf /"},
    agent_context={"intent": "delete all files"}
)

if result.allowed:
    # Safe to execute
    pass
else:
    print(f"Decision: {result.decision}")
    print(f"Risk Level: {result.risk_level}")
    if result.threat:
        print(f"Threat Detected: {result.threat.type} - {result.threat.severity}")
```

## Security & Fail-Closed Design

The SDK is strictly a client. It does **not** evaluate risk, check permissions, or make final security decisions locally. All logic is handled by the authoritative Aegis backend.

- **Fail-closed**: If the backend is unreachable or returns a server error, the SDK will exhaust its retries and raise an `AegisUnavailableError`. Protected tools will refuse to run.
- **Privacy**: The SDK actively scrubs credentials from its structured logging. Exceptions and `repr` outputs never leak your API key.
