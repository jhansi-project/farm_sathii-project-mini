"""
FastAPI router for weather endpoints.
Provides real weather data, caching, and geocoding with non-blocking location fallbacks.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.common import StandardResponse
from app.schemas.weather import WeatherResponse, GeocodingResultItem
from app.services.weather import WeatherService
from app.services.weather.exceptions import (
    InvalidCoordinateError,
    WeatherLocationUnavailableError,
    WeatherProviderError,
    WeatherProviderTimeoutError,
    WeatherNetworkError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/weather", tags=["Weather"])


def get_weather_service(session: AsyncSession = Depends(get_db)) -> WeatherService:
    """Dependency provider for WeatherService."""
    return WeatherService(session)


@router.get(
    "/current",
    response_model=StandardResponse[WeatherResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Current Weather",
    description="Retrieve live or cached current weather conditions for given coordinates (lat -90..90, lon -180..180).",
)
async def get_current_weather(
    latitude: float = Query(..., description="Latitude (-90 to 90)"),
    longitude: float = Query(..., description="Longitude (-180 to 180)"),
    location_name: Optional[str] = Query(None, description="Optional human-readable location label"),
    service: WeatherService = Depends(get_weather_service),
):
    try:
        weather_data = await service.get_current_weather(
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
        )

        return StandardResponse(
            success=True,
            data=weather_data,
            message="Current weather retrieved successfully",
        )
    except InvalidCoordinateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except WeatherProviderTimeoutError as e:
        logger.error("Weather provider timeout: %s", e)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Weather service provider timed out: {str(e)}",
        )
    except (WeatherNetworkError, WeatherProviderError) as e:
        logger.error("Weather provider error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Weather service provider error: {str(e)}",
        )


@router.get(
    "/forecast",
    response_model=StandardResponse[WeatherResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Weather Forecast",
    description="Retrieve live or cached multi-day forecast (1-16 days) for given coordinates.",
)
async def get_weather_forecast(
    latitude: float = Query(..., description="Latitude (-90 to 90)"),
    longitude: float = Query(..., description="Longitude (-180 to 180)"),
    days: int = Query(7, ge=1, le=16, description="Number of forecast days"),
    location_name: Optional[str] = Query(None, description="Optional human-readable location label"),
    service: WeatherService = Depends(get_weather_service),
):
    try:
        weather_data = await service.get_forecast(
            latitude=latitude,
            longitude=longitude,
            days=days,
            location_name=location_name,
        )
        return StandardResponse(
            success=True,
            data=weather_data,
            message="Weather forecast retrieved successfully",
        )
    except InvalidCoordinateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except WeatherProviderTimeoutError as e:
        logger.error("Weather provider timeout: %s", e)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Weather service provider timed out: {str(e)}",
        )
    except (WeatherNetworkError, WeatherProviderError) as e:
        logger.error("Weather provider error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Weather service provider error: {str(e)}",
        )


@router.get(
    "/profile",
    response_model=StandardResponse[WeatherResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Weather for Authenticated Farmer Profile",
    description="Retrieve current weather based on the registered coordinates in the authenticated farmer's profile.",
)
async def get_profile_weather(
    current_user: User = Depends(get_current_active_user),
    service: WeatherService = Depends(get_weather_service),
):
    try:
        weather_data = await service.get_weather_for_farmer_profile(user_id=current_user.id)
        return StandardResponse(
            success=True,
            data=weather_data,
            message="Profile weather retrieved successfully",
        )
    except WeatherLocationUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidCoordinateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except WeatherProviderTimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Weather service provider timed out: {str(e)}",
        )
    except (WeatherNetworkError, WeatherProviderError) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Weather service provider error: {str(e)}",
        )


@router.get(
    "/search",
    response_model=StandardResponse[List[GeocodingResultItem]],
    status_code=status.HTTP_200_OK,
    summary="Search Locations (Geocoding)",
    description="Search geographic locations and return coordinates for manual location selection.",
)
async def search_locations(
    query: str = Query(..., min_length=2, max_length=100, description="City or village name"),
    limit: int = Query(5, ge=1, le=10, description="Max results"),
    service: WeatherService = Depends(get_weather_service),
):
    try:
        results = await service.search_locations(query=query, limit=limit)
        return StandardResponse(
            success=True,
            data=results,
            message=f"Found {len(results)} locations",
        )
    except Exception as e:
        logger.error("Geocoding search failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to resolve locations from geocoding provider",
        )


@router.get(
    "/reverse-geocode",
    response_model=StandardResponse[GeocodingResultItem],
    status_code=status.HTTP_200_OK,
    summary="Reverse Geocode Coordinates",
    description="Resolve GPS coordinates into a human-readable city/district/state location for farmer UI.",
)
async def reverse_geocode(
    latitude: float = Query(..., description="Latitude (-90 to 90)"),
    longitude: float = Query(..., description="Longitude (-180 to 180)"),
    service: WeatherService = Depends(get_weather_service),
):
    try:
        result = await service.reverse_geocode(latitude=latitude, longitude=longitude)
        return StandardResponse(
            success=True,
            data=result,
            message="Location resolved successfully",
        )
    except Exception as e:
        logger.warning("Reverse geocoding failed: %s", e)
        return StandardResponse(
            success=True,
            data=GeocodingResultItem(
                name="Current Location",
                latitude=latitude,
                longitude=longitude,
                country="India",
            ),
            message="Default location fallback",
        )

