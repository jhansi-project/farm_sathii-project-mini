import re
from typing import Dict, List, Tuple
from app.schemas.advisory import AdvisoryProviderStatus
from app.services.advisory.providers.base import AdvisoryProviderResult


class SafetyLayer:
    """
    Implements agricultural safety, uncertainty management, and regulatory compliance
    for FarmSathi Natural-Language Advisory.
    """

    GENERAL_DISCLAIMER = (
        "ℹ️ FarmSathi Advisory Notice: Agronomic recommendations are for informational "
        "and guidance purposes based on available field context. Always observe field-level "
        "conditions and consult a certified agronomist or local Krishi Vigyan Kendra (KVK) "
        "before significant chemical or economic interventions."
    )

    CHEMICAL_SAFETY_DISCLAIMER = (
        "⚠️ Chemical Safety Notice: For precise chemical pesticide/fungicide formulations, "
        "label dosages, safety waiting periods, and brand availability, consult a qualified "
        "local Krishi Vigyan Kendra (KVK) specialist or state agricultural extension officer."
    )

    VISUAL_DIAGNOSIS_RECOMMENDATION = (
        "📸 Visual Diagnosis Recommendation: Accurate plant disease identification requires "
        "leaf imagery. Please use FarmSathi's dedicated Disease Detection feature to upload a clear "
        "photograph of the affected leaf for computer vision diagnosis."
    )

    IMAGE_ADVISORY_NOTICE = (
        "📸 Visual Advisory Notice: Advisory observations on attached images are for field guidance "
        "and do not replace FarmSathi's dedicated Disease Detection deep-learning classifier. "
        "For lab-level disease diagnosis and verified management practices, run a Disease Scan."
    )

    CHEMICAL_KEYWORDS = [
        "spray",
        "pesticide",
        "insecticide",
        "fungicide",
        "chemical",
        "dosage",
        "dose",
        "ml/l",
        "fertilizer",
        "urea",
        "dap",
        "npk",
        "chlorpyrifos",
        "monocrotophos",
        "mancozeb",
        "carbendazim",
        "weedicide",
        "herbicide",
    ]

    DISEASE_IDENTIFICATION_KEYWORDS = [
        "what disease",
        "diagnose",
        "spots on leaf",
        "spots on leaves",
        "yellow spots",
        "brown spots",
        "black spots",
        "leaf curling",
        "blight",
        "rust",
        "mildew",
        "fungus",
        "fungal",
        "rot",
        "leaf spot",
    ]

    def build_system_instructions(self, language: str = "en") -> str:
        """
        Builds strict system prompt guidelines for LLM providers.
        """
        return (
            "You are the FarmSathi Natural-Language Agronomy Advisor, assisting Indian farmers.\n"
            "Strict Guidelines:\n"
            "1. GROUNDING & CONTEXT: Only use context explicitly provided under 'FARM CONTEXT'. "
            "Never fabricate farmer soil, crop, disease diagnosis, or weather data if not provided.\n"
            "2. NEVER CLAIM TO BE AN ML MODEL: You provide agronomic advisory text. "
            "Crop recommendations and disease detections are produced by dedicated FarmSathi ML models.\n"
            "3. CHEMICAL PRECAUTIONS: Do not invent arbitrary chemical pesticide dosages or mixing ratios. "
            "Prioritize integrated pest management (IPM), cultural sanitation, and bio-friendly methods. "
            "For hazardous chemicals, advise consulting local Krishi Vigyan Kendra (KVK) experts.\n"
            "4. VISUAL DIAGNOSIS: When asked to diagnose a plant disease purely from text, "
            "explicitly remind the farmer to use FarmSathi's Disease Detection feature to upload a leaf photograph.\n"
            "5. ATTACHED IMAGES: When an image is provided under visual context, comment on observable crop traits "
            "(discoloration, wilting, insect signs, mechanical damage). Never present your observations as an infallible "
            "laboratory disease diagnosis; recommend FarmSathi's dedicated Disease Detection feature for automated ML classification.\n"
            "6. UNCERTAINTY & INCOMPLETE DATA: If the farmer's question lacks essential context "
            "(e.g., crop variety, plant age, watering status), state what information is missing and ask clarifying questions.\n"
            "7. TONE & STRUCTURE: Be respectful, practical, empathetic, and concise. "
            "Structure advice with clear bullet points."
        )

    def post_process(
        self,
        farmer_question: str,
        provider_result: AdvisoryProviderResult,
        structured_context: Dict,
    ) -> Tuple[str, List[str], AdvisoryProviderStatus]:
        """
        Analyzes question and provider result, appends regulatory disclaimers,
        and determines the final provider status.
        """
        disclaimers: List[str] = [self.GENERAL_DISCLAIMER]
        q_lower = farmer_question.lower()

        # Check for insufficient context
        words = q_lower.strip().split()
        if len(words) <= 2 and not any(
            k in q_lower for k in ["crop", "fertilizer", "weather", "disease"]
        ):
            # Extremely terse query like "help" or "plant die"
            if provider_result.status == AdvisoryProviderStatus.SUCCESS:
                # Ensure user knows more context is needed
                clarification = (
                    "\n\n*To provide more accurate assistance, please specify your crop name, "
                    "current growth stage, and any symptoms observed.*"
                )
                text = provider_result.content + clarification
                return text, disclaimers, AdvisoryProviderStatus.INSUFFICIENT_CONTEXT

        # Check chemical keywords
        if any(re.search(rf"\b{re.escape(kw)}\b", q_lower) for kw in self.CHEMICAL_KEYWORDS):
            disclaimers.append(self.CHEMICAL_SAFETY_DISCLAIMER)

        # Check image context and visual diagnosis keywords
        has_attached_image = bool(structured_context.get("attached_image"))
        if has_attached_image:
            disclaimers.append(self.IMAGE_ADVISORY_NOTICE)
        elif any(kw in q_lower for kw in self.DISEASE_IDENTIFICATION_KEYWORDS):
            disclaimers.append(self.VISUAL_DIAGNOSIS_RECOMMENDATION)

        # Provider status passthrough
        return provider_result.content, disclaimers, provider_result.status
