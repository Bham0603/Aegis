# Audit & Observability Model

Aegis provides forensic-level visibility into autonomous AI operations. The Audit layer records a structured event for every evaluated Action, preserving the complete decision provenance for later forensic reconstruction.

## 1. Audit Event Structure

An Audit Event is an **append-oriented persisted record** combining the original `Action` context with the resulting security evaluation provenance.

```json
{
  "event_id": "evt_act123_eval",
  "event_version": "1.0",
  "event_type": "ACTION_EVALUATED",
  "timestamp": "2026-09-08T10:05:01Z",
  "correlation_id": "trace_abc",
  "action_id": "act_123",

  "user_id": "usr_456",
  "agent_id": "agt_123",
  "session_id": "ses_789",

  "tool_id": "database.query",
  "operation": "delete",
  "resource": "production_db",
  "environment": "production",

  "permission_result": "GRANTED",
  "trust_result": "TRUSTED",
  "policy_result": "ALLOW",
  "risk_score": 85,
  "risk_level": "HIGH",
  "threat_severity": "MEDIUM",
  "approval_result": "REQUESTED",

  "final_decision": "REVIEW",
  "decision_reasons": [
    "Matched Policy 'prod_delete' (Priority 100) -> ALLOW",
    "Risk Threshold: REVIEW required due to HIGH risk score (85)."
  ],

  "redacted_parameters": {
    "table": "users",
    "password": "[REDACTED]"
  }
}
```

## 2. Event Types

| Event Type | Emitted By | Purpose |
|---|---|---|
| `ACTION_RECEIVED` | Gateway | Records initial action interception |
| `ACTION_EVALUATED` | Evaluator | Records full security decision with provenance |
| `APPROVAL_REQUESTED` | Evaluator | Records approval request creation |
| `APPROVAL_APPROVED` | Approval Service | Records approval resolution |
| `APPROVAL_DENIED` | Approval Service | Records denial resolution |
| `APPROVAL_EXPIRED` | Approval Service | Records expiration |
| `SECURITY_EVALUATION_FAILED` | Evaluator | Records evaluation failures |

## 3. Decision Provenance (IMPLEMENTED)

Each `ACTION_EVALUATED` event preserves the following provenance:

| Field | Source | Description |
|---|---|---|
| `permission_result` | PermissionEngine | GRANTED, DENIED, or INSUFFICIENT |
| `trust_result` | TrustEngine | TRUSTED, INTERNAL, UNKNOWN, or BLOCKED |
| `policy_result` | PolicyEngine | ALLOW, BLOCK, or REVIEW |
| `risk_score` | RiskEngine | 0-100 integer |
| `risk_level` | RiskEngine | LOW, MODERATE, HIGH, or CRITICAL |
| `threat_severity` | ThreatEngine | LOW, MEDIUM, HIGH, CRITICAL, or null |
| `approval_result` | Evaluator | REQUESTED, BYPASSED, or NONE |
| `final_decision` | Evaluator | ALLOW, REVIEW, or BLOCK |
| `decision_reasons` | Evaluator | List of human-readable explanation strings |

The audit layer **records** these values as produced by the evaluation pipeline. It does **not** recalculate them.

## 4. Redaction & Data Protection (IMPLEMENTED)

Sensitive parameters are **redacted** (replaced with `[REDACTED]`) before persistence. The current implementation:

- **REDACT**: Fields matching keywords: `password`, `token`, `secret`, `api_key`, `authorization`
- **REDACT**: Nested dictionaries are recursively processed
- **REDACT**: Lists whose key matches a sensitive keyword are replaced entirely with `[REDACTED]`
- **SAFE**: Lists of dicts have each dict recursively processed
- **SAFE**: Non-sensitive fields are stored as-is
- **OMIT**: Raw credentials are never stored — the original unredacted payload is not persisted

> **FUTURE**: Cryptographic hashing (SHA-256) of redacted values is not currently implemented. The current implementation uses simple omission/replacement. Adding hash-based verification of redacted values is planned for a future phase.

> **LIMITATION**: The keyword matching is substring-based. Field names like `private_key` do not currently match because the keyword set is `{password, token, secret, api_key, authorization}`. Expanding the keyword set is straightforward but requires careful review.

## 5. Persistence Model (IMPLEMENTED)

- Events are persisted to the `audit_events` SQL table via SQLAlchemy
- Indexed columns: `event_id`, `event_type`, `timestamp`, `correlation_id`, `action_id`, `user_id`, `agent_id`, `session_id`, `final_decision`
- The full event payload is stored as JSON in the `payload` column for complete provenance
- String IDs (not foreign keys) are used for actor/target references, ensuring historical records survive entity state changes

## 6. Audit Failure Semantics (IMPLEMENTED)

- Audit persistence failure is caught and logged via `structlog` (`audit_persistence_failed`)
- Failure **cannot** turn BLOCK into ALLOW — audit runs **after** the security decision
- The database transaction is rolled back on failure
- The security decision is returned to the caller regardless of audit success
- Audit failures are **observable** through structured logging

## 7. Read-Only API (IMPLEMENTED)

The audit API exposes only read endpoints. No PUT, PATCH, DELETE, or POST mutation endpoints exist for audit records.

## 8. Integrity & Retention

- Audit events are written synchronously in the evaluation path, not asynchronously
- In a production deployment, structured JSON logs are intended for SIEM ingestion or cold storage

> **FUTURE**: Cryptographic tamper-evidence (hash chaining, signing) is not currently implemented. The current system provides **append-oriented persisted audit events** without cryptographic integrity guarantees. Implementing a hash chain or Merkle tree for non-repudiation is planned for a future phase.
