# Decision Model

## Phase 8 - Updated with Approval Integration

The Decision Engine is the final arbiter in the Aegis gateway. It aggregates inputs from the Policy Engine, the Risk Engine, the Threat/Trust Engines, and (Phase 8) the Approval Engine to produce the official `SecurityDecision`.

## 1. The Decision Object
Conceptually, the decision produced looks like this:

```json
{
  "action_id": "act_123",
  "correlation_id": "trace_abc",
  "timestamp": "2026-09-06T10:05:00Z",
  "decision": "BLOCK",
  "risk_score": 100,
  "risk_level": "CRITICAL",
  "risk_explanation": "Risk Score: 100\nRisk Level: CRITICAL\n...",
  "risk_factors": [
    {
      "name": "Destructive Operation",
      "contribution": 80,
      "category": "OPERATION_SENSITIVITY",
      "reason": "Destructive operation"
    }
  ],
  "reasons": [
    "Matched Policy 'Allow DB' (Priority 10) -> ALLOW",
    "Threat Threshold: REVIEW required due to HIGH threat detection."
  ],
  "violated_policies": [],
  "highest_threat_severity": "HIGH",
  "threat_results": [
    {
      "detector_id": "malformed_action_detector",
      "detector_version": "1.0",
      "threat_type": "MALFORMED_ACTION",
      "severity": "HIGH",
      "confidence": "HIGH",
      "reason": "Missing operation"
    }
  ],
  "approval_required": true
}
```

## 2. The Decision States
Aegis issues exactly one of three decisions:
- **`ALLOW`**: The action is deemed safe, permitted by policy, falls below risk thresholds, and can be immediately routed to the Tool/Resource.
- **`REVIEW`**: The action is not explicitly blocked, but it violates a Review policy or exceeds a risk threshold. The action is paused pending human approval via the Approval Engine (Phase 8).
- **`BLOCK`**: The action violates an explicit Block policy, fails authentication/authorization checks, or triggers a severe Threat detector. The action is immediately rejected and returned to the Agent as an error.

## 3. Precedence & Aggregation Logic
The Decision Engine follows a strict cascade:
1. **Critical Failure Check**: If Identity, Context, or schema validation fails -> **`BLOCK`**.
2. **Permission Check**: If the Permission Engine evaluates to `DENIED` -> **`BLOCK`**.
3. **Trust Check**: If the Trust Engine evaluates to `BLOCKED` -> **`BLOCK`**.
4. **Policy Engine Check**: 
   - If an explicit BLOCK policy matches -> **`BLOCK`**.
   - If an explicit REVIEW policy matches -> **`REVIEW`**.
   - If an explicit ALLOW policy matches -> **`ALLOW`**.
   - Otherwise -> **`BLOCK`** (Default Deny).
5. **Risk Engine Thresholds**: 
   - If Policy evaluated to **`ALLOW`**, Risk Engine thresholds are applied:
     - If `risk_score == 100` -> **`BLOCK`**.
     - If `risk_score > 75` -> **`REVIEW`**.
     - Else -> remains **`ALLOW`**.
6. **Threat Engine Check**: 
   - Evaluated last to analyze the fully constructed context. 
   - If `overall_severity == CRITICAL` -> **`BLOCK`** (escalates ALLOW/REVIEW).
   - If `overall_severity == HIGH` and current decision is ALLOW -> **`REVIEW`**.
   - Does not override existing BLOCK.
7. **Approval Check (Phase 8)**: 
   - If final decision is **`REVIEW`**, the `approval_required` flag is set to `true`.
   - The action enters the Approval Engine workflow.
   - **(FUTURE - Tool Execution Layer)**: Before executing a REVIEW action, the tool layer will verify approval status via `ApprovalService.verify_approval()`.

*Note: Threat and Risk calculations can only escalate an `ALLOW` to `REVIEW` or `BLOCK`. They cannot override a Policy `BLOCK` or Permission `DENIED`.*

## 4. Approval Integration (Phase 8)

When `decision = REVIEW`:
1. An `ApprovalRequest` is created by `ApprovalService.create_request()` containing:
   - Action context (action_id, agent_id, tool_id, operation, resource, environment)
   - Security context (risk_score, risk_level, threat_severity, reasons)
   - Cryptographic action fingerprint (SHA-256)
   - Expiration timestamp (default: 30 minutes)

2. The approval request status is `PENDING` until a human approver:
   - **Approves** via `POST /api/v1/approvals/{id}/approve` → status becomes `APPROVED`
   - **Denies** via `POST /api/v1/approvals/{id}/deny` → status becomes `DENIED`
   - **Expires** → status becomes `EXPIRED` (after TTL)

3. **(FUTURE - Tool Execution Layer)**: Before executing the action, the tool layer calls:
   ```python
   is_valid, reason = await approval_service.verify_approval(action, approval_request_id)
   ```
   
   Verification checks:
   - Approval status is `APPROVED`
   - Not expired
   - Action fingerprint matches (prevents action substitution)
   - All other security conditions still valid

4. **Security Override Rule**: Stronger security blocks override approvals:
   - `Permission DENIED` → `BLOCK` (even if approved)
   - `Trust BLOCKED` → `BLOCK` (even if approved)
   - `Policy BLOCK` → `BLOCK` (even if approved)
   - `Critical Threat` → `BLOCK` (even if approved)
   - `Approval DENIED` → `BLOCK`
   - `Approval EXPIRED` → `BLOCK`
   - `Fingerprint Mismatch` → `BLOCK`

## 5. Fail-Safe / Fail-Closed Behavior
If any downstream dependency of the Decision Engine fails (e.g., the Redis cache holding the risk matrix goes offline, or the Policy Engine times out), the Decision Engine defaults to **`BLOCK`**. Security logic must never fail-open.

If the Approval Engine is unavailable when a `REVIEW` decision is reached, the system should fail-closed and return `BLOCK` rather than allowing unapproved high-risk actions.

