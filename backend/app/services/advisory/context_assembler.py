import logging
import re
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.profile_repo import FarmerProfileRepository
from app.repositories.crop_repo import CropRecommendationRepository
from app.repositories.disease_repo import DiseaseDiagnosisRepository
from app.repositories.weather_repo import WeatherCacheRepository
from app.repositories.advisory_repo import AdvisoryRepository

logger = logging.getLogger(__name__)


@dataclass
class AssembledContext:
    structured_context: Dict[str, Any]
    context_summary: Dict[str, Any]
    formatted_prompt_context: str
    conversation_history: List[Dict[str, str]]


class ContextAssembler:
    """
    Assembles verified, query-relevant context from PostgreSQL repositories and live services.
    Strictly avoids attaching unrelated diagnostic or recommendation data.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.profile_repo = FarmerProfileRepository(session)
        self.crop_repo = CropRecommendationRepository(session)
        self.disease_repo = DiseaseDiagnosisRepository(session)
        self.weather_repo = WeatherCacheRepository(session)
        self.advisory_repo = AdvisoryRepository(session)

    async def assemble(
        self,
        user_id: uuid.UUID,
        conversation_id: Optional[uuid.UUID] = None,
        farmer_question: str = "",
        image_metadata: Optional[Dict[str, Any]] = None,
        image_bytes: Optional[bytes] = None,
        image_mime_type: Optional[str] = None,
        image_filename: Optional[str] = None,
        language: str = "en",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        location_name: Optional[str] = None,
    ) -> AssembledContext:
        structured: Dict[str, Any] = {
            "farmer_profile": None,
            "crop_recommendation": None,
            "disease_diagnosis": None,
            "weather": None,
            "attached_image": image_metadata,
        }
        prompt_sections: List[str] = []

        # 1. Farmer Profile
        profile = await self.profile_repo.get_by_user_id(user_id)
        if profile:
            profile_data: Dict[str, Any] = {}
            if profile.state:
                profile_data["state"] = profile.state
            if profile.district:
                profile_data["district"] = profile.district
            if profile.village:
                profile_data["village"] = profile.village
            if profile.land_size_acres is not None:
                profile_data["land_size_acres"] = float(profile.land_size_acres)
            if profile.soil_type:
                profile_data["soil_type"] = profile.soil_type
            if profile.irrigation_source:
                profile_data["irrigation_source"] = profile.irrigation_source

            if profile_data:
                if profile.preferred_language:
                    profile_data["preferred_language"] = profile.preferred_language
                structured["farmer_profile"] = profile_data
                lines = [f"- {k.replace('_', ' ').title()}: {v}" for k, v in profile_data.items()]
                prompt_sections.append("### Farmer Profile:\n" + "\n".join(lines))

        # Query intent analysis for strict relevance
        q_lower = (farmer_question or "").lower().strip()

        weather_patterns = [
            r"\b(rain|raining|rainfall|weather|temperature|temp|forecast|cloud|sunny|humid|humidity|storm|precipitation|climate|wind)\b",
            r"\b(spray|spraying|pesticide|fungicide|chemical|irrigate|irrigation|water my field|water the crop)\b",
            r"\b(వర్షం|వాతావరణం|ఎండ|ఉష్ణోగ్రత|తేమ|గాలి|మందు కొట్టవచ్చా|నీరు పెట్టవచ్చా|పిచికారీ)\b",
            r"\b(मौसम|बारिश|तापमान|वर्षा|हवा|छिड़काव|सिंचाई|कीटनाशक)\b",
        ]
        crop_patterns = [
            r"\b(which crops?|what crops?|recommend.*crops?|crops? to grow|crops? should i|suitable crops?|crop recommendation)\b",
            r"\b(crop selection|best crops?|suggest.*crops?|variety to sow|what should i plant|crops? will grow|grow in|sow in|plant in)\b",
            r"\b(what crop did you recommend|recommended crop for my soil)\b",
            r"\b(fertilizer schedule|soil nutrients|nitrogen level|phosphorus level|potassium level|soil ph)\b",
            r"\b(ఏ పంట|పంట సిఫార్సు|ఏ పంట వేయాలి)\b",
            r"\b(कौन सी फसल|फसल सिफ़ारिश|फसल लगाएं)\b",
            r"\b(எந்த பயிர்|பயிர் பரிந்துரை)\b",
            r"\b(ಯಾವ ಬೆಳೆ|ಬೆಳೆ ಶಿಫಾರಸು)\b",
            r"\b(कोणते पीक|पीक शिफारस)\b",
        ]
        disease_patterns = [
            r"\b(disease|pest|fungus|fungal|blight|spot|spots|rot|rust|mildew|canker|wilt|wilting|bug|insect|worm|caterpillar)\b",
            r"\b(leaves.*yellow|yellow.*leaves|leaf.*curl|curling.*leaves|brown spots|leaf damage|leaf problem|problem in the leaf|problem in the crop|leaf image)\b",
            r"\b(పురుగు|తెగులు|రోగం|మచ్చలు|ఆకుముడత|ఆకులు పసుపు)\b",
            r"\b(रोग|कीड़ा|झुलसा|फफूंद|धब्बे|पत्तियां पीली|पत्ती मुड़)\b",
        ]

        is_weather_q = any(re.search(pat, q_lower) for pat in weather_patterns)
        is_crop_q = any(re.search(pat, q_lower) for pat in crop_patterns)
        is_disease_q = any(re.search(pat, q_lower) for pat in disease_patterns) or bool(image_bytes)

        # Weather questions must NEVER contain crop recommendation or disease diagnosis context
        if not q_lower:
            # If no question is specified (e.g. general context assemble in tests/admin), include both
            include_crop_rec = True
            include_disease_diag = True
        elif is_weather_q and not (is_crop_q or is_disease_q):
            include_crop_rec = False
            include_disease_diag = False
        else:
            include_crop_rec = is_crop_q
            include_disease_diag = is_disease_q

        # 2. Crop Recommendation History (strictly only if relevant to current query)
        if include_crop_rec:
            crop_recs = await self.crop_repo.get_by_user_id(user_id, skip=0, limit=1)
            if crop_recs:
                latest_crop = crop_recs[0]
                crop_data = {
                    "recommended_crop": latest_crop.recommended_crop,
                    "soil_nitrogen": float(latest_crop.nitrogen),
                    "soil_phosphorus": float(latest_crop.phosphorus),
                    "soil_potassium": float(latest_crop.potassium),
                    "soil_ph": float(latest_crop.ph),
                    "rainfall": float(latest_crop.rainfall),
                    "date": latest_crop.created_at.strftime("%Y-%m-%d"),
                }
                structured["crop_recommendation"] = crop_data
                prompt_sections.append(
                    f"### Crop Recommendation History:\n"
                    f"- Recommended Crop: {crop_data['recommended_crop']}\n"
                    f"- Recorded Soil N-P-K: {crop_data['soil_nitrogen']}-{crop_data['soil_phosphorus']}-{crop_data['soil_potassium']}\n"
                    f"- Soil pH: {crop_data['soil_ph']}\n"
                    f"- Recommendation Date: {crop_data['date']}"
                )

        # 3. Disease Diagnosis (Attached Image MobileNetV3 or History)
        if image_bytes:
            try:
                from app.services.disease_service import disease_service
                fname = image_filename or (image_metadata.get("filename") if image_metadata else "farmer_leaf.jpg")
                mtype = image_mime_type or (image_metadata.get("mime_type") if image_metadata else "image/jpeg")
                pil_image = disease_service.validate_image_file(image_bytes, fname, mtype)
                diag_result = disease_service.predict(pil_image)

                is_suitable = diag_result.get("is_suitable", True)
                suitability_msg = diag_result.get("suitability_message")

                if is_suitable:
                    conf_pct = round(diag_result["confidence"] * 100, 1)
                    diag_data = {
                        "predicted_condition": diag_result["display_name"],
                        "raw_class": diag_result["predicted_condition"],
                        "crop": diag_result["crop"],
                        "condition": diag_result["condition"],
                        "confidence_percent": conf_pct,
                        "confidence": diag_result["confidence"],
                        "is_confident": diag_result["is_confident"],
                        "is_healthy": diag_result["is_healthy"],
                        "is_suitable": True,
                        "suitability_message": None,
                        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    }
                    structured["disease_diagnosis"] = diag_data

                    guidance = diag_result.get("management_guidance")
                    guidance_lines = []
                    if guidance:
                        if hasattr(guidance, "cultural_practices") and guidance.cultural_practices:
                            guidance_lines.append("  * Cultural: " + "; ".join(guidance.cultural_practices[:3]))
                        if hasattr(guidance, "sanitation") and guidance.sanitation:
                            guidance_lines.append("  * Sanitation: " + "; ".join(guidance.sanitation[:2]))
                        if hasattr(guidance, "prevention") and guidance.prevention:
                            guidance_lines.append("  * Prevention: " + "; ".join(guidance.prevention[:2]))
                    mgmt_str = ("\n" + "\n".join(guidance_lines)) if guidance_lines else ""

                    prompt_sections.append(
                        f"### Attached Image Foliar Disease Diagnosis (Verified MobileNetV3):\n"
                        f"- Diagnosed Condition: {diag_data['predicted_condition']}\n"
                        f"- Diagnostic Confidence: {conf_pct}% (Verified: {diag_data['is_confident']})\n"
                        f"- Primary Crop: {diag_data['crop']}\n"
                        f"- Foliar Condition: {diag_data['condition']}\n"
                        f"- Is Healthy: {diag_data['is_healthy']}\n"
                        f"- Management Practices:{mgmt_str}"
                    )
                else:
                    diag_data = {
                        "predicted_condition": "Unsuitable Image",
                        "is_suitable": False,
                        "suitability_message": suitability_msg or "Image does not appear to contain crop foliage.",
                        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    }
                    structured["disease_diagnosis"] = diag_data
                    prompt_sections.append(
                        f"### Attached Image Foliar Diagnosis Result:\n"
                        f"- Image Suitability: Unsuitable\n"
                        f"- Assessment: {diag_data['suitability_message']}"
                    )
            except Exception as exc:
                logger.warning("Advisory image disease analysis failed: %s", exc)
        elif include_disease_diag:
            disease_diags = await self.disease_repo.get_by_user_id(user_id, skip=0, limit=1)
            if disease_diags:
                latest_diag = disease_diags[0]
                cond_clean = latest_diag.predicted_condition or ""
                if cond_clean:
                    cond_clean = cond_clean.replace("___", " - ").replace("__", " - ").replace("_", " ")
                diag_data = {
                    "predicted_condition": cond_clean,
                    "confidence_percent": (
                        round(float(latest_diag.confidence) * 100, 1)
                        if latest_diag.confidence is not None
                        else None
                    ),
                    "is_confident": latest_diag.is_confident,
                    "date": latest_diag.created_at.strftime("%Y-%m-%d"),
                }
                structured["disease_diagnosis"] = diag_data
                conf_str = (
                    f"{diag_data['confidence_percent']}%"
                    if diag_data["confidence_percent"] is not None
                    else "N/A"
                )
                prompt_sections.append(
                    f"### Recent Disease Diagnosis:\n"
                    f"- Diagnosed Condition: {diag_data['predicted_condition']}\n"
                    f"- Diagnostic Confidence: {conf_str} (Verified: {diag_data['is_confident']})\n"
                    f"- Diagnosis Date: {diag_data['date']}"
                )

        # 4. Location & Weather Resolution
        eff_lat: Optional[float] = None
        eff_lon: Optional[float] = None
        if latitude is not None and longitude is not None:
            eff_lat, eff_lon = float(latitude), float(longitude)
        elif profile and profile.latitude is not None and profile.longitude is not None:
            eff_lat, eff_lon = float(profile.latitude), float(profile.longitude)

        eff_loc_name: Optional[str] = (
            location_name.strip() if location_name and location_name.strip() else None
        )
        if not eff_loc_name and farmer_question:
            loc_m = re.search(
                r"\b(?:in|at|near|location of)\s+([A-Za-z\s]+?)(?:\s+village|\s+located|\s+mandal|\s+district|\?|\.|$)",
                farmer_question,
                re.IGNORECASE,
            )
            if loc_m:
                cand = loc_m.group(1).strip()
                if len(cand) >= 3 and cand.lower() not in ["the", "my", "our", "this", "a"]:
                    eff_loc_name = cand
        if not eff_loc_name and profile:
            parts = [p for p in [profile.village, profile.district, profile.state] if p]
            if parts:
                eff_loc_name = ", ".join(parts)

        # Geocoding resolution fallback if coordinates are missing but location_name exists
        if (eff_lat is None or eff_lon is None) and eff_loc_name:
            try:
                from app.services.weather.weather_service import WeatherService
                ws = WeatherService(self.session)
                geo_results = await ws.search_locations(eff_loc_name, limit=1)
                if geo_results:
                    eff_lat = geo_results[0].latitude
                    eff_lon = geo_results[0].longitude
            except Exception as geo_exc:
                logger.warning("Geocoding resolution failed for '%s': %s", eff_loc_name, geo_exc)

        # Retrieve weather:
        # If coordinates or location are explicitly provided in request (live session), fetch live forecast.
        # Otherwise, check if valid weather cache exists for the user's profile location.
        if eff_lat is not None and eff_lon is not None:
            if latitude is not None or location_name is not None:
                loc_title = eff_loc_name or f"Coordinates ({round(eff_lat, 2)}, {round(eff_lon, 2)})"
                try:
                    from app.services.weather.weather_service import WeatherService
                    weather_service = WeatherService(self.session)
                    weather_res = await weather_service.get_forecast(
                        latitude=eff_lat,
                        longitude=eff_lon,
                        days=3,
                        location_name=eff_loc_name,
                    )
                    if weather_res:
                        conds: Dict[str, Any] = {}
                        if weather_res.current:
                            conds = weather_res.current.model_dump()
                        conds["location_name"] = eff_loc_name or (
                            weather_res.location.name if weather_res.location else None
                        )
                        conds["latitude"] = eff_lat
                        conds["longitude"] = eff_lon

                        # Extract tomorrow's daily forecast
                        tomorrow_info = None
                        if weather_res.forecast and len(weather_res.forecast) > 1:
                            tm = weather_res.forecast[1]
                            rain_exp = (
                                tm.precipitation_sum_mm > 0.5
                                or any(
                                    w in tm.condition_text.lower()
                                    for w in ["rain", "drizzle", "shower", "thunderstorm"]
                                )
                            )
                            tomorrow_info = {
                                "date": tm.date,
                                "condition_text": tm.condition_text,
                                "temperature_max_celsius": tm.temperature_max_celsius,
                                "temperature_min_celsius": tm.temperature_min_celsius,
                                "precipitation_sum_mm": tm.precipitation_sum_mm,
                                "rain_expected": rain_exp,
                            }
                            conds["tomorrow"] = tomorrow_info

                        structured["weather"] = conds

                        weather_lines = ["### Local Weather (Real/Live Cache):"]
                        weather_lines.append(f"- Location: {loc_title}")
                        if conds.get("temperature_celsius") is not None:
                            weather_lines.append(f"- Temperature: {conds['temperature_celsius']}°C")
                        if conds.get("condition_text"):
                            weather_lines.append(f"- Condition: {conds['condition_text']}")
                        if conds.get("relative_humidity_percent") is not None:
                            weather_lines.append(f"- Relative Humidity: {conds['relative_humidity_percent']}%")
                        if conds.get("precipitation_mm") is not None:
                            weather_lines.append(f"- Precipitation: {conds['precipitation_mm']} mm")
                        if conds.get("wind_speed_kmh") is not None:
                            weather_lines.append(f"- Wind Speed: {conds['wind_speed_kmh']} km/h")

                        if tomorrow_info:
                            weather_lines.append(
                                f"- Tomorrow's Forecast ({tomorrow_info['date']}): {tomorrow_info['condition_text']}, "
                                f"Rain Expected: {'Yes' if tomorrow_info['rain_expected'] else 'No'}, "
                                f"Precipitation: {tomorrow_info['precipitation_sum_mm']} mm, "
                                f"Temp: {tomorrow_info['temperature_min_celsius']}°C to {tomorrow_info['temperature_max_celsius']}°C"
                            )
                        prompt_sections.append("\n".join(weather_lines))
                except Exception as exc:
                    logger.warning("Advisory live weather retrieval failed: %s", exc)
                    # Fallback to direct cache lookup
                    cache_key = f"{round(eff_lat, 2)}_{round(eff_lon, 2)}"
                    weather_entry = await self.weather_repo.get_valid_cache(cache_key)
                    if weather_entry and weather_entry.current_conditions:
                        conds = dict(weather_entry.current_conditions)
                        if eff_loc_name:
                            conds["location_name"] = eff_loc_name
                        structured["weather"] = conds
                        loc_title = eff_loc_name or f"Coordinates ({round(eff_lat, 2)}, {round(eff_lon, 2)})"
                        weather_lines = ["### Local Weather (Real/Live Cache):"]
                        weather_lines.append(f"- Location: {loc_title}")
                        if "temperature_celsius" in conds:
                            weather_lines.append(f"- Temperature: {conds['temperature_celsius']}°C")
                        cond_text = conds.get("condition_text") or conds.get("condition")
                        if cond_text:
                            weather_lines.append(f"- Condition: {cond_text}")
                        prompt_sections.append("\n".join(weather_lines))
                    else:
                        structured["weather"] = {
                            "location_name": loc_title,
                            "status": "provider_unavailable",
                            "error_message": "Weather service temporarily unavailable",
                        }
                        prompt_sections.append(
                            f"### Local Weather (Real/Live Cache):\n"
                            f"- Location: {loc_title}\n"
                            f"- Status: Live weather provider temporarily unavailable. General agronomic principles apply."
                        )
            else:
                # No explicit coordinates supplied with request (e.g. background/profile-only inspection)
                cache_key = f"{round(eff_lat, 2)}_{round(eff_lon, 2)}"
                weather_entry = await self.weather_repo.get_valid_cache(cache_key)
                if weather_entry and weather_entry.current_conditions:
                    conds = dict(weather_entry.current_conditions)
                    if eff_loc_name:
                        conds["location_name"] = eff_loc_name
                    # If daily forecast is cached, extract tomorrow
                    if weather_entry.forecast_daily and len(weather_entry.forecast_daily) > 1:
                        tm_item = weather_entry.forecast_daily[1]
                        precip_sum = float(tm_item.get("precipitation_sum_mm", 0.0))
                        cond_txt = tm_item.get("condition_text", "")
                        rain_exp = precip_sum > 0.5 or any(
                            w in cond_txt.lower() for w in ["rain", "drizzle", "shower", "thunderstorm"]
                        )
                        conds["tomorrow"] = {
                            "date": tm_item.get("date"),
                            "condition_text": cond_txt,
                            "temperature_max_celsius": tm_item.get("temperature_max_celsius"),
                            "temperature_min_celsius": tm_item.get("temperature_min_celsius"),
                            "precipitation_sum_mm": precip_sum,
                            "rain_expected": rain_exp,
                        }
                    structured["weather"] = conds
                    loc_title = eff_loc_name or f"Coordinates ({round(eff_lat, 2)}, {round(eff_lon, 2)})"
                    weather_lines = ["### Local Weather (Real/Live Cache):"]
                    weather_lines.append(f"- Location: {loc_title}")
                    if "temperature_celsius" in conds:
                        weather_lines.append(f"- Temperature: {conds['temperature_celsius']}°C")
                    cond_text = conds.get("condition_text") or conds.get("condition")
                    if cond_text:
                        weather_lines.append(f"- Condition: {cond_text}")
                    prompt_sections.append("\n".join(weather_lines))

        # 5. Attached Image Information (if provided)
        if image_metadata:
            prompt_sections.append(
                f"### Farmer-Provided Visual Image Context:\n"
                f"- Attached File: {image_metadata.get('filename', 'image.jpg')}\n"
                f"- Media Type: {image_metadata.get('mime_type', 'image/jpeg')}\n"
                f"- Dimensions: {image_metadata.get('width', 'unknown')}x{image_metadata.get('height', 'unknown')}\n"
                f"- Note: The farmer attached this image to accompany their query."
            )

        # 6. Conversation History
        conversation_history: List[Dict[str, str]] = []
        if conversation_id:
            conv = await self.advisory_repo.get_with_messages(conversation_id)
            if conv and conv.messages:
                # Include up to last 6 messages
                recent_msgs = conv.messages[-6:]
                for msg in recent_msgs:
                    conversation_history.append(
                        {
                            "role": msg.sender_role,
                            "text": msg.message_text,
                        }
                    )

        # Build human-readable context summary
        summary = {
            "has_profile": structured["farmer_profile"] is not None,
            "has_crop_recommendation": structured["crop_recommendation"] is not None,
            "has_disease_diagnosis": structured["disease_diagnosis"] is not None,
            "has_weather": structured["weather"] is not None,
            "has_attached_image": image_metadata is not None,
            "language": language,
            "history_turns": len(conversation_history),
        }

        formatted_context_text = (
            "\n\n".join(prompt_sections)
            if prompt_sections
            else "No prior farmer profile or diagnostic records found on file."
        )

        return AssembledContext(
            structured_context=structured,
            context_summary=summary,
            formatted_prompt_context=formatted_context_text,
            conversation_history=conversation_history,
        )
