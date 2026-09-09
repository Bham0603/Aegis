# Development Roadmap

This phased engineering roadmap guides the implementation of Aegis from architecture to full deployment. 

## PHASE 0: Product Foundation + Threat Model + Architecture (COMPLETED)
- **Objective**: Establish the conceptual and technical boundaries of Aegis.
- **Deliverables**: Comprehensive architecture documentation, domain models, and threat models.
- **Acceptance Criteria**: All models defined, MVP scoped, tech stack selected, no implementation code yet.

## PHASE 1: Repository + Development Foundation (COMPLETED)
- **Objective**: Setup the monorepo and initial infrastructure.
- **Deliverables**:
  - FastAPI backend foundation
  - PostgreSQL/Alembic infrastructure
  - Redis infrastructure
  - Docker development environment
  - Next.js frontend foundation
  - testing infrastructure
  - linting and formatting
  - type checking
  - structured logging
  - X-Correlation-ID middleware
  - environment-based configuration
  - secret hygiene

**IMPORTANT**: Phase 1 did NOT implement full Aegis domain tables, policy tables, risk tables, approval tables, or security-event persistence.

## PHASE 2: Core Action Interception / Security Gateway (COMPLETED)
- **Objective**: Implement the standard Action schema and basic REST endpoints.
- **Deliverables**:
  - ActionRequest contract
  - API/domain model separation
  - action normalization
  - action validation
  - SecurityContext foundation
  - gateway orchestration
  - extensible evaluation pipeline
  - deterministic baseline evaluator
  - ALLOW / REVIEW / BLOCK decision model
  - deterministic decision precedence
  - fail-closed behavior
  - sensitive parameter redaction
  - POST /api/v1/actions/evaluate
  - unit tests
  - API tests
  - security tests

**IMPORTANT**: Do NOT describe Phase 2 as merely returning a hardcoded decision. Policy Engine, Risk Engine, Threat Detection, Human Approval, Audit Persistence, Dashboard, VS Code Extension, and SDK remain future phases.

## PHASE 3: Agent + Tool Registry
- **Objective**: Database persistence for Agents, Users, and Tools.
- **Deliverables**: CRUD endpoints for identity objects.
- **Acceptance Criteria**: Agents can be registered and tied to specific allowed tools.

## PHASE 4: Policy Engine
- **Objective**: Implement the deterministic JSON rule evaluator.
- **Deliverables**: Policy evaluation logic supporting ALLOW, BLOCK, and REVIEW.
- **Acceptance Criteria**: Unit tests prove that overlapping policies resolve according to strict precedence rules.

## PHASE 5: Permission + Trust Model
- **Objective**: Bind identity to the policy engine.
- **Deliverables**: Validation that an Agent is permitted to act on behalf of a User.
- **Acceptance Criteria**: Actions are blocked if the Agent lacks explicit permission for the Tool.

## PHASE 6: Risk Engine
- **Objective**: Implement the deterministic risk scoring matrix.
- **Deliverables**: Scoring logic based on operation sensitivity, environment, and tool trust.
- **Acceptance Criteria**: Destructive operations in production always score > 85.

## PHASE 7: Threat Detection
- **Objective**: Establish the pluggable Threat Detection architecture and implement initial deterministic detectors.
- **Deliverables**:
  - payload anomalies
  - malformed arguments
  - suspicious action patterns

Advanced ML/LLM-based threat detection remains deferred to Phase 11.

## PHASE 8: Human Approval Engine
- **Objective**: Implement the REVIEW workflow.
- **Deliverables**: ApprovalRequest generation, expiration tracking, and decision consumption.
- **Acceptance Criteria**: Approvals expire correctly; expired approvals result in a BLOCKED action.

## PHASE 9: Audit + Observability (COMPLETED)
- **Objective**: Complete the forensic logging pipeline.
- **Deliverables**:
  - AuditEvent domain model with full decision provenance
  - AuditEventDB persistence model (SQLAlchemy)
  - Alembic migration (33247aa65223)
  - AuditService with redaction, persistence, and query
  - ACTION_RECEIVED emission in Gateway
  - ACTION_EVALUATED emission in Evaluator with 7-dimension provenance
  - Read-only audit API (events, actions, correlations)
  - Pagination and filtering
  - Deterministic timestamp ordering
  - Audit failure resilience (fail-safe, non-blocking)
  - Redaction of sensitive parameters (password, token, secret, api_key, authorization)
- **Acceptance Criteria**: 145 tests pass; sensitive arguments are redacted; logs contain full decision provenance.
- **FUTURE**: Cryptographic hash chaining for tamper-evidence; SHA-256 hashing of redacted values; expanded sensitive keyword set.

## PHASE 10: Attack Lab
- **Objective**: Build a synthetic environment to prove Aegis\'s effectiveness.
- **Deliverables**: Demo scripts simulating Prompt Injections and Destructive actions against mock tools.
- **Acceptance Criteria**: Aegis successfully intercepts and blocks the simulated attacks.

## PHASE 11: AI Security Intelligence
- **Objective**: Integrate LLM-based threat detectors into the Threat Engine.
- **Deliverables**: Prompt Injection detection via secondary LLM evaluation.

## PHASE 12: Backend API Hardening
- **Objective**: Prepare the API for production use.
- **Deliverables**: Rate limiting, JWT authentication, and comprehensive integration testing.

## PHASE 13: Web Dashboard
- **Objective**: Build the Next.js administration interface.
- **Deliverables**: UI for viewing events, managing policies, and handling approvals.

## PHASE 14: VS Code Extension
- **Objective**: Bring security visibility to the developer environment.
- **Deliverables**: Extension that highlights security warnings during agent development.

## PHASE 15: SDK + Framework Integrations
- **Objective**: Make Aegis easy to use.
- **Deliverables**: Python SDK, LangChain wrapper, LlamaIndex middleware.

## PHASE 16: Adversarial Testing
- **Objective**: Break the system.
- **Deliverables**: Penetration testing, bypass attempts on the Policy Engine.

## PHASE 17: Deployment
- **Objective**: Production readiness.
- **Deliverables**: Helm charts, Terraform modules for AWS/GCP.

## PHASE 18: Documentation + Portfolio + Demo + Resume
- **Objective**: Finalize public facing presence.
- **Deliverables**: Public website, detailed API documentation, open-source release preparation.
