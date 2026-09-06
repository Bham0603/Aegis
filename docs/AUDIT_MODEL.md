# Audit & Telemetry Model

Aegis is designed to provide forensic-level visibility into autonomous AI operations. The Audit Engine records a structured event for every evaluated Action, regardless of the final decision.

## 1. Audit Event Structure
An Audit Event is an immutable record combining the original `Action` context with the resulting `SecurityDecision`.

```json
{
  "event_id": "evt_999...",
  "timestamp": "2026-09-06T10:05:01Z",
  "correlation_id": "trace_abc",
  
  "actor": {
    "user_id": "usr_456",
    "agent_id": "agt_123",
    "session_id": "ses_789"
  },
  
  "target": {
    "tool_id": "database.query",
    "operation": "delete",
    "resource": "production_db",
    "environment": "production"
  },
  
  "action_metadata": {
    "redacted_arguments": true,
    "arguments_hash": "sha256:abcd..."
  },
  
  "evaluation": {
    "decision": "BLOCK",
    "risk_score": 85,
    "matched_policies": ["pol_prod_delete_block"],
    "threat_signals": []
  },
  
  "approval_context": null
}
```

## 2. Redaction & Data Protection
To comply with security and privacy standards (e.g., SOC2, GDPR, HIPAA):
- Aegis **NEVER** casually logs API keys, passwords, or raw credentials.
- Sensitive arguments marked by the Tool schema are scrubbed from the `Action` payload before logging.
- When an argument is redacted, a cryptographic hash (e.g., SHA-256) of the original value is logged instead. This allows security teams to verify if an agent repeatedly attempted to use the *exact same* malicious payload without storing the payload itself in plain text.

## 3. Retention & Integrity
- Audit events are written asynchronously to prevent blocking the execution path.
- In a production deployment, these structured JSON logs are intended to be ingested by enterprise SIEMs (e.g., Splunk, Datadog) or stored in cold storage (e.g., AWS S3) for long-term retention.
- Future phases will implement cryptographic signing of audit logs to guarantee non-repudiation.
