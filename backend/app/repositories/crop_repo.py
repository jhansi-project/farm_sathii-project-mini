import uuid
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crop_recommendation import CropRecommendation
from app.repositories.base import BaseRepository


class CropRecommendationRepository(BaseRepository[CropRecommendation]):
    def __init__(self, session: AsyncSession):
        super().__init__(CropRecommendation, session)

    async def get_by_user_id(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> List[CropRecommendation]:
        result = await self.session.execute(
            select(CropRecommendation)
            .where(CropRecommendation.user_id == user_id)
            .order_by(CropRecommendation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id_and_user_id(
        self, id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[CropRecommendation]:
        result = await self.session.execute(
            select(CropRecommendation).where(
                CropRecommendation.id == id,
                CropRecommendation.user_id == user_id,
            )
        )
        return result.scalars().first()

    async def count_by_user_id(self, user_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(CropRecommendation).where(
                CropRecommendation.user_id == user_id
            )
        )
        return result.scalar() or 0
