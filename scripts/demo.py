import asyncio
import os
import sys
import logging

from aegis_sdk.client import AegisClient
from aegis_sdk.errors import ActionBlockedError, ApprovalRequiredError, AegisUnavailableError

# Add the parent directory to the path so we can import the scenarios
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.services.attack_lab.scenarios import SCENARIOS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("aegis_demo")

async def run_scenario(client, scenario):
    logger.info(f"--- SCENARIO: [{scenario.scenario_id}] {scenario.name} ---")
    try:
        res = await client.evaluate_action(
            agent_id=scenario.synthetic_inputs["agent_id"],
            tool_id=scenario.synthetic_inputs["tool_id"],
            operation=scenario.synthetic_inputs["operation"],
            parameters=scenario.synthetic_inputs.get("parameters", {}),
            session_id=scenario.synthetic_inputs.get("session_id", "demo_session")
        )
        logger.info(f"Decision: {res.decision}")
        if res.reasons:
            logger.info(f"Reasons: {res.reasons}")
    except ActionBlockedError as e:
        logger.warning(f"BLOCKED: {e.reasons}")
    except ApprovalRequiredError as e:
        logger.info(f"REVIEW REQUIRED (ID: {e.approval_request_id}): {e.reasons}")
    except AegisUnavailableError as e:
        logger.error(f"AEGIS UNAVAILABLE: {e}")
    except Exception as e:
        logger.error(f"UNEXPECTED ERROR: {e}")

async def run_mcp_examples():
    """Run the MCP Gateway example directly to show real integration."""
    logger.info("--- RUNNING FULL MCP GATEWAY EXAMPLE ---")
    
    # We can just import and run the main function from the MCP example
    from examples.mcp_gateway.main import main as mcp_main
    
    # We need to temporarily suppress its asyncio.run
    original_run = asyncio.run
    try:
        asyncio.run = lambda coro: None  # mock it out so we can await it ourselves if it was synchronous, but it's not.
        await mcp_main()
    except Exception as e:
        logger.error(f"MCP Gateway demo failed: {e}")
    finally:
        asyncio.run = original_run

async def main():
    logger.info("===========================================")
    logger.info("  Aegis Runtime Security & Governance Demo ")
    logger.info("===========================================")
    
    client = AegisClient(
        base_url=os.getenv("AEGIS_URL", "http://localhost:8000"),
        api_key=os.getenv("AEGIS_API_KEY", "demo-key"),
        max_retries=1
    )
    
    logger.info("1. Running System Configuration Scenarios (Allow, Block, Review)...")
    for s in SCENARIOS:
        await run_scenario(client, s)
        await asyncio.sleep(0.5)  # slight pause for readability
        
    logger.info("\n2. Launching End-to-End MCP Security Gateway Demo...")
    await run_mcp_examples()
    
    await client.close()
    logger.info("===========================================")
    logger.info("  Demo Complete.                           ")
    logger.info("===========================================")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
