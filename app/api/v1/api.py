from fastapi import APIRouter, Depends

from app.api.rate_limit import RateLimitDependency
from app.api.security import RequireRole
from app.api.v1.endpoints import (
    agents,
    approvals,
    approvers,
    attack_lab,
    audit,
    gateway,
    policies,
    sessions,
    tools,
    users,
)
from app.domain.auth import Role

api_router = APIRouter()
rate_limit = Depends(RateLimitDependency())

api_router.include_router(
    gateway.router,
    prefix="/actions",
    tags=["Gateway"],
    dependencies=[Depends(RequireRole(Role.AGENT, Role.ADMIN)), rate_limit],
)
api_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["agents"],
    dependencies=[Depends(RequireRole(Role.ADMIN, Role.OPERATOR)), rate_limit],
)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(RequireRole(Role.ADMIN)), rate_limit],
)
api_router.include_router(
    tools.router,
    prefix="/tools",
    tags=["tools"],
    dependencies=[Depends(RequireRole(Role.ADMIN, Role.OPERATOR)), rate_limit],
)
api_router.include_router(
    sessions.router,
    prefix="/sessions",
    tags=["sessions"],
    dependencies=[Depends(RequireRole(Role.ADMIN, Role.OPERATOR)), rate_limit],
)
api_router.include_router(
    policies.router,
    prefix="/policies",
    tags=["policies"],
    dependencies=[Depends(RequireRole(Role.ADMIN)), rate_limit],
)
api_router.include_router(
    approvals.router,
    prefix="/approvals",
    tags=["approvals"],
    dependencies=[Depends(RequireRole(Role.APPROVER, Role.ADMIN)), rate_limit],
)
api_router.include_router(
    approvers.router,
    prefix="/approvers",
    tags=["approvers"],
    dependencies=[Depends(RequireRole(Role.ADMIN)), rate_limit],
)
api_router.include_router(
    audit.router,
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(RequireRole(Role.AUDITOR, Role.ADMIN)), rate_limit],
)
api_router.include_router(
    attack_lab.router,
    prefix="/attack-lab",
    tags=["attack-lab"],
    dependencies=[Depends(RequireRole(Role.OPERATOR, Role.ADMIN)), rate_limit],
)
