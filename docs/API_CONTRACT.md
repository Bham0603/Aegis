# API Contract

The Aegis Security Gateway operates primarily as a REST API. This ensures it remains framework-agnostic and can be integrated into LangChain, LlamaIndex, direct HTTP clients, or future MCP routers.

## 1. Core Evaluation Endpoint

### `POST /api/v1/actions/evaluate`

**Purpose**: Called by an Agent (via a middleware SDK) *before* attempting to execute a tool.

**Request Body**:
```json
{
  "agent_id": "agt_123",
  "user_id": "usr_456",
  "session_id": "ses_789",
  "tool_id": "database.delete",
  "operation": "delete",
  "resource": "production_db",
  "environment": "production",
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
  "risk_level": "HIGH",
  "reasons": ["Destructive operation in production environment"],
  "approval_required": true,
  "approval_request_id": "app_555"
}
```

## 2. Registry Endpoints
- `POST /api/v1/agents` — Register an agent
- `GET /api/v1/agents/{id}` — Get agent details
- `POST /api/v1/users` — Register a user
- `GET /api/v1/users/{id}` — Get user details
- `POST /api/v1/tools` — Register a tool
- `GET /api/v1/tools/{id}` — Get tool details
- `POST /api/v1/sessions` — Create a session
- `GET /api/v1/sessions/{id}` — Get session details

## 3. Policy Management Endpoints
- `GET /api/v1/policies` — List active policies
- `POST /api/v1/policies` — Create a policy
- `GET /api/v1/policies/{id}` — Get policy details
- `PUT /api/v1/policies/{id}` — Update a policy
- `DELETE /api/v1/policies/{id}` — Delete a policy

## 4. Approval Endpoints
- `GET /api/v1/approvals/{id}` — Get approval request
- `POST /api/v1/approvals/{id}/resolve` — Approve or deny a request
- `POST /api/v1/approvers` — Register an approver
- `GET /api/v1/approvers/{id}` — Get approver details

## 5. Audit Endpoints (Read-Only)
- `GET /api/v1/audit/events` — List events (supports pagination and filtering)
  - Query params: `limit` (1-100), `offset`, `event_type`, `agent_id`, `user_id`, `decision`
- `GET /api/v1/audit/events/{event_id}` — Get a specific audit event
- `GET /api/v1/audit/actions/{action_id}` — Get all events for an action (deterministic timestamp ordering)
- `GET /api/v1/audit/correlations/{correlation_id}` — Get all events for a correlation (deterministic timestamp ordering)

> **Note**: There are intentionally no PUT, PATCH, DELETE, or POST endpoints for audit records. Audit events are append-only by design.
