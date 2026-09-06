# Glossary

- **Action**: A standardized, normalized request from an Agent to execute a specific Operation on a Resource using a Tool.
- **Agent**: An autonomous or semi-autonomous AI system that formulates plans and attempts to execute tools to achieve a goal.
- **Decision Engine**: The core Aegis component that aggregates inputs from all other engines to formulate an ALLOW, BLOCK, or REVIEW decision.
- **Human-in-the-Loop (HITL)**: A workflow requiring explicit human approval before an action is permitted to execute.
- **MCP (Model Context Protocol)**: An emerging standard for connecting AI models to external tools and context sources. Aegis treats MCP servers as highly relevant future integration targets.
- **Policy Engine**: A deterministic rule evaluator that checks an Action against predefined ALLOW, BLOCK, and REVIEW rules.
- **Prompt Injection**: An attack where malicious instructions are embedded in user input, causing the LLM to ignore its original system prompt and execute the attacker's intent.
- **Risk Engine**: A system that calculates a deterministic score (0-100) representing the potential danger of an Action.
- **Threat Engine**: A pluggable system designed to detect specific attack signatures (like data exfiltration or injection patterns) independent of the deterministic Policy Engine.
- **Tool Poisoning**: An attack where a compromised tool returns malicious data designed to exploit the agent (Indirect Prompt Injection).
