import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_and_update_profile(async_client: AsyncClient):
    unique_phone = f"+9194{uuid.uuid4().hex[:8]}"
    pwd = "FarmerSecret@789"

    # Register new farmer
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Gita Devi",
            "phone": unique_phone,
            "password": pwd,
            "preferred_language": "hi",
        },
    )
    assert reg_res.status_code == 201
    access_token = reg_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 1. Fetch current profile
    profile_res = await async_client.get("/api/v1/profile", headers=headers)
    assert profile_res.status_code == 200
    data = profile_res.json()["data"]
    assert data["preferred_language"] == "hi"
    assert data["state"] is None

    # 2. Update profile with land details
    update_payload = {
        "state": "Uttar Pradesh",
        "district": "Varanasi",
        "village": "Rohania",
        "latitude": 25.3176,
        "longitude": 82.9739,
        "land_size_acres": 8.5,
        "soil_type": "Loamy Soil",
        "irrigation_source": "Tube Well",
        "preferred_language": "hi",
    }
    update_res = await async_client.put(
        "/api/v1/profile", json=update_payload, headers=headers
    )
    assert update_res.status_code == 200
    updated_data = update_res.json()["data"]
    assert updated_data["state"] == "Uttar Pradesh"
    assert updated_data["district"] == "Varanasi"
    assert float(updated_data["land_size_acres"]) == 8.5
    assert updated_data["soil_type"] == "Loamy Soil"

    # 3. Verify persistence with another GET
    verify_res = await async_client.get("/api/v1/profile", headers=headers)
    assert verify_res.status_code == 200
    assert verify_res.json()["data"]["district"] == "Varanasi"
