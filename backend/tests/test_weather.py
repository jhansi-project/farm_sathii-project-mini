"""
Comprehensive Test Suite for Phase 8 - Weather + Location Services.
Tests coordinate validation, caching, provider fallback, stale cache behavior,
geocoding search, profile weather, and advisory integration.
All tests use deterministic mock providers without live network calls.
"""

import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import pytest
import httpx
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.weather import get_weather_service
from app.core.database import AsyncSessionLocal
from app.main import app
from app.models.profile import FarmerProfile
from app.models.weather_cache import WeatherCache
from app.repositories.weather_repo import WeatherCacheRepository
from app.services.advisory.context_assembler import ContextAssembler
from app.services.weather.condition_mapper import map_wmo_code_to_condition
from app.services.weather.exceptions import (
    InvalidCoordinateError,
    WeatherProviderTimeoutError,
    WeatherNetworkError,
    WeatherProviderError,
)
from app.services.weather.providers.mock_provider import MockWeatherProvider, MockGeocodingProvider
from app.services.weather.providers.open_meteo_geocoding import OpenMeteoGeocodingProvider
from app.services.weather.weather_service import WeatherService, validate_coordinates, make_cache_key


async def register_farmer(client: AsyncClient, name: str = "Weather Farmer") -> dict:
    unique_phone = f"+9197{uuid.uuid4().hex[:8]}"
    pwd = "FarmerSecret@123"
    res = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": name,
            "phone": unique_phone,
            "password": pwd,
            "preferred_language": "en",
        },
    )
    assert res.status_code == 201
    token = res.json()["data"]["access_token"]
    user_id = res.json()["data"]["user"]["id"]
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "user_id": uuid.UUID(user_id),
        "token": token,
    }


# =========================================================================
# 1. Coordinate Validation Tests
# =========================================================================
def test_valid_coordinates():
    lat, lon = validate_coordinates(18.5204, 73.8567)
    assert lat == 18.5204
    assert lon == 73.8567

    # Edge of valid ranges
    lat, lon = validate_coordinates(90.0, 180.0)
    assert lat == 90.0
    assert lon == 180.0

    lat, lon = validate_coordinates(-90.0, -180.0)
    assert lat == -90.0
    assert lon == -180.0


def test_invalid_coordinates():
    with pytest.raises(InvalidCoordinateError):
        validate_coordinates(91.0, 73.0)

    with pytest.raises(InvalidCoordinateError):
        validate_coordinates(-90.1, 73.0)

    with pytest.raises(InvalidCoordinateError):
        validate_coordinates(18.0, 181.0)

    with pytest.raises(InvalidCoordinateError):
        validate_coordinates(18.0, -180.1)


# =========================================================================
# 2. WMO Weather Code Mapping Tests
# =========================================================================
def test_wmo_code_mapper():
    desc, icon = map_wmo_code_to_condition(0)
    assert desc == "Clear Sky"
    assert icon in ["sunny", "wb_sunny"]

    desc, icon = map_wmo_code_to_condition(63)
    assert "Rain" in desc
    assert icon in ["rainy", "water_drop"]

    desc, icon = map_wmo_code_to_condition(95)
    assert "Thunderstorm" in desc
    assert icon == "thunderstorm"

    # Unknown code falls back safely without error
    desc, icon = map_wmo_code_to_condition(999)
    assert desc == "Unknown"
    assert icon == "cloud"


# =========================================================================
# 3. Weather Endpoints - Coordinate Validation via HTTP
# =========================================================================
@pytest.mark.asyncio
async def test_endpoint_invalid_coordinates(async_client: AsyncClient):
    # Latitude out of bounds
    res = await async_client.get("/api/v1/weather/current?latitude=105.0&longitude=78.0")
    assert res.status_code in [400, 422]

    # Longitude out of bounds
    res = await async_client.get("/api/v1/weather/current?latitude=20.0&longitude=195.0")
    assert res.status_code in [400, 422]

    # Missing parameters
    res = await async_client.get("/api/v1/weather/current?latitude=20.0")
    assert res.status_code == 422


