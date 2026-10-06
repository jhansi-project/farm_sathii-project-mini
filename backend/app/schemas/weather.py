from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CoordinateQuery(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude between -90 and 90 degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude between -180 and 180 degrees")


class CurrentWeatherCondition(BaseModel):
    temperature_celsius: float = Field(..., description="Observed temperature in Celsius")
    relative_humidity_percent: float = Field(..., description="Relative humidity percentage")
    precipitation_mm: float = Field(..., description="Current precipitation in millimeters")
    weather_code: int = Field(..., description="WMO weather interpretation code")
    condition_text: str = Field(..., description="Human-readable weather description")
    condition_icon: str = Field(..., description="Material Symbols icon name")
    wind_speed_kmh: Optional[float] = Field(None, description="Wind speed in km/h")
    observation_time: str = Field(..., description="Observation timestamp in ISO format")

    model_config = ConfigDict(from_attributes=True)


class DailyForecastItem(BaseModel):
    date: str = Field(..., description="Forecast date (YYYY-MM-DD)")
    temperature_max_celsius: float = Field(..., description="Maximum forecasted temperature in Celsius")
    temperature_min_celsius: float = Field(..., description="Minimum forecasted temperature in Celsius")
    precipitation_sum_mm: float = Field(..., description="Total forecasted precipitation in mm")
    weather_code: int = Field(..., description="WMO weather interpretation code")
    condition_text: str = Field(..., description="Human-readable condition description")
    condition_icon: str = Field(..., description="Material Symbols icon name")

    model_config = ConfigDict(from_attributes=True)


class LocationInfo(BaseModel):
    latitude: float
    longitude: float
    name: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class WeatherResponse(BaseModel):
    location: LocationInfo
    current: Optional[CurrentWeatherCondition] = None
    forecast: Optional[List[DailyForecastItem]] = None
    is_cached: bool = False
    cached_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    provider_name: str
    status: str = "success"  # "success" | "stale_cached" | "provider_unavailable" | "error"
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class GeocodingResultItem(BaseModel):
    id: Optional[int] = None
    name: str
    latitude: float
    longitude: float
    state: Optional[str] = None
    country: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
