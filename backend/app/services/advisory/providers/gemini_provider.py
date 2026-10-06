import base64
import logging
from typing import Optional
import httpx

from app.core.languages import get_language_name
from app.schemas.advisory import AdvisoryProviderStatus
from app.services.advisory.providers.base import (
    BaseAdvisoryProvider,
    AdvisoryPromptRequest,
    AdvisoryProviderResult,
)

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAdvisoryProvider):
    """
    Google Gemini Advisory Provider using the official REST endpoints via httpx.
    Activated when GEMINI_API_KEY is present in settings or environment.
    Supports multimodal images and multilingual agronomy advisory.
    """

    def __init__(
        self,
        api_key: Optional[str],
        model: str = "gemini-2.5-flash",
        timeout_seconds: int = 20,
    ):
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    @property
    def supports_images(self) -> bool:
        return True

    @property
    def supports_multilingual(self) -> bool:
        return True

    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def get_provider_name(self) -> str:
        return f"gemini ({self.model})"

    async def generate_advisory(
        self, request: AdvisoryPromptRequest
    ) -> AdvisoryProviderResult:
        if not self.is_available():
            return AdvisoryProviderResult(
                content="We're unable to provide an advisory right now. Please try again shortly.",
                status=AdvisoryProviderStatus.PROVIDER_UNAVAILABLE,
                provider_name=self.get_provider_name(),
                error_message="Provider unavailable",
            )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        # Build language instruction if not English
        lang_instruction = ""
        if request.language and request.language.lower() != "en":
            lang_name = get_language_name(request.language)
            lang_instruction = (
                f"\n\nCRITICAL LANGUAGE REQUIREMENT: You MUST formulate your entire response in "
                f"{lang_name} ({request.language}). Ensure natural, respectful, and standard agricultural phrasing "
                f"accessible to local farmers."
            )

        # Construct payload with system instructions, farm context, and multi-turn history
        contents = [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            f"SYSTEM INSTRUCTIONS:\n{request.system_instructions}{lang_instruction}\n\n"
                            f"FARM CONTEXT:\n{request.context_text}"
                        )
                    }
                ],
            },
            {
                "role": "model",
                "parts": [
                    {
                        "text": (
                            "Understood. I am FarmSathi Agronomy Advisor. I will provide practical, "
                            "safe, contextual agricultural advice adhering strictly to these guidelines."
                        )
                    }
                ],
            },
        ]

        # Multi-turn history
        for turn in request.conversation_history:
            role = "user" if turn.get("role") == "user" else "model"
            text_val = turn.get("text", "").strip()
            if text_val:
                contents.append({"role": role, "parts": [{"text": text_val}]})

        # Latest farmer question parts (text + optional image)
        question_parts = []
        if request.image_bytes and request.image_mime_type:
            try:
                b64_data = base64.b64encode(request.image_bytes).decode("utf-8")
                question_parts.append(
                    {
                        "inlineData": {
                            "mimeType": request.image_mime_type,
                            "data": b64_data,
                        }
                    }
                )
                image_guidance = (
                    "[FARMER ATTACHED IMAGE]: The farmer has attached an image illustrating the condition of their "
                    "crop/plant. Inspect visible signs (foliage color, wilting, lesions, pests, or structure) and relate "
                    "them to the question. Do NOT fabricate an absolute diagnosis; if ambiguous or indicative of foliar disease, "
                    "clearly describe visible observations and recommend FarmSathi's dedicated Disease Detection feature or a local KVK specialist.\n"
                )
                question_parts.append({"text": image_guidance + request.farmer_question.strip()})
            except Exception as e:
                logger.error(f"Failed to encode image data for Gemini request: {e}")
                question_parts.append({"text": request.farmer_question.strip()})
        else:
            question_parts.append({"text": request.farmer_question.strip()})

        contents.append({"role": "user", "parts": question_parts})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1024,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=float(self.timeout_seconds)) as client:
                resp = await client.post(url, json=payload)

            if resp.status_code != 200:
                logger.error(
                    f"Gemini API returned error HTTP {resp.status_code}: {resp.text}"
                )
                return AdvisoryProviderResult(
                    content="The advisory provider returned an error while processing your question.",
                    status=AdvisoryProviderStatus.PROVIDER_ERROR,
                    provider_name=self.get_provider_name(),
                    error_message=f"Gemini API HTTP {resp.status_code}",
                )

            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return AdvisoryProviderResult(
                    content="No advisory advice could be generated for this query.",
                    status=AdvisoryProviderStatus.PROVIDER_ERROR,
                    provider_name=self.get_provider_name(),
                    error_message="Gemini returned 0 candidates",
                )

            parts = candidates[0].get("content", {}).get("parts", [])
            text_content = "".join([p.get("text", "") for p in parts]).strip()

            if not text_content:
                return AdvisoryProviderResult(
                    content="Empty response from advisory model.",
                    status=AdvisoryProviderStatus.PROVIDER_ERROR,
                    provider_name=self.get_provider_name(),
                    error_message="Empty candidate parts",
                )

            return AdvisoryProviderResult(
                content=text_content,
                status=AdvisoryProviderStatus.SUCCESS,
                provider_name=self.get_provider_name(),
                raw_metadata={"model": self.model},
            )

        except httpx.TimeoutException:
            logger.warning("Gemini API request timed out")
            return AdvisoryProviderResult(
                content="The advisory service timed out. Please try asking again in a moment.",
                status=AdvisoryProviderStatus.PROVIDER_TIMEOUT,
                provider_name=self.get_provider_name(),
                error_message="Request timeout",
            )
        except Exception as e:
            logger.exception("Unexpected error communicating with Gemini API")
            return AdvisoryProviderResult(
                content="Network error communicating with the advisory service.",
                status=AdvisoryProviderStatus.PROVIDER_ERROR,
                provider_name=self.get_provider_name(),
                error_message=str(e),
            )
