# Aegis Threat Model

## 1. Overview
The Aegis Threat Engine evaluates normalized agent actions against a suite of deterministic detectors to identify suspicious patterns, malformed requests, or unusually dangerous operations.

The Threat Engine is responsible for the question:
> **"Does this action or action pattern contain a detectable security threat?"**

It does **NOT** enforce identity authorization (Permission Engine), organizational rules (Policy Engine), or numeric risk calculation (Risk Engine). It produces a `ThreatAssessment` which acts as a signal for the overall Decision Engine to escalate or block.

## 2. Threat Severity
Findings from detectors are mapped to one of the following severity levels:
- `LOW`: Anomalies that are unusual but not inherently dangerous.
- `MEDIUM`: Anomalies that warrant observation but do not strictly mandate blocking unless combined with other factors.
- `HIGH`: Severe anomalies (e.g., impossible payloads) that mandate a `REVIEW` if the action is otherwise allowed.
- `CRITICAL`: Highly dangerous deterministic patterns (e.g., destructive ops against external resources) that mandate an immediate `BLOCK`.

## 3. Implemented Threat Types
Currently, Aegis supports deterministic heuristics for the following threat types:
- `MALFORMED_ACTION`: Detects missing operations or mutually exclusive metadata states.
- `SUSPICIOUS_PAYLOAD`: Detects payloads exceeding bounds (e.g., >50 parameters, strings >10,000 chars, nesting >10 levels).
- `DANGEROUS_OPERATION_PATTERN`: Detects destructive operations (`delete`, `drop`) targeting sensitive resources (`production`, `auth`) or external web destinations.

## 4. Threat Engine Pipeline
1. The gateway constructs an `Action` and `SecurityContext`.
2. The `ThreatEngine` registers a list of `BaseThreatDetector` implementations.
3. The engine sequentially executes each detector.
4. Any raised `ThreatDetectionResult` is collected.
5. The engine aggregates findings deterministically, taking the **highest severity** as the overall `ThreatAssessment` severity.
6. If a detector crashes during execution, the engine fails-closed and injects a `HIGH` severity finding to prevent silent evaluation bypasses.

## 5. Exclusions & Future Capabilities
The following threat categories are **NOT** currently supported by the deterministic engine:
- LLM Prompt Injection or Indirect Prompt Injection.
- Tool Semantic Poisoning.
- Advanced Social Engineering detection.
- Cross-session persistent behavioral anomaly tracking.

These capabilities are deferred to Phase 11 (AI-assisted security intelligence) and Phase 9 (Persistent Audit History).
