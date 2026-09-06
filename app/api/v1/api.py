from fastapi import APIRouter

from app.api.v1.endpoints import agents, gateway, policies, sessions, tools, users

api_router = APIRouter()
api_router.include_router(gateway.router, prefix="/actions", tags=["Gateway"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(tools.router, prefix="/tools", tags=["Tools"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(policies.router, prefix="/policies", tags=["Policies"])
