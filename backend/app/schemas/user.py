import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.profile import FarmerProfileResponse


class UserBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserWithProfileResponse(UserResponse):
    profile: Optional[FarmerProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)
