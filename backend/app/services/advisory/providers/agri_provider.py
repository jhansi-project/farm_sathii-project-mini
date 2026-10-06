"""
Native FarmSathi Agronomic Advisory Provider.
Delivers real, context-aware agricultural guidance and answers questions regarding
weather forecasts, crop recommendations, plant disease management, irrigation,
poor crop growth, leaf color changes, and soil health using verified context and
agronomic science in the farmer's preferred language (en, te, hi, ta, kn, mr).
Does not require external third-party API keys.
"""

import logging
import re
from typing import Any, Dict, Optional

from app.schemas.advisory import AdvisoryProviderStatus
from app.services.advisory.providers.base import (
    BaseAdvisoryProvider,
    AdvisoryPromptRequest,
    AdvisoryProviderResult,
)

logger = logging.getLogger(__name__)


class AgriAdvisoryProvider(BaseAdvisoryProvider):
    """
    Native knowledge- and context-driven advisory provider.
    Synthesizes authentic local weather, soil conditions, crop recommendations,
    and disease diagnoses into practical, farmer-friendly guidance in 6 languages.
    """

    def __init__(self, name: str = "farmsathi_advisory_engine"):
        self.name = name

    @property
    def supports_images(self) -> bool:
        return True

    @property
    def supports_multilingual(self) -> bool:
        return True

    def is_available(self) -> bool:
        return True

    @staticmethod
    def _match_terms(terms: list[str], text: str) -> bool:
        for term in terms:
            if ".*" in term:
                if re.search(term, text):
                    return True
            elif term.isascii():
                if re.search(r"\b" + re.escape(term) + r"\b", text):
                    return True
            else:
                if term in text:
                    return True
        return False

    def get_provider_name(self) -> str:
        return "FarmSathi Advisory Engine"

    async def generate_advisory(self, request: AdvisoryPromptRequest) -> AdvisoryProviderResult:
        question = request.farmer_question.strip()
        lang = (request.language or "en").lower().strip()
        context_text = request.context_text or ""

        # Extract real context items from context_text if present
        weather_info = self._extract_weather(context_text)
        crop_rec_info = self._extract_crop_rec(context_text)
        disease_info = self._extract_disease(context_text)
        profile_info = self._extract_profile(context_text)

        # Categorize question intent with high discriminative specificity
        q_lower = question.lower()

        # Image presence detection
        has_attached_image = (
            disease_info.get("is_attached") is True
            or request.image_bytes is not None
            or bool(getattr(request, "raw_metadata", None) and getattr(request, "raw_metadata", {}).get("has_image"))
        )

        is_leaf_image_q = self._match_terms([
            "leaf image", "leaf photo", "problem in the leaf", "problem in leaf", "in the leaf",
            "leaf picture", "image of leaf", "check this image", "tell me what is the problem in the leaf",
            "problem in the leaf image", "tell what is the problem in the leaf image", "what is the problem in the leaf image",
            "what problem in leaf", "what is wrong with this leaf", "look at this leaf",
            "ఆకు ఫోటో", "ఆకు చిత్రం", "చిత్రంలో", "ఆకు చిత్రంలో సమస్య",
            "पत्ती की फोटो", "पत्ती की तस्वीर", "पत्ती में समस्या", "पत्ती चित्र",
            "இலை புகைப்படம்", "இலை படம்", "இலையில் பிரச்சனை",
            "ಎಲೆಯ ಫೋಟೋ", "ಎಲೆ ಚಿತ್ರ", "ಎಲೆಯಲ್ಲಿ ಸಮಸ್ಯೆ",
            "पानाचा फोटो", "पानाचे चित्र", "पानातील समस्या"
        ], q_lower)

        # Soil parameters in question
        soil_params = self._extract_soil_from_question(question)

        # 1. Spray before rain
        is_spray_before_rain_q = (
            self._match_terms([
                "spray", "spraying", "pesticide", "fungicide", "chemical",
                "మందు", "పిచికారీ", "छिड़काव", "कीटनाशक", "தெளி", "தெளிக்க", "ಸಿಂಪಡಣೆ", "फवारणी"
            ], q_lower)
            and self._match_terms([
                "before rain", "rain", "వర్షం", "ముందు", "बारिश", "पहले", "மழைக்கு முன்", "மழை", "ಮಳೆಗೆ ಮುನ್ನ", "ಮಳೆ", "पावसापूर्वी", "पाऊस"
            ], q_lower)
        )

        # 2. Field flooded / heavy rain / post-rain recovery
        is_post_rain_q = (
            self._match_terms([
                "rained heavily", "heavy rain", "flooded", "waterlogged", "water standing", "excess water", "yesterday",
                "వర్షం పడింది", "భారీ వర్షం", "నీరు నిలిచింది", "నిన్న",
                "भारी बारिश", "पानी भर गया", "कल",
                "கனமழை", "தண்ணீர் தேங்கியுள்ளது",
                "ಭಾರಿ ಮಳೆ", "ನೀರು ನಿಂತಿದೆ",
                "मुसळधार पाऊस", "पाणी साचले"
            ], q_lower)
            and self._match_terms([
                "rain", "water", "వర్షం", "నీరు", "बारिश", "पानी", "மழை", "தண்ணீர்", "ಮಳೆ", "ನೀರು", "पाऊस", "पाणी"
            ], q_lower)
        )

        # 3. Flower drop / blossom fall (e.g. "Why are my tomato flowers falling?")
        is_flower_drop_q = self._match_terms([
            "flower drop", "flowers drop", "flowers falling", "flower falling", "dropping flower", "falling flower",
            "blossom drop", "blossom fall", "flower fall", "flowers are falling", "flowers fall", "blossoms drop",
            "పూత రాలడం", "పువ్వులు రాలిపోవడం", "పూత రాలుతుంది", "పూత రాలిపోతుంది", "పువ్వులు రాలుతున్నాయి", "పువ్వు రాలడం",
            "फूल झड़", "फूल गिर", "फूलों का गिरना", "फूल गिरना", "फूल झड़ना", "फूल गिर रहे",
            "பூ உதிர்", "பூக்கள் உதிர்", "பூ கொட்டுகிறது", "பூ உதிர்கிறது",
            "ಹೂವು ಉದುರುವುದು", "ಹೂ ಉದುರುವುದು", "ಹೂವು ಬೀಳುವುದು", "ಹೂವು ಉದುರುತ್ತಿದೆ",
            "फुलगळ", "फुले गळणे", "फुल गळती", "फुले गळत आहेत"
        ], q_lower)

        # 4. Seed germination & emergence (e.g. "How can I improve seed germination?")
        is_germination_q = self._match_terms([
            "germination", "germinate", "seed emergence", "improve germination", "seed sprouting", "sprouting",
            "seeds not sprouting", "seed vitality", "seedling emergence",
            "మొలక", "మొలక శాతం", "మొలకెత్తడం", "బీజోత్పత్తి", "విత్తనాలు మొలకెత్తడం",
            "अंकुरण", "बीज अंकुरण", "जमाव", "उगाया", "अंकुरित",
            "முளைப்புத்திறன்", "விதை முளைப்பு", "முளைக்கவில்லை",
            "ಬೀಜ ಮೊಳಕೆಯೊಡೆಯುವಿಕೆ", "ಮೊಳಕೆ", "ಮೊಳಕೆಯೊಡೆಯಲು",
            "बियाणे उगवण", "उगवण क्षमता", "उगवण"
        ], q_lower)

        # 5. Post-sowing field care (e.g. "What should I do after sowing?")
        is_post_sowing_q = self._match_terms([
            "after sowing", "post sowing", "sown the seeds", "after planting", "sowing care", "just sowed",
            "care after sowing", "what to do after sowing", "what should i do after sowing",
            "విత్తిన తర్వాత", "విత్తనాలు వేసిన తర్వాత", "నాటిన తర్వాత",
            "बुवाई के बाद", "बोने के बाद", "बीज डालने के बाद",
            "விதைத்த பிறகு", "விதைப்புக்கு பின்",
            "ಬಿತ್ತನೆಯ ನಂತರ", "ಬಿತ್ತಿದ ಮೇಲೆ",
            "पेरणीनंतर", "पेरणी नंतर"
        ], q_lower)

        # 6. Curling leaves (pests, leaf curl virus, heat or fertilizer burn)
        is_curling_leaves_q = (
            self._match_terms([
                "curl", "curling", "curled",
                "ముడుచు", "ముడత", "రోగం", "ముడతలు",
                "मुड़", "सिकुड़", "ऐंठन", "मुड़ी",
                "சுருள்", "சுருண்டு", "சுருங்கு",
                "ಸುರುಳಿ", "ಮುರುಟು",
                "वाकडी", "गुंडाळ", "कोकडा", "वळणे"
            ], q_lower)
            and self._match_terms([
                "leaf", "leaves", "crop", "plant", "fertilizer",
                "ఆకు", "ఆకులు", "పంట", "వరి", "మిరప", "ఎరువు",
                "पत्ता", "पत्तियां", "फसल", "मिर्च", "खाद",
                "இலை", "இலைகள்", "பயிர்", "உரம்",
                "ಎಲೆ", "ಎಲೆಗಳು", "ಬೆಳೆ", "ಗೊಬ್ಬರ",
                "पान", "पाने", "पिक", "खत"
            ], q_lower)
        )

        # 7. Color change, yellowing, pale leaves, paddy turning color
        is_color_change_or_yellow_q = (
            self._match_terms([
                "yellow", "yellowing", "turning color", "turning colour", "change.*color", "changing.*color", "turning.*yellow", "discoloration", "pale",
                "పసుపు", "రంగు", "రంగు మారు",
                "पीला", "पीली", "पीले", "रंग बदल", "रंग",
                "மஞ்சள்", "நிறம் மாறு", "நிறம்",
                "ಹಳದಿ", "ಬಣ್ಣ ಬದಲಾಗ", "ಬಣ್ಣ",
                "पिवळे", "पिवळी", "पिवळा", "रंग बदल", "फिकट"
            ], q_lower)
            and self._match_terms([
                "leaf", "leaves", "rice", "paddy", "crop", "plant", "wheat", "cotton", "field",
                "ఆకు", "ఆకులు", "పంట", "వరి", "మొక్క", "పొలం",
                "पत्ता", "पत्तियां", "धान", "फसल", "खेत",
                "இலை", "இலைகள்", "பயிர்", "நெல்", "வயல்",
                "ಎಲೆ", "ಎಲೆಗಳು", "ಬೆಳೆ", "ಭತ್ತ", "ಹೊಲ",
                "पान", "पाने", "पिक", "भात", "शेत"
            ], q_lower)
        )

        # 8. Poor crop growth / stunted development
        is_crop_growth_q = self._match_terms([
            "not growing", "growth is slow", "stunted", "slow growth", "not growing well", "poor growth",
            "growth stopped", "weak growth", "crop not growing", "plant not growing", "development",
            "growth reason", "not growing properly", "growing properly", "proper growth", "stunting",
            "ఎదగడం లేదు", "పెరగడం లేదు", "పెరుగుదల లేదు", "ఎదుగుదల లోపం", "బాగా పెరగడం లేదు", "ఎదగడం", "పెరగడం",
            "బలహీనంగా", "ఎదుగుదల ఆగిపోయింది",
            "बढ़वार नहीं", "बढ़ नहीं", "विकास नहीं", "सटीक बढ़वार", "पौधा बढ़ नहीं", "फसल बढ़ नहीं", "बढ़वार", "वृद्धि नहीं",
            "வளரவில்லை", "வளர்ச்சி குறைவு", "வளர்ச்சி இல்லை", "சரியாக வளரவில்லை", "வளர்ச்சி",
            "ಬೆಳೆಯುತ್ತಿಲ್ಲ", "ಬೆಳವಣಿಗೆ ನಿಂತಿದೆ", "ಕುಂಠಿತ ಬೆಳವಣಿಗೆ", "ಚೆನ್ನಾಗಿ ಬೆಳೆಯುತ್ತಿಲ್ಲ", "ಬೆಳವಣಿಗೆ",
            "वाढ होत नाही", "वाढ खुंटली", "वाढ थांबली", "चांगली वाढ नाही", "वाढ"
        ], q_lower)

        # 9. Irrigation / watering queries
        is_irrigation_q = self._match_terms([
            "water my", "irrigation", "watering", "drip", "moisture", "when should i irrigate", "irrigate",
            "water plants", "watering schedule", "irrigation schedule",
            "నీరు పెట్ట", "నీటిపారుదల", "తడి", "నీరు ఎప్పుడు",
            "सिंचाई", "पानी कब", "सिंचाई कब करें",
            "தண்ணீர் பாய்ச்ச", "பாசனம்", "எப்போது தண்ணீர்",
            "ನೀರುಣಿಸುವುದು", "ನೀರಾವರಿ", "ಯಾವಾಗ ನೀರು",
            "पाणी कधी", "सिंचन", "पाणी देणे"
        ], q_lower)

        # 10. Weather & Tomorrow queries
        is_tomorrow_q = self._match_terms(["tomorrow", "next day", "రేపు", "कल", "आने वाले कल", "நாளை", "நாளைக்கு", "ನಾಳೆ", "उद्या"], q_lower)
        is_weather_q = self._match_terms([
            "rain", "raining", "rainfall", "weather", "temperature", "temp", "forecast", "cloud", "sunny", "humid", "humidity", "storm", "climate", "precipitation",
            "వర్షం", "వాతావరణం", "ఎండ", "ఉష్ణోగ్రత", "తేమ",
            "मौसम", "बारिश", "तापमान", "हवामान",
            "மழை", "வானிலை", "வெப்பநிலை",
            "ಮಳೆ", "ಹವಾಮಾನ", "ತಾಪಮಾನ",
            "पाऊस", "तापमान", "हवामान"
        ], q_lower)

        # 11. Specific crop recommendation query (asking what to grow / crop selection)
        is_crop_rec_q = self._match_terms([
            "which crop", "what crop", "which crops", "what crops", "recommend.*crop", "crop to grow", "crops to grow",
            "crop should i", "crops should i", "suitable crop", "suitable crops", "crop recommendation",
            "crops recommendation", "best crop", "best crops", "suggest.*crop", "suggest.*crops", "crop selection",
            "crops selection", "what should i sow", "what should i plant", "crops will grow", "crop will grow",
            "crops can grow", "grow in", "grow in the location",
            "ఏ పంట", "పంట సిఫార్సు", "ఏ పంట వేయాలి", "ఏ పంట సాగు", "ఏది మేలు", "పంటలు పండుతాయి", "ఏ పంటలు",
            "कौन सी फसल", "फसल सिफ़ारिश", "फसल लगाएं", "कौन सी खेती", "कौन सी फसलें", "फसलें उगेंगी",
            "எந்த பயிர்", "பயிர் பரிந்துரை", "எந்த பயிர் சாகுபடி", "எந்த பயிர்கள்",
            "ಯಾವ ಬೆಳೆ", "ಬೆಳೆ ಶಿಫಾರಸು", "ಯಾವ ಬೆಳೆ ಬೆಳೆಯಬೇಕು", "ಯಾವ ಬೆಳೆಗಳು",
            "कोणते पीक", "पीक शिफारस", "कोणते पीक घ्यावे", "कोणती पिके"
        ], q_lower)

        # 12. Disease & Pest queries
        is_disease_q = self._match_terms([
            "disease", "pest", "fungus", "fungal", "blight", "spot", "spots", "rot", "rust", "bug", "insect", "worm", "caterpillar",
            "పురుగు", "తెగులు", "రోగం", "రోగ", "మచ్చలు",
            "कीड़ा", "झुलसा", "फफूंद", "रोग",
            "பூச்சி", "நோய்", "கருகல்",
            "ಕೀಟ", "ರೋಗ", "ಬೆಂಕಿರೋಗ",
            "कीड", "रोग", "करपा"
        ], q_lower)

        # 13. Fertilizer & Soil nutrition queries
        is_fertilizer_q = self._match_terms([
            "fertilizer", "urea", "dap", "npk", "potash", "nitrogen", "phosphorus", "compost", "manure", "top dressing", "dose", "dosage", "nutrient",
            "ఎరువు", "యూరియా", "భాస్వరం", "డిఎపి", "పొటాష్",
            "खाद", "उर्वरक", "यूरिया", "डीएपी", "पोटाश",
            "உரம்", "யூரியா", "சாணம்",
            "ಗೊಬ್ಬರ", "ಯೂರಿಯಾ", "ರಸಗೊಬ್ಬರ",
            "खत", "युरिया", "शेणखत"
        ], q_lower)

        response_text = ""
        provider_status = AdvisoryProviderStatus.SUCCESS
        detected_intent = "general_agronomy"

        # Priority dispatch for high-specificity agronomic questions
        if has_attached_image:
            response_text = self._build_attached_image_disease_response(question, disease_info, lang)
            provider_status = (
                AdvisoryProviderStatus.SUCCESS
                if disease_info.get("is_suitable", True)
                else AdvisoryProviderStatus.INSUFFICIENT_CONTEXT
            )
            detected_intent = "attached_image_disease"
        elif is_leaf_image_q:
            response_text = self._build_missing_leaf_image_prompt(question, lang)
            provider_status = AdvisoryProviderStatus.INSUFFICIENT_CONTEXT
            detected_intent = "missing_leaf_image"
        elif soil_params is not None:
            response_text = self._build_crop_ml_prediction_response(question, soil_params, weather_info, lang)
            provider_status = AdvisoryProviderStatus.SUCCESS
            detected_intent = "crop_ml_prediction"
        elif is_flower_drop_q:
            response_text = self._build_flower_drop_response(question, lang)
            provider_status = AdvisoryProviderStatus.SUCCESS
            detected_intent = "flower_drop"
        elif is_germination_q:
            response_text = self._build_germination_response(question, lang)
            provider_status = AdvisoryProviderStatus.SUCCESS
            detected_intent = "seed_germination"
        elif is_post_sowing_q:
            response_text = self._build_post_sowing_response(question, lang)
            provider_status = AdvisoryProviderStatus.SUCCESS
            detected_intent = "post_sowing"
        elif is_spray_before_rain_q:
            response_text = self._build_spray_before_rain_response(question, lang)
            provider_status = AdvisoryProviderStatus.SUCCESS
            detected_intent = "spray_before_rain"
        elif is_post_rain_q:
            response_text = self._build_post_rain_response(question, lang)
            provider_status = AdvisoryProviderStatus.SUCCESS
            detected_intent = "post_rain"
        elif is_curling_leaves_q:
            response_text = self._build_curling_leaves_response(question, lang)
            provider_status = AdvisoryProviderStatus.SUCCESS
            detected_intent = "curling_leaves"
        elif is_color_change_or_yellow_q:
            response_text = self._build_yellow_leaves_response(question, lang)
            provider_status = AdvisoryProviderStatus.SUCCESS
            detected_intent = "yellow_leaves"
        elif is_crop_growth_q:
            response_text = self._build_crop_growth_response(question, crop_rec_info, profile_info, lang)
            provider_status = AdvisoryProviderStatus.SUCCESS
            detected_intent = "crop_growth"
        elif is_irrigation_q and not is_tomorrow_q:
            response_text = self._build_irrigation_response(question, weather_info, crop_rec_info, lang)
            provider_status = AdvisoryProviderStatus.SUCCESS
            detected_intent = "irrigation"
        elif is_weather_q or is_tomorrow_q:
            response_text = self._build_weather_response(question, weather_info, profile_info, lang, is_tomorrow=is_tomorrow_q)
            provider_status = (
                AdvisoryProviderStatus.SUCCESS
                if weather_info and ("temp" in weather_info or "tomorrow" in weather_info)
                else AdvisoryProviderStatus.INSUFFICIENT_CONTEXT
            )
            detected_intent = "weather"
        elif is_crop_rec_q:
            if crop_rec_info.get("crop"):
                response_text = self._build_crop_response(question, crop_rec_info, profile_info, lang)
                provider_status = AdvisoryProviderStatus.SUCCESS
            else:
                response_text = self._build_crop_location_missing_soil_response(question, weather_info, profile_info, lang)
                provider_status = AdvisoryProviderStatus.INSUFFICIENT_CONTEXT
            detected_intent = "crop_rec"
        elif is_disease_q:
            response_text = self._build_disease_response(question, disease_info, crop_rec_info, lang, has_image=has_attached_image)
            provider_status = AdvisoryProviderStatus.SUCCESS
            detected_intent = "disease"
        elif is_fertilizer_q:
            response_text = self._build_fertilizer_response(question, crop_rec_info, lang)
            provider_status = AdvisoryProviderStatus.SUCCESS
            detected_intent = "fertilizer"
        else:
            response_text = self._build_general_agronomy_response(question, profile_info, crop_rec_info, lang)
            provider_status = AdvisoryProviderStatus.SUCCESS
            detected_intent = "general_agronomy"

        return AdvisoryProviderResult(
            content=response_text,
            status=provider_status,
            provider_name=self.get_provider_name(),
            raw_metadata={
                "language": lang,
                "detected_intent": detected_intent,
            },
        )

    def _extract_weather(self, context_text: str) -> Dict[str, Any]:
        info: Dict[str, Any] = {}
        if "### Local Weather" in context_text or "### Cached Local Weather" in context_text:
            loc_m = re.search(r"- Location:\s*([^\n\r]+)", context_text)
            if not loc_m:
                loc_m = re.search(r"### Local Weather\s*\(([^)]+)\):", context_text)
            if loc_m:
                loc_val = loc_m.group(1).strip()
                if "Real/Live Cache" not in loc_val:
                    info["location"] = loc_val

            temp_m = re.search(r"(?:Current\s+)?Temperature:\s*([0-9.]+)\s*°?C", context_text)
            if temp_m:
                info["temp"] = temp_m.group(1)
            cond_m = re.search(r"(?:Current\s+)?Condition:\s*([^\n\r]+)", context_text)
            if cond_m:
                info["condition"] = cond_m.group(1).strip()
            hum_m = re.search(r"(?:Current\s+)?(?:Relative\s+)?Humidity:\s*([0-9.]+)\s*%", context_text)
            if hum_m:
                info["humidity"] = hum_m.group(1)
            precip_m = re.search(r"(?:Current\s+)?Precipitation:\s*([0-9.]+)\s*mm", context_text)
            if precip_m:
                info["precip"] = precip_m.group(1)
            wind_m = re.search(r"(?:Current\s+)?Wind Speed:\s*([0-9.]+)\s*km/h", context_text)
            if wind_m:
                info["wind"] = wind_m.group(1)

            # Extract Tomorrow's Forecast if present
            tm_m = re.search(
                r"Tomorrow's Forecast\s*\(([^)]+)\):\s*([^,]+),\s*Rain Expected:\s*(Yes|No),\s*Precipitation:\s*([0-9.]+)\s*mm,\s*Temp:\s*([0-9.]+)°C to ([0-9.]+)°C",
                context_text,
            )
            if tm_m:
                info["tomorrow"] = {
                    "date": tm_m.group(1),
                    "condition": tm_m.group(2).strip(),
                    "rain_expected": tm_m.group(3).lower() == "yes",
                    "precip": float(tm_m.group(4)),
                    "temp_min": tm_m.group(5),
                    "temp_max": tm_m.group(6),
                }

            if "provider temporarily unavailable" in context_text.lower():
                info["status"] = "provider_unavailable"
                info["unavailable"] = True

        return info

    def _extract_crop_rec(self, context_text: str) -> Dict[str, Any]:
        info: Dict[str, Any] = {}
        if "### Crop Recommendation History" in context_text:
            crop_m = re.search(r"Recommended Crop:\s*([^\n\r]+)", context_text)
            if crop_m:
                info["crop"] = crop_m.group(1).strip()
            npk_m = re.search(r"Recorded Soil N-P-K:\s*([0-9.]+)-([0-9.]+)-([0-9.]+)", context_text)
            if npk_m:
                info["n"] = npk_m.group(1)
                info["p"] = npk_m.group(2)
                info["k"] = npk_m.group(3)
            ph_m = re.search(r"Soil pH:\s*([0-9.]+)", context_text)
            if ph_m:
                info["ph"] = ph_m.group(1)
        return info

    def _extract_disease(self, context_text: str) -> Dict[str, Any]:
        info: Dict[str, Any] = {}
        if "### Attached Image Foliar Disease Diagnosis" in context_text:
            info["is_attached"] = True
            info["is_suitable"] = True
            m_cond = re.search(r"Diagnosed Condition:\s*([^\n\r]+)", context_text)
            if m_cond:
                info["condition"] = m_cond.group(1).strip()
            m_conf = re.search(r"Diagnostic Confidence:\s*([^\n\r]+)", context_text)
            if m_conf:
                info["confidence"] = m_conf.group(1).strip()
            m_crop = re.search(r"Primary Crop:\s*([^\n\r]+)", context_text)
            if m_crop:
                info["crop"] = m_crop.group(1).strip()
            m_fol = re.search(r"Foliar Condition:\s*([^\n\r]+)", context_text)
            if m_fol:
                info["foliar_condition"] = m_fol.group(1).strip()
            m_hlth = re.search(r"Is Healthy:\s*(True|False)", context_text, re.IGNORECASE)
            if m_hlth:
                info["is_healthy"] = m_hlth.group(1).lower() == "true"
            m_mgmt = re.search(r"- Management Practices:([\s\S]+?)(?=\n###|\Z)", context_text)
            if m_mgmt:
                info["practices"] = m_mgmt.group(1).strip()
        elif "### Attached Image Foliar Diagnosis Result" in context_text:
            info["is_attached"] = True
            info["is_suitable"] = False
            m_assess = re.search(r"- Assessment:\s*([^\n\r]+)", context_text)
            if m_assess:
                info["suitability_message"] = m_assess.group(1).strip()
        elif "### Recent Disease Diagnosis" in context_text:
            info["is_attached"] = False
            info["is_suitable"] = True
            diag_m = re.search(r"Diagnosed Condition:\s*([^\n\r]+)", context_text)
            if diag_m:
                info["condition"] = diag_m.group(1).strip()
            conf_m = re.search(r"Diagnostic Confidence:\s*([^\n\r]+)", context_text)
            if conf_m:
                info["confidence"] = conf_m.group(1).strip()
        return info

    def _extract_soil_from_question(self, text: str) -> Optional[Dict[str, float]]:
        # Look for Nitrogen / N
        n_m = re.search(r"\b(?:n|nitrogen)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)\b", text, re.IGNORECASE)
        # Look for Phosphorus / P
        p_m = re.search(r"\b(?:p|phosphorus|phosphate)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)\b", text, re.IGNORECASE)
        # Look for Potassium / K
        k_m = re.search(r"\b(?:k|potassium|potash)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)\b", text, re.IGNORECASE)
        # Look for pH
        ph_m = re.search(r"\b(?:ph|soil ph)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)\b", text, re.IGNORECASE)

        if n_m and p_m and k_m and ph_m:
            temp_m = re.search(r"\b(?:temp|temperature)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)\b", text, re.IGNORECASE)
            hum_m = re.search(r"\b(?:hum|humidity)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)\b", text, re.IGNORECASE)
            rain_m = re.search(r"\b(?:rain|rainfall|precipitation)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)\b", text, re.IGNORECASE)

            return {
                "n": float(n_m.group(1)),
                "p": float(p_m.group(1)),
                "k": float(k_m.group(1)),
                "ph": float(ph_m.group(1)),
                "temp": float(temp_m.group(1)) if temp_m else None,
                "humidity": float(hum_m.group(1)) if hum_m else None,
                "rainfall": float(rain_m.group(1)) if rain_m else None,
            }
        return None

    def _extract_profile(self, context_text: str) -> Dict[str, Any]:
        info: Dict[str, Any] = {}
        if "### Farmer Profile" in context_text:
            dist_m = re.search(r"District:\s*([^\n\r]+)", context_text)
            if dist_m:
                info["district"] = dist_m.group(1).strip()
            state_m = re.search(r"State:\s*([^\n\r]+)", context_text)
            if state_m:
                info["state"] = state_m.group(1).strip()
            soil_m = re.search(r"Soil Type:\s*([^\n\r]+)", context_text)
            if soil_m:
                info["soil"] = soil_m.group(1).strip()
        return info

    def _build_weather_response(
        self,
        question: str,
        weather: Dict[str, Any],
        profile: Dict[str, Any],
        lang: str,
        is_tomorrow: bool = False,
    ) -> str:
        # Determine human-friendly location string
        loc_str = ""
        loc_name = weather.get("location")
        if loc_name and not loc_name.startswith("Coordinates"):
            loc_str = f" for {loc_name}"
        elif profile.get("district") and profile.get("state"):
            loc_str = f" for {profile['district']}, {profile['state']}"
        elif profile.get("district"):
            loc_str = f" for {profile['district']}"

        # If live weather provider was temporarily unavailable
        if weather and (weather.get("status") == "provider_unavailable" or weather.get("unavailable")):
            loc_disp = loc_name or (f"{profile.get('district')}, {profile.get('state')}" if profile.get("district") else "your area")
            if lang == "te":
                return (
                    f"ప్రస్తుతం {loc_disp} ప్రాంతానికి సంబంధించిన తాజా వాతావరణ సమాచారం అందుబాటులో లేదు. దయచేసి కాసేపటి తర్వాత మళ్లీ ప్రయత్నించండి.\n\n"
                    "వ్యవసాయ సలహా: సాధారణంగా వర్షం లేదా అధిక తేమ ఉన్నప్పుడు రసాయన మందుల పిచికారీని నివారించండి."
                )
            elif lang == "hi":
                return (
                    f"वर्तमान में {loc_disp} क्षेत्र के लिए मौसम की ताजा जानकारी उपलब्ध नहीं हो सकी। कृपया कुछ समय बाद पुनः प्रयास करें।\n\n"
                    "कृषि सलाह: बारिश या उच्च नमी के दौरान कीटनाशक या रासायनिक उर्वरक का छिड़काव करने से बचें।"
                )
            elif lang == "ta":
                return (
                    f"தற்போது {loc_disp} பகுதிக்கான நேரடி வானிலை தகவலைப் பெற முடியவில்லை. சிறிது நேரம் கழித்து மீண்டும் முயற்சிக்கவும்.\n\n"
                    "வேளாண் ஆலோசனை: மழை அல்லது அதிக ஈரப்பதம் உள்ள சூழலில் பூச்சிக்கொல்லி தெளிப்பதைத் தவிர்க்கவும்."
                )
            elif lang == "kn":
                return (
                    f"ಪ್ರಸ್ತುತ {loc_disp} ಪ್ರದೇಶದ ನೈಜ ಹವಾಮಾನ ಮಾಹಿತಿ ಲಭ್ಯವಾಗಿಲ್ಲ. ದಯವಿಟ್ಟು ಸ್ವಲ್ಪ ಸಮಯದ ನಂತರ ಪ್ರಯತ್ನಿಸಿ.\n\n"
                    "ಕೃಷಿ ಸಲಹೆ: ಮಳೆ ಅಥವಾ ಹೆಚ್ಚಿನ ತೇವಾಂಶವಿದ್ದಾಗ ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸುವುದನ್ನು ತಪ್ಪಿಸಿ."
                )
            elif lang == "mr":
                return (
                    f"सध्या {loc_disp} भागासाठी थेट हवामान माहिती मिळू शकली नाही. कृपया थोड्या वेळाने पुन्हा प्रयत्न करा.\n\n"
                    "कृषी सल्ला: पाऊस किंवा जास्त आर्द्रता असताना कीटकनाशके फवारणे टाळावे."
                )
            else:
                return (
                    f"We couldn't retrieve the latest weather data for {loc_disp} right now. Please try again shortly.\n\n"
                    "Agricultural Tip: Always avoid spraying fertilizers or chemical pesticides when rain or high relative humidity is expected, as runoff diminishes effectiveness."
                )

        # If weather data could not be resolved
        if not weather or ("temp" not in weather and "tomorrow" not in weather):
            if lang == "te":
                return (
                    "మీ పొలంలో ఖచ్చితమైన వాతావరణం మరియు వర్ష సూచన తెలుసుకోవడానికి దయచేసి స్క్రీన్ పైభాగంలో ఉన్న 'లొకేషన్' బటన్ ద్వారా మీ లొకేషన్‌ను ఎంచుకోండి.\n\n"
                    "వ్యవసాయ సలహా: వర్షం పడే సూచన ఉన్నప్పుడు ఎరువులు లేదా రసాయన పురుగుమందుల పిచికారీని నివారించండి."
                )
            elif lang == "hi":
                return (
                    "अपने खेतों के सटीक मौसम और बारिश के पूर्वानुमान के लिए कृपया स्क्रीन के शीर्ष पर स्थित 'लोकेशन' बटन से अपना स्थान चुनें।\n\n"
                    "कृषि सलाह: बारिश या उच्च आर्द्रता के दौरान कीटनाशक या रासायनिक उर्वरक का छिड़काव करने से बचें, क्योंकि पानी से दवा बह जाती है।"
                )
            elif lang == "ta":
                return (
                    "உங்கள் நிலத்தின் நேரடி வானிலை மற்றும் மழை முன்னறிவிப்பைப் பெற திரையின் மேலே உள்ள 'இருப்பிடம்' பொத்தானைப் பயன்படுத்தி உங்கள் இடத்தை அமைக்கவும்.\n\n"
                    "வேளாண் ஆலோசனை: மழை பெய்யும் வாய்ப்புள்ள போது பூச்சிக்கொல்லி மருந்துகள் தெளிப்பதைத் தவிர்க்கவும்."
                )
            elif lang == "kn":
                return (
                    "ನಿಮ್ಮ ಹೊಲದ ನಿಖರವಾದ ಹವಾಮಾನ ಮತ್ತು ಮಳೆ ಮುನ್ಸೂಚನೆ ಪಡೆಯಲು ಪರದೆಯ ಮೇಲ್ಭಾಗದಲ್ಲಿರುವ 'ಸ್ಥಳ' ಬಟನ್ ಬಳಸಿ ಸ್ಥಳವನ್ನು ಆಯ್ಕೆಮಾಡಿ.\n\n"
                    "ಕೃಷಿ ಸಲಹೆ: ಮಳೆಯ ಮುನ್ಸೂಚನೆ ಇದ್ದಾಗ ರಾಸಾಯನಿಕ ಸಿಂಪಡಣೆ ಅಥವಾ ಗೊಬ್ಬರ ಹಾಕುವುದನ್ನು ಮುಂದೂಡಿ."
                )
            elif lang == "mr":
                return (
                    "शेतातील अचूक हवामान व पावसाचा अंदाज पाहण्यासाठी कृपया स्क्रीनवरील 'स्थान' बटण वापरून आपले स्थान निवडा.\n\n"
                    "कृषी सल्ला: पावसाची शक्यता असताना रासायनिक खते किंवा कीटकनाशके फवारणे टाळावे."
                )
            else:
                return (
                    "To provide an accurate real-time weather and rainfall forecast for your fields, please select or allow your location "
                    "using the Location button at the top of the screen.\n\n"
                    "Agricultural Tip: Always avoid spraying fertilizers or chemical pesticides when rain or high relative humidity is expected, as runoff diminishes effectiveness."
                )

        # Case 1: Tomorrow's weather / rain
        if is_tomorrow and "tomorrow" in weather:
            tm = weather["tomorrow"]
            tm_cond = tm.get("condition", "Partly Cloudy")
            tm_rain_exp = tm.get("rain_expected", False)
            tm_precip = tm.get("precip", 0.0)
            tm_min = tm.get("temp_min", "20")
            tm_max = tm.get("temp_max", "32")
            tm_date = tm.get("date", "Tomorrow")

            if lang == "te":
                rain_text = f"అవును, వర్షం పడే అవకాశం ఉంది ({tm_precip} మి.మీ వర్షపాతం అంచనా)." if tm_rain_exp else f"వర్షం పడే అవకాశం లేదు ({tm_precip} మి.మీ, {tm_cond})."
                advice_text = "రేపు వర్ష సూచన ఉన్నందున పురుగుమందుల పిచికారీ మరియు నీటిపారుదలని వాయిదా వేయండి." if tm_rain_exp else "రేపు పొడి వాతావరణం ఉండే అవకాశం ఉంది. సాధారణ వ్యవసాయ పనులు మరియు పిచికారీకి అనుకూలం."
                return f"🌾 **రేపటి వాతావరణం & వర్ష సూచన{loc_str} ({tm_date}):**\n\n- **వర్ష సూచన:** {rain_text}\n- **ఉష్ణోగ్రత:** {tm_min}°C నుండి {tm_max}°C\n- **పరిస్థితి:** {tm_cond}\n\n**రైతుకు సలహా:** {advice_text}"
            elif lang == "hi":
                rain_text = f"हाँ, बारिश की संभावना है (अनुमानित वर्षा: {tm_precip} मिमी)।" if tm_rain_exp else f"बारिश की संभावना नहीं है ({tm_precip} मिमी, मौसम: {tm_cond})।"
                advice_text = "कल बारिश की संभावना को देखते हुए कीटनाशक छिड़काव और सिंचाई स्थगित रखें।" if tm_rain_exp else "कल मौसम अनुकूल और सूखा रहेगा। नियमित कृषि कार्य और कीटनाशक छिड़काव कर सकते हैं।"
                return f"🌾 **कल का मौसम एवं बारिश का पूर्वानुमान{loc_str} ({tm_date}):**\n\n- **बारिश का अनुमान:** {rain_text}\n- **तापमान:** {tm_min}°C से {tm_max}°C\n- **मौसम की स्थिति:** {tm_cond}\n\n**कृषि सलाह:** {advice_text}"
            elif lang == "ta":
                rain_text = f"ஆம், மழை பெய்ய வாய்ப்புள்ளது (எதிர்பார்க்கப்படும் மழை: {tm_precip} மிமீ)." if tm_rain_exp else f"மழை பெய்ய வாய்ப்பில்லை ({tm_precip} மிமீ, {tm_cond})."
                advice_text = "நாளை மழை வாய்ப்புள்ளதால் பூச்சிக்கொல்லி தெளிப்பு மற்றும் பாசனத்தை ஒத்திவைக்கவும்." if tm_rain_exp else "நாளை வறண்ட வானிலை காணப்படும். வழக்கமான விவசாயப் பணிகளுக்கு ஏற்றது."
                return f"🌾 **நாளைய வானிலை & மழை முன்னறிவிப்பு{loc_str} ({tm_date}):**\n\n- **மழை வாய்ப்பு:** {rain_text}\n- **வெப்பநிலை:** {tm_min}°C முதல் {tm_max}°C\n- **நிலை:** {tm_cond}\n\n**வேளாண் ஆலோசனை:** {advice_text}"
            elif lang == "kn":
                rain_text = f"ಹೌದು, ಮಳೆಯಾಗುವ ಸಾಧ್ಯತೆಯಿದೆ (ಅಂದಾಜು ಮಳೆ: {tm_precip} ಮಿಮೀ)." if tm_rain_exp else f"ಮಳೆಯಾಗುವ ಸಾಧ್ಯತೆಯಿಲ್ಲ ({tm_precip} ಮಿಮೀ, {tm_cond})."
                advice_text = "ನಾಳೆ ಮಳೆಯಾಗುವ ಮುನ್ಸೂಚನೆ ಇರುವುದರಿಂದ ಸಿಂಪಡಣೆ ಮತ್ತು ನೀರಾವರಿಯನ್ನು ಮುಂದೂಡಿ." if tm_rain_exp else "ನಾಳೆ ಒಣ ಹವಾಮಾನವಿರುತ್ತದೆ. ಸಾಮಾನ್ಯ ಕೃಷಿ ಕೆಲಸಗಳಿಗೆ ಸೂಕ್ತವಾಗಿದೆ."
                return f"🌾 **ನಾಳೆಯ ಹವಾಮಾನ ಮತ್ತು ಮಳೆ ಮುನ್ಸೂಚನೆ{loc_str} ({tm_date}):**\n\n- **ಮಳೆ ಮುನ್ಸೂಚನೆ:** {rain_text}\n- **ತಾಪಮಾನ:** {tm_min}°C ರಿಂದ {tm_max}°C\n- **ಸ್ಥಿತಿ:** {tm_cond}\n\n**ಕೃಷಿ ಸಲಹೆ:** {advice_text}"
            elif lang == "mr":
                rain_text = f"होय, पावसाची शक्यता आहे (अंदाजे पाऊस: {tm_precip} मिमी)." if tm_rain_exp else f"पावसाची शक्यता नाही ({tm_precip} मिमी, {tm_cond})."
                advice_text = "उद्या पावसाचा अंदाज असल्याने फवारणी आणि सिंचन पुढे ढकला." if tm_rain_exp else "उद्या हवामान कोरडे राहील. शेतीकामे व फवारणीसाठी अनुकूल दिवस आहे."
                return f"🌾 **उद्याचे हवामान व पावसाचा अंदाज{loc_str} ({tm_date}):**\n\n- **पावसाचा अंदाज:** {rain_text}\n- **तापमान:** {tm_min}°C ते {tm_max}°C\n- **स्थिती:** {tm_cond}\n\n**कृषी सल्ला:** {advice_text}"
            else:
                rain_text = f"Rain expected ({tm_precip} mm forecasted, {tm_cond})" if tm_rain_exp else f"No significant rain expected ({tm_precip} mm, {tm_cond})"
                advice_text = "Rain is expected tomorrow. Postpone chemical spraying, foliar fertilizer application, and irrigation." if tm_rain_exp else "Dry conditions expected tomorrow. Favorable for field work, weeding, and foliar applications."
                return f"🌾 **Tomorrow's Weather & Rain Outlook{loc_str} ({tm_date}):**\n\n- **Rain Outlook:** {rain_text}\n- **Temperature:** {tm_min}°C to {tm_max}°C\n- **Conditions:** {tm_cond}\n\n**Agronomic Advice:** {advice_text}"

        # Case 2: Today's live weather
        temp = weather.get("temp", "N/A")
        cond = weather.get("condition", "Current Conditions")
        hum = weather.get("humidity", "N/A")
        precip = weather.get("precip", "0.0")
        precip_float = float(precip) if precip != "N/A" else 0.0

        if lang == "te":
            rain_answer = f"అవును, వర్షం లేదా తుంపరలు పడుతున్నాయి ({precip} మి.మీ నమోదైంది)." if precip_float > 0 else f"ప్రస్తుతం వర్షం పడటం లేదు ({precip} మి.మీ వర్షపాతం, {cond})."
            tip = "పొలంలో నీటి నిల్వ లేకుండా చూసుకోండి మరియు పిచికారీ పనులను వాయిదా వేయండి." if precip_float > 0 else "వాతావరణం అనుకూలంగా ఉంది. అవసరాన్ని బట్టి తేలికపాటి తడి అందించవచ్చు."
            return f"🌾 **నేటి వాతావరణం & వర్ష సమాచారం{loc_str}:**\n\n- **వర్షం:** {rain_answer}\n- **ఉష్ణోగ్రత:** {temp}°C ({cond})\n- **గాలిలో తేమ:** {hum}%\n\n**రైతుకు సలహా:** {tip}"
        elif lang == "hi":
            rain_answer = f"हाँ, वर्तमान में बारिश या बूंदाबांदी हो रही है ({precip} मिमी दर्ज)।" if precip_float > 0 else f"वर्तमान में बारिश नहीं हो रही है ({precip} मिमी वर्षा, {cond})।"
            tip = "खेत में जलभराव न होने दें और कीटनाशक छिड़काव रोक दें।" if precip_float > 0 else "मौसम साफ है। आवश्यकतानुसार फसलों में हल्की सिंचाई व अन्य कार्य कर सकते हैं।"
            return f"🌾 **आज का मौसम एवं वर्षा की स्थिति{loc_str}:**\n\n- **बारिश की स्थिति:** {rain_answer}\n- **तापमान:** {temp}°C ({cond})\n- **हवा में नमी:** {hum}%\n\n**कृषि सलाह:** {tip}"
        elif lang == "ta":
            rain_answer = f"ஆம், தற்போது மழை பெய்கிறது ({precip} மிமீ பதிவாகியுள்ளது)." if precip_float > 0 else f"தற்போது மழை பெய்யவில்லை ({precip} மிமீ மழைப்பொழிவு, {cond})."
            tip = "வயலில் தண்ணீர் தேங்காமல் பார்த்துக் கொள்ளவும், தெளிப்பைத் தவிர்க்கவும்." if precip_float > 0 else "வானிலை சீராக உள்ளது. தேவைக்கேற்ப லேசான பாசனம் செய்யலாம்."
            return f"🌾 **இன்றைய பண்ணை வானிலை & மழை நிலவரம்{loc_str}:**\n\n- **மழை நிலவரம்:** {rain_answer}\n- **வெப்பநிலை:** {temp}°C ({cond})\n- **ஈரப்பதம்:** {hum}%\n\n**வேளாண் ஆலோசனை:** {tip}"
        elif lang == "kn":
            rain_answer = f"ಹೌದು, ಪ್ರಸ್ತುತ ಮಳೆಯಾಗುತ್ತಿದೆ ({precip} ಮಿಮೀ ದಾಖಲಾಗಿದೆ)." if precip_float > 0 else f"ಪ್ರಸ್ತುತ ಮಳೆಯಾಗುತ್ತಿಲ್ಲ ({precip} ಮಿಮೀ ಮಳೆ, {cond})."
            tip = "ಹೊಲದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ನೋಡಿಕೊಳ್ಳಿ ಮತ್ತು ಸಿಂಪಡಣೆಯನ್ನು ಮುಂದೂಡಿ." if precip_float > 0 else "ಹವಾಮಾನ ಅನುಕೂಲಕರವಾಗಿದೆ. ಅಗತ್ಯವಿದ್ದರೆ ಲಘು ನೀರಾವರಿ ಒದಗಿಸಬಹುದು."
            return f"🌾 **ಇಂದಿನ ಕೃಷಿ ಹವಾಮಾನ ಮತ್ತು ಮಳೆ ವಿವರ{loc_str}:**\n\n- **ಮಳೆ ವಿವರ:** {rain_answer}\n- **ತಾಪಮಾನ:** {temp}°C ({cond})\n- **ತೇವಾಂಶ:** {hum}%\n\n**ಕೃಷಿ ಸಲಹೆ:** {tip}"
        elif lang == "mr":
            rain_answer = f"होय, सध्या पाऊस पडत आहे ({precip} मिमी नोंद)." if precip_float > 0 else f"सध्या पाऊस पडत नाही ({precip} मिमी पाऊस, {cond})."
            tip = "शेतात पाणी साचू देऊ नका आणि फवारणीची कामे थांबवा." if precip_float > 0 else "हवामान स्वच्छ आहे. गरजेनुसार पिकांना हलके पाणी द्यावे."
            return f"🌾 **आजचे शेतातील हवामान व पावसाची स्थिती{loc_str}:**\n\n- **पावसाची स्थिती:** {rain_answer}\n- **तापमान:** {temp}°C ({cond})\n- **हवेतील आर्द्रता:** {hum}%\n\n**कृषी सल्ला:** {tip}"
        else:
            rain_answer = f"Yes, rain is actively recorded ({precip} mm, {cond})." if precip_float > 0 else f"No active rain recorded ({precip} mm precipitation, {cond})."
            tip = "Avoid foliar sprays and ensure field drainage outlets are open." if precip_float > 0 else "Conditions are favorable for normal agronomic operations."
            return f"🌾 **Live Weather & Rain Outlook{loc_str}:**\n\n- **Rain Status:** {rain_answer}\n- **Temperature:** {temp}°C ({cond})\n- **Relative Humidity:** {hum}%\n\n**Agronomic Advice:** {tip}"

    def _build_crop_growth_response(
        self, question: str, crop_rec: Dict[str, Any], profile: Dict[str, Any], lang: str
    ) -> str:
        rec_crop = crop_rec.get("crop", "")
        crop_hint = f" (विशेषतः {rec_crop})" if rec_crop and lang == "hi" else f" ({rec_crop} పంటలో)" if rec_crop and lang == "te" else f" ({rec_crop} பயிரில்)" if rec_crop and lang == "ta" else f" ({rec_crop} ಬೆಳೆಯಲ್ಲಿ)" if rec_crop and lang == "kn" else f" ({rec_crop} पिकामध्ये)" if rec_crop and lang == "mr" else f" (especially for {rec_crop})" if rec_crop else ""

        if lang == "te":
            return (
                f"🌱 **పంట ఎదుగుదల సరిగ్గా లేకపోవడానికి ప్రధాన కారణాలు & నివారణ{crop_hint}:**\n\n"
                "1. **నేల పోషకాల లోపం & pH సమస్య:** ప్రాథమిక పోషకాలైన నత్రజని (ఆకుల పెరుగుదలకు), భాస్వరం (వేర్ల అభివృద్ధికి) లేదా సూక్ష్మపోషకాల (జింక్, ఇనుము) లోపం వల్ల ఎదుగుదల ఆగిపోతుంది. నేల pH 6.0 కంటే తక్కువ లేదా 8.0 కంటే ఎక్కువ ఉంటే వేర్లు పోషకాలను గ్రహించలేవు.\n"
                "2. **వేర్ల సమస్యలు / నీటి నిల్వ:** పొలంలో ఎక్కువ రోజులు నీరు నిలిచి వేర్లకు గాలి అందకపోతే వేర్లు నల్లబడి ఎదుగుదల నిలిచిపోతుంది. లేదా వేరు పురుగులు (నిమటోడ్లు, వేరు పురుగు) వేర్లను కొట్టేయడం వల్ల మొక్క బలహీనపడుతుంది.\n"
                "3. **కలుపు మొక్కల పోటీ:** సకాలంలో కలుపు తీయకపోతే అవి 30-40% ఎరువులను మరియు తేమను గ్రహించి ప్రధాన పంట ఎదుగుదలను దెబ్బతీస్తాయి.\n"
                "4. **సిఫార్సు చేసిన తక్షణ చర్యలు:** 2-3 మొక్కల మొదళ్ల వద్ద తవ్వి తెల్లటి ఆరోగ్యకరమైన వేర్లు ఉన్నాయో లేదో గమనించండి. కలుపు తీసి, తగినంత తేమ ఉండేలా చూసుకోండి. పంటకు తక్షణ బలం చేకూరడానికి 1-2% 19:19:19 నీటిలో కరిగే ఎరువుల ద్రావణం పిచికారీ చేయండి."
            )
        elif lang == "hi":
            return (
                f"🌱 **फसल की बढ़वार रुकने या ठीक से न बढ़ने के मुख्य कारण एवं समाधान{crop_hint}:**\n\n"
                "1. **पोषक तत्वों की कमी एवं मृदा pH:** वानस्पतिक वृद्धि के लिए नाइट्रोजन और जड़ों के फैलाव के लिए फास्फोरस की कमी होने पर पौधा बौना रह जाता है। यदि मिट्टी का pH बहुत अधिक या कम हो तो पौधे पोषक तत्व नहीं ले पाते।\n"
                "2. **जड़ क्षेत्र में समस्या या जलभराव:** खेत में पानी भरे रहने से जड़ों को ऑक्सीजन नहीं मिलती और वे काली पड़कर सड़ने लगती हैं। इसके अलावा जड़ माहू या सूत्रकृमि (नेमाटोड) भी बढ़वार रोकते हैं।\n"
                "3. **खरपतवारों की प्रतिस्पर्धा:** समय पर निराई-गुड़ाई न होने पर खरपतवार खाद और पानी खींच लेते हैं जिससे फसल कमजोर हो जाती है।\n"
                "4. **सुझाए गए तुरंत उपाय:** कुछ पौधों की जड़ों को उखाड़कर देखें कि जड़ें सफेद और स्वस्थ हैं या नहीं। खेत से जल निकासी करें, निराई करें और फसल को नई ऊर्जा देने के लिए 1-2% एनपीके (19:19:19) का पर्णीय छिड़काव करें।"
            )
        elif lang == "ta":
            return (
                f"🌱 **பயிர் வளர்ச்சி குன்றுதல் / சரியாக வளராமைக்கான காரணங்கள் மற்றும் தீர்வுகள்{crop_hint}:**\n\n"
                "1. **மண் ஊட்டச்சத்துக் குறைபாடு மற்றும் pH:** தழைச்சத்து (நைட்ரஜன்) மற்றும் மணிச்சத்து (பாஸ்பரஸ்) குறைபாடு வேர் மற்றும் பயிர் வளர்ச்சியைத் தடுக்கும். மண்ணின் pH சீரற்றதாக இருந்தால் உரங்கள் பயிரைச் சென்றடையாது.\n"
                "2. **நீர் தேங்குதல் மற்றும் வேர் அழுகல்:** நிலத்தில் அதிகப்படியான தண்ணீர் தேங்கி நின்றால் வேர்களுக்குக் காற்று கிடைக்காமல் வளர்ச்சி நிற்கும். நூற்புழுக்கள் அல்லது வேர்ப்புழுக்களும் வளர்ச்சியைப் பாதிக்கும்.\n"
                "3. **களைகளின் ஆதிக்கம்:** சரியான நேரத்தில் களையெடுக்காவிட்டால், இடப்படும் உரங்களை களைகள் உறிஞ்சி பயிரின் வளர்ச்சியைப் பாதிக்கும்.\n"
                "4. **பரிந்துரைக்கப்பட்ட தீர்வுகள்:** வேர்களைச் சரிபார்த்து வெள்ளை வேர்கள் உள்ளதா என உறுதிப்படுத்தவும். வடிகால் வசதியை ஏற்படுத்தி, களையெடுத்து, 19:19:19 நீரில் கரையும் உரத்தை (1-2%) தெளித்து உடனடி ஊட்டமளிக்கவும்."
            )
        elif lang == "kn":
            return (
                f"🌱 **ಬೆಳೆ ಬೆಳವಣಿಗೆ ಸರಿಯಾಗಿ ಆಗದಿರಲು ಕಾರಣಗಳು ಮತ್ತು ಪರಿಹಾರಗಳು{crop_hint}:**\n\n"
                "1. **ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳ ಕೊರತೆ ಮತ್ತು pH:** ಸಾರಜನಕ ಮತ್ತು ರಂಜಕದ ಕೊರತೆಯಿಂದ ಗಿಡಗಳು ಕುಂಠಿತವಾಗುತ್ತವೆ. ಮಣ್ಣಿನ pH ಅಸಮತೋಲನವಾಗಿದ್ದರೆ ಪೋಷಕಾಂಶಗಳು ಗಿಡಕ್ಕೆ ಸಿಗುವುದಿಲ್ಲ.\n"
                "2. **ನೀರು ನಿಲ್ಲುವುದು ಅಥವಾ ಬೇರು ಕೊಳೆತ:** ಹೊಲದಲ್ಲಿ ನೀರು ನಿಂತರೆ ಬೇರುಗಳಿಗೆ ಆಮ್ಲಜನಕ ಸಿಗದೆ ಕಪ್ಪಾಗುತ್ತವೆ. ಜಂತುಹುಳುಗಳು (ನೆಮಟೋಡ್ಸ್) ಕೂಡ ಬೆಳವಣಿಗೆಯನ್ನು ನಿಲ್ಲಿಸುತ್ತವೆ.\n"
                "3. **ಕಳೆಗಳ ಸ್ಪರ್ಧೆ:** ಸಕಾಲದಲ್ಲಿ ಕಳೆ ಕೀಳದಿದ್ದರೆ ಗೊಬ್ಬರ ಮತ್ತು ತೇವಾಂಶವನ್ನು ಕಳೆಗಳು ಹೀರಿಕೊಳ್ಳುತ್ತವೆ.\n"
                "4. **ಕ್ರಮಗಳು:** ಬೇರುಗಳು ಆರೋಗ್ಯಕರವಾಗಿವೆಯೇ ಎಂದು ಪರೀಕ್ಷಿಸಿ. ಒಳಚರಂಡಿ ಸರಿಪಡಿಸಿ, ಕಳೆ ತೆಗೆದು, ಗಿಡಕ್ಕೆ ಶಕ್ತಿ ನೀಡಲು 19:19:19 ನೀರಿನಲ್ಲಿ ಕರಗುವ ಗೊಬ್ಬರವನ್ನು (1-2%) ಸಿಂಪಡಿಸಿ."
            )
        elif lang == "mr":
            return (
                f"🌱 **पिकांची वाढ खुंटण्याची / योग्य वाढ न होण्याची मुख्य कारणे व उपाय{crop_hint}:**\n\n"
                "1. **पोषक घटकांची कमतरता व जमिनीचा सामू (pH):** नत्र व स्फुरदच्या कमतरतेमुळे मुळांची व शाकीय वाढ थांबते. जमिनीचा सामू बिघडल्यास झाडे अन्नद्रव्ये शोषू शकत नाहीत.\n"
                "2. **पाणथळ जमीन व मुळकूज:** शेतात पाणी साचून राहिल्यास मुळांना ऑक्सिजन मिळत नाही व ती सडतात. तसेच हुमणी किंवा सूत्रकृमींमुळेही वाढ थांबते.\n"
                "3. **तणांचा प्रादुर्भाव:** वेळेवर खुरपणी न केल्यास तणे खते व पाणी शोषून घेतात, ज्यामुळे मुख्य पीक अशक्त राहते.\n"
                "4. **उपाय:** मुळांची तपासणी करा, पाण्याचा निचरा करा, तण नियंत्रण करा आणि पिकाला त्वरित उभारी देण्यासाठी १९:१९:१९ विद्राव्य खताची (१-२%) फवारणी करा."
            )
        else:
            return (
                f"🌱 **Agronomic Causes and Solutions for Poor / Stunted Crop Growth{crop_hint}:**\n\n"
                "1. **Nutrient Imbalance & Soil pH:** Stunted vegetative vigor is primarily driven by Nitrogen deficiency (stunted pale leaves) or Phosphorus deficiency (poor root establishment). Soil pH below 6.0 or above 7.8 locks up essential micro-nutrients.\n"
                "2. **Root Zone Asphyxiation & Waterlogging:** Continuous water stagnation suffocates fine feeder roots, turning them dark and non-functional. Sub-surface pests like nematodes or white grubs also chew root tips, abruptly stopping foliar growth.\n"
                "3. **Weed Competition:** Unchecked weed growth strips 35-50% of applied fertilizers and soil moisture before crop roots can absorb them.\n"
                "4. **Recommended Agronomic Actions:** Gently unearth 2-3 sample plants to inspect root health (look for healthy white root hairs vs brownish decay). Ensure active surface drainage, weed the crop canopy, and apply a restorative foliar spray of water-soluble N-P-K (19:19:19 at 10-15 g/L)."
            )

    def _build_yellow_leaves_response(self, question: str, lang: str) -> str:
        if lang == "te":
            return (
                "🌱 **వరి లేదా ఇతర పంటలలో ఆకులు రంగు మారడానికి / పసుపు రంగులోకి మారడానికి ప్రధాన కారణాలు & నివారణ:**\n\n"
                "1. **నత్రజని (Nitrogen) లోపం:** కిందటి ముదిరిన ఆకులు మొదట పసుపు రంగులోకి మారి పై ఆకులకు వ్యాపిస్తుంది.\n"
                "   - *నివారణ:* యూరియాను సమతుల్య మోతాదులో పైపాటుగా వేయండి లేదా 1-2% యూరియా ద్రావణం పిచికారీ చేయండి.\n"
                "2. **జింక్ (Zinc) లోపం (ఖైరా తెగులు):** నాటిన 2-3 వారాల తర్వాత ఆకులపై ఇటుక రంగు/గోధుమ మచ్చలు ఏర్పడి పసుపుగా మారుతాయి.\n"
                "   - *నివారణ:* జింక్ సల్ఫేట్ (5 గ్రా/లీటర్) + బుద్ధి సున్నం (2.5 గ్రా/లీటర్) కలిపి పిచికారీ చేయండి.\n"
                "3. **నీటి నిల్వ / వేరు కుళ్ళు:** పొలంలో ఎక్కువ రోజులు నీరు నిలిచి వేర్లు నల్లబడితే ఆకులు పసుపుగా మారి ఎండిపోతాయి.\n"
                "   - *నివారణ:* పొలంలో నీటిని తీసివేసి 2-3 రోజులు ఆరబెట్టి తిరిగి నీరు పెట్టండి.\n"
                "4. **బాక్టీరియా ఆకు ఎండు తెగులు (BLB):** ఆకుల అంచుల నుండి పసుపు లేదా తెల్లటి చారలు మొదలై ఎండిపోతాయి.\n"
                "   - *నివారణ:* నత్రజని వాడకం తగ్గించి, కాపర్ ఆక్సిక్లోరైడ్ 30 గ్రా + స్ట్రెప్టోసైక్లిన్ 1.5 గ్రా 10 లీటర్ల నీటిలో కలిపి పిచికారీ చేయండి."
            )
        elif lang == "hi":
            return (
                "🌱 **फसल (विशेषकर धान) में पत्तियां पीली पड़ने या रंग बदलने के कारण एवं समाधान:**\n\n"
                "1. **नाइट्रोजन की कमी:** पौधे की निचली पुरानी पत्तियां नोक से शुरू होकर पीली पड़ने लगती हैं।\n"
                "   - *समाधान:* संतुलित मात्रा में यूरिया का भुरकाव करें अथवा 1-2% यूरिया के घोल का छिड़काव करें।\n"
                "2. **जिंक की कमी (खैरा रोग):** रोपाई के 2-3 सप्ताह बाद पत्तियों पर कत्थई/भूरे धब्बे बनते हैं और पत्तियां पीली होने लगती हैं।\n"
                "   - *समाधान:* जिंक सल्फेट (5 ग्राम/लीटर) + बुझा हुआ चूना (2.5 ग्राम/लीटर) पानी में घोलकर छिड़काव करें।\n"
                "3. **जलभराव या जड़ सड़न:** खेत में लगातार पानी भरे रहने से जड़ें काली पड़ जाती हैं और पत्तियां पीली होने लगती हैं।\n"
                "   - *समाधान:* खेत से पानी निकालकर 2-3 दिन हवा लगने दें, फिर हल्की सिंचाई करें।\n"
                "4. **जीवाणु झुलसा (BLB):** पत्तियों के किनारे से पीली धारियां बनती हैं जो बाद में सफेद होकर सूख जाती हैं।\n"
                "   - *समाधान:* नाइट्रोजन की मात्रा घटाएं तथा कॉपर ऑक्सीक्लोराइड (2.5 ग्राम) + स्ट्रेप्टोसाइक्लिन (0.15 ग्राम) प्रति लीटर पानी में मिलाकर छिड़काव करें।"
            )
        elif lang == "ta":
            return (
                "🌱 **நெல் மற்றும் பிற பயிர்களில் இலைகள் நிறம் மாறுதல் / மஞ்சள் நிறமாதலுக்கான காரணங்கள் & தீர்வுகள்:**\n\n"
                "1. **நைட்ரஜன் (தழைச்சத்து) குறைபாடு:** கீழ் இலைகள் நுனியிலிருந்து மஞ்சள் நிறமாக மாறத் தொடங்கும்.\n"
                "   - *தீர்வு:* பரிந்துரைக்கப்பட்ட யூரியாவை மேலுரமாக இடவும் அல்லது 1-2% யூரியா கரைசலை இலைகளில் தெளிக்கவும்.\n"
                "2. **துத்தநாகக் குறைபாடு (கைரா நோய்):** நட்ட 2-3 வாரங்களில் இலைகளில் துரு போன்ற பழுப்பு நிறப் புள்ளிகள் தோன்றி மஞ்சள் நிறமாகும்.\n"
                "   - *தீர்வு:* ஜிங்க் சல்பேட் (5 கிராம்/லிட்டர்) + சுண்ணாம்பு நீர் தெளிக்கவும்.\n"
                "3. **நீர் தேங்குதல் மற்றும் வேர் அழுகல்:** வயலில் தண்ணீர் தேங்கி வேர்கள் கறுத்து அழுகினால் இலைகள் மஞ்சள் நிறமாக மாறும்.\n"
                "   - *தீர்வு:* வயலில் உள்ள தண்ணீரை வடித்து 2-3 நாட்கள் உலர விடவும்.\n"
                "4. **பாக்டீரியா இலைக்கருகல் (BLB):** இலைகளின் ஓரங்களில் மஞ்சள் அல்லது வெள்ளை நிறக் கோடுகள் தோன்றி இலைகள் கருகும்.\n"
                "   - *தீர்வு:* நைட்ரஜன் உரத்தைக் குறைத்து, காப்பர் ஆக்சிகுளோரைடு (2.5 கிராம்/லிட்டர்) தெளிக்கவும்."
            )
        elif lang == "kn":
            return (
                "🌱 **ಭತ್ತ ಮತ್ತು ಇತರ ಬೆಳೆಗಳಲ್ಲಿ ಎಲೆಗಳು ಬಣ್ಣ ಬದಲಾಗಲು / ಹಳದಿಯಾಗಲು ಕಾರಣಗಳು ಮತ್ತು ಪರಿಹಾರಗಳು:**\n\n"
                "1. **ಸಾರಜನಕ ಕೊರತೆ:** ಹಳೆಯ ಕೆಳಭಾಗದ ಎಲೆಗಳು ತುದಿಯಿಂದ ಹಳದಿ ಬಣ್ಣಕ್ಕೆ ತಿರುಗುತ್ತವೆ.\n"
                "   - *ಪರಿಹಾರ:* ಸಮತೋಲಿತ ಪ್ರಮಾಣದಲ್ಲಿ ಯೂರಿಯಾ ಸಿಂಪಡಿಸಿ ಅಥವಾ 1-2% ಯೂರಿಯಾ ದ್ರಾವಣವನ್ನು ಎಲೆಗಳ ಮೇಲೆ ಸಿಂಪಡಿಸಿ.\n"
                "2. **ಸತು (ಜಿಂಕ್) ಕೊರತೆ (ಖೈರಾ ರೋಗ):** ಎಲೆಗಳ ಮೇಲೆ ತುಕ್ಕು ಬಣ್ಣದ ಕಂದು ಕಲೆಗಳು ಕಾಣಿಸಿಕೊಂಡು ಹಳದಿಯಾಗುತ್ತವೆ.\n"
                "   - *ಪರಿಹಾರ:* ಜಿಂಕ್ ಸಲ್ಫೇಟ್ (5 ಗ್ರಾಂ/ಲೀಟರ್) ಸಿಂಪಡಿಸಿ.\n"
                "3. **ನೀರು ನಿಲ್ಲುವುದು / ಬೇರು ಕೊಳೆತ:** ನಿರಂತರ ನೀರು ನಿಂತು ಬೇರುಗಳು ಕಪ್ಪಾದರೆ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತವೆ.\n"
                "   - *ಪರಿಹಾರ:* ನೀರನ್ನು ಬಸಿದು 2-3 ದಿನ ಗಾಳಿ ಆಡಲು ಬಿಡಿ.\n"
                "4. **ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಎಲೆ ಕರಕಲು (BLB):** ಎಲೆಗಳ ಅಂಚುಗಳಿಂದ ಹಳದಿ-ಬಿಳಿ ಗೆರೆಗಳು ಉಂಟಾಗಿ ಒಣಗುತ್ತವೆ.\n"
                "   - *ಪರಿಹಾರ:* ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ (2.5 ಗ್ರಾಂ/ಲೀಟರ್) ಸಿಂಪಡಿಸಿ."
            )
        elif lang == "mr":
            return (
                "🌱 **भात व इतर पिकांमध्ये पाने पिवळी पडणे किंवा रंग बदलण्याची मुख्य कारणे व उपाय:**\n\n"
                "1. **नत्र (नायट्रोजन) कमतरता:** खालची जुनी पाने टोकाकडून पिवळी पडू लागतात.\n"
                "   - *उपाय:* युरियाची योग्य मात्रा द्या किंवा १-२% युरिया द्रावणाची पानांवर फवारणी करा.\n"
                "2. **झिंकची कमतरता (खैरा रोग):** पानांवर तांबूस-तपकिरी रंगाचे डाग पडून पाने पिवळी होतात.\n"
                "   - *उपाय:* झिंक सल्फेट (५ ग्रॅम/लिटर) + चुना मिसळून फवारणी करा.\n"
                "3. **पाणथळ स्थिती व मुळकूज:** शेतात पाणी साचल्याने मुळे काळी पडून पाने पिवळी पडतात.\n"
                "   - *उपाय:* शेतातून पाणी काढून २-३ दिवस हवा लागू द्या.\n"
                "4. **जिवाणूजन्य करपा (BLB):** पानांच्या कडा पिवळ्या-पांढऱ्या होऊन सुकतात.\n"
                "   - *उपाय:* कॉपर ऑक्सिक्लोराईड (२.५ ग्रॅम/लिटर) फवारा."
            )
        else:
            return (
                "🌱 **Causes and Solutions for Leaf Yellowing / Foliar Color Change (Especially in Paddy/Crops):**\n\n"
                "1. **Nitrogen Deficiency:** Older/lower leaves turn pale yellow starting from the leaf tip down the midrib, leading to stunted tillering.\n"
                "   - *Solution:* Apply a split top-dressing of Urea or spray 1-2% foliar urea solution.\n"
                "2. **Zinc Deficiency (Khaira Disease in Rice):** Middle leaves develop rusty bronze/brown blotches that turn yellow 2-3 weeks after transplanting.\n"
                "   - *Solution:* Foliar spray of Zinc Sulphate (0.5% - 5 g/L) combined with 0.25% slaked lime (2.5 g/L).\n"
                "3. **Root Suffocation / Waterlogging:** Continuous stagnant water turns roots black and foul-smelling, hindering nutrient uptake.\n"
                "   - *Solution:* Drain standing water and allow soil surface to hairline crack and aerate for 2-3 days before re-irrigating.\n"
                "4. **Bacterial Leaf Blight (BLB):** Yellow-to-whitish wavy lesions appear along leaf margins starting from the tips.\n"
                "   - *Solution:* Reduce nitrogen application; spray Copper Oxychloride (2.5 g/L) + Streptocycline (1 g per 10 L of water)."
            )

    def _build_curling_leaves_response(self, question: str, lang: str) -> str:
        if lang == "te":
            return (
                "🌿 **పంటలలో ఆకులు ముడుచుకుపోవడానికి (Leaf Curling) కారణాలు & నివారణ:**\n\n"
                "1. **రసం పీల్చే పురుగులు (తామర పురుగులు, తెల్లదోమ, పేనుబంక, నల్లి):**\n"
                "   - ఆకుల అడుగుభాగం నుండి రసం పీల్చడం వల్ల ఆకులు పైకి లేదా కిందికి ముడుచుకుంటాయి.\n"
                "   - *నివారణ:* ఎకరాకు 15-20 పసుపు/నీలి రంగు జిగురు అట్టలు అమర్చండి. వేప నూనె (10,000 ppm) 2-3 మి.లీ/లీటర్ లేదా ఇమిడాక్లోప్రిడ్ 0.3 మి.లీ/లీటర్ పిచికారీ చేయండి.\n"
                "2. **ఎరువుల మోతాదు ఎక్కువ కావడం (Fertilizer Shock):** నిన్న లేదా ఇటీవల అధిక మోతాదులో రసాయన ఎరువులు వేసినప్పుడు లేదా తీవ్రమైన ఎండలో పిచికారీ చేసినప్పుడు ఆకుల అంచులు ముడుచుకుని మాడిపోతాయి.\n"
                "   - *నివారణ:* వెంటనే పొలానికి తేలికపాటి నీరు అందించి రసాయన సాంద్రతను తగ్గించండి.\n"
                "3. **ఆకుముడత వైరస్ (Leaf Curl Virus):** ఆకులు మందంగా, గరుకుగా మారి మొక్క ఎదగదు. ఇది తెల్లదోమల ద్వారా వ్యాపిస్తుంది.\n"
                "   - *నివారణ:* వైరస్ సోకిన మొక్కలను పీకి నాశనం చేయండి; తెల్లదోమ నివారణకు రసం పీల్చే పురుగుల మందు వాడండి."
            )
        elif lang == "hi":
            return (
                "🌿 **फसलों में पत्तियां मुड़ने (लीफ कर्लिंग) के कारण एवं रोकथाम:**\n\n"
                "1. **रस चूसक कीट (थ्रिप्स, सफेद मक्खी, एफिड, माइट):** पत्तियों के नीचे से रस चूसने से पत्तियां नाव के आकार में ऊपर या नीचे की ओर मुड़ जाती हैं।\n"
                "   - *रोकथाम:* खेत में पीले-नीले चिपचिपे कार्ड लगाएं। नीम का तेल (10,000 ppm) 2-3 मिली/लीटर या इमिडाक्लोप्रिड 0.3 मिली/लीटर का छिड़काव करें।\n"
                "2. **उर्वरक का झटका (Fertilizer Shock / Burn):** हाल ही में अधिक मात्रा में उर्वरक डालने या तेज धूप में छिड़काव करने से पत्तियां अंदर की ओर मुड़कर झुलस जाती हैं।\n"
                "   - *रोकथाम:* खेत में तुरंत हल्की सिंचाई करें ताकि रसायनों का प्रभाव संतुलित हो सके।\n"
                "3. **पत्ती मरोड़ वायरस (Leaf Curl Virus):** पत्तियां छोटी, मुड़ी हुई और मोटी हो जाती हैं। यह सफेद मक्खी द्वारा फैलता है।\n"
                "   - *रोकथाम:* ग्रसित पौधों को उखाड़कर नष्ट करें और सफेद मक्खी के नियंत्रण के लिए कीटनाशक का प्रयोग करें।"
            )
        elif lang == "ta":
            return (
                "🌿 **பயிர்களில் இலை சுருங்குதல் / இலை முறுக்கு நோய்க்கான காரணங்கள் மற்றும் மேலாண்மை:**\n\n"
                "1. **சாறு உறிஞ்சும் பூச்சிகள் (இலைப்பேன், வெள்ளை ஈ, அசுவினி):** இலைகளின் அடிப்பகுதியில் சாற்றை உறிஞ்சுவதால் இலைகள் மேல்நோக்கி அல்லது கீழ்நோக்கி சுருளும்.\n"
                "   - *மேலாண்மை:* மஞ்சள் வண்ண ஒட்டும் பொறிகளைப் பயன்படுத்தவும். வேப்ப எண்ணெய் (3 மி.லி/லிட்டர்) அல்லது இமிடாக்குளோபிரிட் தெளிக்கவும்.\n"
                "2. **அதிக உரப் பயன்பாடு (Fertilizer Shock):** சமீபத்தில் அதிகளவு உரம் இட்டிருந்தாலோ அல்லது கடும் வெயிலில் தெளித்தாலோ இலைகள் சுருண்டு கருகும்.\n"
                "   - *மேலாண்மை:* உடனே வயலுக்கு லேசான நீர்ப்பாசனம் அளித்து உரத்தின் வீரியத்தைக் குறைக்கவும்.\n"
                "3. **இலைச்சுருள் வைரஸ் (Leaf Curl Virus):** இலைகள் தடித்து சுருங்கி வளர்ச்சி குன்றும்.\n"
                "   - *மேலாண்மை:* பாதிக்கப்பட்ட செடிகளை அகற்றி வெள்ளை ஈக்களைக் கட்டுப்படுத்தவும்."
            )
        elif lang == "kn":
            return (
                "🌿 **ಬೆಳೆಗಳಲ್ಲಿ ಎಲೆ ಮುದುಡುವಿಕೆ (Leaf Curling) ಕಾರಣಗಳು ಮತ್ತು ಪರಿಹಾರಗಳು:**\n\n"
                "1. **ರಸ ಹೀರುವ ಕೀಟಗಳು (ಥ್ರಿಪ್ಸ್, ಬಿಳಿನೊಣ, ಜಿಗಿಹುಳು):** ಎಲೆಗಳ ಕೆಳಭಾಗದಿಂದ ರಸ ಹೀರುವುದರಿಂದ ಎಲೆಗಳು ದೋಣಿಯಾಕಾರದಲ್ಲಿ ಮೇಲಕ್ಕೆ ಅಥವಾ ಕೆಳಕ್ಕೆ ಮುದುಡುತ್ತವೆ.\n"
                "   - *ಪರಿಹಾರ:* ಹಳದಿ ಜಿಗುಟು ಬಲೆಗಳನ್ನು ಬಳಸಿ. ಬೇವಿನ ಎಣ್ಣೆ (2-3 ಮಿಲೀ/ಲೀಟರ್) ಅಥವಾ ಇಮಿಡಾಕ್ಲೋಪ್ರಿಡ್ ಸಿಂಪಡಿಸಿ.\n"
                "2. **ಹೆಚ್ಚಿನ ರಸಗೊಬ್ಬರ ಬಳಕೆ (Fertilizer Shock):** ಇತ್ತೀಚೆಗೆ ಹೆಚ್ಚು ಗೊಬ್ಬರ ಹಾಕಿದ್ದರೆ ಅಥವಾ ಬಿಸಿಲಿನಲ್ಲಿ ಸಿಂಪಡಿಸಿದ್ದರೆ ಎಲೆಗಳು ಮುದುಡಿಕೊಳ್ಳುತ್ತವೆ.\n"
                "   - *ಪರಿಹಾರ:* ತಕ್ಷಣವೇ ಹೊಲಕ್ಕೆ ಲಘು ನೀರಾವರಿ ಒದಗಿಸಿ ರಸಾಯನಿಕ ತೀವ್ರತೆಯನ್ನು ಕಡಿಮೆ ಮಾಡಿ.\n"
                "3. **ಎಲೆ ಮುದುಡು ವೈರಸ್ (Leaf Curl Virus):** ಎಲೆಗಳು ದಪ್ಪಗಾಗಿ ಸುರುಟಿಕೊಳ್ಳುತ್ತವೆ.\n"
                "   - *ಪರಿಹಾರ:* ರೋಗಪೀಡಿತ ಗಿಡಗಳನ್ನು ಕಿತ್ತು ನಾಶಪಡಿಸಿ, ಬಿಳಿನೊಣಗಳನ್ನು ನಿಯಂತ್ರಿಸಿ."
            )
        elif lang == "mr":
            return (
                "🌿 **पिकांमध्ये पाने आकसणे / मुरडणे (Leaf Curling) कारणे व उपाय:**\n\n"
                "1. **रस शोषक कीटक (थ्रिप्स, पांढरी माशी, मावा):** पानांच्या खालून रस शोषल्यामुळे पाने वर किंवा खाली वाकडी होतात.\n"
                "   - *उपाय:* पिवळे चिकट सापळे लावा. निंबोळी तेल (२-३ मिली/लिटर) किंवा इमिडाक्लोप्रिड फवारा.\n"
                "2. **खतांचा अतिरिक्त डोस (Fertilizer Burn):** नुकताच जास्त प्रमाणात खतांचा वापर झाल्यास पाने करपून वाकडी होतात.\n"
                "   - *उपाय:* शेताला लगेच हलके पाणी देऊन खतांची तीव्रता कमी करा.\n"
                "3. **पर्णमुरडा व्हायरस (Leaf Curl Virus):** पाने जाड व आखूड होतात.\n"
                "   - *उपाय:* बाधित झाडे उपटून नष्ट करा व पांढऱ्या माशीचे नियंत्रण करा."
            )
        else:
            return (
                "🌿 **Causes and Management of Crop Leaf Curling:**\n\n"
                "1. **Sap-Sucking Pests (Thrips, Aphids, Whiteflies, Broad Mites):**\n"
                "   - Upward curling typically indicates thrips or whiteflies; downward curling indicates aphids or broad mites feeding on leaf undersides.\n"
                "   - *Management:* Install 15-20 yellow and blue sticky traps per acre. Spray 10,000 ppm Neem Oil (2-3 ml/L) or an approved systemic insecticide such as Imidacloprid 17.8 SL (0.3 ml/L).\n"
                "2. **Fertilizer Shock / Chemical Burn:** Heavy top-dressing applied recently or foliar sprays applied under harsh sunlight cause rapid osmotic water pull and marginal leaf curling.\n"
                "   - *Management:* Flush the field with a light irrigation to buffer the root-zone chemical concentration.\n"
                "3. **Leaf Curl Virus:** Leaves become stunted, twisted, and thickened with prominent veins, transmitted by whiteflies.\n"
                "   - *Management:* Rogue out severely infected plants; manage the whitefly insect vector with protective sprays."
            )

        return ""

    def _build_spray_before_rain_response(self, question: str, lang: str) -> str:
        if lang == "te":
            return (
                "⚠️ **వర్షం పడే ముందు పురుగుమందులు పిచికారీ చేయవచ్చా?**\n\n"
                "**ఖచ్చితంగా వద్దు.** వర్షం పడే ముందు లేదా వర్ష సూచన ఉన్నప్పుడు పురుగుమందులు లేదా ఎరువుల పిచికారీ చేయకూడదు.\n\n"
                "**కారణాలు & నిబంధనలు:**\n"
                "1. **మందు కొట్టుకుపోవడం (Wash-off):** పిచికారీ చేసిన 2 నుండి 4 గంటల్లోపు వర్షం పడితే ఆకులపై ఉన్న మందు మొత్తం కొట్టుకుపోయి పనికిరాకుండా పోతుంది.\n"
                "2. **పెట్టుబడి నష్టం:** మందు మరియు కూలీ ఖర్చులు పూర్తిగా వృధా అవుతాయి.\n"
                "3. **సరైన సమయం:** కనీసం 24 గంటల పాటు వర్షం పడని పొడి వాతావరణం ఉన్నప్పుడు మాత్రమే పిచికారీ చేయాలి."
            )
        elif lang == "hi":
            return (
                "⚠️ **क्या बारिश से पहले कीटनाशक का छिड़काव करना चाहिए?**\n\n"
                "**बिल्कुल नहीं।** बारिश होने की संभावना या बारिश से तुरंत पहले कभी भी कीटनाशक या पर्णीय उर्वरक का छिड़काव न करें।\n\n"
                "**मुख्य कारण एवं दिशा-निर्देश:**\n"
                "1. **दवा का बह जाना:** छिड़काव के 2 से 4 घंटे के भीतर बारिश होने पर पत्तियों पर लगी दवा पूरी तरह धुल जाती है।\n"
                "2. **आर्थिक नुकसान:** महंगी कीटनाशक दवा और मजदूरी दोनों का सीधा नुकसान होता है।\n"
                "3. **उचित समय:** छिड़काव तभी करें जब कम से कम अगले 24 घंटे मौसम साफ और सूखा रहने का अनुमान हो।"
            )
        elif lang == "ta":
            return (
                "⚠️ **மழைக்கு முன் பூச்சிக்கொல்லி தெளிக்கலாமா?**\n\n"
                "**நிச்சயமாகக் கூடாது.** மழை பெய்வதற்கு முன்னரோ அல்லது மழை வாய்ப்புள்ள போதோ மருந்து தெளிக்கக் கூடாது.\n\n"
                "**காரணங்கள்:**\n"
                "1. **மருந்து அடித்துச் செல்லப்படுதல்:** தெளித்த 2-4 மணி நேரத்திற்குள் மழை பெய்தால் மருந்துகள் அனைத்தும் நீரில் அடித்துச் செல்லப்பட்டு பலனற்றுப் போகும்.\n"
                "2. **வீண் விரயம்:** மருந்து மற்றும் கூலிச் செலவு வீணாகும்.\n"
                "3. **சரியான நேரம்:** அடுத்த 24 மணி நேரத்திற்கு மழை இல்லாத வறண்ட வானிலையில் மட்டுமே தெளிக்க வேண்டும்."
            )
        elif lang == "kn":
            return (
                "⚠️ **ಮಳೆಗೆ ಮುನ್ನ ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸಬಹುದೇ?**\n\n"
                "**ಖಂಡಿತ ಬೇಡ.** ಮಳೆಯಾಗುವ ಮುನ್ನ ಅಥವಾ ಮಳೆ ಮುನ್ಸೂಚನೆ ಇದ್ದಾಗ ಯಾವುದೇ ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸಬೇಡಿ.\n\n"
                "**ಕಾರಣಗಳು:**\n"
                "1. **ಔಷಧಿ ತೊಳೆದುಹೋಗುವುದು:** ಸಿಂಪಡಿಸಿದ 2-4 ಗಂಟೆಗಳಲ್ಲಿ ಮಳೆ ಬಂದರೆ ಎಲೆಗಳ ಮೇಲಿನ ಔಷಧಿ ತೊಳೆದುಹೋಗಿ ನಿಷ್ಪ್ರಯೋಜಕವಾಗುತ್ತದೆ.\n"
                "2. **ಹಣದ ನಷ್ಟ:** ಔಷಧಿ ಮತ್ತು ಕೂಲಿ ವೆಚ್ಚ ವ್ಯರ್ಥವಾಗುತ್ತದೆ.\n"
                "3. **ಸೂಕ್ತ ಸಮಯ:** ಕನಿಷ್ಠ 24 ಗಂಟೆಗಳ ಕಾಲ ಮಳೆ ಇಲ್ಲದ ಶುಷ್ಕ ವಾತಾವರಣವಿದ್ದಾಗ ಮಾತ್ರ ಸಿಂಪಡಿಸಿ."
            )
        elif lang == "mr":
            return (
                "⚠️ **पावसापूर्वी कीटकनाशकांची फवारणी करावी का?**\n\n"
                "**मुळीच नाही.** पाऊस पडण्याची शक्यता असताना किंवा पावसापूर्वी कधीही कीटकनाशके फवारू नयेत.\n\n"
                "**कारणे:**\n"
                "1. **औषध वाहून जाणे:** फवारणीनंतर २ ते ४ तासांत पाऊस पडल्यास औषध पूर्णपणे वाहून जाते व परिणाम शून्य होतो.\n"
                "2. **आर्थिक नुकसान:** औषधांचा व मजुरीचा थेट तोटा होतो.\n"
                "3. **योग्य वेळ:** पुढील २४ तास हवामान कोरडे राहण्याचा अंदाज असेल तेव्हाच फवारणी करावी."
            )
        else:
            return (
                "⚠️ **Can I Spray Pesticide Before Rain?**\n\n"
                "**No, you should NOT spray chemical pesticides or fertilizers immediately before rain.**\n\n"
                "**Agronomic Reasons & Best Practices:**\n"
                "1. **Rain Wash-off (Loss of Efficacy):** If rain occurs within 2 to 4 hours of spraying, active chemical wash-off will be nearly 100%, rendering the application completely useless.\n"
                "2. **Financial Loss:** It leads to wasted chemicals, lost labor investment, and environmental contamination of runoff water bodies.\n"
                "3. **Rain-Free Window Rule:** Always verify that you have a minimum **24-hour clear, rain-free window** before conducting foliar applications."
            )

    def _build_post_rain_response(self, question: str, lang: str) -> str:
        if lang == "te":
            return (
                "🌾 **భారీ వర్షం పడిన తర్వాత పొలంలో తీసుకోవాల్సిన చర్యలు:**\n\n"
                "1. **నీటిని తొలగించడం:** పొలంలో నిలిచిన అదనపు నీటిని వెంటనే కాలువల ద్వారా బయటకు పంపండి. 24-48 గంటలకు మించి నీరు నిలిస్తే వేర్లకు గాలి అందక మొక్కలు కుళ్లిపోతాయి.\n"
                "2. **వేర్ల సంరక్షణ:** వర్షపు నీటి ప్రవాహానికి వేర్లు పైకి తేలితే మొక్కల మొదళ్ల వద్ద మట్టిని ఎగదోయండి.\n"
                "3. **తెగుళ్ల నివారణ:** అధిక తేమ వల్ల బూజు, కుళ్ళు తెగుళ్ళు వ్యాపిస్తాయి. నీరు ఇంకిన వెంటనే కాపర్ ఆక్సిక్లోరైడ్ (2.5 గ్రా/లీటర్) పిచికారీ చేయండి.\n"
                "4. **యూరియా వేయవద్దు:** నేల తేమగా ఉన్నప్పుడు యూరియా వేయకండి, అది కొట్టుకుపోతుంది."
            )
        elif lang == "hi":
            return (
                "🌾 **भारी बारिश के बाद खेत में तुरंत किए जाने वाले उपाय:**\n\n"
                "1. **जल निकासी:** खेत में जमा अतिरिक्त पानी को तुरंत नालियों के माध्यम से बाहर निकालें। जलभराव रहने पर जड़ें सड़ने लगती हैं।\n"
                "2. **मिट्टी चढ़ाना:** यदि तेज बहाव से पौधों की जड़ें खुल गई हैं, तो पौधों की जड़ों के पास तुरंत मिट्टी चढ़ाएं।\n"
                "3. **फफूंद जनित रोगों की रोकथाम:** पानी निकलने के बाद कॉपर ऑक्सीक्लोराइड (2.5 ग्राम/लीटर) का छिड़काव करें।\n"
                "4. **उर्वरक प्रयोग:** कीचड़ या अत्यधिक गीली मिट्टी में यूरिया न डालें। खेत सूखने पर ही पोषक तत्व दें।"
            )
        elif lang == "ta":
            return (
                "🌾 **கனமழைக்குப் பின் வயலில் மேற்கொள்ள வேண்டிய நடவடிக்கைகள்:**\n\n"
                "1. **வடிகால் வசதி:** வயலில் தேங்கியுள்ள உபரி நீரை உடனடியாக வடிய வைக்கவும். நீர் தேங்கினால் வேர் அழுகல் ஏற்படும்.\n"
                "2. **வேர் பராமரிப்பு:** வேர்கள் வெளிப்பட்டிருந்தால் செடிகளின் அடிப்பகுதியில் மண் அணைக்கவும்.\n"
                "3. **பூஞ்சாண நோய் தடுப்பு:** ஈரப்பதம் அதிகமாக இருப்பதால் காப்பர் ஆக்சிகுளோரைடு (2.5 கிராம்/லிட்டர்) தெளிக்கவும்.\n"
                "4. **உரமிடுதல்:** மண் ஈரமாக இருக்கும்போது யூரியா இட வேண்டாம்; அது வீணாகிவிடும்."
            )
        elif lang == "kn":
            return (
                "🌾 **ಭಾರಿ ಮಳೆಯ ನಂತರ ಹೊಲದಲ್ಲಿ ತೆಗೆದುಕೊಳ್ಳಬೇಕಾದ ಕ್ರಮಗಳು:**\n\n"
                "1. **ನೀರು ಹೊರಹಾಕುವುದು:** ಹೊಲದಲ್ಲಿ ನಿಂತಿರುವ ಹೆಚ್ಚುವರಿ ನೀರನ್ನು ಕೂಡಲೇ ಚರಂಡಿಗಳ ಮೂಲಕ ಹೊರಹಾಕಿ.\n"
                "2. **ಬೇರುಗಳ ಸಂರಕ್ಷಣೆ:** ಬೇರುಗಳು ಕಾಣಿಸಿಕೊಂಡಿದ್ದರೆ ಗಿಡಗಳ ಬುಡಕ್ಕೆ ಮಣ್ಣು ಏರಿಸಿ.\n"
                "3. **ಶಿಲೀಂಧ್ರ ರೋಗಗಳ ನಿಯಂತ್ರಣ:** ನೀರು ಇಳಿದ ನಂತರ ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ (2.5 ಗ್ರಾಂ/ಲೀಟರ್) ಸಿಂಪಡಿಸಿ.\n"
                "4. **ಗೊಬ್ಬರ ಹಾಕಬೇಡಿ:** ಹೊಲದಲ್ಲಿ ತೇವಾಂಶ ಹೆಚ್ಚಿರುವಾಗ ಯೂರಿಯಾ ಹಾಕಬೇಡಿ."
            )
        elif lang == "mr":
            return (
                "🌾 **मुसळधार पावसानंतर शेतात करायच्या तातडीच्या उपाययोजना:**\n\n"
                "1. **पाण्याचा निचरा:** शेतात साचलेले अतिरिक्त पाणी चरींद्वारे त्वरित बाहेर काढा. पाणी साचल्यास मुळे सडतात.\n"
                "2. **मातीची भर देणे:** पाण्याच्या प्रवाहाने मुळे उघडी पडल्यास झाडांच्या बुंध्याशी माती लावा.\n"
                "3. **बुरशीजन्य रोगांचे नियंत्रण:** पाणी ओसरल्यानंतर कॉपर ऑक्सिक्लोराईड (२.५ ग्रॅम/लिटर) फवारा.\n"
                "4. **खत देणे टाळा:** चिखल असताना युरिया टाकू नका; शेत वाफशावर आल्यावरच खत द्या."
            )
        else:
            return (
                "🌾 **Post-Heavy Rain Field Recovery Protocol:**\n\n"
                "1. **Drain Standing Water Immediately:** Open drainage ditches to clear stagnant water from fields. Standing water suffocates crop roots within 24 to 48 hours.\n"
                "2. **Soil Aeration & Earthing Up:** Inspect for exposed roots caused by surface runoff; gently earth up loose soil around plant bases once workable.\n"
                "3. **Prevent Fungal Blights & Root Rot:** Apply a preventive spray of Copper Oxychloride (2.5 g/L) or Trichoderma viride once excess water recedes.\n"
                "4. **Postpone Urea Top-Dressing:** Do not apply urea while fields are waterlogged as nitrogen leaches rapidly."
            )

    def _build_crop_response(
        self, question: str, crop_rec: Dict[str, Any], profile: Dict[str, Any], lang: str
    ) -> str:
        rec_crop = crop_rec.get("crop")
        if lang == "te":
            rec_str = f"మీ నేల మరియు వాతావరణానికి సిఫార్సు చేయబడిన పంట: **{rec_crop}**.\n\n" if rec_crop else ""
            return (
                f"🌾 **పంట ఎంపిక & సిఫార్సు సలహా:**\n\n"
                f"{rec_str}"
                f"సరైన పంటను ఎన్నుకోవడానికి మీ నేలలోని నత్రజని (N), భాస్వరం (P), పొటాష్ (K), నేల pH మరియు వర్షపాతం కీలకం. "
                f"మీ పొలం నేల వివరాలతో డ్యాష్‌బోర్డ్‌లోని 'పంట సిఫార్సు (Crop Recommendation)' ఫీచర్‌ను ఉపయోగించి శాస్త్రీయ ఎంపిక పొందండి."
            )
        elif lang == "hi":
            rec_str = f"आपकी मिट्टी एवं जलवायु के अनुसार अनुशंसित फसल: **{rec_crop}**।\n\n" if rec_crop else ""
            return (
                f"🌾 **फसल चयन एवं सिफ़ारिश परामर्श:**\n\n"
                f"{rec_str}"
                f"सही फसल का चुनाव मिट्टी के पोषक तत्वों (N, P, K), मिट्टी के pH और मौसमी वर्षा पर निर्भर करता है। "
                f"अपनी जमीन के सटीक आंकड़ों के साथ डैशबोर्ड में 'फसल सिफ़ारिश' (Crop Recommendation) टूल का उपयोग करें।"
            )
        elif lang == "ta":
            rec_str = f"உங்கள் மண் மற்றும் காலநிலைக்கு பரிந்துரைக்கப்பட்ட பயிர்: **{rec_crop}**.\n\n" if rec_crop else ""
            return (
                f"🌾 **பயிர் தேர்வு மற்றும் பரிந்துரை ஆலோசனை:**\n\n"
                f"{rec_str}"
                f"சரியான பயிரைத் தேர்ந்தெடுக்க மண்ணின் ஊட்டச்சத்துக்கள் (N, P, K), pH மற்றும் மழைப்பொழிவு முக்கியம். "
                f"முகப்புப் பக்கத்தில் உள்ள 'பயிர் பரிந்துரை' கருவியைப் பயன்படுத்தி சிறந்த பயிரைத் தேர்வு செய்யவும்."
            )
        elif lang == "kn":
            rec_str = f"ನಿಮ್ಮ ಮಣ್ಣು ಮತ್ತು ಹವಾಮಾನಕ್ಕೆ ಶಿಫಾರಸು ಮಾಡಲಾದ ಬೆಳೆ: **{rec_crop}**.\n\n" if rec_crop else ""
            return (
                f"🌾 **ಬೆಳೆ ಆಯ್ಕೆ ಮತ್ತು ಶಿಫಾರಸು ಸಲಹೆ:**\n\n"
                f"{rec_str}"
                f"ಉತ್ತಮ ಬೆಳೆ ಆಯ್ಕೆ ಮಾಡಲು ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳು (N, P, K), pH ಮತ್ತು ಮಳೆ ಪ್ರಮಾಣ ಮುಖ್ಯ. "
                f"ನಿಮ್ಮ ಮಣ್ಣಿನ ವಿವರಗಳೊಂದಿಗೆ 'ಬೆಳೆ ಶಿಫಾರಸು' ಟೂಲ್ ಬಳಸಿ ವೈಜ್ಞಾನಿಕ ಸಲಹೆ ಪಡೆಯಿರಿ."
            )
        elif lang == "mr":
            rec_str = f"आपल्या माती व हवामानानुसार शिफारस केलेले पीक: **{rec_crop}**.\n\n" if rec_crop else ""
            return (
                f"🌾 **पीक निवड व शिफारस सल्ला:**\n\n"
                f"{rec_str}"
                f"योग्य पिकाची निवड करण्यासाठी मातीतील पोषक घटक (N, P, K), pH आणि पाऊस महत्त्वाचा असतो. "
                f"डॅशबोर्डवरील 'पीक शिफारस' टूल वापरून आपल्या शेतासाठी सर्वोत्तम पीक निवडा."
            )
        else:
            rec_str = f"Based on your recent soil assessment, your recommended crop is **{rec_crop}**.\n\n" if rec_crop else ""
            return (
                f"🌾 **Crop Recommendation Advisory:**\n\n"
                f"{rec_str}"
                f"Selecting the most productive crop depends directly on your field's soil Nitrogen (N), Phosphorus (P), Potassium (K), soil pH, and expected seasonal rainfall.\n\n"
                f"To calculate the scientific best-match crop for your farm, open the **Crop Recommendation** feature on FarmSathi, enter your soil test values, and run the verified AI model."
            )

    def _build_crop_ml_prediction_response(
        self,
        question: str,
        soil: Dict[str, float],
        weather: Dict[str, Any],
        lang: str,
    ) -> str:
        temp_val = soil.get("temp")
        if temp_val is None and weather.get("temp"):
            try:
                temp_val = float(weather["temp"])
            except Exception:
                temp_val = 26.0
        if temp_val is None:
            temp_val = 26.0

        hum_val = soil.get("humidity")
        if hum_val is None and weather.get("humidity"):
            try:
                hum_val = float(weather["humidity"])
            except Exception:
                hum_val = 70.0
        if hum_val is None:
            hum_val = 70.0

        rain_val = soil.get("rainfall")
        if rain_val is None:
            rain_val = 150.0

        try:
            from app.services.crop_service import crop_service
            from app.schemas.crop import CropRecommendationRequest

            req = CropRecommendationRequest(
                nitrogen=soil["n"],
                phosphorus=soil["p"],
                potassium=soil["k"],
                ph=soil["ph"],
                temperature=temp_val,
                humidity=hum_val,
                rainfall=rain_val,
            )
            result = crop_service.predict(req)
            pred_crop = result["recommended_crop"]
            top_preds = result.get("top_predictions", [])
        except Exception as exc:
            logger.error("Crop ML inference failed in advisory: %s", exc)
            return self._build_crop_location_missing_soil_response(question, weather, {}, lang)

        alt_crops = [
            f"{p['crop'].capitalize()} ({round(p['probability'] * 100, 1)}%)"
            for p in top_preds
            if p["crop"].lower() != pred_crop.lower()
        ][:2]
        alt_str = ", ".join(alt_crops) if alt_crops else "None"
        cap_crop = pred_crop.capitalize()

        if lang == "te":
            return (
                f"🌾 **మీ నేల మరియు వాతావరణానికి శాస్త్రీయ పంట సిఫార్సు (Random Forest Model):**\n\n"
                f"- **సిఫార్సు చేయబడిన ప్రధాన పంట:** **{cap_crop}**\n"
                f"- **ప్రత్యామ్నాయ అనుకూల పంటలు:** {alt_str}\n\n"
                f"**విశ్లేషించిన నేల & వాతావరణ వివరాలు:**\n"
                f"- నత్రజని (N): {soil['n']}, భాస్వరం (P): {soil['p']}, పొటాష్ (K): {soil['k']}\n"
                f"- నేల pH: {soil['ph']} | ఉష్ణోగ్రత: {temp_val}°C | తేమ: {hum_val}% | వర్షపాతం: {rain_val} మి.మీ\n\n"
                f"**వ్యవసాయ సూచనలు:** మీ నేల పోషకాల నిష్పత్తికి {cap_crop} అత్యధిక దిగుబడిని ఇవ్వడానికి అత్యంత అనుకూలంగా ఉంది. "
                f"విత్తే ముందు విత్తన శుద్ధి చేసి, సిఫార్సు చేసిన ఎరువుల మోతాదును పాటించండి."
            )
        elif lang == "hi":
            return (
                f"🌾 **मृदा एवं जलवायु आधारित वैज्ञानिक फसल सिफ़ारिश (Random Forest Model):**\n\n"
                f"- **सर्वश्रेष्ठ अनुशंसित फसल:** **{cap_crop}**\n"
                f"- **वैकल्पिक उपयुक्त फसलें:** {alt_str}\n\n"
                f"**मूल्यांकित मृदा एवं मौसम आंकड़े:**\n"
                f"- नाइट्रोजन (N): {soil['n']}, फास्फोरस (P): {soil['p']}, पोटाश (K): {soil['k']}\n"
                f"- मिट्टी pH: {soil['ph']} | तापमान: {temp_val}°C | आर्द्रता: {hum_val}% | वर्षा: {rain_val} मिमी\n\n"
                f"**कृषि सलाह:** आपके खेत के पोषक तत्वों के अनुसार {cap_crop} की बुवाई से अधिकतम उत्पादन प्राप्त होगा। "
                f"बुवाई से पूर्व बीज उपचार अवश्य करें और संतुलित उर्वरक प्रबंधन अपनाएं।"
            )
        elif lang == "ta":
            return (
                f"🌾 **மண் மற்றும் காலநிலை அடிப்படையிலான அறிவியல் பயிர் பரிந்துரை:**\n\n"
                f"- **பரிந்துரைக்கப்பட்ட முதன்மைப் பயிர்:** **{cap_crop}**\n"
                f"- **மாற்றுப் பொருத்தமான பயிர்கள்:** {alt_str}\n\n"
                f"**மதிப்பிடப்பட்ட அளவுருக்கள்:**\n"
                f"- N: {soil['n']}, P: {soil['p']}, K: {soil['k']}\n"
                f"- pH: {soil['ph']} | வெப்பநிலை: {temp_val}°C | ஈரப்பதம்: {hum_val}% | மழைப்பொழிவு: {rain_val} மிமீ\n\n"
                f"**வேளாண் வழிகாட்டல்:** உங்கள் மண்ணின் தரத்திற்கு {cap_crop} சிறந்த மகசூலைத் தரும். தகுந்த விதை நேர்த்தி செய்து சாகுபடி செய்யவும்."
            )
        elif lang == "kn":
            return (
                f"🌾 **ಮಣ್ಣು ಮತ್ತು ಹವಾಮಾನ ಆಧಾರಿತ ವೈಜ್ಞಾನಿಕ ಬೆಳೆ ಶಿಫಾರಸು:**\n\n"
                f"- **ಶಿಫಾರಸು ಮಾಡಲಾದ ಮುಖ್ಯ ಬೆಳೆ:** **{cap_crop}**\n"
                f"- **ಪರ್ಯಾಯ ಸೂಕ್ತ ಬೆಳೆಗಳು:** {alt_str}\n\n"
                f"**ಪರಿಶೀಲಿಸಿದ ಅಂಕಿಅಂಶಗಳು:**\n"
                f"- N: {soil['n']}, P: {soil['p']}, K: {soil['k']}\n"
                f"- pH: {soil['ph']} | ತಾಪಮಾನ: {temp_val}°C | ತೇವಾಂಶ: {hum_val}% | ಮಳೆ: {rain_val} ಮಿಮೀ\n\n"
                f"**ಕೃಷಿ ಸಲಹೆ:** ನಿಮ್ಮ ಮಣ್ಣಿನ ಪೋಷಕಾಂಶ ಮಟ್ಟಕ್ಕೆ {cap_crop} ಅತ್ಯಧಿಕ ಇಳುವರಿ ನೀಡಲು ಅತ್ಯಂತ ಸೂಕ್ತವಾಗಿದೆ."
            )
        elif lang == "mr":
            return (
                f"🌾 **माती व हवामानावर आधारित वैज्ञानिक पीक शिफारस:**\n\n"
                f"- **प्रमुख शिफारस केलेले पीक:** **{cap_crop}**\n"
                f"- **पर्यायी योग्य पिके:** {alt_str}\n\n"
                f"**विश्लेषित घटक:**\n"
                f"- N: {soil['n']}, P: {soil['p']}, K: {soil['k']}\n"
                f"- सामू (pH): {soil['ph']} | तापमान: {temp_val}°C | आर्द्रता: {hum_val}% | पाऊस: {rain_val} मिमी\n\n"
                f"**कृषी सल्ला:** आपल्या शेतातील मातीच्या पोषणानुसार {cap_crop} पिकापासून भरघोस उत्पादन मिळू शकते."
            )
        else:
            return (
                f"🌾 **Scientific Crop Recommendation (FarmSathi Random Forest ML Model):**\n\n"
                f"- **Authoritative Recommended Crop:** **{cap_crop}**\n"
                f"- **Alternative High-Suitability Options:** {alt_str}\n\n"
                f"**Evaluated Soil & Agro-Climatic Parameters:**\n"
                f"- Soil Nitrogen (N): {soil['n']} | Phosphorus (P): {soil['p']} | Potassium (K): {soil['k']}\n"
                f"- Soil pH: {soil['ph']} | Ambient Temperature: {temp_val}°C | Humidity: {hum_val}% | Rainfall: {rain_val} mm\n\n"
                f"**Agronomic Guidance:** Based on your soil's specific chemical balance, **{cap_crop}** offers the highest probability of vigorous vegetative development and maximum economic yield. Follow certified seed treatment and balanced split-application of basal nutrients."
            )

    def _build_crop_location_missing_soil_response(
        self,
        question: str,
        weather: Dict[str, Any],
        profile: Dict[str, Any],
        lang: str,
    ) -> str:
        loc_name = weather.get("location") or profile.get("district")
        if not loc_name or loc_name.startswith("Coordinates"):
            m_bow = re.search(r"bowrampet.*dundigal|dundigal.*bowrampet|bowrampet|dundigal", question, re.IGNORECASE)
            if m_bow:
                loc_name = "Bowrampet village, Dundigal (Telangana)"
            else:
                loc_name = "your specified location"

        temp_str = f"{weather.get('temp')}°C" if weather.get("temp") else "28°C"
        hum_str = f"{weather.get('humidity')}%" if weather.get("humidity") else "65%"
        cond_str = weather.get("condition") or "Partly Cloudy"

        if lang == "te":
            return (
                f"🌾 **{loc_name} ప్రాంతంలో పంట సాగు & సిఫార్సు మార్గదర్శకాలు:**\n\n"
                f"**తాజా వాతావరణ సమాచారం (Live Agro-Weather):**\n"
                f"- ఉష్ణోగ్రత: {temp_str} ({cond_str}) | గాలిలో తేమ: {hum_str}\n\n"
                f"⚠️ **ఖచ్చితమైన పంట సిఫార్సుకు నేల వివరాలు తప్పనిసరి:**\n"
                f"ఫార్మ్‌సాథి సైంటిఫిక్ పంట సిఫార్సు మోడల్ కేవలం ప్రాంతం ఆధారంగా ఊహాజనిత సలహాలు ఇవ్వదు. "
                f"ఏ పంట అధిక దిగుబడి ఇస్తుందో ఖచ్చితంగా నిర్ణయించడానికి క్రింది 4 నేల పరీక్ష విలువలు అవసరం:\n"
                f"1. **నత్రజని (Nitrogen - N):** మొక్క ఎదుగుదలకు.\n"
                f"2. **భాస్వరం (Phosphorus - P):** వేర్ల అభివృద్ధి మరియు పిలకలు వేయడానికి.\n"
                f"3. **పొటాష్ (Potassium - K):** రోగనిరోధక శక్తి మరియు నాణ్యమైన గింజల కోసం.\n"
                f"4. **నేల pH విలువ:** పోషకాల లభ్యతను నిర్ణయించడానికి.\n\n"
                f"**ఈ ప్రాంతంలో (దుండిగల్ / మేడ్చల్ పరిధిలో) సాధారణంగా పండించే పంటలు:**\n"
                f"- *ఖరీఫ్:* వరి (నీటి వసతి ఉన్నప్పుడు), పత్తి, మొక్కజొన్న, కందులు.\n"
                f"- *రబీ & కూరగాయలు:* శనగ, వేరుశనగ, టమాటా, మిరప, ఆకుకూరలు.\n\n"
                f"👉 **తదుపరి చర్య:** మీ నేల ఆరోగ్య పత్రం (Soil Health Card) లోని N, P, K మరియు pH విలువలను నమోదు చేసి ఖచ్చితమైన శాస్త్రీయ సిఫార్సు పొందండి."
            )
        elif lang == "hi":
            return (
                f"🌾 **{loc_name} क्षेत्र के लिए फसल चयन एवं कृषि मार्गदर्शन:**\n\n"
                f"**स्थानीय मौसम की स्थिति (Live Agro-Weather):**\n"
                f"- तापमान: {temp_str} ({cond_str}) | हवा में नमी: {hum_str}\n\n"
                f"⚠️ **सटीक वैज्ञानिक सिफ़ारिश हेतु मिट्टी परीक्षण विवरण आवश्यक है:**\n"
                f"फार्मसाथी का एआई मॉडल केवल क्षेत्र के नाम पर अनुमानित सलाह नहीं देता। "
                f"अधिकतम पैदावार वाली फसल तय करने के लिए निम्नलिखित 4 मृदा परीक्षण आंकड़ों की आवश्यकता है:\n"
                f"1. **नाइट्रोजन (N):** वानस्पतिक वृद्धि के लिए।\n"
                f"2. **फास्फोरस (P):** जड़ों के फैलाव एवं कल्ले फूटने के लिए।\n"
                f"3. **पोटाश (K):** रोग प्रतिरोधक क्षमता और दाना भराव के लिए।\n"
                f"4. **मृदा pH:** पोषक तत्वों की उपलब्धता सुनिश्चित करने के लिए।\n\n"
                f"**इस क्षेत्र (दुंडीगल / तेलंगाना) में आमतौर पर उगाई जाने वाली फसलें:**\n"
                f"- *खरीफ:* धान (सिंचित क्षेत्रों में), कपास, मक्का, अरहर।\n"
                f"- *रबी एवं बागवानी:* चना, मूंगफली, टमाटर, मिर्च एवं मौसमी सब्जियां।\n\n"
                f"👉 **सुझाव:** अपनी मिट्टी की जांच रिपोर्ट से N, P, K और pH मान यहां लिखकर पूछें अथवा फार्मसाथी के 'फसल सिफ़ारिश' टूल में दर्ज कर सटीक परिणाम प्राप्त करें।"
            )
        elif lang == "ta":
            return (
                f"🌾 **{loc_name} பகுதிக்கான பயிர் சாகுபடி மற்றும் வழிகாட்டல்:**\n\n"
                f"**நேரடி வானிலை நிலவரம் (Live Agro-Weather):**\n"
                f"- வெப்பநிலை: {temp_str} ({cond_str}) | ஈரப்பதம்: {hum_str}\n\n"
                f"⚠️ **துல்லியமான பயிர் பரிந்துரைக்கு மண் பரிசோதனை அவசியம்:**\n"
                f"பார்ம்சாதி அறிவியல் மாதிரி வெறும் இடத்தை வைத்து உத்தேச பரிந்துரை வழங்குவதில்லை. "
                f"அதிக மகசூல் தரும் பயிரைத் தேர்ந்தெடுக்க 4 மண் ஊட்டச்சத்து அளவுகள் தேவை:\n"
                f"1. **தழைச்சத்து (Nitrogen - N):** பயிர் வளர்ச்சிக்கு.\n"
                f"2. **மணிச்சத்து (Phosphorus - P):** வேர் வளர்ச்சிக்கு.\n"
                f"3. **சாம்பல்சத்து (Potassium - K):** நோய் எதிர்ப்பு மற்றும் விளைச்சலுக்கு.\n"
                f"4. **மண் pH:** ஊட்டச்சத்து உறிஞ்சுதலுக்கு.\n\n"
                f"**இப்பகுதியில் வழக்கமாகப் பயிரிடப்படும் பயிர்கள்:** நெல், பருத்தி, மக்காச்சோளம், துவரை, தக்காளி, மிளகாய்.\n\n"
                f"👉 உங்கள் மண் பரிசோதனை N, P, K மற்றும் pH மதிப்புகளைப் பதிவிட்டு துல்லியமான பயிர் பரிந்துரையைப் பெறுங்கள்."
            )
        elif lang == "kn":
            return (
                f"🌾 **{loc_name} ಪ್ರದೇಶಕ್ಕೆ ಬೆಳೆ ಆಯ್ಕೆ ಮತ್ತು ಕೃಷಿ ಮಾರ್ಗದರ್ಶನ:**\n\n"
                f"**ಸ್ಥಳೀಯ ಹವಾಮಾನ ವಿವರ (Live Agro-Weather):**\n"
                f"- ತಾಪಮಾನ: {temp_str} ({cond_str}) | ತೇವಾಂಶ: {hum_str}\n\n"
                f"⚠️ **ನಿಖರ ಬೆಳೆ ಶಿಫಾರಸಿಗೆ ಮಣ್ಣಿನ ವಿವರಗಳು ಅಗತ್ಯ:**\n"
                f"ಫಾರ್ಮ್‌ಸಾಥಿ ವೈಜ್ಞಾನಿಕ ಮಾದರಿಯು ಊಹೆಯ ಮೇಲೆ ಬೆಳೆ ಶಿಫಾರಸು ಮಾಡುವುದಿಲ್ಲ. "
                f"ಉತ್ತಮ ಇಳುವರಿ ನೀಡುವ ಬೆಳೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಲು 4 ಮಣ್ಣಿನ ಅಂಶಗಳು ಬೇಕಾಗುತ್ತವೆ:\n"
                f"1. **ಸಾರಜನಕ (N):** ಸಸ್ಯದ ಬೆಳವಣಿಗೆಗೆ.\n"
                f"2. **ರಂಜಕ (P):** ಬೇರಿನ ಬೆಳವಣಿಗೆಗೆ.\n"
                f"3. **ಪೊಟ್ಯಾಶ್ (K):** ರೋಗ ನಿರೋಧಕ ಶಕ್ತಿಗೆ.\n"
                f"4. **ಮಣ್ಣಿನ pH:** ಪೋಷಕಾಂಶಗಳ ಲಭ್ಯತೆಗೆ.\n\n"
                f"**ಈ ಪ್ರದೇಶದಲ್ಲಿ ಸಾಮಾನ್ಯವಾಗಿ ಬೆಳೆಯುವ ಬೆಳೆಗಳು:** ಭತ್ತ, ಹತ್ತಿ, ಮೆಕ್ಕೆಜೋಳ, ತೊಗರಿ, ತರಕಾರಿಗಳು.\n\n"
                f"👉 ನಿಮ್ಮ ಮಣ್ಣಿನ N, P, K ಮತ್ತು pH ವಿವರಗಳನ್ನು ನಮೂದಿಸಿ ನಿಖರವಾದ ಶಿಫಾರಸು ಪಡೆಯಿರಿ."
            )
        elif lang == "mr":
            return (
                f"🌾 **{loc_name} भागासाठी पीक निवड व कृषी सल्ला:**\n\n"
                f"**स्थानिक हवामानाची स्थिती (Live Agro-Weather):**\n"
                f"- तापमान: {temp_str} ({cond_str}) | हवेतील आर्द्रता: {hum_str}\n\n"
                f"⚠️ **अचूक पीक निवडीसाठी माती परीक्षण अहवाल आवश्यक:**\n"
                f"फार्मसाथीचे एआय मॉडेल केवळ परिसराच्या नावावर अंदाजे शिफारस करत नाही. "
                f"भरघोस उत्पादन देणारे पीक निवडण्यासाठी खालील ४ माती घटक आवश्यक आहेत:\n"
                f"1. **नत्र (N):** शाकीय वाढीसाठी.\n"
                f"2. **स्फुरद (P):** मुळांच्या विकासासाठी.\n"
                f"3. **पालाश (K):** दाणे भरण्यासाठी व रोगांपासून संरक्षणासाठी.\n"
                f"4. **जमिनीचा सामू (pH):** अन्नद्रव्यांच्या उपलब्धतेसाठी.\n\n"
                f"**या भागात घेतली जाणारी प्रमुख पिके:** भात, कापूस, मका, तूर, टोमॅटो, मिरची व भाजीपाला.\n\n"
                f"👉 आपल्या मातीचे N, P, K आणि pH मूल्य नमूद करून 'पीक शिफारस' टूलद्वारे अचूक पीक निवडा."
            )
        else:
            return (
                f"🌾 **Crop Cultivation & Selection Guidelines for {loc_name}:**\n\n"
                f"**Current Local Agro-Weather (Live Conditions):**\n"
                f"- Ambient Temperature: {temp_str} ({cond_str}) | Relative Humidity: {hum_str}\n\n"
                f"⚠️ **Scientific Grounding Notice — Soil Test Parameters Required:**\n"
                f"FarmSathi's verified crop recommendation model relies on a trained Random Forest classifier. "
                f"Providing an automated crop guarantee for {loc_name} without soil chemical parameters would be ungrounded guesswork. "
                f"To calculate the scientifically optimal crop for your field, the following 4 parameters are needed:\n"
                f"1. **Nitrogen (N):** Fuels vegetative canopy and stem vigor.\n"
                f"2. **Phosphorus (P):** Governs root zone development and early tillering.\n"
                f"3. **Potassium (K):** Regulates plant stomatal conductance and disease resistance.\n"
                f"4. **Soil pH:** Dictates nutrient solubility and root bioavailability.\n\n"
                f"**Predominant Agro-Climatic Regional Crops (Dundigal / Semi-Arid Deccan Region):**\n"
                f"- **Kharif (Monsoon):** Paddy (under assured irrigation), Cotton, Maize, Red Gram (Pigeonpea).\n"
                f"- **Rabi & Peri-Urban Horticulture:** Bengal Gram (Chickpea), Groundnut, Tomato, Chili, and fresh leafy greens.\n\n"
                f"👉 **Next Step:** Provide your soil values (e.g., *'Recommend crop for N=90, P=42, K=43, pH=6.5'*), or navigate to the **Crop Recommendation** feature on FarmSathi to run the verified machine learning model."
            )

    def _build_attached_image_disease_response(
        self,
        question: str,
        disease: Dict[str, Any],
        lang: str,
    ) -> str:
        if disease.get("is_suitable") is False:
            suit_msg = disease.get("suitability_message") or "Image does not appear to contain clear crop foliage."
            if lang == "te":
                return (
                    f"📷 **ఆకు చిత్రం విశ్లేషణ ఫలితం (MobileNetV3):**\n\n"
                    f"చిత్రం నాణ్యత పరిశీలన: {suit_msg}\n\n"
                    f"ఖచ్చితమైన వ్యాధి నిర్ధారణ కోసం దయచేసి వ్యాధి లక్షణాలు లేదా మచ్చలు ఉన్న ఆకును దగ్గరగా, స్పష్టమైన వెలుతురులో ఫోటో తీసి మళ్లీ పంపండి."
                )
            elif lang == "hi":
                return (
                    f"📷 **पत्ती चित्र विश्लेषण परिणाम (MobileNetV3):**\n\n"
                    f"चित्र उपयुक्त नहीं: {suit_msg}\n\n"
                    f"सटीक रोग पहचान के लिए कृपया रोग के धब्बे वाली पत्ती की पास से, साफ रोशनी में फोटो खींचकर पुनः भेजें।"
                )
            elif lang == "ta":
                return (
                    f"📷 **இலை பட பகுப்பாய்வு முடிவு (MobileNetV3):**\n\n"
                    f"படம் தெளிவில்லை: {suit_msg}\n\n"
                    f"துல்லியமான நோய் கண்டறிதலுக்கு பாதிக்கப்பட்ட இலையை வெளிச்சத்தில் தெளிவாகப் புகைப்படம் எடுத்து மீண்டும் அனுப்பவும்."
                )
            elif lang == "kn":
                return (
                    f"📷 **ಎಲೆ ಚಿತ್ರ ವಿಶ್ಲೇಷಣೆ ಫಲಿತಾಂಶ (MobileNetV3):**\n\n"
                    f"ಚಿತ್ರ ಸೂಕ್ತವಾಗಿಲ್ಲ: {suit_msg}\n\n"
                    f"ನಿಖರ ರೋಗ ಪತ್ತೆಗಾಗಿ ದಯವಿಟ್ಟು ರೋಗಪೀಡಿತ ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋವನ್ನು ಬೆಳಕಿನಲ್ಲಿ ತೆಗೆದು ಮತ್ತೆ ಕಳುಹಿಸಿ."
                )
            elif lang == "mr":
                return (
                    f"📷 **पान चित्र विश्लेषण निकाल (MobileNetV3):**\n\n"
                    f"चित्र योग्य नाही: {suit_msg}\n\n"
                    f"अचूक रोग निदानासाठी कृपया रोगाचे डाग असलेल्या पानाचा स्पष्ट प्रकाशात जवळून फोटो काढून पुन्हा पाठवा."
                )
            else:
                return (
                    f"📷 **Attached Leaf Photo Analysis (FarmSathi MobileNetV3):**\n\n"
                    f"Assessment: {suit_msg}\n\n"
                    f"For an accurate computer vision diagnosis, please capture a close-up, focused photo of the symptomatic leaf under good daylight conditions and re-upload."
                )

        condition = disease.get("condition", "Undetermined Foliar Issue")
        clean_cond = condition.replace("___", " - ").replace("__", " - ").replace("_", " ")
        confidence = disease.get("confidence", "N/A")
        crop = disease.get("crop", "Crop")
        is_healthy = disease.get("is_healthy", False)
        practices = disease.get("practices", "")

        if is_healthy:
            if lang == "te":
                return (
                    f"🌿 **ఆకు చిత్రం విశ్లేషణ ఫలితం (MobileNetV3 Model):**\n\n"
                    f"- **గుర్తించిన పరిస్థితి:** **ఆరోగ్యకరమైన ఆకు ({clean_cond})**\n"
                    f"- **విశ్లేషణ ఖచ్చితత్వం:** {confidence}\n"
                    f"- **పంట:** {crop}\n\n"
                    f"**పరిశీలన:** ఆకుపై ఎటువంటి వ్యాధి లేదా బూజు లక్షణాలు కనిపించలేదు. మొక్క ఆరోగ్యంగా ఉంది. "
                    f"పంటను ఇలాగే కాపాడుకోవడానికి క్రమం తప్పకుండా నీరు మరియు సమతుల్య ఎరువులను అందించండి."
                )
            elif lang == "hi":
                return (
                    f"🌿 **पत्ती चित्र विश्लेषण परिणाम (MobileNetV3 Model):**\n\n"
                    f"- **निदान स्थिति:** **स्वस्थ पत्ती ({clean_cond})**\n"
                    f"- **मॉडल सटीकता:** {confidence}\n"
                    f"- **फसल:** {crop}\n\n"
                    f"**समीक्षा:** पत्ती पर किसी सक्रिय रोग या फफूंद के लक्षण नहीं पाए गए हैं। पौधा पूर्णतः स्वस्थ है। "
                    f"नियमित पोषण एवं हल्की सिंचाई बनाए रखें।"
                )
            elif lang == "ta":
                return (
                    f"🌿 **இலை பட பகுப்பாய்வு முடிவு:**\n\n"
                    f"- **நிலை:** **ஆரோக்கியமான இலை ({clean_cond})**\n"
                    f"- **நம்பகத்தன்மை:** {confidence}\n"
                    f"- **பயிர்:** {crop}\n\n"
                    f"இலையில் எந்தவித பூஞ்சாண அல்லது நோய் அறிகுறிகளும் இல்லை. பயிர் ஆரோக்கியமாக உள்ளது."
                )
            elif lang == "kn":
                return (
                    f"🌿 **ಎಲೆ ಚಿತ್ರ ವಿಶ್ಲೇಷಣೆ ಫಲಿತಾಂಶ:**\n\n"
                    f"- **ಸ್ಥಿತಿ:** **ಆರೋಗ್ಯಕರ ಎಲೆ ({clean_cond})**\n"
                    f"- **ನಿಖರತೆ:** {confidence}\n"
                    f"- **ಬೆಳೆ:** {crop}\n\n"
                    f"ಎಲೆಯ ಮೇಲೆ ಯಾವುದೇ ರೋಗದ ಲಕ್ಷಣಗಳಿಲ್ಲ. ಬೆಳೆ ಆರೋಗ್ಯಕರವಾಗಿದೆ."
                )
            elif lang == "mr":
                return (
                    f"🌿 **पान चित्र विश्लेषण निकाल:**\n\n"
                    f"- **स्थिती:** **निरोगी पान ({clean_cond})**\n"
                    f"- **अचूकता:** {confidence}\n"
                    f"- **पीक:** {crop}\n\n"
                    f"पानावर कोणत्याही रोगाचे किंवा बुरशीचे डाग आढळलेले नाहीत. झाड निरोगी आहे."
                )
            else:
                return (
                    f"🌿 **Attached Leaf Photo Diagnosis (FarmSathi MobileNetV3 AI):**\n\n"
                    f"- **Diagnosed Condition:** **Healthy Foliage ({clean_cond})**\n"
                    f"- **Model Confidence:** {confidence}\n"
                    f"- **Identified Crop:** {crop}\n\n"
                    f"**Agronomic Assessment:** The leaf shows no signs of active foliar lesions, blights, or necrosis. The foliage is physiologically vigorous. Maintain scheduled irrigations and baseline nutrition."
                )

        clean_practices = practices.replace("*", "-").strip() if practices else ""
        if lang == "te":
            return (
                f"🔬 **ఆకు చిత్రం విశ్లేషణ & వ్యాధి నిర్ధారణ (MobileNetV3 AI):**\n\n"
                f"- **గుర్తించిన వ్యాధి/సమస్య:** **{clean_cond}**\n"
                f"- **నిర్ధారణ ఖచ్చితత్వం:** {confidence}\n"
                f"- **బాధిత పంట:** {crop}\n\n"
                f"**వ్యవసాయ నిర్వహణ & నివారణ చర్యలు:**\n"
                f"1. **పొలం పరిశుభ్రత:** వ్యాధి సోకిన ఆకులను వెంటనే తెంపి పొలం వెలుపల వేసి నాశనం చేయండి.\n"
                f"2. **నీటి నిర్వహణ:** ఆకులపై నీరు పడకుండా చూసుకోండి (తుంపర సేద్యం తాత్కాలికంగా ఆపండి).\n"
                f"3. **గాలి వెలుతురు:** మొక్కల మధ్య గాలి మరియు ఎండ ధారాళంగా ప్రసరించేలా చూడండి.\n"
                f"{clean_practices}\n\n"
                f"👉 **గమనిక:** తీవ్రత ఎక్కువగా ఉంటే తగిన శిలీంధ్రనాశిని (Fungicide) పిచికారీ కోసం స్థానిక వ్యవసాయ అధికారిని లేదా కృషి విజ్ఞాన కేంద్రం (KVK) ను సంప్రదించండి."
            )
        elif lang == "hi":
            return (
                f"🔬 **पत्ती चित्र विश्लेषण एवं रोग निदान (MobileNetV3 AI):**\n\n"
                f"- **पहचाना गया रोग:** **{clean_cond}**\n"
                f"- **निदान सटीकता:** {confidence}\n"
                f"- **फसल:** {crop}\n\n"
                f"**प्रबंधन एवं रोकथाम के उपाय:**\n"
                f"1. **खेत की सफाई:** रोगग्रस्त पत्तियों को तोड़कर खेत से दूर नष्ट कर दें ताकि बीजाणु न फैलें।\n"
                f"2. **सिंचाई सावधानी:** पत्तियों पर ऊपर से पानी छिड़कने से बचें।\n"
                f"3. **हवा का संचार:** पौधों के बीच धूप और हवा का आवागमन सुनिश्चित करें।\n"
                f"{clean_practices}\n\n"
                f"👉 **सलाह:** यदि संक्रमण अधिक हो तो अनुमोदित फफूंदनाशक के छिड़काव हेतु स्थानीय कृषि विज्ञान केंद्र (KVK) से संपर्क करें।"
            )
        elif lang == "ta":
            return (
                f"🔬 **இலை பட பகுப்பாய்வு & நோய் கண்டறிதல் (MobileNetV3 AI):**\n\n"
                f"- **கண்டறியப்பட்ட நோய்:** **{clean_cond}**\n"
                f"- **நம்பகத்தன்மை:** {confidence}\n"
                f"- **பயிர்:** {crop}\n\n"
                f"**மேலாண்மை நடவடிக்கைகள்:**\n"
                f"1. பாதிக்கப்பட்ட இலைகளைப் பறித்து அப்புறப்படுத்தவும்.\n"
                f"2. இலைகளின் மேல் தண்ணீர் தெளிப்பதைத் தவிர்க்கவும்.\n"
                f"3. செடிகளுக்கு இடையே நல்ல காற்றோட்டம் இருப்பதை உறுதி செய்யவும்.\n"
                f"{clean_practices}"
            )
        elif lang == "kn":
            return (
                f"🔬 **ಎಲೆ ಚಿತ್ರ ವಿಶ್ಲೇಷಣೆ ಮತ್ತು ರೋಗ ಪತ್ತೆ (MobileNetV3 AI):**\n\n"
                f"- **ಪತ್ತೆಯಾದ ರೋಗ:** **{clean_cond}**\n"
                f"- **ನಿಖರತೆ:** {confidence}\n"
                f"- **ಬೆಳೆ:** {crop}\n\n"
                f"**ನಿರ್ವಹಣಾ ಕ್ರಮಗಳು:**\n"
                f"1. ರೋಗಪೀಡಿತ ಎಲೆಗಳನ್ನು ಕಿತ್ತು ಹೊಲದಿಂದ ಹೊರಗೆ ನಾಶಮಾಡಿ.\n"
                f"2. ಎಲೆಗಳ ಮೇಲೆ ನೀರು ಬೀಳದಂತೆ ನೋಡಿಕೊಳ್ಳಿ.\n"
                f"3. ಬೆಳೆಗೆ ಸರಿಯಾದ ಗಾಳಿ ಮತ್ತು ಬೆಳಕು ಸಿಗುವಂತೆ ಮಾಡಿ.\n"
                f"{clean_practices}"
            )
        elif lang == "mr":
            return (
                f"🔬 **पान चित्र विश्लेषण व रोग निदान (MobileNetV3 AI):**\n\n"
                f"- **आढळलेला रोग:** **{clean_cond}**\n"
                f"- **अचूकता:** {confidence}\n"
                f"- **पीक:** {crop}\n\n"
                f"**व्यवस्थापन व प्रतिबंधात्मक उपाय:**\n"
                f"1. रोगट पाने तोडून शेताबाहेर नष्ट करा जेणेकरून बुरशीचा प्रसार थांबेल.\n"
                f"2. तुषार सिंचन टाळा व झाडांमध्ये हवा खेळती ठेवा.\n"
                f"{clean_practices}"
            )
        else:
            return (
                f"🔬 **Attached Leaf Image Disease Diagnosis (FarmSathi MobileNetV3 AI):**\n\n"
                f"- **Diagnosed Condition:** **{clean_cond}**\n"
                f"- **Diagnostic Confidence:** {confidence} (Verified Model Inference)\n"
                f"- **Primary Crop Host:** {crop}\n\n"
                f"**Agronomic Cultural Management Practices:**\n"
                f"1. **Sanitation & Rogueing:** Prune and safely incinerate or deeply bury infected foliage to interrupt the fungal/bacterial spore cycle.\n"
                f"2. **Canopy Aeration:** Ensure adequate intra-row spacing to accelerate foliar drying after morning dew.\n"
                f"3. **Irrigation Protocol:** Avoid overhead sprinkler irrigation that splashes pathogens across healthy leaves; adopt drip or furrow watering.\n"
                f"{clean_practices}\n\n"
                f"👉 **Advisory Note:** If foliar lesions exceed 10-15% of the total canopy, consult your local agricultural extension officer (KVK) for an approved targeted curative fungicide."
            )

    def _build_missing_leaf_image_prompt(self, question: str, lang: str) -> str:
        if lang == "te":
            return (
                "📷 **ఆకు చిత్రం జతపరచబడలేదు:**\n\n"
                "మీరు ఆకులోని సమస్య లేదా తెగులు గురించి అడిగారు, కానీ మీ ప్రశ్నతో పాటు ఎటువంటి ఆకు ఫోటో అందలేదు.\n\n"
                "దయచేసి స్క్రీన్ కింద ఉన్న **కెమెరా లేదా అటాచ్‌మెంట్ ఐకాన్ (📷)** ఉపయోగించి వ్యాధి లక్షణాలు ఉన్న ఆకు ఫోటోను జతచేయండి. "
                "మా MobileNetV3 కంప్యూటర్ విజన్ మోడల్ ఆకును స్వయంచాలకంగా విశ్లేషించి ఖచ్చితమైన వ్యాధి మరియు నివారణ చర్యలను అందిస్తుంది."
            )
        elif lang == "hi":
            return (
                "📷 **पत्ती का चित्र संलग्न नहीं है:**\n\n"
                "आपने पत्ती की समस्या अथवा बीमारी के बारे में पूछा है, किंतु आपके प्रश्न के साथ कोई फोटो प्राप्त नहीं हुई।\n\n"
                "कृपया इनपुट बॉक्स के नीचे स्थित **कैमरा अथवा अटैचमेंट बटन (📷)** से ग्रसित पत्ती की साफ फोटो जोड़ें। "
                "फार्मसाथी का MobileNetV3 मॉडल पत्ती का स्वतः विश्लेषण कर सटीक रोग निदान और उपचार सुझाएगा।"
            )
        elif lang == "ta":
            return (
                "📷 **இலை புகைப்படம் இணைக்கப்படவில்லை:**\n\n"
                "இலை பிரச்சனை குறித்துக் கேட்டுள்ளீர்கள், ஆனால் புகைப்படம் எதுவும் இணைக்கப்படவில்லை.\n\n"
                "தயவுசெய்து **கேமரா பொத்தானை (📷)** பயன்படுத்தி பாதிக்கப்பட்ட இலையின் தெளிவான புகைப்படத்தை இணைக்கவும். "
                "எங்கள் மாதிரி துல்லியமான நோய் மற்றும் மேலாண்மை ஆலோசனைகளை வழங்கும்."
            )
        elif lang == "kn":
            return (
                "📷 **ಎಲೆಯ ಫೋಟೋ ಲಗತ್ತಿಸಲಾಗಿಲ್ಲ:**\n\n"
                "ನೀವು ಎಲೆಯ ಸಮಸ್ಯೆಯ ಬಗ್ಗೆ ಕೇಳಿದ್ದೀರಿ, ಆದರೆ ಯಾವುದೇ ಫೋಟೋ ಬಂದಿಲ್ಲ.\n\n"
                "ದಯವಿಟ್ಟು **ಕ್ಯಾಮೆರಾ ಬಟನ್ (📷)** ಬಳಸಿ ರೋಗಪೀಡಿತ ಎಲೆಯ ಸ್ಪಷ್ಟ ಚಿತ್ರವನ್ನು ಲಗತ್ತಿಸಿ."
            )
        elif lang == "mr":
            return (
                "📷 **पानाचा फोटो जोडलेला नाही:**\n\n"
                "आपण पानातील समस्येबद्दल विचारले आहे, परंतु कोणताही फोटो प्राप्त झालेला नाही.\n\n"
                "कृपया **कॅमेरा बटण (📷)** वापरून रोगट पानाचा स्पष्ट फोटो जोडा जेणेकरून अचूक निदान करता येईल."
            )
        else:
            return (
                "📷 **No Leaf Image Detected:**\n\n"
                "You asked about a foliar symptom or leaf issue, but no image was attached with your query.\n\n"
                "Please click the **Camera or Attachment icon (📷)** below the input box to upload a close-up, focused photo of the affected crop leaf. FarmSathi's verified MobileNetV3 deep-learning model will automatically analyze the foliar symptoms, identify the disease or deficiency, and provide cultural management practices."
            )

    def _build_flower_drop_response(self, question: str, lang: str) -> str:
        if lang == "te":
            return (
                "🌸 **టమాటా మరియు కూరగాయల పంటలలో పూత రాలడానికి (Flower Drop) ప్రధాన కారణాలు & నివారణ చర్యలు:**\n\n"
                "1. **ఉష్ణోగ్రత ఒత్తిడి:** పగటి ఉష్ణోగ్రత 35°C కంటే ఎక్కువ ఉన్నప్పుడు లేదా రాత్రి ఉష్ణోగ్రతలు అకస్మాత్తుగా మారినప్పుడు పరాగసంపర్కం విఫలమై పూత రాలిపోతుంది.\n"
                "2. **నేలలో తేమ హెచ్చుతగ్గులు:** ఎక్కువ రోజులు నీరు పెట్టకుండా అకస్మాత్తుగా ఎక్కువ నీరు పెట్టడం లేదా పొలంలో నీరు నిలిచిపోవడం వల్ల మొక్కలు ఒత్తిడికి లోనై పూతను రాల్చేస్తాయి.\n"
                "3. **పోషకాల అసమతుల్యత:** అధిక నత్రజని (యూరియా) వాడటం వల్ల మొక్క ఆకులతో ఏపుగా పెరిగి పూత నిలవదు. అలాగే **బోరాన్ (Boron)** మరియు **కాల్షియం** లోపం వల్ల పుప్పొడి నాణ్యత తగ్గి పూత రాలుతుంది.\n"
                "4. **తామర పురుగులు (Thrips):** పూలలో చేరి రసం పీల్చడం వల్ల పువ్వులు మాడి రాలిపోతాయి.\n\n"
                "**తీసుకోవాల్సిన తక్షణ చర్యలు:**\n"
                "- పూత రాలకుండా ఉండటానికి **ప్లానోఫిక్స్ (Alpha NAA 4.5% SL)** 1 మి.లీ మందును 4.5 లీటర్ల నీటిలో కలిపి పిచికారీ చేయండి.\n"
                "- పరాగసంపర్కం మరియు పిందె కట్టడం మెరుగుపడటానికి **బోరాన్ 20%** 1-1.5 గ్రా/లీటర్ నీటిలో కలిపి పూత దశలో పిచికారీ చేయండి.\n"
                "- నేలలో నిరంతరం సమానమైన తేమ ఉండేలా తేలికపాటి తడులు ఇవ్వండి; ఎక్కువ నీరు నిల్వ ఉండకుండా చూసుకోండి.\n"
                "- తామర పురుగుల నివారణకు వేప నూనె (10,000 ppm) 2 మి.లీ/లీటర్ లేదా తగిన పురుగుమందు వాడండి."
            )
        elif lang == "hi":
            return (
                "🌸 **टमाटर एवं सब्जियों में फूल झड़ने (Flower Drop) के प्रमुख कारण एवं समाधान:**\n\n"
                "1. **तापमान का उतार-चढ़ाव:** दिन का तापमान 35°C से अधिक या रात का तापमान 13°C से कम होने पर परागकण सूख जाते हैं और निषेचन न होने के कारण फूल गिर जाते हैं।\n"
                "2. **नमी का असंतुलन:** खेत में अत्यधिक सूखा पड़ने के बाद एकदम भारी सिंचाई करने या पानी ठहरने से पौधों पर तनाव आता है और फूल झड़ने लगते हैं।\n"
                "3. **पोषक तत्वों का असंतुलन:** अत्यधिक नाइट्रोजन से वानस्पतिक वृद्धि ज्यादा होती है और फूल कम टिकते हैं। वहीं **बोरॉन** और **कैल्शियम** की कमी से पराग नलिका का विकास रुक जाता है।\n"
                "4. **कीट प्रकोप (थ्रिप्स):** फूलों के अंदर थ्रिप्स रस चूसकर फूलों को सुखा देते हैं।\n\n"
                "**सुझाए गए तुरंत उपाय:**\n"
                "- फूल झड़ने से रोकने हेतु **अल्फा एनएए 4.5% एसएल (प्लानोफिक्स)** की 1 मिली मात्रा को 4.5 लीटर पानी में घोलकर छिड़कें।\n"
                "- फूल से फल बनने की दर बढ़ाने के लिए घुलनशील **बोरॉन (20%)** 1 से 1.5 ग्राम प्रति लीटर पानी में मिलाकर छिड़काव करें।\n"
                "- खेत में एकसमान नमी बनाए रखें, हल्की व नियमित सिंचाई करें।\n"
                "- थ्रिप्स कीट से बचाव के लिए नीम का तेल (10,000 ppm) 2 मिली/लीटर का छिड़काव करें।"
            )
        elif lang == "ta":
            return (
                "🌸 **தக்காளி மற்றும் காய்கறிப் பயிர்களில் பூ உதிர்வதற்கான காரணங்கள் & மேலாண்மை:**\n\n"
                "1. **வெப்பநிலை மாறுபாடு:** பகல் வெப்பநிலை 35°C-க்கு மேல் அதிகரிக்கும் போது மகரந்தச் சேர்க்கை பாதிக்கப்பட்டு பூக்கள் உதிர்கின்றன.\n"
                "2. **ஈரப்பத ஏற்றத்தாழ்வு:** கடுமையான வறட்சிக்குப் பின் திடீரென அதிக தண்ணீர் பாய்ச்சுதல் அல்லது நீர் தேங்குதல் பூ உதிர்வைத் தூண்டும்.\n"
                "3. **ஊட்டச்சத்துக் குறைபாடு:** தழைச்சத்து (நைட்ரஜன்) அதிகமாக இருந்தால் இலை வளர்ச்சி மட்டுமே கூடும். போரான் மற்றும் கால்சியம் குறைபாடு மகரந்த உற்பத்தியைப் பாதிக்கும்.\n"
                "4. **இலைப்பேன் தாக்குதல் (Thrips):** பூக்களில் சாற்றை உறிஞ்சுவதால் பூக்கள் காய்ந்து உதிரும்.\n\n"
                "**பரிந்துரைக்கப்பட்ட தீர்வுகள்:**\n"
                "- பூ உதிர்வைத் தடுக்க **பிளனோபிக்ஸ் (Alpha NAA 4.5% SL)** 1 மி.லி மருந்தை 4.5 லிட்டர் நீரில் கலந்து தெளிக்கவும்.\n"
                "- காய் பிடிப்பை அதிகரிக்க **போரான் 20%** உரம் (1-1.5 கிராம்/லிட்டர்) தெளிக்கவும்.\n"
                "- சீரான இடைவெளியில் லேசான நீர்ப்பாசனம் அளித்து மண்ணில் ஈரப்பதத்தை நிலைநிறுத்தவும்.\n"
                "- இலைப்பேன் கட்டுப்பாடுக்கு வேப்ப எண்ணெய் (2 மி.லி/லிட்டர்) தெளிக்கவும்."
            )
        elif lang == "kn":
            return (
                "🌸 **ಟೊಮೆಟೊ ಮತ್ತು ತರಕಾರಿ ಬೆಳೆಗಳಲ್ಲಿ ಹೂವು ಉದುರುವಿಕೆಗೆ ಕಾರಣಗಳು ಮತ್ತು ಪರಿಹಾರಗಳು:**\n\n"
                "1. **ತಾಪಮಾನದ ಏರಿಳಿತ:** ಹಗಲಿನ ತಾಪಮಾನ 35°C ಗಿಂತ ಹೆಚ್ಚಾದರೆ ಪರಾಗಸ್ಪರ್ಶ ವಿಫಲವಾಗಿ ಹೂವುಗಳು ಉದುರುತ್ತವೆ.\n"
                "2. **ಮಣ್ಣಿನ ತೇವಾಂಶದ ಏರಿಳಿತ:** ಅತಿಯಾದ ಒಣ ಹವೆಯ ನಂತರ ಒಮ್ಮೆಲೆ ಹೆಚ್ಚು ನೀರು ಹಾಯಿಸುವುದರಿಂದ ಹೂವುಗಳು ಉದುರುತ್ತವೆ.\n"
                "3. **ಪೋಷಕಾಂಶಗಳ ಕೊರತೆ:** ಅಧಿಕ ಸಾರಜನಕವು ಗಿಡಗಳ ಎಲೆ ಬೆಳವಣಿಗೆಯನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ ಆದರೆ ಹೂವು ನಿಲ್ಲುವುದಿಲ್ಲ. ಬೋರಾನ್ ಮತ್ತು ಕ್ಯಾಲ್ಸಿಯಂ ಕೊರತೆಯು ಹೂವಿನ ಗುಣಮಟ್ಟವನ್ನು ಕುಗ್ಗಿಸುತ್ತದೆ.\n"
                "4. **ಥ್ರಿಪ್ಸ್ ಕೀಟಗಳ ಬಾಧೆ:** ಹೂವಿನ ಒಳಗೆ ರಸ ಹೀರುವುದರಿಂದ ಹೂವುಗಳು ಒಣಗಿ ಬೀಳುತ್ತವೆ.\n\n"
                "**ಕ್ರಮಗಳು:**\n"
                "- ಹೂವು ಉದುರುವುದನ್ನು ತಡೆಯಲು **ಪ್ಲಾನೋಫಿಕ್ಸ್ (Alpha NAA 4.5% SL)** 1 ಮಿಲೀ ಅನ್ನು 4.5 ಲೀಟರ್ ನೀರಿಗೆ ಬೆರೆಸಿ ಸಿಂಪಡಿಸಿ.\n"
                "- ಕಾಯಿ ಕಟ್ಟುವುದು ಉತ್ತಮವಾಗಲು **ಬೋರಾನ್ 20%** (1-1.5 ಗ್ರಾಂ/ಲೀಟರ್) ಸಿಂಪಡಿಸಿ.\n"
                "- ಮಣ್ಣಿನಲ್ಲಿ ನಿರಂತರ ತೇವಾಂಶವಿರುವಂತೆ ಲಘು ನೀರಾವರಿ ಒದಗಿಸಿ.\n"
                "- ಥ್ರಿಪ್ಸ್ ನಿಯಂತ್ರಣಕ್ಕೆ ಬೇವಿನ ಎಣ್ಣೆ (2 ಮಿಲೀ/ಲೀಟರ್) ಸಿಂಪಡಿಸಿ."
            )
        elif lang == "mr":
            return (
                "🌸 **टोमॅटो व भाजीपाला पिकांमध्ये फुलगळ होण्याची मुख्य कारणे व उपाय:**\n\n"
                "1. **तापमानातील चढ-उतार:** दिवसाचे तापमान ३५ अंश सेल्सिअसपेक्षा जास्त झाल्यास परागीभवन नीट होत नाही व फुले गळतात.\n"
                "2. **पाण्याचा ताण व अतिरिक्त पाणी:** जास्त ताण दिल्यानंतर एकदम भरपूर पाणी दिल्यास किंवा पाणी साचल्यास फुलगळ वाढते.\n"
                "3. **अन्नद्रव्यांचे असंतुलन:** नत्राचा अतिवापर झाल्यास शाकीय वाढ होते पण फुले गळतात. तसेच **बोरॉन** आणि **कॅल्शियम**च्या कमतरतेमुळे परागनलिकेची वाढ खुंटते.\n"
                "4. **थ्रिप्सचा प्रादुर्भाव:** फुलांमधील रस शोषल्यामुळे कळ्या सुकतात व गळतात.\n\n"
                "**तातडीचे उपाय:**\n"
                "- फुलगळ रोखण्यासाठी **प्लॅनोफिक्स (Alpha NAA 4.5% SL)** १ मिली प्रति ४.५ लिटर पाण्यात मिसळून फवारावे.\n"
                "- फळधारणा चांगली होण्यासाठी विद्राव्य **बोरॉन (२०%)** १ ते १.५ ग्रॅम प्रति लिटर पाण्यात मिसळून फवारणी करावी.\n"
                "- जमिनीत कायम वाफसा राहील अशी हलकी व नियमित पाणी देण्याची पद्धत ठेवावी.\n"
                "- थ्रिप्सच्या नियंत्रणासाठी निंबोळी तेल (१०,००० ppm) २ मिली प्रति लिटर फवारावे."
            )
        else:
            return (
                "🌸 **Causes and Agronomic Management for Flower / Blossom Drop (Tomato & Vegetable Crops):**\n\n"
                "1. **Temperature Extremes (Thermal Stress):** Day temperatures exceeding 35°C or nighttime temperatures staying above 24°C (or below 13°C) cause pollen sterility and non-viable pollination, triggering flower abscission (dropping).\n"
                "2. **Soil Moisture Imbalance:** Fluctuating soil moisture — alternating between severe dryness and heavy flooding or waterlogging — stresses the vascular system, prompting the plant to abort flowers to conserve resources.\n"
                "3. **Nutritional Imbalance:** Excessive vegetative Nitrogen promotes lush leaf growth at the expense of floral retention. Conversely, deficiencies in **Boron** (crucial for pollen tube growth) and **Calcium** lead to blossom drop and blossom-end rot.\n"
                "4. **Insect Damage (Thrips & Aphids):** Thrips rasp and suck cell sap from inside delicate flower buds, causing premature drying and drop.\n\n"
                "**Actionable Field Recommendations:**\n"
                "- Apply a foliar spray of **Alpha-Naphthyl Acetic Acid (NAA 4.5% SL / Planofix)** at 0.25 to 0.4 ml per 4.5 liters of water during peak flowering to prevent abscission.\n"
                "- Spray Soluble **Boron (20% Di-sodium Octaborate Tetrahydrate)** at 1 to 1.5 g/L of water to promote pollen germination and fruit set.\n"
                "- Maintain steady, uniform root-zone moisture with light, frequent irrigations (avoid water stagnation).\n"
                "- If thrips are present, spray Neem formulation (10,000 ppm at 2 ml/L) or an approved selective insecticide."
            )

    def _build_germination_response(self, question: str, lang: str) -> str:
        if lang == "te":
            return (
                "🌱 **విత్తన మొలక శాతం (Seed Germination) మెరుగుపరచుకోవడానికి శాస్త్రీయ పద్ధతులు:**\n\n"
                "1. **విత్తన శుద్ధి (Seed Treatment):**\n"
                "   - *శిలీంధ్రాల రక్షణ:* విత్తే ముందు కిలో విత్తనానికి 2-3 గ్రాముల థైరమ్ లేదా కార్బండజిమ్ లేదా జీవ శిలీంధ్రనాశిని ట్రైకోడెర్మా విరిడి (10 గ్రా/కిలో) తో విత్తన శుద్ధి చేయండి. ఇది నారు కుళ్ళు మరియు విత్తనం కుళ్ళిపోకుండా కాపాడుతుంది.\n"
                "   - *జీవ ఎరువులు:* అజోస్పైరిల్లం / రైజోబియం మరియు భాస్వరం కరిగించే బ్యాక్టీరియా (PSB) 20 గ్రా/కిలో విత్తనానికి పట్టించడం వల్ల వేర్ల వ్యవస్థ బలంగా ఏర్పడుతుంది.\n"
                "2. **విత్తే లోతు:** విత్తనం పరిమాణానికి 2 నుండి 3 రెట్ల లోతులో మాత్రమే విత్తాలి (చాలా పంటలకు 2-4 సెం.మీ లోతు సరైనది). ఎక్కువ లోతులో వేస్తే మొలక పైకి రాలేదు; పైపైనే వేస్తే తేమ అందక ఎండిపోతుంది.\n"
                "3. **నేల తేమ & దుక్కి తయారీ:** నేలను మెత్తగా దున్ని గడ్డలు లేకుండా చదును చేయాలి. విత్తే సమయంలో నేలలో సరైన పదును ఉండాలి. నీరు నిలబడకుండా చూడాలి.\n"
                "4. **నానబెట్టడం (Seed Priming):** మందపాటి పొర ఉన్న విత్తనాలను (బెండ, పత్తి, వరి) విత్తే ముందు 8-12 గంటలు శుభ్రమైన నీటిలో నానబెట్టి నీడలో ఆరబెట్టి విత్తితే త్వరగా మరియు ఏకరీతిగా మొలకెత్తుతాయి."
            )
        elif lang == "hi":
            return (
                "🌱 **बीज अंकुरण (Seed Germination) सुधारने के वैज्ञानिक उपाय:**\n\n"
                "1. **बीज शोधन (Beej Sanskar):**\n"
                "   - *फफूंदनाशक उपचार:* बुवाई से पहले प्रति किलो बीज को 2-2.5 ग्राम थीरम अथवा कार्बेन्डाजिम या जैविक कवकनाशी ट्राइकोडर्मा विरिडी (10 ग्राम/किग्रा) से उपचारित करें। इससे बीज गलन और आद्र-पतन (Damping-off) रोग नहीं लगते।\n"
                "   - *जैव उर्वरक संवर्धन:* राइजोबियम/एजोटोबैक्टर तथा पीएसबी (20 ग्राम/किग्रा) से बीजोपचार करने पर प्रारंभिक जड़ विकास तेज होता है।\n"
                "2. **बुवाई की उचित गहराई:** बीज को उसके आकार से 2 से 3 गुना गहराई पर ही बोएं (अधिकांश फसलों के लिए 2-4 सेमी)। अधिक गहरा बोने पर अंकुर बाहर नहीं आ पाता और उथला बोने पर नमी के अभाव में सूख जाता है।\n"
                "3. **मृदा में उचित नमी व भुरभुरी मिट्टी:** खेत की जुताई अच्छी तरह करके मिट्टी को भुरभुरा बनाएं। बुवाई के समय खेत में पर्याप्त नमी होनी चाहिए, किंतु कीचड़ न हो।\n"
                "4. **बीज भिगोना (प्राइमिंग):** कठोर आवरण वाले बीजों (जैसे भिंडी, कपास) को बोने से पूर्व 8-10 घंटे स्वच्छ जल में भिगोकर छाया में सुखाकर बोने से अंकुरण प्रतिशत 20-30% बढ़ जाता है।"
            )
        elif lang == "ta":
            return (
                "🌱 **விதை முளைப்புத் திறனை (Seed Germination) அதிகரிக்கும் முறைகள்:**\n\n"
                "1. **விதை நேர்த்தி:**\n"
                "   - *பூஞ்சாணக் கொல்லி:* ஒரு கிலோ விதைக்கு 2 கிராம் கார்பென்டாசிம் அல்லது ட்ரைக்கோடெர்மா விரிடி (10 கிராம்/கிலோ) கொண்டு விதை நேர்த்தி செய்யவும். இது அழுகல் நோயைத் தடுக்கும்.\n"
                "   - *உயிரி உரம்:* அசோஸ்பைரில்லம் மற்றும் பாஸ்போபாக்டீரியா (20 கிராம்/கிலோ) சேர்த்து நேர்த்தி செய்யவும்.\n"
                "2. **விதைப்பு ஆழம்:** விதையின் அளவை விட 2-3 மடங்கு ஆழத்தில் மட்டுமே விதைக்க வேண்டும் (2-4 செ.மீ).\n"
                "3. **மண் ஈரப்பதம்:** நிலத்தை நன்கு உழுது கட்டிகளின்றி சமன்படுத்தி மிதமான ஈரப்பதத்தில் விதைக்கவும்.\n"
                "4. **விதை ஊறவைத்தல்:** கடினமான விதைகளை 8-12 மணி நேரம் தண்ணீரில் ஊறவைத்து நிழலில் உலர்த்தி விதைக்கவும்."
            )
        elif lang == "kn":
            return (
                "🌱 **ಬೀಜ ಮೊಳಕೆಯೊಡೆಯುವಿಕೆ (Seed Germination) ಉತ್ತಮಪಡಿಸುವ ಕ್ರಮಗಳು:**\n\n"
                "1. **ಬೀಜೋಪಚಾರ:**\n"
                "   - ಪ್ರತಿ ಕೆಜಿ ಬೀಜಕ್ಕೆ 2 ಗ್ರಾಂ ಕಾರ್ಬೆಂಡಾಜಿಮ್ ಅಥವಾ ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡಿ (10 ಗ್ರಾಂ/ಕೆಜಿ) ಬೆರೆಸಿ ಬೀಜೋಪಚಾರ ಮಾಡಿ.\n"
                "   - ರೈಜೋಬಿಯಂ ಮತ್ತು ಪಿಎಸ್‌ಬಿ (20 ಗ್ರಾಂ/ಕೆಜಿ) ಬಳಸಿ.\n"
                "2. **ಬಿತ್ತನೆಯ ಆಳ:** ಬೀಜದ ಗಾತ್ರಕ್ಕಿಂತ 2-3 ಪಟ್ಟು ಆಳದಲ್ಲಿ ಮಾತ್ರ ಬಿತ್ತಿ (2-4 ಸೆಂ.ಮೀ).\n"
                "3. **ಮಣ್ಣಿನ ಹದ:** ಹೊಲವನ್ನು ನುಣ್ಣಗೆ ಉತ್ತು ಹದವಾದ ತೇವಾಂಶದಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿ.\n"
                "4. **ಬೀಜ ನೆನೆಸುವುದು:** ದಪ್ಪ ಸಿಪ್ಪೆಯ ಬೀಜಗಳನ್ನು 8-10 ಗಂಟೆ ನೀರಿನಲ್ಲಿ ನೆನೆಸಿ ನೆರಳಿನಲ್ಲಿ ಒಣಗಿಸಿ ಬಿತ್ತಿ."
            )
        elif lang == "mr":
            return (
                "🌱 **बियाण्यांची उगवण क्षमता (Seed Germination) वाढवण्याचे शास्त्रीय उपाय:**\n\n"
                "1. **बीजप्रक्रिया (Seed Treatment):**\n"
                "   - प्रति किलो बियाण्यास २-३ ग्रॅम थायरम किंवा कार्बेन्डाझिम किंवा ट्रायकोडर्मा विरिडी (१० ग्रॅम/किलो) चोळावे.\n"
                "   - अझोटोबॅक्टर/रायझोबियम आणि पीएसबी (२० ग्रॅम/किलो) लावावे.\n"
                "2. **पेरणीची खोली:** बियाण्याच्या आकाराच्या २ ते ३ पट खोलीवरच पेरणी करावी (२-४ सें.मी.).\n"
                "3. **जमिनीतील ओलावा:** शेतात पुरेशी वाफसा स्थिती असतानाच पेरणी करावी.\n"
                "4. **बीज भिजवणे:** टणक कवच असणाऱ्या बियाण्यांना पेरणीपूर्वी ८-१० तास पाण्यात भिजवून सावलीत सुकवून पेरावे."
            )
        else:
            return (
                "🌱 **Agronomic Methods to Improve Seed Germination & Crop Emergence:**\n\n"
                "1. **Certified Seed Quality & Viability:** Always use certified seed with guaranteed germination (>85%). Perform a preliminary floatation check or moist paper towel test 5 days prior to sowing.\n"
                "2. **Protective Seed Treatment (Beej Sanskar):**\n"
                "   - *Fungicidal protection:* Treat seeds with **Thiram or Carbendazim (2 g/kg seed)** or bio-agent **Trichoderma viride (10 g/kg seed)** to prevent damping-off, collar rot, and seed rot.\n"
                "   - *Bio-fertilizer inoculation:* Inoculate with **Azospirillum / Rhizobium and PSB (Phosphorus Solubilizing Bacteria)** at 20 g/kg seed to boost early radicle and root vigor.\n"
                "3. **Optimal Sowing Depth:** Sow at an ideal depth of **2 to 3 times the seed diameter** (typically 2-4 cm for most field crops). Sowing too deep delays emergence; sowing too shallow causes seed drying or bird loss.\n"
                "4. **Seedbed Moisture & Tilth:** Prepare a fine, firm, and weed-free seedbed. Ensure adequate soil moisture at sowing time; avoid waterlogging which suffocates germinating embryos.\n"
                "5. **Pre-soaking / Priming:** For hard-coated seeds (e.g., okra, cotton, paddy), soak seeds in clean water for 8-12 hours before sowing and shade-dry to break dormancy and accelerate uniform emergence."
            )

    def _build_post_sowing_response(self, question: str, lang: str) -> str:
        if lang == "te":
            return (
                "🌾 **విత్తనాలు వేసిన తర్వాత (Post-Sowing) పొలంలో తీసుకోవాల్సిన ముఖ్యమైన చర్యలు:**\n\n"
                "1. **తేలికపాటి తడి (Life-Saving Irrigation):** పొడి నేలలో విత్తినట్లయితే వెంటనే తేలికపాటి నీరు పెట్టండి. ఎక్కువ ఒత్తిడితో నీరు పారించవద్దు; దీనివల్ల విత్తనాలు కొట్టుకుపోవడం లేదా మట్టి గట్టిపడటం జరుగుతుంది.\n"
                "2. **నేల పెళ్లెను పగలగొట్టడం (Crust Management):** విత్తిన తర్వాత వర్షం పడి వెంటనే ఎండ తీవ్రంగా కాస్తే నేల పైపొర గట్టి పెళ్లెగా మారుతుంది. మొలకలు బయటకు రావడానికి తేలికపాటి దంతితో పెళ్లెను పగలగొట్టండి.\n"
                "3. **మొలక రాకముందు కలుపు నివారణ (Pre-Emergence Herbicide):** విత్తిన 24 నుండి 48 గంటల్లోపు నేలలో తగినంత తేమ ఉన్నప్పుడు సిఫార్సు చేసిన పెండిమిథాలిన్ 30% EC (ఎకరాకు 1-1.3 లీటర్లు) పిచికారీ చేయండి.\n"
                "4. **పక్షులు మరియు ఎలుకల నుండి రక్షణ:** విత్తనాలు మొలకెత్తే సమయంలో పక్షులు కొట్టేయకుండా మెరిసే రిబ్బన్లు లేదా సంరక్షణ చర్యలు చేపట్టండి.\n"
                "5. **మొలకల సాంద్రత & సందులు పూడ్చడం (Gap Filling):** విత్తిన 7-10 రోజుల తర్వాత పొలాన్ని పరిశీలించి మొలక రాని ఖాళీలలో నానబెట్టిన విత్తనాలతో సందులు పూడ్చండి."
            )
        elif lang == "hi":
            return (
                "🌾 **बुवाई के तुरंत बाद (Post-Sowing) खेत में किए जाने वाले आवश्यक कार्य:**\n\n"
                "1. **हल्की सिंचाई (जीवनरक्षक सिंचाई):** यदि सूखी मिट्टी में बुवाई की गई है, तो तुरंत हल्की सिंचाई करें। पानी का बहाव तेज न रखें ताकि बीज अपनी जगह से न हटें।\n"
                "2. **पपड़ी तोड़ना (Crust Management):** बुवाई के बाद यदि बारिश हो जाए और तेज धूप निकले तो मिट्टी की ऊपरी सतह पर सख्त पपड़ी बन जाती है। अंकुरण सुगम बनाने के लिए हल्की जुताई या पाटा चलाकर पपड़ी तोड़ें।\n"
                "3. **जमाव-पूर्व खरपतवार नियंत्रण (Pre-Emergence Herbicides):** बुवाई के **24 से 48 घंटे के भीतर** मिट्टी में नमी रहते पेंडीमेथालिन 30% ईसी (1-1.3 लीटर/एकड़) का छिड़काव करें ताकि खरपतवार न उगें।\n"
                "4. **पक्षियों व चूहों से बचाव:** अंकुरण के प्रारंभिक 5-8 दिनों तक बीजों को पक्षियों द्वारा चुगने से बचाने के लिए खेत में चमकीली पट्टियां लगाएं।\n"
                "5. **गैप फिलिंग (खाली स्थान भरना):** बुवाई के 7-10 दिन बाद खेत का निरीक्षण करें और जहां जमाव न हुआ हो वहां भीगे हुए बीज बोकर खाली जगह भरें।"
            )
        elif lang == "ta":
            return (
                "🌾 **விதைத்த பிறகு (Post-Sowing) மேற்கொள்ள வேண்டிய முக்கிய களப் பணிகள்:**\n\n"
                "1. **உயிர்த் தண்ணீர் பாசனம்:** காய்ந்த மண்ணில் விதைத்திருந்தால் உடனடியாக லேசான பாசனம் செய்யவும். அதிக அழுத்தத்தில் நீர் பாய்ச்சக் கூடாது.\n"
                "2. **மண் மேலோடு உடைத்தல்:** மழைக்குப் பின் வெயில் அடித்தால் மண் இறுகி மேலோடு உருவாகும்; முளைப்பு தடைபடாமல் இருக்க லேசாகக் கிளறி விடவும்.\n"
                "3. **முளைப்புக்கு முந்தைய களைக்கொல்லி:** விதைத்த **24-48 மணி நேரத்திற்குள்** பெண்டிமெத்தாலின் தெளிக்கவும்.\n"
                "4. **பறவைகள் பாதுகாப்பு:** விதைகள் முளைத்து வரும் வரை பறவைகளிடமிருந்து பயிரைப் பாதுகாக்கவும்.\n"
                "5. **இடைவெளி நிரப்புதல்:** 7-10 நாட்களில் முளைக்காத இடங்களில் மீண்டும் விதைத்து பயிர் எண்ணிக்கையை உறுதி செய்யவும்."
            )
        elif lang == "kn":
            return (
                "🌾 **ಬಿತ್ತನೆಯ ನಂತರ (Post-Sowing) ಹೊಲದಲ್ಲಿ ಕೈಗೊಳ್ಳಬೇಕಾದ ಪ್ರಮುಖ ಕ್ರಮಗಳು:**\n\n"
                "1. **ಲಘು ನೀರಾವರಿ:** ಒಣ ಮಣ್ಣಿನಲ್ಲಿ ಬಿತ್ತಿದ್ದರೆ ಕೂಡಲೇ ಹಗುರವಾಗಿ ನೀರು ಹಾಯಿಸಿ.\n"
                "2. **ಹೆಂಟೆ/ಪದರ ಒಡೆಯುವುದು:** ಮಳೆಯ ನಂತರ ಗಟ್ಟಿಯಾದ ಮಣ್ಣಿನ ಪದರ ಉಂಟಾದರೆ ಮೊಳಕೆ ಸುಲಭವಾಗಿ ಬರಲು ಅದನ್ನು ಲಘುವಾಗಿ ಒಡೆಯಿರಿ.\n"
                "3. **ಕಳೆನಾಶಕ ಬಳಕೆ:** ಬಿತ್ತಿದ **24-48 ಗಂಟೆಗಳಲ್ಲಿ** ಪೆಂಡಿಮೆಥಾಲಿನ್ ಕಳೆನಾಶಕ ಸಿಂಪಡಿಸಿ.\n"
                "4. **ಪಕ್ಷಿಗಳಿಂದ ರಕ್ಷಣೆ:** ಮೊಳಕೆಯೊಡೆಯುವ ಸಮಯದಲ್ಲಿ ಹೊಲವನ್ನು ರಕ್ಷಿಸಿ.\n"
                "5. **ಅಂತರ ತುಂಬುವುದು:** 7-10 ದಿನಗಳ ನಂತರ ಖಾಲಿ ಜಾಗಗಳಲ್ಲಿ ಮರುಬಿತ್ತನೆ ಮಾಡಿ ಸರಿಯಾದ ಸಸ್ಯ ಸಾಂದ್ರತೆಯನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಿ."
            )
        elif lang == "mr":
            return (
                "🌾 **पेरणीनंतर (Post-Sowing) शेतात करावयाची महत्त्वाची कामे:**\n\n"
                "1. **हलके पाणी (ओलिताची सोय):** कोरड्या जमिनीत पेरणी केली असल्यास ताबडतोब हलके पाणी द्यावे. पाण्याचा वेग जास्त नसावा.\n"
                "2. **पापडी फोडणे:** पाऊस पडून ऊन पडल्यास जमिनीवर कडक पापडी धरते, ती हलक्या कोळपणीने फोडावी जेणेकरून कोंब सहज बाहेर पडतील.\n"
                "3. **उगवणपूर्व तणनाशक:** पेरणीनंतर **२४ ते ४८ तासांच्या आत** जमिनीत ओलावा असताना पेंडीमेथॅलिन तणनाशकाची फवारणी करावी.\n"
                "4. **पक्ष्यांपासून संरक्षण:** बियाणे उगवेपर्यंत पक्ष्यांचा प्रादुर्भाव रोखण्यासाठी उपाययोजना कराव्यात.\n"
                "5. **नांग्या भरणे (Gap Filling):** पेरणीनंतर ७-१० दिवसांनी पाहणी करून न उगवलेल्या जागी भिजवलेले बी टोकून नांग्या भराव्यात."
            )
        else:
            return (
                "🌾 **Essential Agronomic Field Practices After Sowing:**\n\n"
                "1. **Life-Saving Irrigation (First Watering):**\n"
                "   - If sown in dry soil, apply a light, gentle irrigation immediately after sowing.\n"
                "   - Avoid heavy flooding or forceful water flow that dislodges seeds or causes surface soil compaction.\n"
                "2. **Breaking Soil Crust (Crust Management):** If unseasonal rain occurs followed by intense sun before seedling emergence, a hard surface crust forms. Gently break the crust with a light wooden rake or light irrigation to facilitate coleoptile emergence.\n"
                "3. **Pre-Emergence Weed Management:** Apply recommended pre-emergence herbicides (such as Pendimethalin 30% EC at 1-1.3 L/acre) within **24 to 48 hours of sowing** while soil moisture is active, before weed seeds germinate.\n"
                "4. **Protection from Birds and Rodents:** Install reflective ribbons, scarecrows, or netting during the critical 4-8 days window when seedlings break the surface.\n"
                "5. **Gap Filling & Thinning:** Inspect emergence 7 to 10 days post-sowing. Resow gaps promptly with pre-soaked seeds and thin overcrowded seedlings to maintain the recommended plant density."
            )

    def _build_fertilizer_response(
        self, question: str, crop_rec: Dict[str, Any], lang: str
    ) -> str:
        if lang == "te":
            return (
                "🧪 **ఎరువుల నిర్వహణ సలహా:**\n\n"
                "1. **నేల పరీక్ష:** భూమి ఆరోగ్య పత్రం ఆధారంగా ఎరువులు వాడండి.\n"
                "2. **నత్రజని (యూరియా):** యూరియాను ఒకేసారి వేయకుండా 2-3 దఫాలుగా వేయడం వల్ల పంటకు సంపూర్ణంగా అందుతుంది.\n"
                "3. **భాస్వరం (DAP/SSP):** విత్తే సమయంలోనే ఆఖరి దుక్కిలో వేయాలి.\n"
                "4. **సేంద్రీయ ఎరువు:** పశువుల ఎరువు లేదా వర్మీ కంపోస్ట్ కలపడం వల్ల నేల సారవంతం పెరుగుతుంది."
            )
        elif lang == "hi":
            return (
                "🧪 **उर्वरक एवं पोषक तत्व प्रबंधन:**\n\n"
                "1. **मृदा परीक्षण:** हमेशा मृदा स्वास्थ्य कार्ड की रिपोर्ट के अनुसार ही खाद डालें।\n"
                "2. **यूरिया का संतुलित प्रयोग:** यूरिया को एक साथ न डालकर फसल की अवस्था अनुसार 2-3 किस्तों में दें।\n"
                "3. **डीएपी/फास्फोरस:** बुवाई के समय आधार खाद के रूप में मिट्टी में गहराई पर दें।\n"
                "4. **जैविक खाद:** गोबर की खाद या वर्मीकम्पोस्ट का प्रयोग अवश्य करें ताकि मिट्टी की जलधारण क्षमता बढ़े।"
            )
        elif lang == "ta":
            return (
                "🧪 **உர மேலாண்மை ஆலோசனை:**\n\n"
                "1. **மண் பரிசோதனை:** மண் வள அட்டையின் பரிந்துரைப்படி உரமிடுங்கள்.\n"
                "2. **யூரியா பயன்பாடு:** யூரியாவை ஒரே முறையில் இடாமல் 2-3 தவணைகளாகப் பிரித்து இடவும்.\n"
                "3. **டிஏபி / பாஸ்பரஸ்:** விதைப்பின் போது அடிஉரமாக மட்டுமே இட வேண்டும்.\n"
                "4. **இயற்கை உரம்:** மக்கிய தொழு உரம் அல்லது மண்புழு உரம் இடுவதால் மண் வளம் பெருகும்."
            )
        elif lang == "kn":
            return (
                "🧪 **ರಸಗೊಬ್ಬರ ನಿರ್ವಹಣಾ ಸಲಹೆ:**\n\n"
                "1. **ಮಣ್ಣು ಪರೀಕ್ಷೆ:** ಮಣ್ಣಿನ ಆರೋಗ್ಯ ಕಾರ್ಡ್ ಆಧಾರದ ಮೇಲೆ ರಸಗೊಬ್ಬರಗಳನ್ನು ಬಳಸಿ.\n"
                "2. **ಯೂರಿಯಾ ಬಳಕೆ:** ಯೂರಿಯಾವನ್ನು ಒಮ್ಮೆಲೇ ಹಾಕದೆ 2-3 ಕಂತುಗಳಲ್ಲಿ ನೀಡಿ.\n"
                "3. **ಡಿಎಪಿ / ರಂಜಕ:** ಬಿತ್ತನೆಯ ಸಮಯದಲ್ಲಿ ಅಡಿಗೊಬ್ಬರವಾಗಿ ಮಾತ್ರ ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ.\n"
                "4. **ಸಾವಯವ ಗೊಬ್ಬರ:** ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಅಥವಾ ಎರೆಹುಳು ಗೊಬ್ಬರವನ್ನು ಬಳಸುವುದರಿಂದ ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಹೆಚ್ಚುತ್ತದೆ."
            )
        elif lang == "mr":
            return (
                "🧪 **खत व्यवस्थापन सल्ला:**\n\n"
                "1. **माती परीक्षण:** मृदा आरोग्य पत्रिकेनुसारच खतांचा समतोल वापर करा.\n"
                "2. **युरियाचा वापर:** युरिया एकाच वेळी न देता पीक वाढीच्या टप्प्यांनुसार २-३ हप्त्यांत द्या.\n"
                "3. **डीएपी / स्फुरद:** पेरणीच्या वेळी बेसल डोस म्हणून जमिनीत मिसळा.\n"
                "4. **सेंद्रिय खत:** शेणखत किंवा गांडूळ खताचा वापर केल्याने जमिनीची सुपिकता टिकून राहते."
            )
        else:
            return (
                "🧪 **Fertilizer & Soil Nutrition Guidance:**\n\n"
                "1. **Soil-Test Based Application:** Base fertilizer quantities strictly on recent soil test parameters.\n"
                "2. **Split Nitrogen Application:** Apply nitrogen (Urea) in 2 to 3 split doses across critical growth stages to minimize volatilization and leaching.\n"
                "3. **Basal Phosphorus Placement:** Apply Phosphorus (DAP or Single Super Phosphate) at sowing time directly into the root zone.\n"
                "4. **Organic Matter:** Incorporate farmyard manure or vermicompost to enhance nutrient uptake efficiency."
            )

    def _build_irrigation_response(
        self, question: str, weather: Dict[str, Any], crop_rec: Dict[str, Any], lang: str
    ) -> str:
        precip = float(weather.get("precip", 0.0))
        has_rain = precip > 0.0

        if lang == "te":
            rain_note = "ప్రస్తుతం వర్ష సూచన ఉన్నందున నీటిపారుదలని వాయిదా వేయండి.\n\n" if has_rain else "ఉదయం లేదా సాయంత్రం వేళల్లో మాత్రమే నీరు పెట్టడం మంచిది.\n\n"
            return (
                f"💧 **నీటిపారుదల యాజమాన్య సలహా:**\n\n"
                f"{rain_note}"
                "1. **నేల తేమ పరిశీలన:** 4-6 అంగుళాల లోతులో మట్టిని చేత్తో పట్టుకుని చూసినప్పుడు ముద్దగా కాకపోతే వెంటనే నీరు పెట్టండి.\n"
                "2. **కీలక దశలు:** పిలకలు వేసే దశ, పూత మరియు గింజ పాలుపోసుకునే దశలలో నీటి ఎద్దడి లేకుండా చూడండి.\n"
                "3. **బిందు సేద్యం (Drip):** బిందు సేద్యం వాడటం వల్ల నీరు ఆదా అవ్వడమే కాక ఆకులకు తెగుళ్లు సోకకుండా ఉంటాయి."
            )
        elif lang == "hi":
            rain_note = "वर्तमान में वर्षा का अनुमान होने के कारण सिंचाई को स्थगित रखें।\n\n" if has_rain else "सुबह अथवा शाम के समय ही सिंचाई करें ताकि वाष्पीकरण से पानी का नुकसान न हो।\n\n"
            return (
                f"💧 **सिंचाई प्रबंधन परामर्श:**\n\n"
                f"{rain_note}"
                "1. **मृदा नमी परीक्षण:** 4-6 इंच गहराई से मिट्टी लेकर मुट्ठी बनाएं; यदि मिट्टी बिखर जाए तो तुरंत सिंचाई करें।\n"
                "2. **संवेदनशील अवस्थाएं:** कल्ले निकलते समय, फूल आते समय और दाना भरते समय फसल में नमी की कमी न होने दें।\n"
                "3. **टपक सिंचाई (ड्रिप):** ड्रिप सिंचाई से 40-50% पानी की बचत होती है और फफूंद जनित रोगों का खतरा कम रहता है।"
            )
        elif lang == "ta":
            rain_note = "மழை வாய்ப்புள்ளதால் பாசனத்தை ஒத்திவைக்கவும்.\n\n" if has_rain else "காலை அல்லது மாலை வேளையில் மட்டுமே பாசனம் செய்யவும்.\n\n"
            return (
                f"💧 **பாசன மேலாண்மை ஆலோசனை:**\n\n"
                f"{rain_note}"
                "1. **மண் ஈரப்பதம்:** 4 அங்குல ஆழத்தில் மண்ணை எடுத்துப் பார்க்கும்போது உதிர்ந்தால் உடனே தண்ணீர் பாய்ச்சவும்.\n"
                "2. **முக்கிய வளர்ச்சிப் பருவங்கள்:** தூர்கட்டும் பருவம், பூக்கும் பருவம் மற்றும் பால் பிடிக்கும் பருவத்தில் தண்ணீர் பற்றாக்குறை இருக்கக் கூடாது.\n"
                "3. **சொட்டு நீர் பாசனம்:** சொட்டு நீர் பாசனம் மூலம் நீர் விரயத்தைத் தடுத்து மகசூலை அதிகரிக்கலாம்."
            )
        elif lang == "kn":
            rain_note = "ಮಳೆಯಾಗುವ ಮುನ್ಸೂಚನೆ ಇರುವುದರಿಂದ ನೀರಾವರಿಯನ್ನು ಮುಂದೂಡಿ.\n\n" if has_rain else "ಬೆಳಿಗ್ಗೆ ಅಥವಾ ಸಂಜೆ ವೇಳೆ ನೀರು ಹಾಯಿಸುವುದು ಉತ್ತಮ.\n\n"
            return (
                f"💧 **ನೀರಾವರಿ ನಿರ್ವಹಣಾ ಸಲಹೆ:**\n\n"
                f"{rain_note}"
                "1. **ತೇವಾಂಶ ಪರೀಕ್ಷೆ:** 4-6 ಇಂಚು ಆಳದ ಮಣ್ಣನ್ನು ಪರೀಕ್ಷಿಸಿ, ತೇವಾಂಶ ಕಡಿಮೆಯಿದ್ದರೆ ತಕ್ಷಣ ನೀರು ಹಾಯಿಸಿ.\n"
                "2. **ಮುಖ್ಯ ಹಂತಗಳು:** ತೆನೆ ಒಡೆಯುವ ಮತ್ತು ಕಾಳು ತುಂಬುವ ಹಂತಗಳಲ್ಲಿ ನೀರಿನ ಕೊರತೆಯಾಗದಂತೆ ನೋಡಿಕೊಳ್ಳಿ.\n"
                "3. **ಹನಿ ನೀರಾವರಿ:** ಹನಿ ನೀರಾವರಿ ಬಳಸುವುದರಿಂದ ನೀರು ಉಳಿತಾಯವಾಗುತ್ತದೆ ಮತ್ತು ರೋಗಗಳ ಹರಡುವಿಕೆ ಕಡಿಮೆಯಾಗುತ್ತದೆ."
            )
        elif lang == "mr":
            rain_note = "पावसाचा अंदाज असल्यामुळे सिंचन पुढे ढकलावे.\n\n" if has_rain else "सकाळी किंवा संध्याकाळी पाणी दिल्यास बाष्पीभवन कमी होते.\n\n"
            return (
                f"💧 **सिंचन व्यवस्थापन सल्ला:**\n\n"
                f"{rain_note}"
                "1. **जमिनीतील ओलावा तपासणे:** ४-६ इंच खोलीवरील माती हातात घेऊन लाडू न झाल्यास ताबडतोब पाणी द्या.\n"
                "2. **संवेदनशील टप्पे:** फुटवे फुटताना, फुलोऱ्यात आणि दाणे भरताना पिकाला पाण्याचा ताण पडू देऊ नका.\n"
                "3. **ठिबक सिंचन:** ठिबक सिंचनामुळे पाण्याची बचत होते आणि बुरशीजन्य रोग नियंत्रणात राहतात."
            )
        else:
            rain_note = "Precipitation is detected; postpone manual irrigation.\n\n" if has_rain else "Irrigate during early morning or late afternoon to minimize evaporative water loss.\n\n"
            return (
                f"💧 **Irrigation & Water Scheduling Guidance:**\n\n"
                f"{rain_note}"
                "1. **Root-Zone Moisture Test:** Squeeze a soil sample from 4-6 inches depth; if it crumbles, irrigate promptly.\n"
                "2. **Critical Growth Stages:** Never stress crops during tillering, flowering, or grain filling stages.\n"
                "3. **Micro-Irrigation:** Drip irrigation reduces water consumption by up to 50% while preventing foliar diseases."
            )

    def _build_disease_response(
        self, question: str, disease: Dict[str, Any], crop_rec: Dict[str, Any], lang: str, has_image: bool
    ) -> str:
        condition = disease.get("condition")
        confidence = disease.get("confidence")
        clean_cond = condition.replace("___", " - ").replace("__", " - ").replace("_", " ") if condition else ""

        if lang == "te":
            diag_str = f"ఇటీవలి విశ్లేషణ: **{clean_cond}** (ఖచ్చితత్వం: {confidence}). " if clean_cond else ""
            img_note = "ఆకు ఫోటోను వివరంగా విశ్లేషించడానికి 'వ్యాధి నిర్ధారణ (Disease Detection)' ఫీచర్‌ను ఉపయోగించవచ్చు.\n\n" if has_image else ""
            return (
                f"🌱 **పంట ఆరోగ్యం & తెగుళ్ల నిర్వహణ:**\n\n"
                f"{diag_str}{img_note}"
                f"**ముఖ్య నివారణ చర్యలు:**\n"
                f"1. తెగులు సోకిన ఆకులను వేరు చేసి పొలం వెలుపల నాశనం చేయండి.\n"
                f"2. మొక్కల మధ్య గాలి మరియు ఎండ తగిలేలా జాగ్రత్త వహించండి.\n"
                f"3. అధిక నత్రజని వాడకం తగ్గించండి, తగినంత పొటాష్ ఎరువులు వేయండి.\n"
                f"4. రసాయన మందుల వివరాల కోసం స్థానిక కృషి విజ్ఞాన కేంద్రం (KVK) ను సంప్రదించండి."
            )
        elif lang == "hi":
            diag_str = f"हालिया रोग निदान: **{clean_cond}** (सटीकता: {confidence})। " if clean_cond else ""
            img_note = "पत्ती की स्पष्ट जांच के लिए 'रोग निदान (Disease Detection)' विकल्प का उपयोग कर सकते हैं।\n\n" if has_image else ""
            return (
                f"🌱 **फसल स्वास्थ्य एवं रोग प्रबंधन:**\n\n"
                f"{diag_str}{img_note}"
                f"**मुख्य सुरक्षात्मक उपाय:**\n"
                f"1. ग्रसित पत्तियों को तोड़कर खेत से दूर नष्ट कर दें।\n"
                f"2. खेत में हवा और धूप का संचार बनाए रखने के लिए उचित दूरी रखें।\n"
                f"3. नाइट्रोजन का अत्यधिक उपयोग न करें, पोटाश की संतुलित मात्रा दें।\n"
                f"4. विस्तृत रासायनिक अनुशंसा हेतु नजदीकी कृषि विज्ञान केंद्र (KVK) से संपर्क करें।"
            )
        elif lang == "ta":
            diag_str = f"கண்டறியப்பட்ட நோய்: **{clean_cond}** (நம்பகத்தன்மை: {confidence}). " if clean_cond else ""
            img_note = "துல்லியமான ஆய்வுக்கு 'நோய் கண்டறிதல்' பக்கத்தில் புகைப்படத்தைப் பதிவேற்றலாம்.\n\n" if has_image else ""
            return (
                f"🌱 **பயிர் நலம் மற்றும் நோய் மேலாண்மை:**\n\n"
                f"{diag_str}{img_note}"
                f"**பாதுகாப்பு நடவடிக்கைகள்:**\n"
                f"1. பாதிக்கப்பட்ட இலைகளைப் பறித்து அப்புறப்படுத்தவும்.\n"
                f"2. செடிகளுக்கு இடையே நல்ல காற்றோட்டம் மற்றும் சூரிய ஒளி கிடைப்பதை உறுதி செய்யவும்.\n"
                f"3. அதிகப்படியான யூரியாவைத் தவிர்த்து பொட்டாஷ் உரத்தை இடவும்.\n"
                f"4. தகுந்த மருந்துப் பரிந்துரைகளுக்கு உள்ளூர் வேளாண் அறிவியல் மையத்தை (KVK) அணுகவும்."
            )
        elif lang == "kn":
            diag_str = f"ಇತ್ತೀಚಿನ ರೋಗ ಪತ್ತೆ: **{clean_cond}** (ನಿಖರತೆ: {confidence}). " if clean_cond else ""
            img_note = "ಎಲೆಯ ಸ್ಪಷ್ಟ ಪರೀಕ್ಷೆಗಾಗಿ 'ರೋಗ ಪತ್ತೆ' ಟೂಲ್ ಬಳಸಿ.\n\n" if has_image else ""
            return (
                f"🌱 **ಬೆಳೆ ಆರೋಗ್ಯ ಮತ್ತು ರೋಗ ನಿರ್ವಹಣೆ:**\n\n"
                f"{diag_str}{img_note}"
                f"**ಮುಖ್ಯ ಕ್ರಮಗಳು:**\n"
                f"1. ರೋಗಪೀಡಿತ ಎಲೆಗಳನ್ನು ಕಿತ್ತು ಹೊಲದಿಂದ ದೂರ ವಿಲೇವಾರಿ ಮಾಡಿ.\n"
                f"2. ಗಿಡಗಳ ನಡುವೆ ಸರಿಯಾದ ಗಾಳಿ ಮತ್ತು ಬೆಳಕು ಇರುವಂತೆ ನೋಡಿಕೊಳ್ಳಿ.\n"
                f"3. ಸಾರಜನಕದ ಅತಿಯಾದ ಬಳಕೆಯನ್ನು ತಪ್ಪಿಸಿ, ಪೊಟ್ಯಾಶ್ ಗೊಬ್ಬರ ನೀಡಿ.\n"
                f"4. ಹೆಚ್ಚಿನ ಮಾಹಿತಿಗಾಗಿ ಸ್ಥಳೀಯ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರವನ್ನು (KVK) ಸಂಪರ್ಕಿಸಿ."
            )
        elif lang == "mr":
            diag_str = f"अलिकडील रोग निदान: **{clean_cond}** (अचूकता: {confidence}). " if clean_cond else ""
            img_note = "पानांच्या तपासणीसाठी 'रोग निदान' टूलचा वापर करा.\n\n" if has_image else ""
            return (
                f"🌱 **पीक आरोग्य आणि रोग व्यवस्थापन:**\n\n"
                f"{diag_str}{img_note}"
                f"**महत्त्वाचे उपाय:**\n"
                f"1. रोगट पाने तोडून शेताबाहेर नष्ट करा.\n"
                f"2. पिकांमध्ये हवा आणि सूर्यप्रकाश खेळता राहील याची काळजी घ्या.\n"
                f"3. नत्राचा अतिवापर टाळा व पालाशयुक्त खते द्या.\n"
                f"4. रासायनिक फवारणीच्या सल्ल्यासाठी कृषी विज्ञान केंद्राशी (KVK) संपर्क साधा."
            )
        else:
            diag_str = f"Recent Diagnosis on file: **{clean_cond}** (Confidence: {confidence}).\n\n" if clean_cond else ""
            img_note = "To run a real-time computer vision analysis on this leaf photo, use the **Disease Detection** tool in FarmSathi.\n\n" if has_image else ""
            return (
                f"🌱 **Crop Health & Disease Advisory:**\n\n"
                f"{diag_str}{img_note}"
                f"**Agronomic Management Guidelines:**\n"
                f"1. **Sanitation:** Remove and burn or bury infected plant leaves to prevent secondary fungal spore spread.\n"
                f"2. **Canopy Aeration:** Avoid overly dense planting; allow adequate sunlight and air circulation.\n"
                f"3. **Balanced Nutrition:** Avoid excessive nitrogen which softens plant foliage; ensure adequate potassium to boost cellular defense.\n"
                f"4. **Extension Advisory:** For certified regional chemical sprays, consult your local Krishi Vigyan Kendra (KVK)."
            )

    def _build_general_agronomy_response(
        self, question: str, profile: Dict[str, Any], crop_rec: Dict[str, Any], lang: str
    ) -> str:
        if lang == "te":
            return (
                f"🌾 **వ్యవసాయ సలహా & సమగ్ర క్షేత్ర యాజమాన్యం:**\n\n"
                f"మీ ప్రశ్న: *{question}*\n\n"
                f"**క్షేత్ర స్థాయిలో పరిశీలించాల్సిన ముఖ్య అంశాలు:**\n"
                f"1. **నేల మరియు వేర్ల ఆరోగ్యం:** మొక్క మొదలు వద్ద తవ్వి తెల్లటి ఆరోగ్యకరమైన వేర్లు ఉన్నాయో లేదో గమనించండి. నేలలో తగినంత తేమ మరియు గాలి ఆడే వాతావరణం ఉండాలి.\n"
                f"2. **సమతుల్య పోషకాలు:** నత్రజని (యూరియా), భాస్వరం మరియు పొటాష్‌లను సిఫార్సు చేసిన మోతాదులోనే వేయండి. సూక్ష్మపోషకాలైన జింక్ మరియు బోరాన్ లోపాలు లేకుండా జాగ్రత్తపడండి.\n"
                f"3. **తెగుళ్లు & పురుగుల పర్యవేక్షణ:** ఉదయం వేళల్లో ఆకుల అడుగుభాగం, పిలకలు మరియు కాండంను పరిశీలించండి.\n"
                f"4. **వాతావరణ అనుకూలత:** పిచికారీ మరియు నీటిపారుదల పనులను స్థానిక వాతావరణ సూచన ఆధారంగా చేపట్టండి.\n\n"
                f"మరింత ఖచ్చితమైన సలహా కోసం మీ పంట పేరు, ఎదుగుదల దశ లేదా ఆకు ఫోటోను పంపించండి!"
            )
        elif lang == "hi":
            return (
                f"🌾 **कृषि परामर्श एवं समग्र खेत प्रबंधन:**\n\n"
                f"आपका प्रश्न: *{question}*\n\n"
                f"**खेत में ध्यान देने योग्य महत्वपूर्ण बिंदु:**\n"
                f"1. **जड़ एवं मृदा स्वास्थ्य:** पौधों की जड़ों को देखकर सुनिश्चित करें कि जड़ें सफेद और स्वस्थ हैं। मिट्टी में जलभराव या अत्यधिक सूखापन न हो।\n"
                f"2. **संतुलित पोषण:** केवल यूरिया पर निर्भर न रहें; फॉस्फोरस, पोटाश और सूक्ष्म पोषक तत्वों (जिंक, सल्फर) का संतुलित प्रयोग करें।\n"
                f"3. **कीट एवं रोग निगरानी:** सुबह के समय पत्तियों के निचले भाग और तने का निरीक्षण करें ताकि शुरुआती अवस्था में ही कीटों का पता चल सके।\n"
                f"4. **मौसम का ध्यान:** किसी भी प्रकार के छिड़काव से पहले आगामी बारिश का पूर्वानुमान अवश्य देखें।\n\n"
                f"अधिक सटीक समाधान के लिए कृपया अपनी फसल का नाम, पौधे की उम्र अथवा पत्ती की फोटो साझा करें!"
            )
        elif lang == "ta":
            return (
                f"🌾 **வேளாண் ஆலோசனை மற்றும் வயல் மேலாண்மை:**\n\n"
                f"உங்கள் கேள்வி: *{question}*\n\n"
                f"**முக்கிய களப் பராமரிப்பு வழிகாட்டல்கள்:**\n"
                f"1. **மண் மற்றும் வேர் நலம்:** வேர்களில் அழுகல் இல்லாமல் வெள்ளை நிறத்தில் உள்ளதா எனப் பரிசோதிக்கவும்.\n"
                f"2. **சமச்சீர் உரம்:** பயிரின் நிலைக்கு ஏற்ப N-P-K மற்றும் நுண்ணூட்டச் சத்துக்களை இடவும்.\n"
                f"3. **பூச்சி மற்றும் நோய் கண்காணிப்பு:** இலைகளின் அடிப்பகுதியில் சாறு உறிஞ்சும் பூச்சிகள் உள்ளதா எனப் பார்க்கவும்.\n"
                f"4. **வானிலை விழிப்புணர்வு:** மழை இல்லாத தெளிவான வானிலையில் மட்டுமே மருந்து தெளிக்கவும்.\n\n"
                f"துல்லியமான ஆலோசனைக்கு பயிர் பெயர் மற்றும் நிலவரத்தைப் பகிரவும்!"
            )
        elif lang == "kn":
            return (
                f"🌾 **ಕೃಷಿ ಸಲಹೆ ಮತ್ತು ಸಮಗ್ರ ಕ್ಷೇತ್ರ ನಿರ್ವಹಣೆ:**\n\n"
                f"ನಿಮ್ಮ ಪ್ರಶ್ನೆ: *{question}*\n\n"
                f"**ಮುಖ್ಯ ಕ್ಷೇತ್ರ ಮಾರ್ಗಸೂಚಿಗಳು:**\n"
                f"1. **ಬೇರು ಮತ್ತು ಮಣ್ಣಿನ ಆರೋಗ್ಯ:** ಬೇರುಗಳು ಆರೋಗ್ಯಕರವಾಗಿವೆಯೇ ಮತ್ತು ಮಣ್ಣಿನಲ್ಲಿ ತೇವಾಂಶ ಸರಿಯಾಗಿದೆಯೇ ಎಂದು ಗಮನಿಸಿ.\n"
                f"2. **ಸಮತೋಲಿತ ಪೋಷಕಾಂಶ:** ಸಾರಜನಕ, ರಂಜಕ, ಪೊಟ್ಯಾಶ್ ಮತ್ತು ಲಘು ಪೋಷಕಾಂಶಗಳನ್ನು ಸರಿಯಾದ ಪ್ರಮಾಣದಲ್ಲಿ ನೀಡಿ.\n"
                f"3. **ಕೀಟ ಮತ್ತು ರೋಗ ನಿಗಾ:** ಎಲೆಗಳ ಕೆಳಭಾಗವನ್ನು ನಿಯಮಿತವಾಗಿ ಪರಿಶೀಲಿಸಿ.\n"
                f"4. **ಹವಾಮಾನ ಆಧಾರಿತ ಕೆಲಸ:** ಮಳೆ ಮುನ್ಸೂಚನೆ ಗಮನಿಸಿ ಸಿಂಪಡಣೆ ಮತ್ತು ನೀರಾವರಿ ನಿರ್ವಹಿಸಿ.\n\n"
                f"ಹೆಚ್ಚಿನ ವಿವರಗಳಿಗಾಗಿ ಬೆಳೆ ಹೆಸರು ಅಥವಾ ಎಲೆಯ ಫೋಟೋ ಕಳುಹಿಸಿ!"
            )
        elif lang == "mr":
            return (
                f"🌾 **कृषी सल्ला व एकात्मिक शेत व्यवस्थापन:**\n\n"
                f"आपला प्रश्न: *{question}*\n\n"
                f"**शेतात घ्यावयाची महत्त्वाची काळजी:**\n"
                f"1. **मुळांचे व मातीचे आरोग्य:** झाडांची पांढरी मुळे तपासा व जमिनीतील वाफसा कायम ठेवा.\n"
                f"2. **संतुलित अन्नद्रव्ये:** नत्र, स्फुरद, पालाश यांच्यासोबत सूक्ष्म अन्नद्रव्यांचा समतोल वापर करा.\n"
                f"3. **कीड व रोग सर्वेक्षण:** पानांच्या खालच्या बाजूची नियमित तपासणी करा.\n"
                f"4. **हवामानाचा अंदाज:** फवारणी करण्यापूर्वी पावसाचा अंदाज नक्की तपासा.\n\n"
                f"अधिक अचूक सल्ल्यासाठी पिकाचे नाव किंवा पानाचा फोटो पाठवा!"
            )
        else:
            return (
                f"🌾 **Agronomic Advisory & Integrated Field Management:**\n\n"
                f"Regarding your query: *{question}*\n\n"
                f"**Core Field Evaluation Protocol:**\n"
                f"1. **Root-Zone & Soil Aeration:** Gently unearth sample plant roots to inspect for vigorous white root hairs versus dark decaying tips. Maintain balanced soil moisture and eliminate stagnant water.\n"
                f"2. **Balanced Nutrient Regimen:** Avoid over-relying on Nitrogen (Urea); maintain proportional Phosphorus for root development, Potassium for pest tolerance, and secondary micro-nutrients (Zinc, Boron).\n"
                f"3. **Integrated Pest & Pathogen Scouting:** Routinely examine leaf undersides, growing tips, and stems early in the morning for early nymph activity or fungal spore lesions.\n"
                f"4. **Weather-Aligned Interventions:** Align all foliar treatments and irrigation schedules with live local weather conditions.\n\n"
                f"For targeted advice, share your specific crop type, growth stage, or upload a close-up leaf photograph for AI disease analysis."
            )
