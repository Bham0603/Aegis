# Risk Model

The Risk Engine calculates a deterministic risk score for every action. This score is used to trigger `REVIEW` workflows for highly sensitive or unusual operations, even if a specific `BLOCK` policy isn't triggered.

Aegis explicitly avoids using an LLM to generate a random number for "risk." The score must be mathematically explainable.

## 1. Score Range & Levels
Scores range from **0 to 100**. The final score is strictly clamped to this range.
- **0-25 (LOW)**: Safe, read-only, routine operations. (e.g., searching a public webpage).
- **26-50 (MEDIUM)**: State-mutating operations in non-production, or reading internal data. (e.g., writing to a staging database).
- **51-85 (HIGH)**: State-mutating operations in production, or external communications. (e.g., sending an email).
- **86-100 (CRITICAL)**: Highly sensitive, destructive, or highly-anomalous operations. (e.g., deleting a production database table).

## 2. Deterministic Scoring Factors
The final score is calculated using the following factors:

- **Action/Operation Sensitivity (Base Score)**
  - `Read/Search/Query`: +10
  - `Write/Update/Create`: +40
  - `Delete/Drop/Destructive`: +80
  - `Unknown`: +20
- **Environment Factor (Multiplier applied to base score)**
  - `Development/Local`: x0.5
  - `Staging/QA`: x1.0
  - `Production`: x1.5
  - `Unknown`: x1.5 (Defaults to safest assumption)
- **Tool Trust Level (Additive)**
  - `Trusted`: 0
  - `Internal`: +5
  - `External`: +15
  - `Untrusted`: +25
  - `Unknown`: +20
- **External Destination (Additive)**
  - `HTTP/Email domains detected in resource/tool`: +15
  - `Internal Destination`: +0

## 3. Threshold Behavior
Risk score thresholds evaluate actions that Policy Engine explicitly `ALLOW`s:
- **Risk Score > 75**: Automatically escalates to `REVIEW`.
- **Risk Score == 100**: Automatically escalates to `BLOCK`.

Note: The Risk Engine cannot override a Policy `BLOCK`. Policy precedence is strictly maintained.

## 4. Explainability
Because the scoring is deterministic, Aegis can answer *exactly* why an action received a specific score.
Example Output:
> Risk Score: 55
> Risk Level: HIGH
> 
> Factors:
> + 40  State-mutating operation
> +  0  Staging environment (x1.0 multiplier)
> +  0  Tool is trusted
> + 15  Action involves an external destination
> 
> Total:
> 55

## 5. Future Extensibility
While Phase 6 relies on a purely deterministic ruleset, future phases can introduce ML models. However, ML models will contribute an *Additive* factor to the deterministic base score, rather than replacing the explainable engine entirely.
