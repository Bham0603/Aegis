import hashlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.domain.auth import Principal, PrincipalType, Role
from app.models.principal import PrincipalDB


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Returns the SHA-256 hash of the API key."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    async def get_principal_by_api_key(self, api_key: str) -> Principal | None:
        key_hash = self.hash_api_key(api_key)

        stmt = select(PrincipalDB).where(
            PrincipalDB.api_key_hash == key_hash, PrincipalDB.is_active == True
        )
        result = await self.db.execute(stmt)
        principal_db = result.scalars().first()

        if not principal_db:
            return None

        return Principal(
            principal_id=principal_db.id,  # type: ignore
            principal_type=PrincipalType(principal_db.principal_type),  # type: ignore
            roles=[Role(r) for r in principal_db.roles],  # type: ignore
            is_active=principal_db.is_active,  # type: ignore
        )
