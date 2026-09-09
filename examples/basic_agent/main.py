"""
Basic Agent Example

Demonstrates manual action evaluation using the AegisClient.
This is useful when you want to handle the Aegis decision logic
yourself rather than relying on decorators or wrappers.
"""

import asyncio
import os

from aegis_sdk import AegisClient


async def main():
    # Initialize the client. In a real app, load from env vars.
    client = AegisClient(
        base_url=os.getenv("AEGIS_URL", "http://localhost:8000"),
        api_key=os.getenv("AEGIS_API_KEY", "dev-api-key")
    )

    print("Evaluating a safe action...")
    result = await client.evaluate_action(
        agent_id="test-agent",
        tool_id="read_file",
        tool_args={"path": "/var/log/app.log"},
        agent_context={"intent": "Checking logs for errors"}
    )
    
    print(f"Decision: {result.decision.value}")
    if result.allowed:
        print("Action is allowed. Executing...")
        # Actually run your tool here
    else:
        print(f"Blocked or needs review: {result.reasons}")

    print("\nEvaluating a dangerous action...")
    result2 = await client.evaluate_action(
        agent_id="test-agent",
        tool_id="shell_exec",
        tool_args={"command": "rm -rf /"},
        agent_context={"intent": "Freeing up disk space"}
    )

    print(f"Decision: {result2.decision.value}")
    print(f"Risk Level: {result2.risk_level.value}")
    if result2.threat:
        print(f"Threat Detected: {result2.threat.type.value} - {result2.threat.severity.value}")


if __name__ == "__main__":
    asyncio.run(main())
