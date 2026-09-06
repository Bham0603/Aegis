# Assumptions

The architecture of Aegis is built upon several core security and operational assumptions regarding the state of AI Agents. If these assumptions change, the architecture must be re-evaluated.

## 1. LLMs are Inherently Vulnerable
We assume that Large Language Models cannot be completely secured against Prompt Injections (Direct or Indirect). Therefore, security controls placed inside the "System Prompt" are insufficient for protecting critical infrastructure.

## 2. AI Agents Will Hallucinate Parameters
We assume that an agent may invent non-existent database tables, format API payloads incorrectly, or generate destructive parameters without malicious intent. Strong schema validation and risk scoring are necessary even for trusted agents.

## 3. External Tool Providers are Untrusted
When integrating with third-party tools or external MCP (Model Context Protocol) servers, we assume the schemas or data returned by those servers may be poisoned or malicious.

## 4. Audit Data is a Target
We assume that if an attacker compromises an agent, they may attempt to exfiltrate data by forcing the agent to log sensitive information. Therefore, the Audit Engine must actively redact payloads.

## 5. Developers Prioritize Speed
We assume that developers building AI agents will bypass security controls if they are too difficult to implement. The Aegis API and SDKs must be lightweight and easy to integrate (e.g., a simple middleware wrapper) to encourage adoption.
