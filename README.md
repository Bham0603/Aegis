# Aegis — Runtime Security & Governance for AI Agents

**Aegis** is a runtime security gateway designed specifically to protect infrastructure, data, and users from autonomous AI agents. As AI systems increasingly connect to real-world tools—like web browsers, databases, email, and GitHub—traditional security boundaries are insufficient. Aegis sits between the AI agent and its tools/resources to evaluate actions independently of the LLM, ensuring that prompt injections, rogue agents, or malicious tool responses cannot cause unauthorized harm.

## Status: V1.0 Release Candidate (Phase 17 Complete)

> **UPDATE**: Aegis has successfully completed Phase 17 (End-to-End Integration, Hardening & Demo Readiness). The system is fully integrated across the Backend, Frontend, SDK, VS Code Extension, and MCP Gateway.

### Fully Implemented Components

- **Backend (FastAPI)**: Deterministic Policy Engine, Permission & Trust Models, Risk Assessment, Human-in-the-loop Approvals, Audit Logging, AI Threat Intelligence.
- **Frontend (Next.js)**: Security Command Center for managing approvals, viewing audits, and configuring policies.
- **Python SDK**: Native `aegis_sdk` for integrating Python-based agents with the Aegis backend.
- **MCP Security Gateway**: A wrapper for the Model Context Protocol (MCP) to enforce zero-trust policies on any MCP server without modifying the server itself.
- **VS Code Extension**: Developer tooling to manage security profiles and handle approvals directly in the IDE.
- **Attack Lab**: A built-in simulation environment for validating security controls against malicious payloads.

## Why Aegis?

An LLM should **NOT** be considered the final authority for whether a sensitive action is allowed. Aegis guarantees that security controls are evaluated in a deterministic, independently enforceable environment. A malicious prompt cannot simply tell Aegis to "ignore the security policy."

## Quickstart & Demo

To experience the full power of Aegis, you can run the end-to-end demo script.

1. **Start the Aegis Backend**
   ```bash
   docker-compose up --build -d
   ```
   *(Alternatively, run `uvicorn app.main:app --reload` locally)*

2. **Run the End-to-End Demo**
   The demo script initializes test scenarios, demonstrates ALLOW, BLOCK, and REVIEW workflows, and runs a live MCP server sandbox.
   ```bash
   python scripts/demo.py
   ```

3. **Explore the Web Dashboard**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Navigate to `http://localhost:3000` to view the security console.

## Documentation

For full architectural details, see the `docs/` directory:
- [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- [Threat Model](docs/THREAT_MODEL.md)
- [Domain Model](docs/DOMAIN_MODEL.md)
- [Policy Model](docs/POLICY_MODEL.md)
- [Development Roadmap](docs/DEVELOPMENT_ROADMAP.md)

---
*Aegis - Never trust the LLM alone for authorization.*
