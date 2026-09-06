# Decision Model

The Decision Engine is the final arbiter in the Aegis gateway. It aggregates inputs from the Policy Engine, the Risk Engine, and the Threat/Trust Engines to produce the official `SecurityDecision`.

## 1. The Decision Object
Conceptually, the decision produced looks like this:

```json
{
  "action_id": "act_123",
  "correlation_id": "trace_abc",
  "timestamp": "2026-09-06T10:05:00Z",
  "decision": "BLOCK",
  "risk_score": 85,
  "risk_level": "HIGH",
  "reasons": [
    "Explicit BLOCK policy matched (pol_prevent_prod_delete)"
  ],
  "violated_policies": ["pol_prevent_prod_delete"],
  "triggered_detectors": [],
  "approval_required": false
}
```

## 2. The Decision States
Aegis issues exactly one of three decisions:
- **`ALLOW`**: The action is deemed safe, permitted by policy, falls below risk thresholds, and can be immediately routed to the Tool/Resource.
- **`REVIEW`**: The action is not explicitly blocked, but it violates a Review policy or exceeds a risk threshold. The action is paused pending human approval.
- **`BLOCK`**: The action violates an explicit Block policy, fails authentication/authorization checks, or triggers a severe Threat detector. The action is immediately rejected and returned to the Agent as an error.

## 3. Precedence & Aggregation Logic
The Decision Engine follows a strict cascade:
1. **Critical Failure Check**: If Identity, Context, or schema validation fails -> **`BLOCK`**.
2. **Threat Engine Check**: If a Threat Detector flags a severe attack (e.g., Prompt Injection) -> **`BLOCK`**.
3. **Policy Engine Check**: 
   - If an explicit BLOCK policy matches -> **`BLOCK`**.
4. **Risk Engine Check**:
   - If `risk_score >= auto_block_threshold` -> **`BLOCK`**.
   - If `risk_score >= review_threshold` -> **`REVIEW`**.
5. **Policy Review Check**: 
   - If an explicit REVIEW policy matches -> **`REVIEW`**.
6. **Default Check**: 
   - If an explicit ALLOW policy matches -> **`ALLOW`**.
   - Otherwise -> **`BLOCK`** (Default Deny).

## 4. Fail-Safe / Fail-Closed Behavior
If any downstream dependency of the Decision Engine fails (e.g., the Redis cache holding the risk matrix goes offline, or the Policy Engine times out), the Decision Engine defaults to **`BLOCK`**. Security logic must never fail-open.
