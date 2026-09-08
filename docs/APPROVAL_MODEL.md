# Approval Model (Human-in-the-Loop)

## Phase 8 - IMPLEMENTED

When the Decision Engine evaluates an action and returns a `REVIEW` decision (either due to an explicit Policy, or a high Risk Score), the Approval Engine manages the workflow to securely acquire human authorization.

## 1. Core Principles

- **No Self-Approval**: The LLM / Agent can never approve its own actions. This is enforced through `ApprovalRequest.validate_approver()` which rejects when `approver_id == agent_id`.
- **Action Binding**: Approvals are cryptographically bound to a specific action via SHA-256 fingerprinting. The `action_fingerprint` is generated from security-relevant fields (action_id, agent_id, tool_id, operation, resource, environment, parameters). An approval cannot be reused for a different action.
- **Expiration**: All approval requests have a strict Time-to-Live (TTL, default 30 minutes). If not approved within the window, the approval expires and cannot authorize execution.
- **Replay Prevention**: Fingerprint verification at execution time prevents approved actions from being modified. Any change to security-relevant fields invalidates the approval.
- **Fail-Safe**: Stronger security blocks (Permission DENIED, Trust BLOCKED, Policy BLOCK) override approvals.

## 2. Approval Lifecycle

1. **Request Generation**: The Decision Engine yields `REVIEW`. `ApprovalService.create_request()` generates an `ApprovalRequest` containing:
   - Unique `approval_request_id`
   - Cryptographic `action_fingerprint` 
   - Action context (agent, session, tool, operation, resource, environment)
   - Security context (risk_score, risk_level, threat_severity, reasons)
   - Expiration timestamp (`expires_at`)

2. **Notification**: **(FUTURE - Phase 9+)** Aegis will trigger webhooks, Slack messages, or emails to designated approvers.

3. **Review**: **(FUTURE - Dashboard/VS Code Extension)** Humans will inspect `ApprovalRequest` via Web Dashboard or VS Code extension.

4. **Decision**: Human submits approval/denial via API:
   - `POST /api/v1/approvals/{id}/approve` → `APPROVED`
   - `POST /api/v1/approvals/{id}/deny` → `DENIED`

5. **Validation**: `ApprovalService.resolve()` performs security checks:
   - Request exists and status is `PENDING`
   - Not expired (`current_time < expires_at`)
   - Approver is not the agent (self-approval prevention)
   - Approver exists and is active
   - Status transition is valid

6. **Consumption**: **(FUTURE - Tool Execution Layer)** Before executing an action with `decision=REVIEW`, the tool layer will call `ApprovalService.verify_approval()` to ensure:
   - Approval status is `APPROVED`
   - Not expired
   - Action fingerprint matches (prevents action substitution)

7. **Audit**: **(FUTURE - Phase 9)** `AuditEvent` will link the approver's identity to the executed action.

## 3. Approval Status Lifecycle

```
PENDING (initial state)
  ↓
  ├─→ APPROVED (human approved)
  ├─→ DENIED (human denied)
  ├─→ EXPIRED (time exceeded expires_at)
  └─→ CANCELLED (administrative cancellation)

Terminal States: APPROVED, DENIED, EXPIRED, CANCELLED
```

**Security Invariant**: Terminal states cannot transition. Once `APPROVED`, `DENIED`, `EXPIRED`, or `CANCELLED`, the status is immutable.

## 4. Action Fingerprinting

### Purpose
Cryptographically bind approvals to exact actions to prevent **action substitution attacks**.

### Algorithm
1. **Canonicalization**: Extract security-relevant fields and sort keys deterministically
2. **Redaction**: Hash sensitive parameters (passwords, tokens, API keys) rather than including plaintext
3. **Serialization**: JSON encode with sorted keys
4. **Hashing**: SHA-256 to produce 64-character hex digest

### Included Fields
- `action_id`
- `agent_id` 
- `user_id`
- `session_id`
- `tool_id`
- `operation`
- `resource`
- `environment`
- `parameters` (with sensitive values hashed)
- `authorization_context`

### Excluded Fields (observability only, not security-relevant)
- `timestamp`
- `correlation_id`

### Security Properties
- **Deterministic**: Same action → same fingerprint
- **Unique**: Different security-relevant actions → different fingerprints
- **Binding**: Approval for Action A cannot authorize Action B
- **Tamper-evident**: Modifying action after approval invalidates fingerprint

## 5. Data Model

### `ApprovalRequest` (Domain Model)

```python
class ApprovalRequest:
    approval_request_id: str           # "apr_abc123def456"
    action_id: str                     # "act_xyz789"
    action_fingerprint: str            # SHA-256 hex (64 chars)
    correlation_id: str
    
    # Identity
    agent_id: str
    user_id: str | None
    session_id: str
    
    # Action context
    tool_id: str
    operation: str | None
    resource: str | None
    environment: str
    
    # Lifecycle
    status: ApprovalStatus             # PENDING, APPROVED, DENIED, EXPIRED, CANCELLED
    created_at: datetime
    expires_at: datetime
    resolved_at: datetime | None
    
    # Approver
    required_approver_role: str | None
    approver_id: str | None
    
    # Security context
    risk_score: int | None
    risk_level: str | None
    highest_threat_severity: str | None
    reasons: list[str]
    
    # Resolution
    resolution_comment: str | None
```

### `ApprovalDecision` (API Request)

```python
class ApprovalDecision:
    approval_request_id: str
    approver_id: str
    decision: ApprovalStatus          # Must be APPROVED or DENIED
    comment: str | None
    timestamp: datetime
```

### `ApproverDB` (Database Model)

