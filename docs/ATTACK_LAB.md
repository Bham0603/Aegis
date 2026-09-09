# Attack Lab Model

## Overview

The Aegis Attack Lab is a controlled, deterministic, synthetic security evaluation environment used to demonstrate and test how Aegis responds to agent attack scenarios. It is built to simulate realistic adversarial behaviors without running arbitrary code or exposing actual secrets, ensuring a safe testing ground for evaluating the runtime security governance.

## Key Features

1. **Deterministic Execution**: The environment is seeded deterministically (`MockEnvironmentSeeder`) so test cases execute identically every time.
2. **Declarative Scenarios**: All attack scenarios are declaratively defined via `AttackScenario` configurations (using Python dictionaries), avoiding arbitrary code execution and complex JSON parsing edge cases.
3. **End-to-End Evaluation**: Execution runs through the `PolicyEngine`, `RiskEngine`, `ThreatEngine`, and `ApprovalService`.
4. **Forensic Provenance**: Evaluated actions generate rich, traceable audit events linking correlation IDs.

## Data Model

- **AttackScenario**: A declarative Pydantic model defining the simulated inputs (such as agent ID, session, tool, parameters) and the expected outcome (`SecurityOutcome`). Scenarios also include `limitations` to document vectors not yet defended by Aegis.
- **AttackRunResult**: Captures the exact outcome, including detailed provenance data (Permission, Trust, Risk, Threat, Policy, and Final Decision). It contrasts `actual_outcome` against `expected_outcome`.
- **AttackRunDB**: The persistence layer, linking `run_id`, `scenario_id`, `status`, and `payload` to ensure historical records of Attack Lab runs.

## Attack Vectors Addressed

1. **Direct Prompt Injection** (Limitation: Threat Engine support needed)
2. **Indirect Prompt Injection** (Limitation: Threat Engine support needed)
3. **Tool Misuse**
4. **Privilege Escalation** (Limitation: Context spoofing heuristic support needed)
5. **Data Exfiltration** (Limitation: Network payload heuristic support needed)
6. **Destructive Action**
7. **Approval Bypass**
8. **Tool Poisoning** (Limitation: Parameter poisoning support needed)
9. **Memory Poisoning** (Limitation: Memory poisoning detection needed)
10. **Excessive Autonomy** (Limitation: Autonomy pattern detection needed)

## Running Scenarios

Scenarios can be executed through the REST API endpoints provided at `/api/v1/attack-lab/*`.
The endpoints allow listing scenarios, retrieving single scenario definitions, submitting a run, retrieving a run's results, and fetching associated audit events.
