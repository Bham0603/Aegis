# Aegis SDK

Python SDK for **Aegis — Runtime Security & Governance for AI Agents**.

## Installation

```bash
pip install aegis-sdk
```

For LangChain integration:

```bash
pip install aegis-sdk[langchain]
```

## Quick Start

```python
from aegis_sdk import AegisClient

async with AegisClient(base_url="http://localhost:8000", api_key="your-key") as client:
    result = await client.evaluate_action(
        agent_id="research-agent",
        tool_id="database",
        operation="query",
        resource="customers",
        environment="production",
    )

    if result.allowed:
        print("Action permitted")
    elif result.review_required:
        print(f"Approval needed: {result.approval_request_id}")
    elif result.blocked:
        print(f"Blocked: {result.reasons}")
```

See [docs/SDK.md](../docs/SDK.md) for full documentation.
