from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.domain.auth import Principal, Role
from app.services.auth_service import AuthService

API_KEY_NAME = "Authorization"
X_API_KEY_NAME = "X-API-Key"
# Use a custom APIKeyHeader because we want to accept `Bearer <token>` or `X-API-Key <token>`
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
x_api_key_header = APIKeyHeader(name=X_API_KEY_NAME, auto_error=False)


async def get_current_principal(
    api_key_header_value: Annotated[str | None, Security(api_key_header)],
    x_api_key_header_value: Annotated[str | None, Security(x_api_key_header)],
    db: AsyncSession = Depends(get_db),
) -> Principal:
    if not api_key_header_value and not x_api_key_header_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key or Authorization header",
        )

    # Use X-API-Key if available, otherwise fallback to Authorization
    api_key = x_api_key_header_value or api_key_header_value
    assert api_key is not None
    # Strip "Bearer " if present
    if api_key.lower().startswith("bearer "):
        api_key = api_key[7:]

    auth_service = AuthService(db)
    principal = await auth_service.get_principal_by_api_key(api_key)

    if not principal:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API Key",
        )

    return principal


class RequireRole:
    """Dependency class to require a specific role (or any of multiple roles)."""

    def __init__(self, *required_roles: Role):
        self.required_roles = required_roles

    def __call__(
        self, principal: Principal = Depends(get_current_principal)
    ) -> Principal:
        if not any(role in principal.roles for role in self.required_roles):
            roles_str = ", ".join([r.value for r in self.required_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Principal lacks required role: {roles_str}",
            )
        return principal
