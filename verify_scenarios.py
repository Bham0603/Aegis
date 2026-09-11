import asyncio
import os

from aegis_sdk.client import AegisClient
from aegis_sdk.errors import (
    ActionBlockedError,
    AegisUnavailableError,
    ApprovalRequiredError,
)

from app.services.attack_lab.scenarios import SCENARIOS


async def run_scenario(client, scenario):
    print(f"\n[{scenario.scenario_id}] {scenario.name}")
    try:
        res = await client.evaluate_action(
            agent_id=scenario.synthetic_inputs["agent_id"],
            tool_id=scenario.synthetic_inputs["tool_id"],
            operation=scenario.synthetic_inputs["operation"],
            parameters=scenario.synthetic_inputs.get("parameters", {}),
            session_id=scenario.synthetic_inputs.get("session_id", "test_session")
        )
        print(f"-> Decision: {res.decision}")
        if res.reasons:
            print(f"-> Reasons: {res.reasons}")
    except ActionBlockedError as e:
        print(f"-> ActionBlockedError: {e.reasons}")
    except ApprovalRequiredError as e:
        print(f"-> ApprovalRequiredError: {e.reasons}")
    except AegisUnavailableError as e:
        print(f"-> AegisUnavailableError: {e}")
    except Exception as e:
        print(f"-> Exception: {e}")


async def main():
    client = AegisClient(base_url="http://localhost:8000", api_key="demo-key")
    mcp_scenarios = [s for s in SCENARIOS if "mcp" in s.scenario_id]
    
    print(f"Found {len(mcp_scenarios)} MCP scenarios.")
    for s in mcp_scenarios:
        await run_scenario(client, s)
        
    await client.close()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
