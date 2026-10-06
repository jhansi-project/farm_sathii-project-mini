import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TopDiseasePrediction(BaseModel):
    raw_class: str
    crop: str
    condition: str
    display_name: str
    is_healthy: bool
    probability: float


class ManagementGuidance(BaseModel):
    cultural_practices: List[str] = Field(default_factory=list)
    sanitation: List[str] = Field(default_factory=list)
    prevention: List[str] = Field(default_factory=list)
    disclaimer: str


class DiseaseDiagnosisResponse(BaseModel):
    id: Optional[uuid.UUID] = None
    predicted_condition: str
    crop: str
    condition: str
    display_name: str
    is_healthy: bool
    confidence: float
    is_confident: bool
    is_suitable: bool = True
    suitability_message: Optional[str] = None
    uncertainty_notice: Optional[str] = None
    top_predictions: List[TopDiseasePrediction]
    management_guidance: ManagementGuidance
    original_image_path: str
    image_url: Optional[str] = None
    model_version: str
    is_saved: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DiseaseHistoryItem(BaseModel):
    id: uuid.UUID
    predicted_condition: str
    crop: str
    condition: str
    display_name: str
    is_healthy: bool
    confidence: float
    is_confident: bool
    management_guidance: Optional[Dict[str, Any]] = None
    original_image_path: str
    image_url: Optional[str] = None
    model_version: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DiseaseModelMetricsResponse(BaseModel):
    architecture: str
    num_classes: int
    test_samples: int
    accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    weighted_f1: float
    model_size_mb: float
    inference_latency_ms: float
    model_version: str
