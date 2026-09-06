# Data Model (Identifiers & Relationships)

A critical security requirement in Aegis is the strict segregation of identifiers. Collapsing concepts into generic "IDs" leads to authorization bypasses and audit failures. 

The following identifiers must be distinct UUIDs or typed ULIDs throughout the database, API, and SDK:

### `USER_ID`
Identifies the human actor. This is the root of identity. If an agent is acting autonomously on a schedule, the `USER_ID` belongs to the human who scheduled it. 

### `AGENT_ID`
Identifies a specific AI configuration or instance. 
- *Relationship*: An `Agent` belongs to a `User` (or an Organization). 

### `SESSION_ID`
Identifies a specific run or workflow iteration. 
- *Relationship*: A `Session` belongs to an `Agent` and a `User`. It binds temporary state (like rate limits) to a specific span of time.

### `TOOL_ID`
Identifies the registered capability.
- *Relationship*: Global or Organization-scoped. 

### `ACTION_ID`
Identifies a specific, unique request made by an agent.
- *Relationship*: An `Action` belongs to a `Session`. If an agent requests to run a tool, is denied, and requests it again, those are **two distinct Actions** with two distinct `ACTION_IDs`.

### `CORRELATION_ID`
Identifies a trace across the entire distributed system.
- *Purpose*: Used for Observability. While the `ACTION_ID` tracks the logical security request, the `CORRELATION_ID` ties together the API gateway request, the policy engine evaluation, the threat detector microservices, and the final tool execution.

## Relational Integrity Constraints
- An `Action` must ALWAYS be linked to a valid `Session_ID`.
- An `ApprovalRequest` must ALWAYS be explicitly bound to a single, immutable `ACTION_ID`.
- A `SecurityDecision` must ALWAYS be 1:1 with an `ACTION_ID`.
