# MVP Scope (Phase 1-9)

The MVP is designed to prove the core concept: intercepting an AI action, evaluating it deterministically, and returning a valid security decision without relying on an LLM for authorization.

## In Scope for MVP

1. **REST API Gateway**: Fast, validated endpoints for `Action` submission and evaluation.
2. **Deterministic Policy Engine**: Support for ALLOW, REVIEW, and BLOCK rules based on JSON configuration.
3. **Deterministic Risk Engine**: A hardcoded scoring matrix based on Action operation, environment, and tool trust.
4. **Decision Engine**: Logic to aggregate policy and risk into a final decision.
5. **Audit Logging**: Structured JSON logging of every decision to stdout / local database.
6. **Mock Tools**: A suite of synthetic tools (e.g., `mock_db_delete`, `mock_email_send`) to demonstrate evaluation. **No real destructive tools will be implemented.**
7. **Local Demo Environment**: A simple script representing an Agent attempting a dangerous action, resulting in an intercepted Aegis block/review.

## Explicit Non-Goals for MVP

To prevent scope creep and ensure timely delivery of the core security mechanics, the following are EXCLUDED from the MVP:

- **Kubernetes / Production Infrastructure**: The MVP will run entirely via local `docker-compose`.
- **Advanced Threat Detection (ML)**: We will not train or deploy anomaly detection models or LLM-based prompt injection detectors in the MVP.
- **Web Dashboard**: The human-in-the-loop review will be simulated via API calls in the MVP; the Next.js UI is reserved for later phases.
- **VS Code Extension**: Reserved for later phases.
- **MCP Server Support**: The MVP will use a generic REST schema for actions; strict MCP protocol parsing will come later.
- **Complex Enterprise Auth (SSO/SAML)**: The MVP will use hardcoded or simple JWT-based identity for testing.
