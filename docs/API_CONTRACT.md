# API Contract (Conceptual)

The Aegis Security Gateway operates primarily as a REST API. This ensures it remains framework-agnostic and can be integrated into LangChain, LlamaIndex, direct HTTP clients, or future MCP routers.

## 1. Core Evaluation Endpoint

### `POST /v1/actions/evaluate`

**Purpose**: Called by an Agent (via a middleware SDK) *before* attempting to execute a tool.

**Request Body**:
```json
{
  "agent_id": "agt_123",
  "session_id": "ses_789",
  "tool_id": "database.delete",
  "operation": "delete",
  "resource": "production_db",
  "parameters": {
    "table": "users",
    "condition": "last_login < '2020-01-01'"
  }
}
```

**Response**:
```json
{
  "action_id": "act_abc123",
  "decision": "REVIEW",
  "risk_score": 85,
  "reasons": ["Destructive operation in production environment"],
  "approval_request_id": "app_555"
}
```

## 2. Policy Management Endpoints
Admin-only endpoints for managing the deterministic ruleset.
- `GET /v1/policies`
- `POST /v1/policies`
- `PUT /v1/policies/{policy_id}`

## 3. Approval Endpoints
Endpoints used by the Web Dashboard or VS Code extension to manage Human-in-the-Loop workflows.
- `GET /v1/approvals/pending`
- `POST /v1/approvals/{approval_id}/decide`
  ```json
  {
    "decision": "APPROVED",
    "comment": "Looks safe."
  }
  ```

## 4. Telemetry / Audit Endpoints
- `GET /v1/audit/events`
- `GET /v1/audit/events/{action_id}`

## 5. Agent & Tool Registry Endpoints
- `POST /v1/agents` (Register a new AI actor and its allowed scopes)
- `POST /v1/tools` (Register a new capability and mark sensitive schema fields)
