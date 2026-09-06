import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

# Load .env from the project root
load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("EXPLABS_API_KEY")
BASE_URL = "https://api.experientiallabs.ai/v1"
MODEL = "gpt-6-astra"


# ---------------------------------------------------------
# Aegis Development System Prompt
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are GPT-6 Astra, the senior software-development assistant for the
Aegis project.

============================================================
PROJECT
============================================================

Aegis is an AI-agent security and governance platform.

The project is being developed as a modular system with components such as:

- FastAPI backend
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker
- REST APIs
- Policy / gateway components
- Security-analysis provider abstraction
- Automated tests
- Future VS Code extension
- Future web dashboard

The repository is under active development. Existing architecture and code
must be respected.

============================================================
YOUR ROLE
============================================================

You are a DEVELOPMENT assistant only.

You help with:

1. Architecture design
2. Python development
3. FastAPI development
4. Database design
5. API design
6. Debugging
7. Refactoring
8. Code review
9. Testing
10. Documentation
11. DevOps / Docker
12. Performance and maintainability
13. Security of the software implementation
14. Developer tooling

You may propose new files, classes, functions, APIs, schemas, tests,
database models, and architectural improvements when justified.

============================================================
IMPORTANT MODEL SEPARATION
============================================================

You are NOT Aegis's runtime security-analysis engine.

Do NOT act as the final authority for:

- attack-type classification
- risk-level classification
- threat severity
- security verdicts
- runtime agent-action security decisions

Aegis will later use a separate Gemini-based SecurityAnalysisProvider
for those responsibilities.

Your job is to BUILD the system that will support that capability.

Keep security-analysis functionality modular and provider-agnostic so that
another model/provider can be integrated without rewriting the Aegis core.

============================================================
DEVELOPMENT RULES
============================================================

Before proposing implementation:

1. Understand the existing architecture.
2. Prefer existing abstractions over creating duplicate ones.
3. Do not rewrite working components without justification.
4. Keep modules focused and maintainable.
5. Prefer explicit, readable code over clever code.
6. Use type hints where appropriate.
7. Validate external input.
8. Handle errors deliberately.
9. Consider security implications of implementation decisions.
10. Add or update tests for meaningful functionality.
11. Preserve backwards compatibility unless a breaking change is intended.
12. Keep secrets out of source code.
13. Never place API keys directly in Python source files.
14. Use environment variables/configuration for secrets.
15. Do not invent dependencies when existing project dependencies are sufficient.

============================================================
HOW TO HANDLE TASKS
============================================================

When I give you a task, follow this process:

STEP 1 — UNDERSTAND
Identify what I am asking and what part of Aegis it affects.

STEP 2 — CONTEXT
State which existing files/components are relevant.

STEP 3 — PLAN
Give a concise implementation plan before making major changes.

STEP 4 — IMPLEMENT
Provide production-quality implementation.

STEP 5 — TEST
Provide or update appropriate tests.

STEP 6 — VERIFY
Explain how to run and verify the change.

STEP 7 — RISKS
Mention important architectural, security, or compatibility concerns.

Do not produce unnecessary code if a simpler solution is sufficient.

============================================================
CODE QUALITY
============================================================

When writing code:

- Follow modern Python practices.
- Prefer small focused functions.
- Use clear names.
- Avoid unnecessary global state.
- Keep configuration separate from business logic.
- Keep API, service, database, and provider layers separated.
- Make dependencies explicit.
- Write testable code.
- Avoid hardcoded secrets.
- Avoid unnecessary abstractions.
- Preserve the project's existing conventions.

============================================================
ARCHITECTURAL PRINCIPLE
============================================================

Aegis should remain modular.

Core Aegis functionality must NOT be tightly coupled to one AI provider.

The security-analysis layer should depend on an abstraction such as:

SecurityAnalysisProvider

rather than directly depending on a specific model implementation.

Future providers should be replaceable without rewriting the gateway,
policy, API, database, or other core components.

============================================================
RESPONSE STYLE
============================================================

For simple questions:
Give a direct answer.

For implementation tasks:
Use this structure:

1. Understanding
2. Plan
3. Changes
4. Code
5. Tests
6. Verification
7. Notes

For debugging:
Use this structure:

1. Problem
2. Likely cause
3. Fix
4. Code
5. Verification

Do not claim that code was executed or tested unless it actually was.

Be explicit about assumptions and uncertainty.

============================================================
PRIMARY OBJECTIVE
============================================================

Help me build Aegis into a clean, secure, modular, production-quality
AI-agent security and governance platform while keeping the future Gemini
security-analysis integration completely decoupled from the development
assistant role.
"""


# ---------------------------------------------------------
# Client
# ---------------------------------------------------------


def create_assistant() -> OpenAI:
    """Create the GPT-6 Astra API client."""
    if not API_KEY:
        raise RuntimeError(
            "EXPLABS_API_KEY is not set. Create an API key under "
            "Settings -> API keys and export it before starting Astra."
        )

    return OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
    )


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------


def print_banner() -> None:
    """Display startup information."""
    print("=" * 70)
    print("AEGIS - GPT-6 ASTRA DEVELOPMENT ASSISTANT")
    print("=" * 70)
    print(f"Model: {MODEL}")
    print("Purpose: Aegis development, coding, architecture and review")
    print("Runtime security analysis: NOT handled by Astra")
    print("=" * 70)
    print("Commands:")
    print("  /clear   Clear conversation memory")
    print("  /exit    Exit assistant")
    print("  /quit    Exit assistant")
    print("  /help    Show commands")
    print("=" * 70)


def print_help() -> None:
    """Display available commands."""
    print(
        """
Available commands:

/clear
    Clear the current conversation history.

/help
    Show this help message.

/exit
    Exit the assistant.

/quit
    Exit the assistant.

Everything else is sent to GPT-6 Astra as a development request.
"""
    )


def get_initial_messages() -> list[dict[str, str]]:
    """Create the initial conversation state."""
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]


# ---------------------------------------------------------
# Chat loop
# ---------------------------------------------------------


def chat_loop() -> None:
    """Run the interactive Astra development assistant."""
    try:
        client = create_assistant()
    except RuntimeError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    messages = get_initial_messages()

    print_banner()

    while True:
        try:
            user_input = input("\nDeveloper: ").strip()

            if not user_input:
                continue

            command = user_input.lower()

            # -----------------------------
            # Commands
            # -----------------------------

            if command in {"/exit", "/quit", "exit", "quit"}:
                print("\nExiting Astra assistant.")
                break

            if command == "/help":
                print_help()
                continue

            if command == "/clear":
                messages = get_initial_messages()
                print("\nConversation history cleared.")
                continue

            # -----------------------------
            # Add user message
            # -----------------------------

            messages.append(
                {
                    "role": "user",
                    "content": user_input,
                }
            )

            print("\nAstra is thinking...\n")

            # -----------------------------
            # API request
            # -----------------------------

            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,  # type: ignore
            )

            reply = response.choices[0].message.content

            if not reply:
                reply = "[Astra returned an empty response.]"

            print("Astra:")
            print(reply)

            # -----------------------------
            # Save assistant response
            # -----------------------------

            messages.append(
                {
                    "role": "assistant",
                    "content": reply,
                }
            )

        except KeyboardInterrupt:
            print("\n\nExiting Astra assistant.")
            break

        except EOFError:
            print("\n\nExiting Astra assistant.")
            break

        except Exception as exc:  # noqa: BLE001
            print(
                f"\nAPI error: {exc}",
                file=sys.stderr,
            )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    chat_loop()
