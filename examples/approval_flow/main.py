"""
Approval Flow Example

Demonstrates how to evaluate an action that triggers a human-in-the-loop
review process, and how to subsequently approve and retrieve the status.
"""

import asyncio
import os

from aegis_sdk import AegisClient
from aegis_sdk.models import Decision


async def main():
    client = AegisClient(
        base_url=os.getenv("AEGIS_URL", "http://localhost:8000"),
        api_key=os.getenv("AEGIS_API_KEY", "dev-api-key")
    )

    print("Evaluating an action that requires approval...")
    
    # In a real setup, this tool/agent combo would be covered by a policy
    # requiring human approval.
    result = await client.evaluate_action(
        agent_id="finance-agent",
        tool_id="wire_transfer",
        tool_args={"amount": 50000, "currency": "USD"},
        agent_context={"intent": "Paying monthly vendor invoice"}
    )

    if result.decision == Decision.REVIEW:
        approval_id = result.approval_request_id
        print(f"Action requires review! Approval Request ID: {approval_id}")
        
        # At this point, the agent would typically pause execution and notify a human.
        # Here, we simulate an administrator coming in and approving the request.
        
        print("\nSimulating administrator approval...")
        # Note: In Aegis, only human users can approve actions, so `approver_id`
        # should map to the human identity, not an agent.
        await client.approve(approval_id, approver_id="admin@example.com")
        print("Approved!")
        
        # Verify the status
        status = await client.get_approval(approval_id)
        print(f"Current Status: {status.status.value}")
        if status.status.value == "approved":
            print("You may now execute the action!")
    else:
        print(f"Decision was not REVIEW. It was {result.decision.value}.")


if __name__ == "__main__":
    asyncio.run(main())
