import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CropRecommendationRequest(BaseModel):
    """
    Validated input for crop recommendation inference.
    Features follow the verified Random Forest training contract:
    [N, P, K, temperature, humidity, ph, rainfall].
    Supports both N/P/K and nitrogen/phosphorus/potassium naming.
    """
    nitrogen: float = Field(
        ...,
        ge=0.0,
        le=300.0,
        description="Soil Nitrogen content (ratio / index)",
        alias="N",
    )
    phosphorus: float = Field(
        ...,
        ge=0.0,
        le=300.0,
        description="Soil Phosphorus content (ratio / index)",
        alias="P",
    )
    potassium: float = Field(
        ...,
        ge=0.0,
        le=300.0,
        description="Soil Potassium content (ratio / index)",
        alias="K",
    )
    temperature: float = Field(
        ...,
        ge=-10.0,
        le=60.0,
        description="Ambient temperature in degrees Celsius",
    )
    humidity: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Relative humidity percentage (0-100%)",
    )
    ph: float = Field(
        ...,
        ge=0.0,
        le=14.0,
        description="Soil pH level (0-14)",
    )
    rainfall: float = Field(
        ...,
        ge=0.0,
        le=1000.0,
        description="Rainfall in mm",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "nitrogen": 90.0,
                "phosphorus": 42.0,
                "potassium": 43.0,
                "temperature": 25.0,
                "humidity": 80.0,
                "ph": 6.5,
                "rainfall": 200.0,
            }
        },
    )


class TopPrediction(BaseModel):
    crop: str
    probability: float


class CropRecommendationResponse(BaseModel):
    """Output prediction and metadata returned to user."""
    id: Optional[uuid.UUID] = None
    recommended_crop: str
    top_predictions: List[TopPrediction]
    inputs: Dict[str, float]
    model_version: str
    is_saved: bool = False
    created_at: Optional[datetime] = None


class CropRecommendationHistoryItem(BaseModel):
    """Historical recommendation record for authenticated user."""
    id: uuid.UUID
    recommended_crop: str
    top_predictions: List[TopPrediction]
    inputs: Dict[str, float]
    model_version: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
