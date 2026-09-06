# Action Model

The `Action` is the primary object that Aegis evaluates. It represents an Agent's intent to interact with the outside world.

Aegis does not hardcode application routes for specific tools (e.g., no `/api/execute-github-pr` endpoint). Instead, it relies on a highly normalized Action schema that can represent any tool, API, or MCP server request.

## Normalized Action Schema

An incoming `ActionRequest` must contain:

```json
{
  "action_id": "act_01HGW...",
  "correlation_id": "trace_...",
  "timestamp": "2026-09-06T10:00:00Z",
  
  "agent_id": "agt_...",
  "user_id": "usr_...",
  "session_id": "ses_...",
  
  "tool_id": "tool_github_api",
  "operation": "create_pr",
  "resource": "aegis-core-repo",
  
  "parameters": {
    "title": "Fix security vulnerability",
    "branch": "fix/auth-bypass",
    "body": "..."
  },
  
  "environment": "production",
  "authorization_context": {
    "authorization_tokens_present": false
  }
}
```

## Taxonomy & Structure
- **Tool**: The logical service (`github`, `database`, `filesystem`, `browser`).
- **Operation**: The verb (`read`, `write`, `update`, `delete`, `query`, `navigate`).
- **Resource**: The noun or specific target (`repository`, `users_table`, `/etc/passwd`).

## Argument Redaction Rules
Because the `Action` object flows through the Policy Engine, Risk Engine, and ultimately the Audit Logger, sensitive arguments MUST be managed carefully.

1. **Schema-defined Sensitivity**: When a Tool is registered with Aegis, specific argument fields can be marked as `sensitive=true`.
2. **Pre-evaluation Hashing**: If a field is sensitive, Aegis maintains the raw value in a secure, ephemeral cache (for actual execution if APPROVED), but replaces the value in the `Action` object with a hash or redaction mask (e.g., `[REDACTED_API_KEY]`) before it enters the logging and evaluation pipelines.
