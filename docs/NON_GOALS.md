# Non-Goals

To maintain focus on the core value proposition—Runtime Security for AI Agents—it is critical to define what Aegis is *not* intended to be.

## 1. Not an LLM Hosting Platform
Aegis does not host, finetune, or route requests to models (like OpenAI, Anthropic, or local LLMs). It intercepts the *actions* the agent attempts to take, not the text generation itself.

## 2. Not a Chatbot or AI Coding Assistant
Aegis is an invisible security gateway and a developer dashboard. It does not provide conversational AI features or code generation assistance to end-users.

## 3. Not a Generic Vulnerability Scanner (SAST/DAST)
Aegis does not scan source code for SQL injection or buffer overflows. It evaluates runtime intent.

## 4. Not a Replacement for Traditional Enterprise SIEMs
While Aegis generates rich security telemetry regarding AI agents, it expects to forward these logs to a dedicated SIEM (like Datadog, Splunk, or Elastic) rather than replacing them entirely.

## 5. Not a Prompt-Engineering Framework
Aegis does not attempt to "fix" the agent's system prompt to make it safer. It assumes the prompt can and will be compromised, and provides an independent layer of defense outside the prompt.
