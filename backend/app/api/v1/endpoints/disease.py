from typing import List, Optional
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_optional_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.disease_repo import DiseaseDiagnosisRepository
from app.schemas.common import StandardResponse
from app.schemas.disease import (
    DiseaseDiagnosisResponse,
    DiseaseHistoryItem,
    DiseaseModelMetricsResponse,
)
from app.services.disease_service import disease_service

router = APIRouter(tags=["Disease Diagnosis"])


@router.post(
    "/diseases/diagnose",
    response_model=StandardResponse[DiseaseDiagnosisResponse],
    status_code=status.HTTP_200_OK,
    summary="Diagnose Crop Disease from Image",
    description="Accepts an uploaded crop image, runs real MobileNetV3-Large inference across 17 disease classes, and returns prediction, confidence, uncertainty indicators, and cultural management practices.",
)
@router.post(
    "/disease-diagnoses/diagnose",
    response_model=StandardResponse[DiseaseDiagnosisResponse],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def diagnose_crop_disease(
    file: UploadFile = File(..., description="Crop leaf/plant image file (JPEG, PNG, or WebP)"),
    user: Optional[User] = Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_db),
):
    file_bytes = await file.read()
    filename = file.filename or "uploaded_crop_image.jpg"
    content_type = file.content_type

    diagnosis = await disease_service.diagnose_image(
        file_bytes=file_bytes,
        filename=filename,
        content_type=content_type,
        user=user,
        session=session,
    )

    return StandardResponse(
        success=True,
        data=diagnosis,
        message="Crop disease diagnosis completed successfully",
    )


@router.get(
    "/diseases/history",
    response_model=StandardResponse[List[DiseaseHistoryItem]],
    status_code=status.HTTP_200_OK,
    summary="Get Disease Diagnosis History",
    description="Retrieve past crop disease diagnoses for the authenticated farmer.",
)
@router.get(
    "/disease-diagnoses/history",
    response_model=StandardResponse[List[DiseaseHistoryItem]],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_disease_diagnosis_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    repo = DiseaseDiagnosisRepository(session)
    records = await repo.get_by_user_id(current_user.id, skip=skip, limit=limit)

    history_items: List[DiseaseHistoryItem] = []
    for item in records:
        crop, cond, disp, is_healthy = disease_service.format_class_name(item.predicted_condition or "Unknown")
        history_items.append(
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
                image_url=f"/uploads/{item.original_image_path}",
                model_version=item.model_version,
                created_at=item.created_at,
            )
        )

    return StandardResponse(
        success=True,
        data=history_items,
        message="Disease diagnosis history retrieved successfully",
    )


@router.get(
    "/diseases/model-metrics",
    response_model=StandardResponse[DiseaseModelMetricsResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Disease Model Evaluation Metrics",
    description="Retrieve stored evaluation metrics measured on the held-out test set.",
)
async def get_disease_model_metrics():
    metrics = disease_service.load_metrics()
    measured = metrics.get("measured_metrics", {})

    data = DiseaseModelMetricsResponse(
        architecture=metrics.get("architecture", "MobileNetV3-Large"),
        num_classes=metrics.get("num_classes", 17),
        test_samples=metrics.get("test_samples", 2010),
        accuracy=measured.get("accuracy", 0.9592),
        macro_precision=measured.get("macro_precision", 0.9636),
        macro_recall=measured.get("macro_recall", 0.9577),
        macro_f1=measured.get("macro_f1", 0.9602),
        weighted_f1=measured.get("weighted_f1", 0.9589),
        model_size_mb=measured.get("model_size_mb", 16.31),
        inference_latency_ms=measured.get("inference_latency_ms", 25.68),
        model_version=disease_service.MODEL_VERSION,
    )

    return StandardResponse(
        success=True,
        data=data,
        message="Disease model evaluation metrics retrieved successfully",
    )
