import logging
from typing import Optional
import httpx

from app.core.config import settings
from app.services.weather.condition_mapper import get_condition_from_wmo_code
from app.services.weather.exceptions import (
    WeatherNetworkError,
    WeatherProviderError,
    WeatherProviderTimeoutError,
)
from app.services.weather.providers.base import (
    BaseWeatherProvider,
    WeatherProviderData,
)

logger = logging.getLogger(__name__)


class OpenMeteoWeatherProvider(BaseWeatherProvider):
    """
    Open-Meteo weather provider implementation.
    Fetches real weather observation and forecast asynchronously via HTTP.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ):
        self.base_url = (base_url or settings.WEATHER_API_BASE_URL).rstrip("/")
        self.timeout_seconds = timeout_seconds or settings.WEATHER_TIMEOUT_SECONDS

    def is_available(self) -> bool:
        return bool(self.base_url)

    def get_name(self) -> str:
        return "open_meteo"

    async def get_weather(
        self, latitude: float, longitude: float, days: int = 7
    ) -> WeatherProviderData:
        url = f"{self.base_url}/forecast"
        safe_days = min(max(days, 1), 14)

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto",
            "forecast_days": safe_days,
        }

        try:
            async with httpx.AsyncClient(timeout=float(self.timeout_seconds)) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                payload = response.json()

        except httpx.TimeoutException as exc:
            logger.warning(f"Open-Meteo weather request timed out: {exc}")
            raise WeatherProviderTimeoutError("Weather provider request timed out") from exc
        except httpx.HTTPStatusError as exc:
            logger.error(f"Open-Meteo HTTP error {exc.response.status_code}: {exc.response.text}")
            raise WeatherProviderError(
                f"Weather provider returned HTTP {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.RequestError as exc:
            logger.error(f"Open-Meteo network connection error: {exc}")
            raise WeatherNetworkError("Failed to connect to weather provider network") from exc
        except Exception as exc:
            logger.exception("Unexpected error communicating with Open-Meteo")
            raise WeatherProviderError(f"Unexpected provider error: {exc}") from exc

        # Parse & map provider response
        try:
            raw_current = payload.get("current", {})
            wmo_code = int(raw_current.get("weather_code", 0))
            condition_text, condition_icon = get_condition_from_wmo_code(wmo_code)

            current_data = {
                "temperature_celsius": float(raw_current.get("temperature_2m", 0.0)),
                "relative_humidity_percent": float(raw_current.get("relative_humidity_2m", 0.0)),
                "precipitation_mm": float(raw_current.get("precipitation", 0.0)),
                "weather_code": wmo_code,
                "condition_text": condition_text,
                "condition_icon": condition_icon,
                "wind_speed_kmh": (
                    float(raw_current["wind_speed_10m"])
                    if "wind_speed_10m" in raw_current and raw_current["wind_speed_10m"] is not None
                    else None
                ),
                "observation_time": str(raw_current.get("time", "")),
            }

            daily_forecast: list = []
            raw_daily = payload.get("daily", {})
            times = raw_daily.get("time", [])
            max_temps = raw_daily.get("temperature_2m_max", [])
            min_temps = raw_daily.get("temperature_2m_min", [])
            precip_sums = raw_daily.get("precipitation_sum", [])
            daily_codes = raw_daily.get("weather_code", [])

            for i in range(len(times)):
                d_code = int(daily_codes[i]) if i < len(daily_codes) else 0
                d_text, d_icon = get_condition_from_wmo_code(d_code)
                daily_forecast.append(
                    {
                        "date": str(times[i]),
                        "temperature_max_celsius": float(max_temps[i]) if i < len(max_temps) else 0.0,
                        "temperature_min_celsius": float(min_temps[i]) if i < len(min_temps) else 0.0,
                        "precipitation_sum_mm": float(precip_sums[i]) if i < len(precip_sums) else 0.0,
                        "weather_code": d_code,
                        "condition_text": d_text,
                        "condition_icon": d_icon,
                    }
                )

            return WeatherProviderData(
                current=current_data,
                forecast=daily_forecast,
                provider_name=self.get_name(),
            )
        except (KeyError, ValueError, TypeError) as exc:
            logger.error(f"Malformed payload from Open-Meteo: {exc}")
            raise WeatherProviderError("Malformed response structure from weather provider") from exc
