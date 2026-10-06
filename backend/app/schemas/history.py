import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.crop import CropRecommendationHistoryItem
from app.schemas.disease import DiseaseHistoryItem
from app.schemas.advisory import AdvisoryConversationSummary


class HistoryCounts(BaseModel):
    crop_recommendations: int = 0
    disease_diagnoses: int = 0
    advisory_conversations: int = 0
    total: int = 0


class UnifiedHistoryItem(BaseModel):
    id: uuid.UUID
    module_type: str = Field(..., description="'crop' | 'disease' | 'advisory'")
    title: str
    subtitle: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class UserHistorySummary(BaseModel):
    counts: HistoryCounts
    recent_activities: List[UnifiedHistoryItem] = []


class PaginatedCropHistory(BaseModel):
    items: List[CropRecommendationHistoryItem]
    total: int
    skip: int
    limit: int


class PaginatedDiseaseHistory(BaseModel):
    items: List[DiseaseHistoryItem]
    total: int
    skip: int
    limit: int


class PaginatedAdvisoryHistory(BaseModel):
    items: List[AdvisoryConversationSummary]
    total: int
    skip: int
    limit: int
