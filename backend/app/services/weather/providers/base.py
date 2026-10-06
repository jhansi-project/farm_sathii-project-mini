from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pydantic import BaseModel


class WeatherProviderData(BaseModel):
    current: Dict[str, Any]
    forecast: List[Dict[str, Any]]
    provider_name: str


class BaseWeatherProvider(ABC):
    """Abstract interface for weather data providers."""

    @abstractmethod
    async def get_weather(
        self, latitude: float, longitude: float, days: int = 7
    ) -> WeatherProviderData:
        """Fetch current weather and daily forecast for the given geographic coordinates."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and operational."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the unique name of this provider."""
        pass


class BaseGeocodingProvider(ABC):
    """Abstract interface for geocoding location search."""

    @abstractmethod
    async def search_location(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search locations by name/query and return normalized coordinates."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if geocoding provider is operational."""
        pass
