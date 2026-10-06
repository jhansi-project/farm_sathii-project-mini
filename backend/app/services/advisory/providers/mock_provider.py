from typing import Optional
from app.schemas.advisory import AdvisoryProviderStatus
from app.services.advisory.providers.base import (
    BaseAdvisoryProvider,
    AdvisoryPromptRequest,
    AdvisoryProviderResult,
)


class MockAdvisoryProvider(BaseAdvisoryProvider):
    """
    Test and fixture advisory provider.
    Allows unit tests to verify provider success, timeout, failure, capability flags, and image inputs.
    """

    def __init__(
        self,
        name: str = "mock_provider",
        status: AdvisoryProviderStatus = AdvisoryProviderStatus.SUCCESS,
        content: str = "This is verified agricultural advisory guidance for testing.",
        available: bool = True,
        error_message: Optional[str] = None,
        should_timeout: bool = False,
        supports_images: bool = True,
        supports_multilingual: bool = True,
    ):
        self.name = name
        self._status = status
        self._content = content
        self._available = available
        self._error_message = error_message
        self._should_timeout = should_timeout
        self._supports_images = supports_images
        self._supports_multilingual = supports_multilingual
        self.last_received_request: Optional[AdvisoryPromptRequest] = None

    @property
    def supports_images(self) -> bool:
        return self._supports_images

    @property
    def supports_multilingual(self) -> bool:
        return self._supports_multilingual

    def is_available(self) -> bool:
        return self._available

    def get_provider_name(self) -> str:
        return self.name

    async def generate_advisory(
        self, request: AdvisoryPromptRequest
    ) -> AdvisoryProviderResult:
        self.last_received_request = request

        if self._should_timeout:
            return AdvisoryProviderResult(
                content="Advisory request timed out.",
                status=AdvisoryProviderStatus.PROVIDER_TIMEOUT,
                provider_name=self.name,
                error_message="Simulated provider timeout",
            )

        if not self._available:
            return AdvisoryProviderResult(
                content="Advisory provider is unavailable.",
                status=AdvisoryProviderStatus.PROVIDER_UNAVAILABLE,
                provider_name=self.name,
                error_message=self._error_message or "Provider unavailable",
            )

        return AdvisoryProviderResult(
            content=self._content,
            status=self._status,
            provider_name=self.name,
            error_message=self._error_message,
            raw_metadata={
                "received_image": bool(request.image_bytes),
                "received_language": request.language,
            },
        )
