from app.schemas.advisory import AdvisoryProviderStatus
from app.services.advisory.providers.base import (
    BaseAdvisoryProvider,
    AdvisoryPromptRequest,
    AdvisoryProviderResult,
)


class UnconfiguredProvider(BaseAdvisoryProvider):
    """
    Default provider when no external AI provider credentials (e.g., GEMINI_API_KEY)
    are configured in the environment.
    
    IMPORTANT ARCHITECTURAL RULE:
    - DO NOT fabricate an AI response.
    - DO NOT create fake/random advisory answers.
    - DO NOT pretend a rule engine is an LLM.
    - Return a clear structured 'advisory provider unavailable/not configured' response.
    """

    @property
    def supports_images(self) -> bool:
        return False

    @property
    def supports_multilingual(self) -> bool:
        return False

    def is_available(self) -> bool:
        return False

    def get_provider_name(self) -> str:
        return "unconfigured"

    async def generate_advisory(self, request: AdvisoryPromptRequest) -> AdvisoryProviderResult:
        explanation = (
            "FarmSathi advisory service is currently unconfigured. "
            "Please check back shortly or consult your local agricultural extension officer (KVK) for specialized guidance."
        )
        return AdvisoryProviderResult(
            content=explanation,
            status=AdvisoryProviderStatus.PROVIDER_UNAVAILABLE,
            provider_name=self.get_provider_name(),
            error_message="Advisory service temporarily unavailable.",
        )
