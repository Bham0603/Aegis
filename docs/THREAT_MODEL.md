# Threat Model

This document outlines the threats Aegis is designed to mitigate, categorized by implementation phase. Aegis assumes that the underlying LLM is a potentially compromised entity due to the nature of Prompt Injections and hallucination.

## 1. MVP Threats (Addressed in Initial Implementation)

These threats represent the fundamental risks of granting autonomy to agents, which Aegis mitigates deterministically in the MVP phase.

- **Excessive Agency / Excessive Autonomy**: Agents executing actions outside their intended scope.
  - *Mitigation*: Policy Engine blocks any action not explicitly allowed for the Agent/Tool combination.
- **Destructive Actions**: Agents accidentally or maliciously deleting data or mutating state.
  - *Mitigation*: Risk Engine flags destructive operations (e.g., `DELETE`); Decision Engine forces human `REVIEW` or `BLOCK`.
- **Privilege Escalation (Basic)**: Agents attempting to use tools reserved for higher-privileged users.
  - *Mitigation*: Identity and Permission Engine validates user/agent binding against tool requirements.
- **Approval Bypass**: Attempting to forge or skip human approval for sensitive actions.
  - *Mitigation*: Approval Engine generates cryptographic, one-time, action-bound tokens that the agent cannot forge.

## 2. V1 Threats (Addressed post-MVP)

These threats require more advanced detection mechanisms, state tracking, and integration with the Trust Engine.

- **Direct Prompt Injection (Jailbreaking)**: A user directly overriding the agent's instructions to perform malicious actions.
  - *Mitigation*: Threat Engine analyzes the action sequence and parameters for malicious intent, independent of the LLM.
- **Runaway Tool Usage / Denial-of-Wallet**: Agents stuck in loops calling expensive tools (e.g., paid APIs, massive DB queries).
  - *Mitigation*: Policy Engine implements rate limiting and anomaly detection based on session history.
- **Secret Exposure**: Agents accidentally passing secrets into tool arguments or logging them.
  - *Mitigation*: Audit Engine implements strict redaction rules; Threat Engine inspects outbound parameters for credential patterns.
- **Data Exfiltration**: Agents sending sensitive local data to untrusted external URLs.
  - *Mitigation*: Trust Engine evaluates external destinations against an Allowlist/Blocklist.

## 3. Future / Research Threats

These are advanced threats specific to the evolving ecosystem of multi-agent architectures and autonomous integration frameworks (like MCP).

- **Indirect Prompt Injection**: Agents ingesting poisoned data from a tool (e.g., reading a compromised webpage) which then alters their behavior.
  - *Mitigation*: Trust Model tags data provenance. Actions triggered by untrusted data incur massive risk score penalties.
- **Tool Poisoning & Malicious MCP Servers**: A registered tool or MCP server intentionally returning malicious schemas or payloads to compromise the agent.
  - *Mitigation*: MCP server trust validation, strict schema enforcement, and payload sanitization before returning to the agent.
- **Cross-Agent Trust Abuse**: A compromised agent attempting to instruct a highly-privileged agent to perform actions on its behalf.
  - *Mitigation*: Identity Engine tracks cross-agent invocation chains; Policy Engine applies the intersection of permissions (least privilege).
- **Memory Poisoning**: Attackers injecting persistent malicious context into an agent's long-term memory store.
  - *Mitigation*: Provenance tracking on memory writes; continuous scanning of memory stores.
