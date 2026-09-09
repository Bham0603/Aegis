# Security Principles

The Aegis architecture and future codebase must strictly adhere to the following principles. Any technical decision that violates these principles should be rejected.

## 1. Never Trust the LLM for Authorization
The LLM is an execution engine, not an enforcement mechanism. System prompts can be overridden, and instructions can be hallucinated. Aegis must evaluate all actions in an independent, deterministic environment that the LLM cannot manipulate.

## 2. Secure Defaults & Fail-Closed
In the event of an engine failure (e.g., Policy Engine timeout, missing risk scoring data, Approval Engine unavailable), Aegis must default to `BLOCK`. Security-sensitive failures must never fail-open.

## 3. Least Privilege
Agents should only have access to the exact tools and resources required for their current task. The Policy Engine must evaluate actions based on the intersection of the User's permissions, the Agent's configured scope, and the Environment constraints.

## 4. Deterministic Enforcement
While ML models may be used in the future to surface threat anomalies, the actual decision to ALLOW or BLOCK must rely on explainable, deterministic criteria (e.g., Policy Rule #45 matched). 

## 5. Explicit Authorization
Human-in-the-loop approvals must be explicitly bound to a specific, immutable `Action` payload. Approvals cannot be generic "allow all" tokens, and they must have strict expiration times.

## 6. Strong Validation & Typed Interfaces
All incoming `Action` requests from agents must be strictly validated against registered schemas. Aegis must reject malformed, unexpected, or excessively large arguments before they reach the evaluation pipeline.

## 7. No Hardcoded Secrets
The Aegis codebase must never contain hardcoded secrets, API keys, or default passwords. All secrets must be injected via secure environment variables or secret management systems.

## 8. Structured and Redacted Audit Logs
Every security decision must be logged as a structured event. To prevent data leakage, raw credentials, sensitive PII, or full sensitive payloads must be redacted before being written to the audit log. The current implementation replaces sensitive field values with `[REDACTED]`. Cryptographic hashing of redacted values (e.g., SHA-256) is planned for a future phase.

## 9. Testable Security
Security controls are only as good as their tests. The codebase must include explicit policy tests, risk engine tests, and adversarial integration tests that prove unauthorized actions are correctly blocked.
