"""
Mock Weather and Geocoding Providers for deterministic unit and integration tests.
Does not make any live network requests.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.services.weather.providers.base import (
    BaseWeatherProvider,
    BaseGeocodingProvider,
    WeatherProviderData,
)
from app.services.weather.exceptions import (
    WeatherProviderTimeoutError,
    WeatherNetworkError,
    WeatherProviderError,
)


class MockWeatherProvider(BaseWeatherProvider):
    """Deterministic mock weather provider for testing."""

    def __init__(
        self,
        should_timeout: bool = False,
        should_fail_network: bool = False,
        should_fail_http: bool = False,
        http_status_code: int = 500,
        custom_current_data: Optional[Dict[str, Any]] = None,
        custom_forecast_data: Optional[List[Dict[str, Any]]] = None,
    ):
        self.should_timeout = should_timeout
        self.should_fail_network = should_fail_network
        self.should_fail_http = should_fail_http
        self.http_status_code = http_status_code
        self.custom_current_data = custom_current_data
        self.custom_forecast_data = custom_forecast_data
        self.call_count = 0

    def is_available(self) -> bool:
        return True

    def get_name(self) -> str:
        return "mock_weather_provider"

    def _check_fault_injection(self) -> None:
        self.call_count += 1
        if self.should_timeout:
            raise WeatherProviderTimeoutError("Mock provider timeout")
        if self.should_fail_network:
            raise WeatherNetworkError("Mock network failure")
        if self.should_fail_http:
            raise WeatherProviderError(
                f"Mock HTTP error: {self.http_status_code}",
                status_code=self.http_status_code,
            )

    async def get_weather(
        self, latitude: float, longitude: float, days: int = 7
    ) -> WeatherProviderData:
        self._check_fault_injection()

        current = self.custom_current_data or {
            "temperature_celsius": 26.5,
            "relative_humidity_percent": 68.0,
            "precipitation_mm": 0.0,
            "weather_code": 1,
            "condition_text": "Mainly Clear",
            "condition_icon": "sunny",
            "wind_speed_kmh": 12.4,
            "observation_time": datetime.now(timezone.utc).isoformat(),
        }

        forecast = self.custom_forecast_data or [
            {
                "date": f"2026-09-2{i}",
                "temperature_max_celsius": 30.0 + (i * 0.5),
                "temperature_min_celsius": 20.0 + (i * 0.2),
                "precipitation_sum_mm": 0.0 if i % 2 == 0 else 3.5,
                "weather_code": 1 if i % 2 == 0 else 61,
                "condition_text": "Mainly Clear" if i % 2 == 0 else "Slight Rain",
                "condition_icon": "sunny" if i % 2 == 0 else "rainy",
            }
            for i in range(days)
        ]

        return WeatherProviderData(
            current=current,
            forecast=forecast[:days],
            provider_name=self.get_name(),
        )


class MockGeocodingProvider(BaseGeocodingProvider):
    """Deterministic mock geocoding provider for testing."""

    def __init__(
        self,
        should_fail: bool = False,
        results_override: Optional[List[Dict[str, Any]]] = None,
    ):
        self.should_fail = should_fail
        self.results_override = results_override
        self.call_count = 0

    def is_available(self) -> bool:
        return True

    async def search_location(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        self.call_count += 1
        if self.should_fail:
            raise WeatherProviderError("Mock geocoding failed")

        if self.results_override is not None:
            return self.results_override

        if "pune" in query.lower():
            return [
                {
                    "name": "Pune",
                    "latitude": 18.5204,
                    "longitude": 73.8567,
                    "state": "Maharashtra",
                    "country": "India",
                    "country_code": "IN",
                }
            ]
        elif "nagpur" in query.lower():
            return [
                {
                    "name": "Nagpur",
                    "latitude": 21.1458,
                    "longitude": 79.0882,
                    "state": "Maharashtra",
                    "country": "India",
                    "country_code": "IN",
                }
            ]
        return []
