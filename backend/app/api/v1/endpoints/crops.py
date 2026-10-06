from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_optional_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.crop_repo import CropRecommendationRepository
from app.schemas.common import StandardResponse
from app.schemas.crop import (
    CropRecommendationHistoryItem,
    CropRecommendationRequest,
    CropRecommendationResponse,
    TopPrediction,
)
from app.services.crop_service import crop_service

router = APIRouter(tags=["Crop Recommendations"])


@router.post(
    "/crops/recommend",
    response_model=StandardResponse[CropRecommendationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Crop Recommendation",
    description="Run real inference using the trained Random Forest model. Supports both guest requests and authenticated requests (with persistence to history).",
)
@router.post(
    "/crop-recommendations/recommend",
    response_model=StandardResponse[CropRecommendationResponse],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_crop_recommendation(
    payload: CropRecommendationRequest,
    user: Optional[User] = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_db),
):
    recommendation = await crop_service.recommend_crop(payload, user, session)
    return StandardResponse(
        success=True,
        data=recommendation,
        message="Crop recommendation generated successfully",
    )


@router.get(
    "/crops/history",
    response_model=StandardResponse[List[CropRecommendationHistoryItem]],
    status_code=status.HTTP_200_OK,
    summary="Get Crop Recommendation History",
    description="Retrieve past crop recommendations for the authenticated farmer.",
)
@router.get(
    "/crop-recommendations/history",
    response_model=StandardResponse[List[CropRecommendationHistoryItem]],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_crop_recommendation_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    crop_repo = CropRecommendationRepository(session)
    history_records = await crop_repo.get_by_user_id(
        current_user.id, skip=skip, limit=limit
    )

    history_items = [
        CropRecommendationHistoryItem(
            id=item.id,
            recommended_crop=item.recommended_crop,
            top_predictions=[TopPrediction(**p) for p in item.top_predictions],
            inputs={
                "N": float(item.nitrogen),
                "P": float(item.phosphorus),
                "K": float(item.potassium),
                "temperature": float(item.temperature),
                "humidity": float(item.humidity),
                "ph": float(item.ph),
                "rainfall": float(item.rainfall),
            },
            model_version=item.model_version,
            created_at=item.created_at,
        )
        for item in history_records
    ]

    return StandardResponse(
        success=True,
        data=history_items,
        message="Crop recommendation history retrieved successfully",
    )
