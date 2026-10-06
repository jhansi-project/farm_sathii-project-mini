import logging
from typing import Optional

from app.core.config import settings
from app.schemas.advisory import AdvisoryProviderStatus
from app.services.advisory.providers.base import (
    BaseAdvisoryProvider,
    AdvisoryPromptRequest,
    AdvisoryProviderResult,
)
from app.services.advisory.providers.agri_provider import AgriAdvisoryProvider
from app.services.advisory.providers.gemini_provider import GeminiProvider
from app.services.advisory.providers.unconfigured import UnconfiguredProvider

logger = logging.getLogger(__name__)


class ProviderRouter:
    """
    Provider-agnostic router that chooses the configured advisory provider.
    Defaults to the native AgriAdvisoryProvider so farmers always receive verified agronomic guidance.
    """

    def __init__(self, override_provider: Optional[BaseAdvisoryProvider] = None):
        self._override_provider = override_provider

    def set_override_provider(self, provider: Optional[BaseAdvisoryProvider]) -> None:
        self._override_provider = provider

    def get_provider(self) -> BaseAdvisoryProvider:
        if self._override_provider is not None:
            return self._override_provider

        # Always use FarmSathi native verified agronomic advisory provider
        return AgriAdvisoryProvider()

    async def route_and_generate(
        self, request: AdvisoryPromptRequest
    ) -> AdvisoryProviderResult:
        provider = self.get_provider()
        try:
            return await provider.generate_advisory(request)
        except Exception as e:
            logger.exception(
                f"Error during provider execution ({provider.get_provider_name()}): {e}"
            )
            return AdvisoryProviderResult(
                content="The advisory provider encountered an internal execution error.",
                status=AdvisoryProviderStatus.PROVIDER_ERROR,
                provider_name=provider.get_provider_name(),
                error_message=str(e),
            )


# Default global router instance
default_provider_router = ProviderRouter()
