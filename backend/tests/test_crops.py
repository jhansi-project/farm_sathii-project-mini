import uuid
import pytest
from httpx import AsyncClient

from app.services.crop_service import crop_service


@pytest.mark.asyncio
async def test_guest_crop_recommendation_success(async_client: AsyncClient):
    """Guest user can request recommendation; output is real inference without database persistence."""
    payload = {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 25.0,
        "humidity": 80.0,
        "ph": 6.5,
        "rainfall": 200.0,
    }
    response = await async_client.post("/api/v1/crops/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    res_data = data["data"]
    assert res_data["recommended_crop"] == "rice"
    assert res_data["is_saved"] is False
    assert res_data["id"] is None
    assert len(res_data["top_predictions"]) == 3
    assert res_data["top_predictions"][0]["crop"] == "rice"
    assert round(res_data["top_predictions"][0]["probability"], 2) == 0.52
    assert res_data["inputs"]["N"] == 90.0
    assert res_data["model_version"] == "farmsathi_crop_rf_v1.0"


@pytest.mark.asyncio
async def test_full_field_names_accepted(async_client: AsyncClient):
    """Payload accepting nitrogen, phosphorus, potassium as field names."""
    payload = {
        "nitrogen": 90,
        "phosphorus": 42,
        "potassium": 43,
        "temperature": 25.0,
        "humidity": 80.0,
        "ph": 6.5,
        "rainfall": 200.0,
    }
    response = await async_client.post("/api/v1/crops/recommend", json=payload)
    assert response.status_code == 200
    assert response.json()["data"]["recommended_crop"] == "rice"


@pytest.mark.asyncio
async def test_authenticated_crop_recommendation_and_persistence(async_client: AsyncClient):
    """Authenticated user recommendation is persisted to PostgreSQL and retrievable via history."""
    phone = f"+9198{uuid.uuid4().hex[:8]}"
    reg_payload = {
        "phone": phone,
        "password": "Password123!",
        "full_name": "Test Crop Farmer",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201

    access_token = reg_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    rec_payload = {
        "N": 85,
        "P": 58,
        "K": 41,
        "temperature": 21.7,
        "humidity": 80.3,
        "ph": 7.04,
        "rainfall": 226.6,
    }
    rec_res = await async_client.post("/api/v1/crops/recommend", json=rec_payload, headers=headers)
    assert rec_res.status_code == 200
    rec_data = rec_res.json()["data"]
    assert rec_data["is_saved"] is True
    assert rec_data["id"] is not None

    # Retrieve history
    hist_res = await async_client.get("/api/v1/crops/history", headers=headers)
    assert hist_res.status_code == 200
    hist_data = hist_res.json()["data"]
    assert len(hist_data) >= 1
    assert hist_data[0]["id"] == rec_data["id"]
    assert hist_data[0]["recommended_crop"] == rec_data["recommended_crop"]
    assert hist_data[0]["inputs"]["N"] == 85.0


@pytest.mark.asyncio
async def test_invalid_input_validation_422(async_client: AsyncClient):
    """Pydantic rejects out-of-bounds or missing parameters with 422 before model inference."""
    # Negative N
    res1 = await async_client.post(
        "/api/v1/crops/recommend",
        json={"N": -5, "P": 40, "K": 40, "temperature": 25, "humidity": 80, "ph": 7, "rainfall": 100},
    )
    assert res1.status_code == 422

    # pH out of range (>14)
    res2 = await async_client.post(
        "/api/v1/crops/recommend",
        json={"N": 50, "P": 40, "K": 40, "temperature": 25, "humidity": 80, "ph": 15, "rainfall": 100},
    )
    assert res2.status_code == 422

    # Missing rainfall
    res3 = await async_client.post(
        "/api/v1/crops/recommend",
        json={"N": 50, "P": 40, "K": 40, "temperature": 25, "humidity": 80, "ph": 7},
    )
    assert res3.status_code == 422


@pytest.mark.asyncio
async def test_missing_model_returns_503(async_client: AsyncClient):
    """When the model artifact is missing, service returns structured 503 rather than fake data."""
    try:
        crop_service.set_model_path_override("ml/models/non_existent_model.pkl")
        payload = {"N": 50, "P": 50, "K": 50, "temperature": 25, "humidity": 80, "ph": 6.5, "rainfall": 100}
        response = await async_client.post("/api/v1/crops/recommend", json=payload)
        assert response.status_code == 503
        data = response.json()
        assert "Crop recommendation model artifact is unavailable" in str(data)
    finally:
        # Restore normal model path
        crop_service.set_model_path_override(None)


@pytest.mark.asyncio
async def test_history_unauthenticated_returns_401(async_client: AsyncClient):
    """History requires active authenticated user."""
    response = await async_client.get("/api/v1/crops/history")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_alias_endpoint_crop_recommendations(async_client: AsyncClient):
    """Alias /crop-recommendations/recommend route works identically."""
    payload = {"N": 90, "P": 42, "K": 43, "temperature": 25.0, "humidity": 80.0, "ph": 6.5, "rainfall": 200.0}
    response = await async_client.post("/api/v1/crop-recommendations/recommend", json=payload)
    assert response.status_code == 200
    assert response.json()["data"]["recommended_crop"] == "rice"
