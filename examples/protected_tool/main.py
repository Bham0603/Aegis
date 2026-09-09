"""
Protected Tool Example

Demonstrates using the @protect decorator to automatically
intercept tool calls, validate them with Aegis, and enforce
fail-closed security.
"""

import asyncio
import os

from aegis_sdk import AegisClient, protect
from aegis_sdk.errors import (
    ActionBlockedError,
    AegisUnavailableError,
    ApprovalRequiredError,
)

# Initialize the Aegis client
client = AegisClient(
    base_url=os.getenv("AEGIS_URL", "http://localhost:8000"),
    api_key=os.getenv("AEGIS_API_KEY", "dev-api-key")
)


# The @protect decorator automatically intercepts calls to this function.
# It evaluates the arguments against the Aegis backend using the specified agent/tool IDs.
@protect(client, agent_id="db-agent", tool_id="execute_query")
async def execute_query(query: str) -> str:
    """Executes a SQL query against the production database."""
    print(f"[Executing] -> {query}")
    return "Query executed successfully."


async def main():
    print("Attempting a safe query...")
    try:
        await execute_query("SELECT * FROM users WHERE status = 'active';")
    except Exception as e:
        print(f"Error: {e}")

    print("\nAttempting a dangerous query...")
    try:
        # This should trigger an Aegis block (assuming a SQL injection or destructive action policy)
        await execute_query("DROP TABLE users;")
    except ActionBlockedError as e:
        print("Blocked!")
        print(f"Reasons: {e.reasons}")
    except ApprovalRequiredError as e:
        print("Approval required.")
        print(f"Approval ID: {e.approval_request_id}")
    except AegisUnavailableError:
        print("Aegis is unreachable. The action was blocked safely (fail-closed).")


if __name__ == "__main__":
    asyncio.run(main())
