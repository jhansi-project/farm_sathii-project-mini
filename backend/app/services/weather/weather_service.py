"""
Weather Service orchestrating caching, provider integration, and coordinate validation.
Follows clean architecture and clean service boundaries.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.weather_repo import WeatherCacheRepository
from app.repositories.profile_repo import FarmerProfileRepository
from app.schemas.weather import (
    CurrentWeatherCondition,
    DailyForecastItem,
    LocationInfo,
    WeatherResponse,
    GeocodingResultItem,
)
from app.services.weather.exceptions import (
    WeatherError,
    InvalidCoordinateError,
    WeatherLocationUnavailableError,
    WeatherProviderError,
    WeatherProviderTimeoutError,
    WeatherNetworkError,
)
from app.services.weather.providers.base import BaseWeatherProvider, BaseGeocodingProvider
from app.services.weather.providers.open_meteo import OpenMeteoWeatherProvider
from app.services.weather.providers.open_meteo_geocoding import OpenMeteoGeocodingProvider

logger = logging.getLogger(__name__)


def validate_coordinates(latitude: float, longitude: float) -> Tuple[float, float]:
    """
    Validate latitude (-90 to 90) and longitude (-180 to 180).
    Raises InvalidCoordinateError if values are outside allowed bounds.
    """
    if latitude is None or longitude is None:
        raise InvalidCoordinateError("Latitude and longitude must both be provided.")
    if not (-90.0 <= latitude <= 90.0):
        raise InvalidCoordinateError(f"Latitude must be between -90 and 90. Got: {latitude}")
    if not (-180.0 <= longitude <= 180.0):
        raise InvalidCoordinateError(f"Longitude must be between -180 and 180. Got: {longitude}")
    return float(latitude), float(longitude)


def make_cache_key(latitude: float, longitude: float) -> str:
    """Standardized coordinate cache key rounding to 2 decimal places (~1.1km precision)."""
    return f"{round(float(latitude), 2)}_{round(float(longitude), 2)}"


class WeatherService:
    """
    Service responsible for coordinating weather fetching, PostgreSQL caching,
    coordinate validation, and geocoding resolution.
    """

    def __init__(
        self,
        db_session: AsyncSession,
        weather_provider: Optional[BaseWeatherProvider] = None,
        geocoding_provider: Optional[BaseGeocodingProvider] = None,
    ):
        self.session = db_session
        self.weather_repo = WeatherCacheRepository(db_session)
        self.profile_repo = FarmerProfileRepository(db_session)
        self.weather_provider = weather_provider or OpenMeteoWeatherProvider()
        self.geocoding_provider = geocoding_provider or OpenMeteoGeocodingProvider()

    async def get_current_weather(
        self,
        latitude: float,
        longitude: float,
        location_name: Optional[str] = None,
    ) -> WeatherResponse:
        """
        Retrieve current weather for given coordinates.
        Checks cache first; fetches from provider on miss/expiry; saves to cache.
        """
        lat, lon = validate_coordinates(latitude, longitude)
        cache_key = make_cache_key(lat, lon)

        # 1. Check fresh cache
        cached_entry = await self.weather_repo.get_valid_cache(cache_key)
        if cached_entry and cached_entry.current_conditions:
            logger.info("Weather cache hit (fresh) for key=%s", cache_key)
            conditions = CurrentWeatherCondition.model_validate(cached_entry.current_conditions)
            forecast = (
                [DailyForecastItem.model_validate(item) for item in cached_entry.forecast_daily]
                if cached_entry.forecast_daily
                else None
            )
            return WeatherResponse(
                location=LocationInfo(
                    latitude=float(cached_entry.latitude),
                    longitude=float(cached_entry.longitude),
                    name=location_name,
                ),
                current=conditions,
                forecast=forecast,
                is_cached=True,
                cached_at=cached_entry.fetched_at,
                expires_at=cached_entry.expires_at,
                provider_name="cache",
                status="success",
            )

        # 2. Cache miss or expired: fetch from provider
        try:
            provider_data = await self.weather_provider.get_weather(lat, lon, days=7)

            # Store into PostgreSQL WeatherCache
            cached = await self.weather_repo.upsert_cache(
                cache_key=cache_key,
                latitude=lat,
                longitude=lon,
                current_conditions=provider_data.current,
                forecast_daily=provider_data.forecast,
                ttl_minutes=settings.WEATHER_CACHE_TTL_MINUTES,
            )

            current_obj = CurrentWeatherCondition.model_validate(provider_data.current)
            forecast_objs = [DailyForecastItem.model_validate(item) for item in provider_data.forecast]

            return WeatherResponse(
                location=LocationInfo(latitude=lat, longitude=lon, name=location_name),
                current=current_obj,
                forecast=forecast_objs,
                is_cached=False,
                cached_at=cached.fetched_at if cached else None,
                expires_at=cached.expires_at if cached else None,
                provider_name=provider_data.provider_name,
                status="success",
            )

        except (WeatherProviderTimeoutError, WeatherNetworkError, WeatherProviderError) as exc:
            # If provider fails, check if we have any stale cache entry
            stale_entry = await self.weather_repo.get_by_key(cache_key)
            if stale_entry and stale_entry.current_conditions:
                logger.warning(
                    "Provider failed (%s). Serving stale cache for key=%s",
                    str(exc),
                    cache_key,
                )
                conditions = CurrentWeatherCondition.model_validate(stale_entry.current_conditions)
                forecast = (
                    [DailyForecastItem.model_validate(item) for item in stale_entry.forecast_daily]
                    if stale_entry.forecast_daily
                    else None
                )
                return WeatherResponse(
                    location=LocationInfo(
                        latitude=float(stale_entry.latitude),
                        longitude=float(stale_entry.longitude),
                        name=location_name,
                    ),
                    current=conditions,
                    forecast=forecast,
                    is_cached=True,
                    cached_at=stale_entry.fetched_at,
                    expires_at=stale_entry.expires_at,
                    provider_name="cache_stale",
                    status="stale_cached",
                    error_message=str(exc),
                )
            raise exc

    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7,
        location_name: Optional[str] = None,
    ) -> WeatherResponse:
        """
        Retrieve weather forecast (up to 14 days) for given coordinates.
        Checks cache first; fetches from provider on miss/expiry; saves to cache.
        """
        lat, lon = validate_coordinates(latitude, longitude)
        days = max(1, min(days, 14))
        cache_key = make_cache_key(lat, lon)

        # 1. Check fresh cache
        cached_entry = await self.weather_repo.get_valid_cache(cache_key)
        if cached_entry and cached_entry.forecast_daily and len(cached_entry.forecast_daily) >= days:
            logger.info("Weather forecast cache hit (fresh) for key=%s", cache_key)
            forecast = [DailyForecastItem.model_validate(item) for item in cached_entry.forecast_daily[:days]]
            current = (
                CurrentWeatherCondition.model_validate(cached_entry.current_conditions)
                if cached_entry.current_conditions
                else None
            )
            return WeatherResponse(
                location=LocationInfo(
                    latitude=float(cached_entry.latitude),
                    longitude=float(cached_entry.longitude),
                    name=location_name,
                ),
                current=current,
                forecast=forecast,
                is_cached=True,
                cached_at=cached_entry.fetched_at,
                expires_at=cached_entry.expires_at,
                provider_name="cache",
                status="success",
            )

        # 2. Fetch from provider
        try:
            provider_data = await self.weather_provider.get_weather(lat, lon, days=days)

            # Store in cache
            cached = await self.weather_repo.upsert_cache(
                cache_key=cache_key,
                latitude=lat,
                longitude=lon,
                current_conditions=provider_data.current,
                forecast_daily=provider_data.forecast,
                ttl_minutes=settings.WEATHER_CACHE_TTL_MINUTES,
            )

            return WeatherResponse(
                location=LocationInfo(latitude=lat, longitude=lon, name=location_name),
                current=CurrentWeatherCondition.model_validate(provider_data.current),
                forecast=[DailyForecastItem.model_validate(item) for item in provider_data.forecast[:days]],
                is_cached=False,
                cached_at=cached.fetched_at if cached else None,
                expires_at=cached.expires_at if cached else None,
                provider_name=provider_data.provider_name,
                status="success",
            )
        except (WeatherProviderTimeoutError, WeatherNetworkError, WeatherProviderError) as exc:
            stale_entry = await self.weather_repo.get_by_key(cache_key)
            if stale_entry and stale_entry.forecast_daily:
                logger.warning("Serving stale forecast cache for key=%s", cache_key)
                return WeatherResponse(
                    location=LocationInfo(
                        latitude=float(stale_entry.latitude),
                        longitude=float(stale_entry.longitude),
                        name=location_name,
                    ),
                    current=CurrentWeatherCondition.model_validate(stale_entry.current_conditions)
                    if stale_entry.current_conditions
                    else None,
                    forecast=[DailyForecastItem.model_validate(item) for item in stale_entry.forecast_daily[:days]],
                    is_cached=True,
                    cached_at=stale_entry.fetched_at,
                    expires_at=stale_entry.expires_at,
                    provider_name="cache_stale",
                    status="stale_cached",
                    error_message=str(exc),
                )
            raise exc

    async def get_weather_for_farmer_profile(self, user_id: str) -> WeatherResponse:
        """
        Retrieve weather using the authenticated farmer profile's registered coordinates.
        Does not accept another user's ID from external input.
        """
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise WeatherLocationUnavailableError("Farmer profile not found.")

        if profile.latitude is None or profile.longitude is None:
            raise WeatherLocationUnavailableError(
                "Farmer profile does not have location coordinates configured. "
                "Please enable location permission or set coordinates in profile."
            )

        location_name = f"{profile.village or profile.taluka or profile.district or ''}, {profile.state or ''}".strip(", ")
        if not location_name:
            location_name = None

        return await self.get_current_weather(
            latitude=float(profile.latitude),
            longitude=float(profile.longitude),
            location_name=location_name,
        )

    async def search_locations(self, query: str, limit: int = 5) -> List[GeocodingResultItem]:
        """Search locations by name using geocoding provider."""
        if not query or len(query.strip()) < 2:
            return []
        results = await self.geocoding_provider.search_location(query.strip(), limit=limit)
        return [GeocodingResultItem.model_validate(r) for r in results]

    async def reverse_geocode(self, latitude: float, longitude: float) -> GeocodingResultItem:
        """Resolve GPS coordinates into a human-readable city/state location."""
        lat, lon = validate_coordinates(latitude, longitude)
        if hasattr(self.geocoding_provider, "reverse_geocode"):
            result = await self.geocoding_provider.reverse_geocode(lat, lon)
            return GeocodingResultItem.model_validate(result)
        return GeocodingResultItem(name="Current Location", latitude=lat, longitude=lon, country="India")
