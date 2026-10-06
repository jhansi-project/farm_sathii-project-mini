from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.advisory import AdvisoryProviderStatus


class AdvisoryPromptRequest(BaseModel):
    farmer_question: str
    system_instructions: str
    context_text: str
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    language: str = "en"
    image_bytes: Optional[bytes] = None
    image_mime_type: Optional[str] = None
    image_filename: Optional[str] = None


class AdvisoryProviderResult(BaseModel):
    content: str
    status: AdvisoryProviderStatus
    provider_name: str
    raw_metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class BaseAdvisoryProvider(ABC):
    """Abstract interface for agricultural advisory LLM providers."""

    @property
    def supports_text(self) -> bool:
        """Indicates whether this provider supports natural language text queries."""
        return True

    @property
    def supports_images(self) -> bool:
        """Indicates whether this provider supports multimodal image inputs."""
        return False

    @property
    def supports_image(self) -> bool:
        """Alias for supports_images."""
        return self.supports_images

    @property
    def supports_multilingual(self) -> bool:
        """Indicates whether this provider supports multilingual queries/responses."""
        return True

    @abstractmethod
    async def generate_advisory(self, request: AdvisoryPromptRequest) -> AdvisoryProviderResult:
        """Call the provider to generate natural language agronomic advice."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider credentials/configuration are present and ready."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the descriptive name of this provider."""
        pass
