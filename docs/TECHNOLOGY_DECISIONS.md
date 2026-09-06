# Technology Decisions

For Aegis to function as a professional security product, the technology stack must prioritize correctness, type safety, performance, and developer experience.

## 1. Architecture Pattern: Modular Monolith
*Alternative considered: Microservices.*
**Decision**: Start as a modular monolith. 
**Justification**: Distributed microservices introduce severe complexity regarding data consistency and tracing, which is counterproductive for an MVP security gateway. A modular monolith allows logical separation (Identity, Policy, Risk) while maintaining speed and simplicity. It can be factored into microservices later if scale demands it.

## 2. Backend Framework: Python & FastAPI
*Alternatives considered: Go, Node.js/Express, Rust.*
**Decision**: Python with FastAPI.
**Justification**: The AI/Agent ecosystem is overwhelmingly Python-centric (LangChain, LlamaIndex, standard MCP implementations). Writing the security gateway in Python allows seamless sharing of types and Pydantic schemas between the agent implementations and the security backend. FastAPI provides excellent async support, auto-generated OpenAPI docs, and strict type validation out of the box.

## 3. Database: PostgreSQL
*Alternatives considered: MongoDB, SQLite.*
**Decision**: PostgreSQL.
**Justification**: Security products require strict relational integrity. An `AuditEvent` must strictly link to a valid `Action`, `Policy`, and `User`. Document databases (MongoDB) lack the strict enforcement required for immutable audit trails. SQLite is insufficient for concurrent API throughput and highly available deployments.

## 4. Caching & Background Jobs: Redis & Celery (or ARQ)
*Alternatives considered: In-memory only, RabbitMQ.*
**Decision**: Redis.
**Justification**: Aegis requires ephemeral state management (e.g., rate limiting by session, temporary storage of unredacted payloads pending approval). Redis is the industry standard. Background tasks (like asynchronous threat detection or dispatching approval webhooks) will utilize a Redis-backed queue.

## 5. Frontend / Dashboard: Next.js (React)
*Alternatives considered: Vue, plain React (Vite).*
**Decision**: Next.js.
**Justification**: Next.js provides robust routing, server-side rendering, and API routes that simplify the creation of a professional, dashboard-oriented security interface. It is the dominant choice for modern enterprise B2B SaaS frontends.

## 6. Containerization: Docker
**Decision**: Docker and Docker Compose.
**Justification**: Ensures that the entire Aegis environment (FastAPI, Postgres, Redis, Next.js) can be spun up locally by a developer in a single command (`docker-compose up`).

## 7. Policy Engine: Custom JSON Evaluator (MVP) -> Open Policy Agent (Future)
*Alternatives considered: Full Rego/OPA integration immediately.*
**Decision**: Custom JSON/YAML rules engine for MVP.
**Justification**: While OPA (Rego) is the industry standard for policy-as-code, it has a notoriously steep learning curve. For the MVP, a custom, deterministic JSON-based evaluator is much faster to implement and easier for users to understand. The architecture will abstract the policy evaluation interface so OPA can be swapped in as a backend provider in later phases.
