import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.policy import Policy
from app.schemas.policy import PolicyCreate, PolicyUpdate


class PolicyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_policy(self, obj_in: PolicyCreate) -> Policy:
        # Convert rules (list of BaseModel) to list of dicts for JSONB
        rules_dict = [r.model_dump() for r in obj_in.rules]

        db_obj = Policy(
            name=obj_in.name,
            description=obj_in.description,
            version=obj_in.version,
            status=obj_in.status,
            priority=obj_in.priority,
            rules=rules_dict,
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_policy(self, id: uuid.UUID) -> Policy | None:
        result = await self.db.execute(select(Policy).where(Policy.id == id))
        return result.scalars().first()

    async def get_policy_by_name(self, name: str) -> Policy | None:
        result = await self.db.execute(select(Policy).where(Policy.name == name))
        return result.scalars().first()

    async def get_multi(self, skip: int = 0, limit: int = 100) -> Sequence[Policy]:
        result = await self.db.execute(select(Policy).offset(skip).limit(limit))
        return result.scalars().all()

    async def update_policy(self, id: uuid.UUID, obj_in: PolicyUpdate) -> Policy | None:
        db_obj = await self.get_policy(id)
        if not db_obj:
            return None

        update_data = obj_in.model_dump(exclude_unset=True)
        if "rules" in update_data and update_data["rules"] is not None:
            update_data["rules"] = [r.model_dump() if hasattr(r, "model_dump") else r for r in update_data["rules"]]

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete_policy(self, id: uuid.UUID) -> bool:
        db_obj = await self.get_policy(id)
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.commit()
        return True

    async def get_active_policies(self) -> Sequence[Policy]:
        result = await self.db.execute(
            select(Policy).where(Policy.status == "ACTIVE")
        )
        return result.scalars().all()
