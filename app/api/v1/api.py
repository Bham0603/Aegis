from fastapi import APIRouter

from app.api.v1.endpoints import (
    agents,
    approvals,
    approvers,
    audit,
    gateway,
    policies,
    sessions,
    tools,
    users,
)

api_router = APIRouter()
api_router.include_router(gateway.router, prefix="/gateway", tags=["gateway"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(approvers.router, prefix="/approvers", tags=["approvers"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
