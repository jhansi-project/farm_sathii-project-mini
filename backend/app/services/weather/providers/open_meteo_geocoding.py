import logging
import unicodedata
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings
from app.services.weather.exceptions import WeatherNetworkError, WeatherProviderError, WeatherProviderTimeoutError
from app.services.weather.providers.base import BaseGeocodingProvider

logger = logging.getLogger(__name__)


def _normalize_text(s: str) -> str:
    """Strips accents and diacritical marks (e.g. Miyāpur -> miyapur)."""
    if not s:
        return ""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


class OpenMeteoGeocodingProvider(BaseGeocodingProvider):
    """
    Open-Meteo Geocoding provider.
    Converts city/town/village query into geographic coordinates.
    Includes dynamic compound query decomposition and a secondary Nominatim fallback
    for rural localities, mandals, and composite location searches.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        transport: Optional[httpx.BaseTransport] = None,
    ):
        self.base_url = (base_url or settings.WEATHER_GEOCODING_API_BASE_URL).rstrip("/")
        self.timeout_seconds = timeout_seconds or settings.WEATHER_TIMEOUT_SECONDS
        self.transport = transport

    def is_available(self) -> bool:
        return bool(self.base_url)

    def _decompose_query(self, query: str) -> tuple[str, list[str]]:
        """
        Decomposes compound query into primary search term and administrative qualifiers.
        E.g. 'Miyapur, Telangana' -> ('Miyapur', ['telangana'])
             'Miyapur, Hyderabad' -> ('Miyapur', ['hyderabad'])
             'Bowrampet, Dundigal' -> ('Bowrampet', ['dundigal'])
             'Hyderabad' -> ('Hyderabad', [])
        """
        parts = [p.strip() for p in query.split(",") if p.strip()]
        if not parts:
            return query.strip(), []
        primary = parts[0]
        qualifiers = [_normalize_text(p) for p in parts[1:] if _normalize_text(p)]
        return primary, qualifiers

    async def _search_open_meteo(
        self, client: httpx.AsyncClient, name: str, count: int = 10
    ) -> List[Dict[str, Any]]:
        """Queries Open-Meteo search API by primary place name."""
        url = f"{self.base_url}/search"
        params = {
            "name": name,
            "count": min(max(count, 1), 10),
            "language": "en",
            "format": "json",
        }
        res = await client.get(url, params=params)
        res.raise_for_status()
        data = res.json()
        raw_results = data.get("results", []) if isinstance(data, dict) else []

        normalized = []
        for item in raw_results:
            if not isinstance(item, dict):
                continue
            admin1 = str(item.get("admin1") or "").strip()
            admin2 = str(item.get("admin2") or "").strip()
            admin3 = str(item.get("admin3") or "").strip()
            country = str(item.get("country") or "").strip()
            name_val = str(item.get("name") or "").strip()
            hierarchy = _normalize_text(f"{name_val} {admin1} {admin2} {admin3} {country}")

            normalized.append(
                {
                    "id": item.get("id"),
                    "name": name_val,
                    "latitude": float(item.get("latitude", 0.0)),
                    "longitude": float(item.get("longitude", 0.0)),
                    "state": admin1 or None,
                    "country": country or None,
                    "_hierarchy": hierarchy,
                }
            )
        return normalized

    def _filter_by_qualifiers(
        self, candidates: List[Dict[str, Any]], qualifiers: List[str]
    ) -> List[Dict[str, Any]]:
        """Filters candidate results by administrative qualifiers."""
        if not qualifiers:
            return candidates

        # First priority: items matching all qualifiers in hierarchy
        all_match = [
            c for c in candidates
            if all(q in c.get("_hierarchy", "") for q in qualifiers)
        ]
        if all_match:
            return all_match

        # Second priority: items matching any qualifier
        any_match = [
            c for c in candidates
            if any(q in c.get("_hierarchy", "") for q in qualifiers)
        ]
        return any_match

    async def _search_nominatim_fallback(
        self, client: httpx.AsyncClient, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Secondary fallback geocoding using OpenStreetMap Nominatim.
        Only called when Open-Meteo yields 0 results, fails, or cannot match compound qualifiers.
        Respects Nominatim usage policies with identifiable User-Agent.
        """
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query,
            "format": "json",
            "countrycodes": "in",
            "addressdetails": 1,
            "limit": min(max(limit, 1), 10),
        }
        headers = {"User-Agent": "FarmSathi-DigitalAgriculture/1.0"}
        res = await client.get(url, params=params, headers=headers)
        if res.status_code != 200:
            logger.warning(f"Nominatim fallback geocoding returned HTTP {res.status_code}")
            return []

        data = res.json()
        if not isinstance(data, list):
            return []

        results = []
        for item in data:
            if not isinstance(item, dict):
                continue
            addr = item.get("address") if isinstance(item.get("address"), dict) else {}
            loc_name = (
                item.get("name")
                or addr.get("village")
                or addr.get("town")
                or addr.get("city")
                or addr.get("suburb")
                or addr.get("county")
                or (str(item.get("display_name", "")).split(",")[0].strip())
            )
            state = addr.get("state") or addr.get("state_district") or None
            country = addr.get("country") or "India"
            place_id = item.get("place_id")
            int_id = None
            if place_id is not None:
                try:
                    int_id = int(place_id)
                except (ValueError, TypeError):
                    int_id = None

            try:
                lat = float(item.get("lat", 0.0))
                lon = float(item.get("lon", 0.0))
            except (ValueError, TypeError):
                continue

            results.append(
                {
                    "id": int_id,
                    "name": str(loc_name),
                    "latitude": lat,
                    "longitude": lon,
                    "state": state,
                    "country": country,
                }
            )
        return results

    async def search_location(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        clean_q = query.strip()
        if not clean_q or len(clean_q) < 2:
            return []

        primary_term, qualifiers = self._decompose_query(clean_q)
        term_to_search = primary_term if len(primary_term) >= 2 else clean_q

        open_meteo_candidates: List[Dict[str, Any]] = []
        open_meteo_failed = False
        last_exc: Optional[Exception] = None

        async with httpx.AsyncClient(
            timeout=float(self.timeout_seconds), transport=self.transport
        ) as client:
            # Step 1: Query Primary Provider (Open-Meteo)
            try:
                open_meteo_candidates = await self._search_open_meteo(
                    client, term_to_search, count=min(max(limit * 2, 5), 10)
                )
            except (httpx.TimeoutException, httpx.RequestError, httpx.HTTPStatusError) as exc:
                logger.warning(f"Open-Meteo geocoding search failed or timed out for '{clean_q}': {exc}")
                open_meteo_failed = True
                last_exc = exc
            except Exception as exc:
                logger.warning(f"Unexpected error in Open-Meteo geocoding for '{clean_q}': {exc}")
                open_meteo_failed = True
                last_exc = exc

            # If qualifiers exist, filter candidates
            if open_meteo_candidates and qualifiers:
                matching_candidates = self._filter_by_qualifiers(open_meteo_candidates, qualifiers)
                if matching_candidates:
                    return [
                        {k: v for k, v in item.items() if not k.startswith("_")}
                        for item in matching_candidates[:limit]
                    ]
                # If qualifiers were specified and Open-Meteo returned 0 matches for them,
                # fall through to Nominatim fallback below!
            elif open_meteo_candidates and not qualifiers:
                # Open-Meteo matched directly without qualifiers
                return [
                    {k: v for k, v in item.items() if not k.startswith("_")}
                    for item in open_meteo_candidates[:limit]
                ]

            # Step 2: Query Secondary Fallback (Nominatim OpenStreetMap)
            # Only reached if:
            # - Open-Meteo yielded 0 results, OR
            # - Open-Meteo failed/timed out, OR
            # - Open-Meteo results did not match user-specified qualifiers.
            try:
                fallback_results = await self._search_nominatim_fallback(
                    client, clean_q, limit=limit
                )
                if fallback_results:
                    return fallback_results[:limit]
            except Exception as exc:
                logger.warning(f"Nominatim fallback geocoding failed for '{clean_q}': {exc}")
                if open_meteo_failed and last_exc:
                    if isinstance(last_exc, httpx.TimeoutException):
                        raise WeatherProviderTimeoutError("Geocoding provider request timed out") from last_exc
                    if isinstance(last_exc, httpx.RequestError):
                        raise WeatherNetworkError("Failed to connect to geocoding network") from last_exc
                    raise WeatherProviderError(f"Geocoding service returned error: {last_exc}") from last_exc

            return []

    async def reverse_geocode(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Reverse geocodes coordinates to a human-readable city/district/state location.
        Tries BigDataCloud client reverse geocoding first, then OpenStreetMap Nominatim.
        Never fabricates arbitrary locations.
        """
        # 1. Try BigDataCloud open client API
        try:
            url = "https://api.bigdatacloud.net/data/reverse-geocode-client"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "localityLanguage": "en",
            }
            async with httpx.AsyncClient(
                timeout=float(self.timeout_seconds), transport=self.transport
            ) as client:
                res = await client.get(url, params=params)
                if res.status_code == 200:
                    d = res.json()
                    city = d.get("city") or d.get("locality") or d.get("principalSubdivisionCode") or ""
                    state = d.get("principalSubdivision") or ""
                    country = d.get("countryName") or "India"
                    formatted = f"{city}, {state}".strip(", ") if city else state or country
                    if formatted:
                        return {
                            "id": None,
                            "name": city or state or "Local Farm",
                            "latitude": latitude,
                            "longitude": longitude,
                            "state": state,
                            "country": country,
                        }
        except Exception as e:
            logger.warning(f"BigDataCloud reverse geocoding failed: {e}")

        # 2. Try Nominatim as fallback
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json"
            headers = {"User-Agent": "FarmSathi-DigitalAgriculture/1.0"}
            async with httpx.AsyncClient(
                timeout=float(self.timeout_seconds), transport=self.transport
            ) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    d = res.json()
                    addr = d.get("address", {})
                    city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county") or ""
                    state = addr.get("state") or ""
                    country = addr.get("country") or "India"
                    if city or state:
                        return {
                            "id": None,
                            "name": city or state,
                            "latitude": latitude,
                            "longitude": longitude,
                            "state": state,
                            "country": country,
                        }
        except Exception as e:
            logger.warning(f"Nominatim reverse geocoding failed: {e}")

        return {
            "id": None,
            "name": "Current Location",
            "latitude": latitude,
            "longitude": longitude,
            "state": "",
            "country": "India",
        }
