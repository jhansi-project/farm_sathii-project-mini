import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.languages import SUPPORTED_LANGUAGES, is_language_supported, DEFAULT_LANGUAGE


class AdvisoryProviderStatus(str, Enum):
    SUCCESS = "success"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    PROVIDER_ERROR = "provider_error"
    PROVIDER_TIMEOUT = "provider_timeout"
    SAFETY_FILTERED = "safety_filtered"
    INSUFFICIENT_CONTEXT = "insufficient_context"


class AdvisoryMessageBase(BaseModel):
    message_text: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Farmer's agricultural query or follow-up question",
    )


class AdvisoryMessageCreate(AdvisoryMessageBase):
    language: Optional[str] = Field(
        DEFAULT_LANGUAGE,
        max_length=10,
        description="Language code for the question/response (e.g., en, te, hi, ta, kn, mr)",
    )
    image_base64: Optional[str] = Field(
        None,
        description="Optional base64-encoded image data for multimodal advisory query",
    )
    image_content_type: Optional[str] = Field(
        None,
        description="Optional MIME type of attached image (image/jpeg, image/png, image/webp)",
    )
    image_filename: Optional[str] = Field(
        None,
        description="Optional original filename of attached image",
    )
    image_path: Optional[str] = Field(
        None,
        description="Optional storage path reference if image was already saved",
    )
    latitude: Optional[float] = Field(
        None,
        ge=-90.0,
        le=90.0,
        description="Optional latitude for location-aware advisory & real-time weather",
    )
    longitude: Optional[float] = Field(
        None,
        ge=-180.0,
        le=180.0,
        description="Optional longitude for location-aware advisory & real-time weather",
    )
    location_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional human-readable location name (e.g., Dundigal mandal, Telangana)",
    )

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> str:
        if not v:
            return DEFAULT_LANGUAGE
        code = v.strip().lower()
        if not is_language_supported(code):
            valid_codes = ", ".join(sorted(SUPPORTED_LANGUAGES.keys()))
            raise ValueError(f"Unsupported language code '{v}'. Supported languages: {valid_codes}")
        return code


class AdvisoryMessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_role: str  # "user" | "assistant"
    message_text: str
    audio_path: Optional[str] = None
    context_used: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdvisoryConversationCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=255, description="Conversation title")
    initial_message: Optional[str] = Field(
        None, min_length=1, max_length=4000, description="Optional first question"
    )
    language: Optional[str] = Field(
        DEFAULT_LANGUAGE,
        max_length=10,
        description="Preferred language code (e.g., en, te, hi, ta, kn, mr)",
    )
    image_base64: Optional[str] = Field(
        None,
        description="Optional base64-encoded image data for initial question",
    )
    image_content_type: Optional[str] = Field(
        None,
        description="Optional MIME type of attached image",
    )
    image_filename: Optional[str] = Field(
        None,
        description="Optional filename of attached image",
    )
    image_path: Optional[str] = Field(
        None,
        description="Optional storage path reference",
    )
    latitude: Optional[float] = Field(
        None,
        ge=-90.0,
        le=90.0,
        description="Optional latitude for location-aware advisory & real-time weather",
    )
    longitude: Optional[float] = Field(
        None,
        ge=-180.0,
        le=180.0,
        description="Optional longitude for location-aware advisory & real-time weather",
    )
    location_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional human-readable location name (e.g., Dundigal mandal, Telangana)",
    )

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> str:
        if not v:
            return DEFAULT_LANGUAGE
        code = v.strip().lower()
        if not is_language_supported(code):
            valid_codes = ", ".join(sorted(SUPPORTED_LANGUAGES.keys()))
            raise ValueError(f"Unsupported language code '{v}'. Supported languages: {valid_codes}")
        return code


class AdvisoryConversationSummary(BaseModel):
    id: uuid.UUID
    title: str
    language: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class AdvisoryConversationDetail(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    language: str
    created_at: datetime
    updated_at: datetime
    messages: List[AdvisoryMessageResponse] = []

    model_config = ConfigDict(from_attributes=True)


class AdvisoryExecutionResponse(BaseModel):
    conversation_id: uuid.UUID
    user_message: AdvisoryMessageResponse
    assistant_message: AdvisoryMessageResponse
    provider_status: AdvisoryProviderStatus
    safety_disclaimers: List[str] = []
    context_summary: Optional[Dict[str, Any]] = None
    provider_name: str
