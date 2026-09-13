import os

from fastapi import APIRouter, HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel

router = APIRouter()

MAX_QUERY_LENGTH = 500
GEMINI_TIMEOUT_SECONDS = 30.0


class CopilotQuery(BaseModel):
    query: str


@router.post("/ask")
def ask_copilot(payload: CopilotQuery):
    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    if len(payload.query) > MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Query too long (max {MAX_QUERY_LENGTH} characters).",
        )

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Aegis Copilot is currently unavailable (missing API key).",
        )

    system_instruction = (
        "You are Aegis Copilot, an AI security analyst for the Aegis platform. "
        "Aegis protects autonomous AI agents from prompt injection, sensitive "
        "data exposure, and unauthorized actions. Answer the user's questions "
        "about security events, threats, agents, risk scores, policies, and "
        "sensitive-data findings. Be concise, professional, and focus on the "
        "security context provided by the Aegis platform. If you do not have "
        "the specific Aegis data a question refers to, say so plainly instead "
        "of inventing details. If a question is unrelated to security or "
        "Aegis, gracefully redirect them."
    )

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=payload.query,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
                http_options=types.HttpOptions(timeout=GEMINI_TIMEOUT_SECONDS * 1000),
            ),
        )

        if not response.text:
            raise HTTPException(
                status_code=502,
                detail="The AI provider returned an empty response.",
            )

        return {"response": response.text}
    except HTTPException:
        raise
    except Exception:
        # Never leak provider internals to the client.
        raise HTTPException(
            status_code=502,
            detail="Error communicating with AI provider. Please try again later.",
        )
