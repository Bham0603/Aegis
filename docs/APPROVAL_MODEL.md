# Approval Model (Human-in-the-Loop)

When the Decision Engine evaluates an action and returns a `REVIEW` decision (either due to an explicit Policy, or a high Risk Score), the Approval Engine manages the workflow to securely acquire human authorization.

## 1. Core Principles
- **No Self-Approval**: The LLM / Agent can never approve its own actions.
- **Action Binding**: Approvals are cryptographically bound to a specific, immutable `ACTION_ID` and its exact parameters. An approval cannot be reused for a different action.
- **Expiration**: All approval requests have a strict Time-to-Live (TTL). If not approved within the window, the action defaults to `BLOCK`.
- **Replay Prevention**: Once an approval token is consumed to execute the action, it is invalidated.

## 2. Approval Lifecycle

1. **Request Generation**: The Decision Engine yields `REVIEW`. Aegis generates an `ApprovalRequest` object containing the Action context, the Risk Score, and the matching policies.
2. **Notification**: Aegis triggers a webhook, Slack message, or email to the designated human approver (e.g., an Admin or the User who spawned the agent).
3. **Review**: The human inspects the `ApprovalRequest` via the Web Dashboard or VS Code extension.
4. **Decision**: The human submits an `ApprovalDecision` (`APPROVED` or `DENIED`).
5. **Consumption**: If `APPROVED`, Aegis releases the Action to the Tool execution layer and immediately invalidates the approval token.
6. **Audit**: An `AuditEvent` is generated, linking the human's Identity (`APPROVER_USER_ID`) to the executed Action.

## 3. Data Model

### `ApprovalRequest`
```json
{
  "approval_id": "app_555",
  "action_id": "act_123",
  "status": "PENDING",
  "expires_at": "2026-09-06T10:15:00Z",
  "required_role": "admin",
  "context": {
     "risk_score": 85,
     "reason": "Exceeds risk threshold for production mutations"
  }
}
```

### `ApprovalDecision`
```json
{
  "approval_id": "app_555",
  "decision": "APPROVED",
  "approver_user_id": "usr_999",
  "timestamp": "2026-09-06T10:06:00Z",
  "comments": "Verified this cleanup script is expected."
}
```