```python
class ApproverDB:
    id: UUID                          # Primary key
    approver_id: str                  # Business ID (unique, indexed)
    display_name: str
    email: str | None
    roles: dict | None                # JSONB (for future RBAC)
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

## 6. API Endpoints

### GET /api/v1/approvals/{approval_request_id}
Retrieve an approval request by ID.

**Response**: `ApprovalRequestResponse`

### POST /api/v1/approvals/{approval_request_id}/approve
Approve a pending approval request.

**Request**:
```json
{
  "approver_id": "human_approver_123",
  "decision": "APPROVED",
  "comment": "Verified this action is safe"
}
```

**Response**: Updated `ApprovalRequestResponse` with `status=APPROVED`

**Security Validations**:
- Request exists and is `PENDING`
- Not expired
- Approver ≠ Agent (self-approval prevention)
- Approver is active

### POST /api/v1/approvals/{approval_request_id}/deny
Deny a pending approval request.

**Request**:
```json
{
  "approver_id": "human_approver_123",
  "decision": "DENIED",
  "comment": "Too risky for production"
}
```

**Response**: Updated `ApprovalRequestResponse` with `status=DENIED`

### POST /api/v1/approvers
Create a new approver identity.

**Request**:
```json
{
  "approver_id": "admin_user_1",
  "display_name": "Admin User",
  "email": "admin@example.com"
}
```

**Response**: Created `ApproverResponse`

## 7. Security Decision Precedence

Approval does NOT override stronger security blocks:

1. **Permission DENIED** → BLOCK (regardless of approval)
2. **Trust BLOCKED** → BLOCK (regardless of approval)
3. **Policy BLOCK** → BLOCK (regardless of approval)
4. **Critical Threat** → BLOCK (per threat model)
5. **Risk Score = 100** → BLOCK
6. **Policy REVIEW** → Create ApprovalRequest
7. **Risk Score > 75** → REVIEW → Create ApprovalRequest
8. **High Threat** → REVIEW → Create ApprovalRequest
9. **Approval APPROVED** + All checks pass → ALLOW (future tool execution)
10. **Approval DENIED** → BLOCK
11. **Approval EXPIRED** → BLOCK

## 8. Concurrency & Race Conditions

**Challenge**: Two approvers attempt to resolve the same PENDING request simultaneously.

**Solution**: Database transaction isolation + status check
- `ApprovalService.resolve()` fetches approval request
- Validates status is `PENDING`
- Updates status in transaction
- If concurrent update occurs, one succeeds, the other fails with "already in terminal state"

**Future Enhancement**: Optimistic locking or database-level row locking for stronger guarantees.

## 9. Expiration Handling

- **Lazy Expiration**: Approvals are checked for expiration on access (`is_expired(current_time)`)
- **No Background Worker Required**: Correctness does not depend on a scheduler
- **Future Enhancement**: Optional background job to mark expired requests and notify approvers

## 10. Current Limitations (MVP)

- **No Notification System**: Approvers must poll `/approvals/{id}` endpoint
- **No Web Dashboard**: API-only approval workflow
- **No VS Code Extension UI**: No IDE-integrated approval
- **Simple Approver Model**: No enterprise SSO, RBAC, or separation of duties
- **No Multi-Person Approval**: One approver per request
- **No Audit Trail**: Full forensic audit is Phase 9
- **No Approval Delegation**: Cannot reassign approval requests
- **No Approval Groups**: Cannot assign to teams/roles

## 11. Future Phases

### Phase 9 - Audit & Observability
- Persistent audit log linking approvals to executed actions
- Forensic timeline reconstruction
- Approval analytics dashboard

### Phase 10+ - Dashboard & Extensions
- Web dashboard for approval review
- VS Code extension for IDE-integrated approval
- Slack/webhook notifications
- Email notifications

### Enterprise Features (Post-MVP)
- SSO integration (SAML, OIDC)
- RBAC with approval groups
- Separation of duties (multi-person approval)
- Approval delegation and reassignment
- Approval policy engine (who can approve what)
- Emergency approval bypass with audit trail

## 12. Testing

### Unit Tests
- `tests/domain/test_approval.py`: Domain model lifecycle and validation
- `tests/services/test_fingerprint.py`: Fingerprinting algorithm
- `tests/services/test_approval_service.py`: Service layer operations

### Security Tests
- `tests/security/test_approval_security.py`: Adversarial security validation
  - Self-approval prevention
  - Fingerprint binding (action substitution prevention)
  - Expiration enforcement
  - Terminal state immutability
  - Sensitive parameter redaction

### API Tests
- `tests/api/test_approvals.py`: HTTP endpoint validation
  - GET, approve, deny endpoints
  - Security validation errors
  - Approver creation

### Regression Tests
All Phase 1-7 tests continue to pass.

## 13. Implementation Files

### Domain Models
- `app/domain/approval.py`: ApprovalRequest, ApprovalStatus, ApprovalDecision

### Services
- `app/services/approval_service.py`: ApprovalService (create, resolve, verify)
- `app/services/fingerprint.py`: Action fingerprinting and verification

### Database
- `app/models/approval.py`: ApprovalRequestDB, ApproverDB
- `alembic/versions/51827df2f207_add_approval_models.py`: Migration

### API
- `app/api/v1/endpoints/approvals.py`: REST API endpoints
- `app/api/v1/api.py`: Router registration

### Tests
- `tests/domain/test_approval.py`
- `tests/services/test_fingerprint.py`
- `tests/services/test_approval_service.py`
- `tests/api/test_approvals.py`
- `tests/security/test_approval_security.py`