# =========================================================================
# 4. Successful Weather Retrieval & PostgreSQL Caching
# =========================================================================
@pytest.mark.asyncio
async def test_successful_weather_and_caching(async_client: AsyncClient):
    mock_provider = MockWeatherProvider()
    unique_id = uuid.uuid4().int % 1000000
    lat = round(10.0 + (unique_id % 7000) / 100.0, 4)
    lon = round(70.0 + ((unique_id // 7000) % 1500) / 100.0, 4)

    def mock_service_factory(session: AsyncSession = pytest.importorskip("fastapi").Depends(pytest.importorskip("app.core.database").get_db)):
        return WeatherService(session, weather_provider=mock_provider)

    app.dependency_overrides[get_weather_service] = mock_service_factory

    try:
        # First call: Cache miss, fetches from mock provider
        res1 = await async_client.get(f"/api/v1/weather/current?latitude={lat}&longitude={lon}")
        assert res1.status_code == 200
        data1 = res1.json()["data"]
        assert data1["is_cached"] is False

        assert data1["provider_name"] == "mock_weather_provider"
        assert data1["current"]["temperature_celsius"] == 26.5
        assert data1["current"]["relative_humidity_percent"] == 68.0
        assert data1["current"]["condition_text"] == "Mainly Clear"
        assert data1["current"]["condition_icon"] in ["sunny", "wb_sunny"]
        assert mock_provider.call_count >= 1

        first_call_count = mock_provider.call_count

        # Second call with same coordinates: Cache hit, provider not called again
        res2 = await async_client.get(f"/api/v1/weather/current?latitude={lat}&longitude={lon}")
        assert res2.status_code == 200
        data2 = res2.json()["data"]
        assert data2["is_cached"] is True
        assert data2["provider_name"] == "cache"
        assert data2["current"]["temperature_celsius"] == 26.5
        # Call count should NOT have increased because cache served it
        assert mock_provider.call_count == first_call_count

    finally:
        app.dependency_overrides.pop(get_weather_service, None)


# =========================================================================
# 5. Forecast Endpoint Tests
# =========================================================================
@pytest.mark.asyncio
async def test_weather_forecast_endpoint(async_client: AsyncClient):
    mock_provider = MockWeatherProvider()
    lat, lon = 17.3850, 78.4867

    def mock_service_factory(session: AsyncSession = pytest.importorskip("fastapi").Depends(pytest.importorskip("app.core.database").get_db)):
        return WeatherService(session, weather_provider=mock_provider)

    app.dependency_overrides[get_weather_service] = mock_service_factory

    try:
        res = await async_client.get(f"/api/v1/weather/forecast?latitude={lat}&longitude={lon}&days=5")
        assert res.status_code == 200
        data = res.json()["data"]
        assert len(data["forecast"]) == 5
        assert data["forecast"][0]["temperature_max_celsius"] == 30.0
    finally:
        app.dependency_overrides.pop(get_weather_service, None)


# =========================================================================
# 6. Provider Error Handling (Timeout, HTTP Error, Network Failure)
# =========================================================================
@pytest.mark.asyncio
async def test_provider_timeout_error(async_client: AsyncClient):
    # Unique coordinates so no cache exists
    lat, lon = 11.1111, 71.1111
    mock_provider = MockWeatherProvider(should_timeout=True)

    def mock_service_factory(session: AsyncSession = pytest.importorskip("fastapi").Depends(pytest.importorskip("app.core.database").get_db)):
        return WeatherService(session, weather_provider=mock_provider)

    app.dependency_overrides[get_weather_service] = mock_service_factory

    try:
        res = await async_client.get(f"/api/v1/weather/current?latitude={lat}&longitude={lon}")
        assert res.status_code == 504
        assert "timed out" in res.json()["detail"].lower()
    finally:
        app.dependency_overrides.pop(get_weather_service, None)


@pytest.mark.asyncio
async def test_provider_network_error(async_client: AsyncClient):
    lat, lon = 12.2222, 72.2222
    mock_provider = MockWeatherProvider(should_fail_network=True)

    def mock_service_factory(session: AsyncSession = pytest.importorskip("fastapi").Depends(pytest.importorskip("app.core.database").get_db)):
        return WeatherService(session, weather_provider=mock_provider)

    app.dependency_overrides[get_weather_service] = mock_service_factory

    try:
        res = await async_client.get(f"/api/v1/weather/current?latitude={lat}&longitude={lon}")
        assert res.status_code == 502
        assert "provider error" in res.json()["detail"].lower()
    finally:
        app.dependency_overrides.pop(get_weather_service, None)


@pytest.mark.asyncio
async def test_provider_http_failure(async_client: AsyncClient):
    lat, lon = 13.3333, 73.3333
    mock_provider = MockWeatherProvider(should_fail_http=True, http_status_code=503)

    def mock_service_factory(session: AsyncSession = pytest.importorskip("fastapi").Depends(pytest.importorskip("app.core.database").get_db)):
        return WeatherService(session, weather_provider=mock_provider)

    app.dependency_overrides[get_weather_service] = mock_service_factory

    try:
        res = await async_client.get(f"/api/v1/weather/current?latitude={lat}&longitude={lon}")
        assert res.status_code == 502
    finally:
        app.dependency_overrides.pop(get_weather_service, None)


# =========================================================================
# 7. Stale Cache Fallback on Provider Failure
# =========================================================================
@pytest.mark.asyncio
async def test_stale_cache_served_on_provider_outage(async_client: AsyncClient):
    unique_id = uuid.uuid4().int % 1000000
    lat = round(10.0 + (unique_id % 7000) / 100.0, 4)
    lon = round(70.0 + ((unique_id // 7000) % 1500) / 100.0, 4)
    working_provider = MockWeatherProvider()

    def working_service_factory(session: AsyncSession = pytest.importorskip("fastapi").Depends(pytest.importorskip("app.core.database").get_db)):
        return WeatherService(session, weather_provider=working_provider)

    app.dependency_overrides[get_weather_service] = working_service_factory

    # 1. Populate initial cache
    res1 = await async_client.get(f"/api/v1/weather/current?latitude={lat}&longitude={lon}")
    assert res1.status_code == 200

    # 2. Expire the cache in PostgreSQL
    from app.core.database import get_db
    async for session in async_client._transport.app.dependency_overrides[get_db]():
        weather_repo = WeatherCacheRepository(session)
        entry = await weather_repo.get_by_key(make_cache_key(lat, lon))
        if entry:
            entry.expires_at = datetime.now(timezone.utc) - timedelta(minutes=10)
            await session.commit()


    # 3. Switch provider to failing mode
    failing_provider = MockWeatherProvider(should_timeout=True)

    def failing_service_factory(session: AsyncSession = pytest.importorskip("fastapi").Depends(pytest.importorskip("app.core.database").get_db)):
        return WeatherService(session, weather_provider=failing_provider)

    app.dependency_overrides[get_weather_service] = failing_service_factory

    try:
        # Access with failing provider -> serves stale cache entry
        res2 = await async_client.get(f"/api/v1/weather/current?latitude={lat}&longitude={lon}")
        assert res2.status_code == 200
        data2 = res2.json()["data"]
        assert data2["is_cached"] is True
        assert data2["status"] == "stale_cached"
        assert data2["provider_name"] == "cache_stale"
        assert data2["current"]["temperature_celsius"] == 26.5
    finally:
        app.dependency_overrides.pop(get_weather_service, None)



# =========================================================================
# 8. Geocoding / Location Search Tests
# =========================================================================
@pytest.mark.asyncio
async def test_geocoding_search(async_client: AsyncClient):
    mock_geo = MockGeocodingProvider()

    def mock_service_factory(session: AsyncSession = pytest.importorskip("fastapi").Depends(pytest.importorskip("app.core.database").get_db)):
        return WeatherService(session, geocoding_provider=mock_geo)

    app.dependency_overrides[get_weather_service] = mock_service_factory

    try:
        res = await async_client.get("/api/v1/weather/search?query=Pune")
        assert res.status_code == 200
        items = res.json()["data"]
        assert len(items) == 1
        assert items[0]["name"] == "Pune"
        assert items[0]["latitude"] == 18.5204
        assert items[0]["longitude"] == 73.8567

        # Query too short
        res_short = await async_client.get("/api/v1/weather/search?query=a")
        assert res_short.status_code == 422
    finally:
        app.dependency_overrides.pop(get_weather_service, None)


@pytest.mark.asyncio
async def test_geocoding_compound_and_fallback_scenarios(async_client: AsyncClient):
    """
    Focused unit & integration tests for location search bug fix:
    - Miyapur
    - Miyapur, Telangana
    - Miyapur, Hyderabad
    - Bowrampet
    - Bowrampet, Dundigal
    - Valid city (Hyderabad)
    - Genuinely invalid location (xyzqwe12345notalocation)
    Verifies that:
    1. Open-Meteo is primary.
    2. Compound query decomposition filters matching regions.
    3. Nominatim is secondary fallback ONLY when necessary.
    4. Deterministic mocks are used (no live network dependencies).
    """
    call_log = []

    def mock_transport_handler(request: httpx.Request) -> httpx.Response:
        url_str = str(request.url)
        if "geocoding-api.open-meteo.com" in url_str:
            name_param = request.url.params.get("name", "").lower()
            call_log.append(("open_meteo", name_param))

            if name_param == "hyderabad":
                return httpx.Response(
                    200,
                    json={
                        "results": [
                            {
                                "id": 1269843,
                                "name": "Hyderabad",
                                "latitude": 17.38405,
                                "longitude": 78.45636,
                                "admin1": "Telangana",
                                "admin2": "Hyderabad",
                                "country": "India",
                            }
                        ]
                    },
                )
            elif name_param == "miyapur":
                # Realistic Open-Meteo response: place in Karnataka (not Telangana)
                return httpx.Response(
                    200,
                    json={
                        "results": [
                            {
                                "id": 1263590,
                                "name": "Miyāpur",
                                "latitude": 16.35,
                                "longitude": 77.01,
                                "admin1": "Karnataka",
                                "admin2": "Raichur district",
                                "country": "India",
                            }
                        ]
                    },
                )
            elif name_param == "bowrampet":
                # Open-Meteo has 0 results for smaller rural areas
                return httpx.Response(200, json={"results": []})
            else:
                return httpx.Response(200, json={"results": []})

        elif "nominatim.openstreetmap.org" in url_str:
            q_param = request.url.params.get("q", "").lower()
            call_log.append(("nominatim", q_param))

            if "miyapur" in q_param:
                return httpx.Response(
                    200,
                    json=[
                        {
                            "place_id": 250300519,
                            "lat": "17.4981608",
                            "lon": "78.3567628",
                            "name": "Miyapur",
                            "display_name": "Miyapur, Ward 108 Miyapur, Telangana, 500049, India",
                            "address": {
                                "suburb": "Miyapur",
                                "city": "Hyderabad",
                                "state": "Telangana",
                                "country": "India",
                            },
                        }
                    ],
                )
            elif "bowrampet" in q_param:
                return httpx.Response(
                    200,
                    json=[
                        {
                            "place_id": 250300520,
                            "lat": "17.5610356",
                            "lon": "78.3982185",
                            "name": "Bowrampet",
                            "display_name": "Bowrampet, Dundigal mandal, Telangana, India",
                            "address": {
                                "suburb": "Bowrampet",
                                "county": "Dundigal mandal",
                                "state": "Telangana",
                                "country": "India",
                            },
                        }
                    ],
                )
            else:
                return httpx.Response(200, json=[])

        return httpx.Response(404, json={})

    transport = httpx.MockTransport(mock_transport_handler)
    provider = OpenMeteoGeocodingProvider(transport=transport)

    # 1. Valid City: "Hyderabad" -> Open-Meteo succeeds directly; Nominatim NOT called
    call_log.clear()
    res_hyd = await provider.search_location("Hyderabad")
    assert len(res_hyd) == 1
    assert res_hyd[0]["name"] == "Hyderabad"
    assert res_hyd[0]["state"] == "Telangana"
    assert round(res_hyd[0]["latitude"], 2) == 17.38
    assert round(res_hyd[0]["longitude"], 2) == 78.46
    assert any(c[0] == "open_meteo" for c in call_log)
    assert not any(c[0] == "nominatim" for c in call_log), "Nominatim should not be called when Open-Meteo succeeds"

    # 2. "Miyapur" without qualifiers -> Open-Meteo primary returns result
    call_log.clear()
    res_miyapur_single = await provider.search_location("Miyapur")
    assert len(res_miyapur_single) == 1
    assert "miy" in res_miyapur_single[0]["name"].lower()
    assert res_miyapur_single[0]["state"] == "Karnataka"

    # 3. Compound search: "Miyapur, Telangana" -> Open-Meteo has no Telangana match -> falls back to Nominatim
    call_log.clear()
    res_miyapur_ts = await provider.search_location("Miyapur, Telangana")
    assert len(res_miyapur_ts) == 1
    assert res_miyapur_ts[0]["name"] == "Miyapur"
    assert res_miyapur_ts[0]["state"] == "Telangana"
    assert round(res_miyapur_ts[0]["latitude"], 2) == 17.50
    assert round(res_miyapur_ts[0]["longitude"], 2) == 78.36
    # Verify Open-Meteo was tried first, then Nominatim fallback was triggered
    assert call_log[0] == ("open_meteo", "miyapur")
    assert call_log[1] == ("nominatim", "miyapur, telangana")

    # 4. Compound search: "Miyapur, Hyderabad" -> falls back to Nominatim
    call_log.clear()
    res_miyapur_hyd = await provider.search_location("Miyapur, Hyderabad")
    assert len(res_miyapur_hyd) == 1
    assert res_miyapur_hyd[0]["name"] == "Miyapur"
    assert res_miyapur_hyd[0]["state"] == "Telangana"
    assert call_log[0] == ("open_meteo", "miyapur")
    assert call_log[1] == ("nominatim", "miyapur, hyderabad")

    # 5. Locality: "Bowrampet" -> Open-Meteo returns 0 -> falls back to Nominatim
    call_log.clear()
    res_bowrampet = await provider.search_location("Bowrampet")
    assert len(res_bowrampet) == 1
    assert res_bowrampet[0]["name"] == "Bowrampet"
    assert res_bowrampet[0]["state"] == "Telangana"
    assert round(res_bowrampet[0]["latitude"], 2) == 17.56
    assert round(res_bowrampet[0]["longitude"], 2) == 78.40
    assert call_log[0] == ("open_meteo", "bowrampet")
    assert call_log[1] == ("nominatim", "bowrampet")

    # 6. Locality with compound query: "Bowrampet, Dundigal" -> falls back to Nominatim
    call_log.clear()
    res_bowrampet_dundigal = await provider.search_location("Bowrampet, Dundigal")
    assert len(res_bowrampet_dundigal) == 1
    assert res_bowrampet_dundigal[0]["name"] == "Bowrampet"
    assert res_bowrampet_dundigal[0]["state"] == "Telangana"
    assert call_log[0] == ("open_meteo", "bowrampet")
    assert call_log[1] == ("nominatim", "bowrampet, dundigal")

    # 7. Genuinely invalid location: "xyzqwe12345notalocation" -> returns empty list []
    call_log.clear()
    res_invalid = await provider.search_location("xyzqwe12345notalocation")
    assert res_invalid == []

    # 8. Test end-to-end with FastAPI /api/v1/weather/search endpoint using provider
    def mock_service_factory(session: AsyncSession = pytest.importorskip("fastapi").Depends(pytest.importorskip("app.core.database").get_db)):
        return WeatherService(session, geocoding_provider=provider)

    app.dependency_overrides[get_weather_service] = mock_service_factory
    try:
        api_res = await async_client.get("/api/v1/weather/search?query=Miyapur,%20Telangana")
        assert api_res.status_code == 200
        body = api_res.json()
        assert body["success"] is True
        items = body["data"]
        assert len(items) == 1
        assert items[0]["name"] == "Miyapur"
        assert items[0]["state"] == "Telangana"

        api_res_bow = await async_client.get("/api/v1/weather/search?query=Bowrampet,%20Dundigal")
        assert api_res_bow.status_code == 200
        items_bow = api_res_bow.json()["data"]
        assert len(items_bow) == 1
        assert items_bow[0]["name"] == "Bowrampet"
        assert items_bow[0]["state"] == "Telangana"
    finally:
        app.dependency_overrides.pop(get_weather_service, None)


# =========================================================================
# 9. Authenticated Farmer Profile Weather Tests
# =========================================================================
@pytest.mark.asyncio
async def test_profile_weather_with_and_without_coords(async_client: AsyncClient):
    farmer = await register_farmer(async_client, name="Coord Farmer")
    mock_weather = MockWeatherProvider()

    def mock_service_factory(session: AsyncSession = pytest.importorskip("fastapi").Depends(pytest.importorskip("app.core.database").get_db)):
        return WeatherService(session, weather_provider=mock_weather)

    app.dependency_overrides[get_weather_service] = mock_service_factory

    try:
        # Profile initially has no coordinates
        res_no_coords = await async_client.get("/api/v1/weather/profile", headers=farmer["headers"])
        assert res_no_coords.status_code == 404
        assert "coordinates" in res_no_coords.json()["detail"].lower()

        # Update profile with valid coordinates
        profile_res = await async_client.put(
            "/api/v1/profile",
            json={
                "state": "Maharashtra",
                "district": "Pune",
                "village": "Baramati",
                "latitude": 18.1500,
                "longitude": 74.5800,
            },
            headers=farmer["headers"],
        )
        assert profile_res.status_code == 200

        # Now profile weather succeeds
        res_with_coords = await async_client.get("/api/v1/weather/profile", headers=farmer["headers"])
        assert res_with_coords.status_code == 200
        pdata = res_with_coords.json()["data"]
        assert pdata["current"]["temperature_celsius"] == 26.5
        assert pdata["location"]["latitude"] == 18.15
        assert pdata["location"]["longitude"] == 74.58
    finally:
        app.dependency_overrides.pop(get_weather_service, None)


# =========================================================================
# 10. Advisory Context Weather Integration Tests
# =========================================================================
@pytest.mark.asyncio
async def test_advisory_context_weather_integration(async_client: AsyncClient):
    farmer = await register_farmer(async_client, name="Advisory Weather Farmer")

    # Set profile with unique coordinates to ensure clean test cache isolation
    unique_id = uuid.uuid4().int % 1000000
    lat = round(10.0 + (unique_id % 7000) / 100.0, 4)
    lon = round(70.0 + ((unique_id // 7000) % 1500) / 100.0, 4)

    await async_client.put(
        "/api/v1/profile",
        json={
            "state": "Maharashtra",
            "district": "Nagpur",
            "latitude": lat,
            "longitude": lon,
        },
        headers=farmer["headers"],
    )


    # Use DB session to test ContextAssembler directly
    from app.core.database import get_db
    async for session in async_client._transport.app.dependency_overrides[get_db]():
        # Case A: No weather cached -> structured context has weather=None, has_weather=False
        assembler = ContextAssembler(session)
        ctx_without_weather = await assembler.assemble(farmer["user_id"])
        assert ctx_without_weather.context_summary["has_weather"] is False
        assert ctx_without_weather.structured_context["weather"] is None
        assert "Local Weather" not in ctx_without_weather.formatted_prompt_context

        # Case B: Populate WeatherCache
        weather_repo = WeatherCacheRepository(session)
        cache_key = make_cache_key(lat, lon)
        await weather_repo.upsert_cache(
            cache_key=cache_key,
            latitude=lat,
            longitude=lon,
            current_conditions={
                "temperature_celsius": 29.2,
                "relative_humidity_percent": 62.0,
                "precipitation_mm": 0.0,
                "weather_code": 0,
                "condition_text": "Clear Sky",
                "condition_icon": "sunny",
                "wind_speed_kmh": 8.5,
            },
            forecast_daily=[],
            ttl_minutes=30,
        )

        # Assemble context again -> must include real weather
        ctx_with_weather = await assembler.assemble(farmer["user_id"])

        assert ctx_with_weather.context_summary["has_weather"] is True
        assert ctx_with_weather.structured_context["weather"] is not None
        assert ctx_with_weather.structured_context["weather"]["temperature_celsius"] == 29.2
        assert "### Local Weather (Real/Live Cache):" in ctx_with_weather.formatted_prompt_context
        assert "- Temperature: 29.2°C" in ctx_with_weather.formatted_prompt_context
        assert "- Condition: Clear Sky" in ctx_with_weather.formatted_prompt_context

