import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.advisory_repo import AdvisoryRepository
from app.repositories.crop_repo import CropRecommendationRepository
from app.repositories.disease_repo import DiseaseDiagnosisRepository
from app.schemas.advisory import (
    AdvisoryConversationDetail,
    AdvisoryConversationSummary,
)
from app.schemas.common import StandardResponse
from app.schemas.crop import (
    CropRecommendationHistoryItem,
    TopPrediction,
)
from app.schemas.disease import DiseaseHistoryItem
from app.schemas.history import (
    HistoryCounts,
    PaginatedAdvisoryHistory,
    PaginatedCropHistory,
    PaginatedDiseaseHistory,
    UnifiedHistoryItem,
    UserHistorySummary,
)
from app.services.advisory.advisory_engine import AdvisoryEngine
from app.services.disease_service import disease_service

router = APIRouter(prefix="/history", tags=["History & Activity"])


@router.get(
    "",
    response_model=StandardResponse[UserHistorySummary],
    status_code=status.HTTP_200_OK,
    summary="Get User Unified History & Recent Activity",
    description="Retrieve activity counts and a unified recent activity feed across crop recommendations, disease diagnoses, and advisory conversations.",
)
async def get_history_summary(
    limit: int = Query(10, ge=1, le=50, description="Max recent activity items to return"),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    crop_repo = CropRecommendationRepository(session)
    disease_repo = DiseaseDiagnosisRepository(session)
    advisory_repo = AdvisoryRepository(session)

    # 1. Total counts per module
    crop_count = await crop_repo.count_by_user_id(current_user.id)
    disease_count = await disease_repo.count_by_user_id(current_user.id)
    advisory_count = await advisory_repo.count_by_user_id(current_user.id)
    total_count = crop_count + disease_count + advisory_count

    counts = HistoryCounts(
        crop_recommendations=crop_count,
        disease_diagnoses=disease_count,
        advisory_conversations=advisory_count,
        total=total_count,
    )

    # 2. Fetch recent records from each module for the unified timeline
    recent_crops = await crop_repo.get_by_user_id(current_user.id, skip=0, limit=limit)
    recent_diseases = await disease_repo.get_by_user_id(current_user.id, skip=0, limit=limit)
    recent_advisories = await advisory_repo.get_by_user_id(current_user.id, skip=0, limit=limit)

    unified_items: List[UnifiedHistoryItem] = []

    for c in recent_crops:
        unified_items.append(
            UnifiedHistoryItem(
                id=c.id,
                module_type="crop",
                title=f"Crop: {c.recommended_crop.capitalize()}",
                subtitle=f"N:{c.nitrogen:.0f} P:{c.phosphorus:.0f} K:{c.potassium:.0f} | pH:{c.ph:.1f}",
                status="Recommended",
                created_at=c.created_at,
                metadata={
                    "recommended_crop": c.recommended_crop,
                    "rainfall": float(c.rainfall),
                    "temperature": float(c.temperature),
                },
            )
        )

    for d in recent_diseases:
        crop, cond, disp, is_healthy = disease_service.format_class_name(d.predicted_condition or "Unknown")
        conf_pct = f"{float(d.confidence) * 100:.1f}%" if d.confidence else "N/A"
        unified_items.append(
            UnifiedHistoryItem(
                id=d.id,
                module_type="disease",
                title=f"{crop}: {disp}",
                subtitle=f"Status: {'Healthy' if is_healthy else 'Infected'} (Confidence: {conf_pct})",
                status="Healthy" if is_healthy else "Disease Detected",
                created_at=d.created_at,
                metadata={
                    "crop": crop,
                    "condition": cond,
                    "display_name": disp,
                    "is_healthy": is_healthy,
                    "confidence": float(d.confidence) if d.confidence is not None else 0.0,
                    "image_url": f"/uploads/{d.original_image_path}" if d.original_image_path else None,
                },
            )
        )

    for a in recent_advisories:
        msg_count = len(a.messages) if a.messages else 0
        unified_items.append(
            UnifiedHistoryItem(
                id=a.id,
                module_type="advisory",
                title=a.title,
                subtitle=f"Advisory Chat ({msg_count} message{'s' if msg_count != 1 else ''})",
                status="Active",
                created_at=a.updated_at or a.created_at,
                metadata={
                    "language": a.language,
                    "message_count": msg_count,
                },
            )
        )

    # Sort descending by created_at and slice to requested limit
    unified_items.sort(key=lambda x: x.created_at, reverse=True)
    unified_items = unified_items[:limit]

    return StandardResponse(
        success=True,
        data=UserHistorySummary(
            counts=counts,
            recent_activities=unified_items,
        ),
        message="User history summary retrieved successfully",
    )


# ---------------------------------------------------------------------------
# Crop Recommendations History
# ---------------------------------------------------------------------------

@router.get(
    "/crop-recommendations",
    response_model=StandardResponse[PaginatedCropHistory],
    status_code=status.HTTP_200_OK,
    summary="Get Paginated Crop Recommendation History",
    description="Retrieve historical crop recommendation records belonging exclusively to the authenticated user.",
)
async def get_crop_recommendations_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    crop_repo = CropRecommendationRepository(session)
    total = await crop_repo.count_by_user_id(current_user.id)
    records = await crop_repo.get_by_user_id(current_user.id, skip=skip, limit=limit)

    items = [
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
        for item in records
    ]

    return StandardResponse(
        success=True,
        data=PaginatedCropHistory(items=items, total=total, skip=skip, limit=limit),
        message="Crop recommendation history retrieved successfully",
    )


@router.get(
    "/crop-recommendations/{recommendation_id}",
    response_model=StandardResponse[CropRecommendationHistoryItem],
    status_code=status.HTTP_200_OK,
    summary="Get Crop Recommendation Detail",
    description="Retrieve a single crop recommendation record. Enforces user isolation (404 if not owned).",
)
async def get_crop_recommendation_detail(
    recommendation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    crop_repo = CropRecommendationRepository(session)
    record = await crop_repo.get_by_id_and_user_id(recommendation_id, current_user.id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop recommendation record not found or access denied.",
        )

    item = CropRecommendationHistoryItem(
        id=record.id,
        recommended_crop=record.recommended_crop,
        top_predictions=[TopPrediction(**p) for p in record.top_predictions],
        inputs={
            "N": float(record.nitrogen),
            "P": float(record.phosphorus),
            "K": float(record.potassium),
            "temperature": float(record.temperature),
            "humidity": float(record.humidity),
            "ph": float(record.ph),
            "rainfall": float(record.rainfall),
        },
        model_version=record.model_version,
        created_at=record.created_at,
    )

    return StandardResponse(
        success=True,
        data=item,
        message="Crop recommendation detail retrieved successfully",
    )


# ---------------------------------------------------------------------------
# Disease Diagnoses History
# ---------------------------------------------------------------------------

@router.get(
    "/disease-diagnoses",
    response_model=StandardResponse[PaginatedDiseaseHistory],
    status_code=status.HTTP_200_OK,
    summary="Get Paginated Disease Diagnosis History",
    description="Retrieve historical disease diagnosis records belonging exclusively to the authenticated user.",
)
async def get_disease_diagnoses_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    disease_repo = DiseaseDiagnosisRepository(session)
    total = await disease_repo.count_by_user_id(current_user.id)
    records = await disease_repo.get_by_user_id(current_user.id, skip=skip, limit=limit)

    items: List[DiseaseHistoryItem] = []
    for item in records:
        crop, cond, disp, is_healthy = disease_service.format_class_name(item.predicted_condition or "Unknown")
        items.append(
            DiseaseHistoryItem(
                id=item.id,
                predicted_condition=item.predicted_condition or "Unknown",
                crop=crop,
                condition=cond,
                display_name=disp,
                is_healthy=is_healthy,
                confidence=float(item.confidence) if item.confidence is not None else 0.0,
                is_confident=item.is_confident,
                management_guidance=item.management_guidance,
                original_image_path=item.original_image_path,
                image_url=f"/uploads/{item.original_image_path}" if item.original_image_path else None,
                model_version=item.model_version,
                created_at=item.created_at,
            )
        )

    return StandardResponse(
        success=True,
        data=PaginatedDiseaseHistory(items=items, total=total, skip=skip, limit=limit),
        message="Disease diagnosis history retrieved successfully",
    )


@router.get(
    "/disease-diagnoses/{diagnosis_id}",
    response_model=StandardResponse[DiseaseHistoryItem],
    status_code=status.HTTP_200_OK,
    summary="Get Disease Diagnosis Detail",
    description="Retrieve a single disease diagnosis record. Enforces user isolation (404 if not owned).",
)
async def get_disease_diagnosis_detail(
    diagnosis_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    disease_repo = DiseaseDiagnosisRepository(session)
    record = await disease_repo.get_by_id_and_user_id(diagnosis_id, current_user.id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease diagnosis record not found or access denied.",
        )

    crop, cond, disp, is_healthy = disease_service.format_class_name(record.predicted_condition or "Unknown")
    item = DiseaseHistoryItem(
        id=record.id,
        predicted_condition=record.predicted_condition or "Unknown",
        crop=crop,
        condition=cond,
        display_name=disp,
        is_healthy=is_healthy,
        confidence=float(record.confidence) if record.confidence is not None else 0.0,
        is_confident=record.is_confident,
        management_guidance=record.management_guidance,
        original_image_path=record.original_image_path,
        image_url=f"/uploads/{record.original_image_path}" if record.original_image_path else None,
        model_version=record.model_version,
        created_at=record.created_at,
    )

    return StandardResponse(
        success=True,
        data=item,
        message="Disease diagnosis detail retrieved successfully",
    )


# ---------------------------------------------------------------------------
# Advisory Conversations History
# ---------------------------------------------------------------------------

@router.get(
    "/advisory-conversations",
    response_model=StandardResponse[PaginatedAdvisoryHistory],
    status_code=status.HTTP_200_OK,
    summary="Get Paginated Advisory Conversations History",
    description="Retrieve historical advisory conversations belonging exclusively to the authenticated user.",
)
async def get_advisory_conversations_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    advisory_repo = AdvisoryRepository(session)
    total = await advisory_repo.count_by_user_id(current_user.id)
    engine = AdvisoryEngine(session)
    summaries = await engine.get_user_conversations(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    return StandardResponse(
        success=True,
        data=PaginatedAdvisoryHistory(items=summaries, total=total, skip=skip, limit=limit),
        message="Advisory conversations history retrieved successfully",
    )


@router.get(
    "/advisory-conversations/{conversation_id}",
    response_model=StandardResponse[AdvisoryConversationDetail],
    status_code=status.HTTP_200_OK,
    summary="Get Advisory Conversation Detail with Messages",
    description="Retrieve full advisory conversation with all messages. Enforces user isolation (404 if not owned).",
)
async def get_advisory_conversation_detail(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    engine = AdvisoryEngine(session)
    detail = await engine.get_conversation_detail(conversation_id, current_user.id)
    return StandardResponse(
        success=True,
        data=detail,
        message="Advisory conversation detail retrieved successfully",
    )
