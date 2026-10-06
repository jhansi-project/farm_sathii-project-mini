from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.common import StandardResponse
from app.schemas.profile import FarmerProfileResponse, FarmerProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["Farmer Profile"])


@router.get(
    "",
    response_model=StandardResponse[FarmerProfileResponse],
    summary="Get current farmer profile and land preferences",
)
async def get_profile(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> StandardResponse[FarmerProfileResponse]:
    profile_service = ProfileService(session)
    profile = await profile_service.get_profile_by_user_id(current_user.id)
    if not profile:
        # Create default profile if not exists
        profile = await profile_service.create_default_profile(current_user.id)

    profile_data = FarmerProfileResponse.model_validate(profile)
    return StandardResponse(
        success=True,
        data=profile_data,
        message="Farmer profile retrieved successfully.",
    )


@router.put(
    "",
    response_model=StandardResponse[FarmerProfileResponse],
    summary="Update farmer land size, soil type, location, or preferred language",
)
async def update_profile(
    profile_in: FarmerProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> StandardResponse[FarmerProfileResponse]:
    profile_service = ProfileService(session)
    updated_profile = await profile_service.update_profile(current_user.id, profile_in)
    profile_data = FarmerProfileResponse.model_validate(updated_profile)
    return StandardResponse(
        success=True,
        data=profile_data,
        message="Farmer profile updated successfully.",
    )
