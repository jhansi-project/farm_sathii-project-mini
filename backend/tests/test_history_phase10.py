import io
import uuid
import pytest
from PIL import Image
from httpx import AsyncClient


def create_test_image_bytes(format: str = "JPEG", size=(224, 224), color=(34, 139, 34)) -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()


async def register_test_user(client: AsyncClient, name: str = "Farmer"):
    phone = f"+9198{uuid.uuid4().hex[:8]}"
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={"phone": phone, "password": "Password123!", "full_name": name},
    )
    assert reg_res.status_code == 201
    token = reg_res.json()["data"]["access_token"]
    user_id = reg_res.json()["data"]["user"]["id"]
    return {
        "id": user_id,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


# ============================================================================
# 1. Authentication & Empty State Tests
# ============================================================================

@pytest.mark.asyncio
async def test_history_unauthenticated_rejected(async_client: AsyncClient):
    """Accessing history endpoints without auth token must return 401."""
    res1 = await async_client.get("/api/v1/history")
    assert res1.status_code == 401

    res2 = await async_client.get("/api/v1/history/crop-recommendations")
    assert res2.status_code == 401

    res3 = await async_client.get("/api/v1/history/disease-diagnoses")
    assert res3.status_code == 401

    res4 = await async_client.get("/api/v1/history/advisory-conversations")
    assert res4.status_code == 401


@pytest.mark.asyncio
async def test_empty_history(async_client: AsyncClient):
    """A newly registered farmer with no records has zero counts and empty lists."""
    farmer = await register_test_user(async_client, "Empty Farmer")
    headers = farmer["headers"]

    # Unified summary
    summary_res = await async_client.get("/api/v1/history", headers=headers)
    assert summary_res.status_code == 200
    data = summary_res.json()["data"]
    assert data["counts"]["total"] == 0
    assert data["counts"]["crop_recommendations"] == 0
    assert data["counts"]["disease_diagnoses"] == 0
    assert data["counts"]["advisory_conversations"] == 0
    assert len(data["recent_activities"]) == 0

    # Crop history
    crop_res = await async_client.get("/api/v1/history/crop-recommendations", headers=headers)
    assert crop_res.status_code == 200
    crop_data = crop_res.json()["data"]
    assert crop_data["total"] == 0
    assert len(crop_data["items"]) == 0

    # Disease history
    disease_res = await async_client.get("/api/v1/history/disease-diagnoses", headers=headers)
    assert disease_res.status_code == 200
    disease_data = disease_res.json()["data"]
    assert disease_data["total"] == 0
    assert len(disease_data["items"]) == 0

    # Advisory history
    advisory_res = await async_client.get("/api/v1/history/advisory-conversations", headers=headers)
    assert advisory_res.status_code == 200
    advisory_data = advisory_res.json()["data"]
    assert advisory_data["total"] == 0
    assert len(advisory_data["items"]) == 0


# ============================================================================
# 2. Crop Recommendation History & Detail
# ============================================================================

@pytest.mark.asyncio
async def test_crop_recommendation_history_and_detail(async_client: AsyncClient):
    """Crop recommendation performed by authenticated farmer appears in history and detail."""
    farmer = await register_test_user(async_client, "Crop Farmer")
    headers = farmer["headers"]

    payload = {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 25.0,
        "humidity": 80.0,
        "ph": 6.5,
        "rainfall": 200.0,
    }
    rec_res = await async_client.post("/api/v1/crops/recommend", json=payload, headers=headers)
    assert rec_res.status_code == 200
    rec_data = rec_res.json()["data"]
    rec_id = rec_data["id"]
    assert rec_data["is_saved"] is True
    assert rec_id is not None

    # Retrieve paginated history
    hist_res = await async_client.get("/api/v1/history/crop-recommendations", headers=headers)
    assert hist_res.status_code == 200
    hist_data = hist_res.json()["data"]
    assert hist_data["total"] == 1
    assert len(hist_data["items"]) == 1
    assert hist_data["items"][0]["id"] == rec_id
    assert hist_data["items"][0]["recommended_crop"] == rec_data["recommended_crop"]
    assert hist_data["items"][0]["inputs"]["N"] == 90.0

    # Retrieve single record detail
    detail_res = await async_client.get(f"/api/v1/history/crop-recommendations/{rec_id}", headers=headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()["data"]
    assert detail_data["id"] == rec_id
    assert detail_data["recommended_crop"] == rec_data["recommended_crop"]
    assert detail_data["inputs"]["rainfall"] == 200.0

    # Nonexistent record returns 404
    fake_id = str(uuid.uuid4())
    not_found_res = await async_client.get(f"/api/v1/history/crop-recommendations/{fake_id}", headers=headers)
    assert not_found_res.status_code == 404


# ============================================================================
# 3. Disease Diagnosis History & Detail
# ============================================================================

@pytest.mark.asyncio
async def test_disease_diagnosis_history_and_detail(async_client: AsyncClient):
    """Disease diagnosis performed by authenticated farmer appears in history and detail."""
    farmer = await register_test_user(async_client, "Disease Farmer")
    headers = farmer["headers"]

    img_bytes = create_test_image_bytes(format="JPEG")
    files = {"file": ("corn_leaf.jpg", img_bytes, "image/jpeg")}
    diag_res = await async_client.post("/api/v1/diseases/diagnose", files=files, headers=headers)
    assert diag_res.status_code == 200
    diag_data = diag_res.json()["data"]
    diag_id = diag_data["id"]
    assert diag_data["is_saved"] is True
    assert diag_id is not None

    # Retrieve paginated history
    hist_res = await async_client.get("/api/v1/history/disease-diagnoses", headers=headers)
    assert hist_res.status_code == 200
    hist_data = hist_res.json()["data"]
    assert hist_data["total"] == 1
    assert len(hist_data["items"]) == 1
    assert hist_data["items"][0]["id"] == diag_id
    assert hist_data["items"][0]["crop"] == diag_data["crop"]
    assert hist_data["items"][0]["display_name"] == diag_data["display_name"]

    # Retrieve single record detail
    detail_res = await async_client.get(f"/api/v1/history/disease-diagnoses/{diag_id}", headers=headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()["data"]
    assert detail_data["id"] == diag_id
    assert detail_data["display_name"] == diag_data["display_name"]
    assert detail_data["management_guidance"] is not None

    # Nonexistent record returns 404
    fake_id = str(uuid.uuid4())
    not_found_res = await async_client.get(f"/api/v1/history/disease-diagnoses/{fake_id}", headers=headers)
    assert not_found_res.status_code == 404


# ============================================================================
# 4. Advisory Conversations History & Detail
# ============================================================================

@pytest.mark.asyncio
async def test_advisory_conversations_history_and_detail(async_client: AsyncClient):
    """Advisory conversation created by farmer appears in history and detail."""
    farmer = await register_test_user(async_client, "Advisory Farmer")
    headers = farmer["headers"]

    conv_res = await async_client.post(
        "/api/v1/advisory/conversations",
        json={"title": "Cotton Irrigation", "initial_message": "How often should I irrigate cotton?"},
        headers=headers,
    )
    assert conv_res.status_code == 201
    conv_data = conv_res.json()["data"]
    conv_id = conv_data["id"]

    # Retrieve paginated history
    hist_res = await async_client.get("/api/v1/history/advisory-conversations", headers=headers)
    assert hist_res.status_code == 200
    hist_data = hist_res.json()["data"]
    assert hist_data["total"] == 1
    assert len(hist_data["items"]) == 1
    assert hist_data["items"][0]["id"] == conv_id
    assert hist_data["items"][0]["title"] == "Cotton Irrigation"
    assert hist_data["items"][0]["message_count"] >= 2

    # Retrieve single conversation detail
    detail_res = await async_client.get(f"/api/v1/history/advisory-conversations/{conv_id}", headers=headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()["data"]
    assert detail_data["id"] == conv_id
    assert len(detail_data["messages"]) >= 2
    assert detail_data["messages"][0]["sender_role"] == "user"
    assert detail_data["messages"][1]["sender_role"] == "assistant"

    # Nonexistent conversation returns 404
    fake_id = str(uuid.uuid4())
    not_found_res = await async_client.get(f"/api/v1/history/advisory-conversations/{fake_id}", headers=headers)
    assert not_found_res.status_code == 404


# ============================================================================
# 5. Strict Cross-User Isolation (IDOR Protection)
# ============================================================================

@pytest.mark.asyncio
async def test_strict_cross_user_isolation(async_client: AsyncClient):
    """User B must never be able to access User A's history or details."""
    farmer_a = await register_test_user(async_client, "Farmer Alice")
    farmer_b = await register_test_user(async_client, "Farmer Bob")

    # Farmer A creates records in all 3 modules
    # Crop
    c_res = await async_client.post(
        "/api/v1/crops/recommend",
        json={"N": 80, "P": 40, "K": 40, "temperature": 25, "humidity": 70, "ph": 6.5, "rainfall": 150},
        headers=farmer_a["headers"],
    )
    rec_a_id = c_res.json()["data"]["id"]

    # Disease
    img_bytes = create_test_image_bytes(format="JPEG")
    d_res = await async_client.post(
        "/api/v1/diseases/diagnose",
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")},
        headers=farmer_a["headers"],
    )
    diag_a_id = d_res.json()["data"]["id"]

    # Advisory
    a_res = await async_client.post(
        "/api/v1/advisory/conversations",
        json={"title": "Alice Private Inquiry", "initial_message": "Tell me about drip irrigation."},
        headers=farmer_a["headers"],
    )
    conv_a_id = a_res.json()["data"]["id"]

    # Farmer B checks their own summary: MUST BE ZERO
    b_summary = await async_client.get("/api/v1/history", headers=farmer_b["headers"])
    assert b_summary.json()["data"]["counts"]["total"] == 0
    assert len(b_summary.json()["data"]["recent_activities"]) == 0

    # Farmer B checks lists: MUST BE EMPTY
    b_crops = await async_client.get("/api/v1/history/crop-recommendations", headers=farmer_b["headers"])
    assert b_crops.json()["data"]["total"] == 0
    assert len(b_crops.json()["data"]["items"]) == 0

    b_diseases = await async_client.get("/api/v1/history/disease-diagnoses", headers=farmer_b["headers"])
    assert b_diseases.json()["data"]["total"] == 0

    b_advisories = await async_client.get("/api/v1/history/advisory-conversations", headers=farmer_b["headers"])
    assert b_advisories.json()["data"]["total"] == 0

    # Farmer B directly attempts to fetch Farmer A's items by UUID: MUST RETURN 404 (IDOR protected)
    b_try_crop = await async_client.get(
        f"/api/v1/history/crop-recommendations/{rec_a_id}",
        headers=farmer_b["headers"],
    )
    assert b_try_crop.status_code == 404

    b_try_disease = await async_client.get(
        f"/api/v1/history/disease-diagnoses/{diag_a_id}",
        headers=farmer_b["headers"],
    )
    assert b_try_disease.status_code == 404

    b_try_advisory = await async_client.get(
        f"/api/v1/history/advisory-conversations/{conv_a_id}",
        headers=farmer_b["headers"],
    )
    assert b_try_advisory.status_code == 404


# ============================================================================
# 6. Complete Cross-Module Integration & Unified Timeline
# ============================================================================

@pytest.mark.asyncio
async def test_unified_cross_module_history(async_client: AsyncClient):
    """Farmer with actions across all modules sees unified summary and timeline."""
    farmer = await register_test_user(async_client, "Active Farmer")
    headers = farmer["headers"]

    # 1. Crop
    await async_client.post(
        "/api/v1/crops/recommend",
        json={"N": 90, "P": 42, "K": 43, "temperature": 25.0, "humidity": 80.0, "ph": 6.5, "rainfall": 200.0},
        headers=headers,
    )

    # 2. Disease
    img_bytes = create_test_image_bytes(format="JPEG")
    await async_client.post(
        "/api/v1/diseases/diagnose",
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")},
        headers=headers,
    )

    # 3. Advisory
    await async_client.post(
        "/api/v1/advisory/conversations",
        json={"title": "Wheat Advisory", "initial_message": "When should I sow wheat?"},
        headers=headers,
    )

    # Check Unified Summary
    summary_res = await async_client.get("/api/v1/history", headers=headers)
    assert summary_res.status_code == 200
    data = summary_res.json()["data"]

    assert data["counts"]["crop_recommendations"] == 1
    assert data["counts"]["disease_diagnoses"] == 1
    assert data["counts"]["advisory_conversations"] == 1
    assert data["counts"]["total"] == 3

    recent = data["recent_activities"]
    assert len(recent) == 3
    module_types = {item["module_type"] for item in recent}
    assert module_types == {"crop", "disease", "advisory"}

    # Ordering: newest first
    for i in range(len(recent) - 1):
        assert recent[i]["created_at"] >= recent[i + 1]["created_at"]
