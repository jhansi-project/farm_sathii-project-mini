from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import FarmerProfile
from app.repositories.base import BaseRepository


class FarmerProfileRepository(BaseRepository[FarmerProfile]):
    def __init__(self, session: AsyncSession):
        super().__init__(FarmerProfile, session)

    async def get_by_user_id(self, user_id) -> Optional[FarmerProfile]:
        result = await self.session.execute(
            select(FarmerProfile).where(FarmerProfile.user_id == user_id)
        )
        return result.scalars().first()
