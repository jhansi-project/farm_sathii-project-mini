import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import FarmerProfile
from app.repositories.profile_repo import FarmerProfileRepository
from app.schemas.profile import FarmerProfileUpdate


class ProfileService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = FarmerProfileRepository(session)

    async def get_profile_by_user_id(self, user_id: uuid.UUID) -> Optional[FarmerProfile]:
        return await self.repo.get_by_user_id(user_id)

    async def create_default_profile(
        self, user_id: uuid.UUID, preferred_language: str = "en"
    ) -> FarmerProfile:
        return await self.repo.create(
            user_id=user_id,
            preferred_language=preferred_language,
        )

    async def update_profile(
        self, user_id: uuid.UUID, profile_in: FarmerProfileUpdate
    ) -> FarmerProfile:
        profile = await self.repo.get_by_user_id(user_id)
        if not profile:
            # Create if missing
            update_data = profile_in.model_dump(exclude_unset=True)
            return await self.repo.create(user_id=user_id, **update_data)

        update_data = profile_in.model_dump(exclude_unset=True)
        return await self.repo.update(profile, **update_data)
