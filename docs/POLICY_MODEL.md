# Policy Model

The Aegis Policy Engine is a deterministic rule evaluator designed to be independent of endpoint handlers. Policies are expressed as human-readable JSON/YAML documents that define the strict authorization boundaries for agents.

## 1. Policy Syntax

Policies consist of a set of Conditions and an Effect (`ALLOW`, `BLOCK`, `REVIEW`).

```yaml
version: "1.0"
policies:
  - id: pol_prevent_prod_delete
    description: "Block any delete operations in production"
    effect: BLOCK
    conditions:
      environment:
        equals: "production"
      operation:
        in: ["delete", "drop", "truncate"]
        
  - id: pol_review_email
    description: "Require human review for external emails"
    effect: REVIEW
    conditions:
      tool_id:
        equals: "email.send"
      arguments.recipient_domain:
        not_in: ["internalcompany.com"]
        
  - id: pol_allow_research
    description: "Allow the research agent to read web pages"
    effect: ALLOW
    conditions:
      agent_id:
        equals: "agt_researcher"
      tool_id:
        equals: "web.browser"
      operation:
        equals: "read"
```

## 2. Evaluation Process
When an `Action` arrives, the Policy Engine iterates through all active policies bound to the User/Agent's organization. It evaluates the `Action`'s context, target, and arguments against the conditions.

## 3. Precedence & Conflict Resolution
Because multiple policies may match a single Action, Aegis uses strict precedence rules:

1. **Explicit BLOCK always wins.** If ANY matching policy evaluates to `BLOCK`, the evaluation halts, and the action is blocked.
2. **REVIEW overrides ALLOW.** If no `BLOCK` policies match, but at least one `REVIEW` policy matches, the action is marked for Human-in-the-Loop review.
3. **Default Deny.** If no `BLOCK` or `REVIEW` policies match, the action must match at least one `ALLOW` policy. If no `ALLOW` policies match, the action is implicitly `BLOCKED`.

## 4. Policy Lifecycle & Versioning
- Policies are versioned immutably.
- When an `AuditEvent` is generated, it records the exact `Policy_ID` and `Version` that triggered the decision, ensuring historical accuracy even if the policy is later modified.
- Policies support "Dry Run" mode, where they evaluate and log their potential effect without actually blocking or allowing the action (useful for testing new rules).
