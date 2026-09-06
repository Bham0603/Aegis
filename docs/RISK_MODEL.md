# Risk Model

The Risk Engine calculates a deterministic risk score for every action. This score is used to trigger `REVIEW` workflows for highly sensitive or unusual operations, even if a specific `BLOCK` policy isn't triggered.

Aegis explicitly avoids using an LLM to generate a random number for "risk." The score must be mathematically explainable.

## 1. Score Range & Levels
Scores range from **0 to 100**.
- **0-25 (LOW)**: Safe, read-only, routine operations. (e.g., searching a public webpage).
- **26-50 (MEDIUM)**: State-mutating operations in non-production, or reading internal data. (e.g., writing to a staging database).
- **51-85 (HIGH)**: State-mutating operations in production, or external communications. (e.g., sending an email).
- **86-100 (CRITICAL)**: Highly sensitive, destructive, or highly-anomalous operations. (e.g., deleting a production database table).

## 2. Deterministic Scoring Factors
The final score is a weighted sum of several factors:

- **Action/Operation Sensitivity (Base Score)**
  - `Read`: +10
  - `Write/Update`: +40
  - `Delete/Destructive`: +80
- **Environment Factor (Multiplier)**
  - `Development`: x0.5
  - `Staging`: x1.0
  - `Production`: x1.5
- **Tool Trust Level (Additive)**
  - `Trusted Tool`: 0
  - `Untrusted / Experimental Tool`: +20
- **Threat Engine Signals (Additive)**
  - `Suspicious parameters detected`: +30
  - `Prompt Injection detected`: +100

## 3. Threshold Behavior
Organizations can define threshold policies:
- "Any action with a Risk Score > 75 requires human `REVIEW`."
- "Any action with a Risk Score = 100 is automatically `BLOCKED`."

## 4. Explainability
Because the scoring is deterministic, Aegis can answer *exactly* why an action received a specific score.
Example Output:
> "Risk Score 85: Base operation is Destructive (80) + Environment is Staging (x1.0) + Tool is Trusted (0)."

## 5. Future Extensibility
While Phase 0/MVP relies on a purely deterministic ruleset, future phases can introduce ML models (e.g., Isolation Forests for anomaly detection). However, ML models will contribute an *Additive* factor to the deterministic base score, rather than replacing the explainable engine entirely.
