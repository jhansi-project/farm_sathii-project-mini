import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class FarmerProfileBase(BaseModel):
    preferred_language: str = Field(default="en", max_length=10)
    state: Optional[str] = Field(default=None, max_length=100)
    district: Optional[str] = Field(default=None, max_length=100)
    village: Optional[str] = Field(default=None, max_length=100)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    land_size_acres: Optional[Decimal] = Field(default=None, ge=0)
    soil_type: Optional[str] = Field(default=None, max_length=50)
    irrigation_source: Optional[str] = Field(default=None, max_length=50)


class FarmerProfileUpdate(BaseModel):
    preferred_language: Optional[str] = Field(default=None, max_length=10)
    state: Optional[str] = Field(default=None, max_length=100)
    district: Optional[str] = Field(default=None, max_length=100)
    village: Optional[str] = Field(default=None, max_length=100)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    land_size_acres: Optional[Decimal] = Field(default=None, ge=0)
    soil_type: Optional[str] = Field(default=None, max_length=50)
    irrigation_source: Optional[str] = Field(default=None, max_length=50)


class FarmerProfileResponse(FarmerProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
