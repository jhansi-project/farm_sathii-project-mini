import uuid
from decimal import Decimal
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crop_recommendation import CropRecommendation
from app.models.disease_diagnosis import DiseaseDiagnosis
from app.models.profile import FarmerProfile
from app.schemas.advisory import AdvisoryProviderStatus
from app.services.advisory.context_assembler import ContextAssembler
from app.services.advisory.providers.mock_provider import MockAdvisoryProvider
from app.services.advisory.providers.router import default_provider_router
from app.services.advisory.providers.unconfigured import UnconfiguredProvider
from app.services.advisory.safety_layer import SafetyLayer


async def register_farmer(client: AsyncClient, name: str = "Ramesh Kumar") -> dict:
    unique_phone = f"+9198{uuid.uuid4().hex[:8]}"
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
# 1. Request Validation Tests
# =========================================================================
@pytest.mark.asyncio
async def test_advisory_request_validation(async_client: AsyncClient):
    farmer = await register_farmer(async_client)

    # Missing/empty question when sending message
    fake_conv_id = uuid.uuid4()
    empty_res = await async_client.post(
        f"/api/v1/advisory/conversations/{fake_conv_id}/messages",
        json={"message_text": "   "},
        headers=farmer["headers"],
    )
    assert empty_res.status_code == 422

    # Malformed UUID in URL
    malformed_res = await async_client.post(
        "/api/v1/advisory/conversations/not-a-uuid/messages",
        json={"message_text": "How much water for rice?"},
        headers=farmer["headers"],
    )
    assert malformed_res.status_code == 422


# =========================================================================
# 2. Authenticated Conversation Creation
# =========================================================================
@pytest.mark.asyncio
async def test_authenticated_conversation_creation(async_client: AsyncClient):
    # Unauthenticated attempt must fail with 401
    unauth_res = await async_client.post(
        "/api/v1/advisory/conversations",
        json={"title": "Wheat inquiry"},
    )
    assert unauth_res.status_code == 401

    # Authenticated creation without initial message
    farmer = await register_farmer(async_client, "Suresh Patel")
    res = await async_client.post(
        "/api/v1/advisory/conversations",
        json={"title": "Cotton nutrient query", "language": "en"},
        headers=farmer["headers"],
    )
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["title"] == "Cotton nutrient query"
    assert data["language"] == "en"
    assert len(data["messages"]) == 0

    # Authenticated creation WITH initial question
    res2 = await async_client.post(
        "/api/v1/advisory/conversations",
        json={
            "initial_message": "My rice leaves have brown spots. What could be the reason?"
        },
        headers=farmer["headers"],
    )
    assert res2.status_code == 201
    data2 = res2.json()["data"]
    assert len(data2["messages"]) == 2  # 1 user message + 1 assistant message
    assert data2["messages"][0]["sender_role"] == "user"
    assert "brown spots" in data2["messages"][0]["message_text"]
    assert data2["messages"][1]["sender_role"] == "assistant"


# =========================================================================
# 3. Message Persistence and Multi-turn Conversation
# =========================================================================
@pytest.mark.asyncio
async def test_authenticated_message_creation_and_persistence(
    async_client: AsyncClient,
):
    farmer = await register_farmer(async_client, "Pooja Sharma")

    # Set mock provider for predictable response
    mock_provider = MockAdvisoryProvider(
        content="Water curling can indicate moisture stress or salt accumulation."
    )
    default_provider_router.set_override_provider(mock_provider)

    try:
        # Create conversation
        conv_res = await async_client.post(
            "/api/v1/advisory/conversations",
            json={"title": "Fertilizer issues"},
            headers=farmer["headers"],
        )
        conv_id = conv_res.json()["data"]["id"]

        # Post message 1
        msg1_res = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_id}/messages",
            json={
                "message_text": "Yesterday morning I applied fertilizer and today the leaves are curling. What should I do?"
            },
            headers=farmer["headers"],
        )
        assert msg1_res.status_code == 200
        data1 = msg1_res.json()["data"]
        assert data1["user_message"]["sender_role"] == "user"
        assert data1["assistant_message"]["sender_role"] == "assistant"
        assert "moisture stress" in data1["assistant_message"]["message_text"]

        # Post message 2 (multi-turn follow-up)
        mock_provider._content = "Flush the soil with fresh irrigation to dilute excess nitrogen."
        msg2_res = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_id}/messages",
            json={"message_text": "Should I irrigate immediately?"},
            headers=farmer["headers"],
        )
        assert msg2_res.status_code == 200

        # Retrieve conversation detail to verify database persistence
        detail_res = await async_client.get(
            f"/api/v1/advisory/conversations/{conv_id}",
            headers=farmer["headers"],
        )
        assert detail_res.status_code == 200
        detail = detail_res.json()["data"]
        assert len(detail["messages"]) == 4  # 2 user questions + 2 assistant replies
        assert detail["messages"][0]["message_text"].startswith("Yesterday morning")
        assert detail["messages"][2]["message_text"] == "Should I irrigate immediately?"
    finally:
        default_provider_router.set_override_provider(None)


# =========================================================================
# 4. User Authorization & Isolation
# =========================================================================
@pytest.mark.asyncio
async def test_user_authorization_and_isolation(async_client: AsyncClient):
    farmer_a = await register_farmer(async_client, "Farmer A")
    farmer_b = await register_farmer(async_client, "Farmer B")

    # Farmer A creates a conversation
    conv_res = await async_client.post(
        "/api/v1/advisory/conversations",
        json={"title": "Farmer A Secret Corn Strategy"},
        headers=farmer_a["headers"],
    )
    conv_id = conv_res.json()["data"]["id"]

    # Farmer B attempts to retrieve Farmer A's conversation -> 404 (isolated)
    get_res = await async_client.get(
        f"/api/v1/advisory/conversations/{conv_id}",
        headers=farmer_b["headers"],
    )
    assert get_res.status_code == 404

    # Farmer B attempts to post message to Farmer A's conversation -> 404
    post_res = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={"message_text": "Can I see your advice?"},
        headers=farmer_b["headers"],
    )
    assert post_res.status_code == 404

    # Farmer B attempts to delete Farmer A's conversation -> 404
    del_res = await async_client.delete(
        f"/api/v1/advisory/conversations/{conv_id}",
        headers=farmer_b["headers"],
    )
    assert del_res.status_code == 404

    # Farmer B's conversation list must NOT contain Farmer A's conversation
    list_res = await async_client.get(
        "/api/v1/advisory/conversations",
        headers=farmer_b["headers"],
    )
    assert list_res.status_code == 200
    b_conv_ids = [c["id"] for c in list_res.json()["data"]]
    assert conv_id not in b_conv_ids


# =========================================================================
# 5. Context Assembly with Available Data
# =========================================================================
@pytest.mark.asyncio
async def test_context_assembly_with_available_data(async_client: AsyncClient):
    from app.core.database import get_db

    farmer = await register_farmer(async_client, "Context Farmer")
    user_id = farmer["user_id"]

    # Insert test profile, crop recommendation, and disease diagnosis
    async for session in async_client._transport.app.dependency_overrides[get_db]():
        from app.repositories.profile_repo import FarmerProfileRepository
        profile_repo = FarmerProfileRepository(session)
        profile = await profile_repo.get_by_user_id(user_id)
        if not profile:
            profile = FarmerProfile(user_id=user_id)
            session.add(profile)
        profile.state = "Punjab"
        profile.district = "Ludhiana"
        profile.village = "Gill"
        profile.land_size_acres = Decimal("12.50")
        profile.soil_type = "Alluvial Soil"
        profile.irrigation_source = "Canal"
        profile.preferred_language = "pa"

        # 2. Crop Recommendation
        crop = CropRecommendation(
            user_id=user_id,
            nitrogen=Decimal("120.0"),
            phosphorus=Decimal("50.0"),
            potassium=Decimal("45.0"),
            temperature=Decimal("24.5"),
            humidity=Decimal("65.0"),
            ph=Decimal("6.8"),
            rainfall=Decimal("750.0"),
            recommended_crop="wheat",
            top_predictions=[{"crop": "wheat", "probability": 0.95}],
            model_version="rf_v1.0",
        )
        session.add(crop)

        # 3. Disease Diagnosis
        diag = DiseaseDiagnosis(
            user_id=user_id,
            original_image_path="storage/uploads/wheat_leaf.jpg",
            predicted_condition="Wheat - Yellow Rust",
            confidence=Decimal("0.8950"),
            model_version="mobilenetv3_large",
            is_confident=True,
            management_guidance={"cultural": "Ensure adequate spacing"},
        )
        session.add(diag)
        await session.commit()

        # Test Context Assembler directly
        assembler = ContextAssembler(session)
        assembled = await assembler.assemble(user_id=user_id)

        # Verify structured context matches DB
        assert assembled.context_summary["has_profile"] is True
        assert assembled.context_summary["has_crop_recommendation"] is True
        assert assembled.context_summary["has_disease_diagnosis"] is True

        assert assembled.structured_context["farmer_profile"]["state"] == "Punjab"
        assert assembled.structured_context["farmer_profile"]["district"] == "Ludhiana"
        assert assembled.structured_context["farmer_profile"]["soil_type"] == "Alluvial Soil"
        assert assembled.structured_context["crop_recommendation"]["recommended_crop"] == "wheat"
        assert assembled.structured_context["disease_diagnosis"]["predicted_condition"] == "Wheat - Yellow Rust"
        assert assembled.structured_context["disease_diagnosis"]["confidence_percent"] == 89.5

        # Verify formatted prompt context
        assert "Punjab" in assembled.formatted_prompt_context
        assert "Ludhiana" in assembled.formatted_prompt_context
        assert "Alluvial Soil" in assembled.formatted_prompt_context
        assert "wheat" in assembled.formatted_prompt_context
        assert "Wheat - Yellow Rust" in assembled.formatted_prompt_context
        break


# =========================================================================
# 6. Context Assembly with Missing Data (Strictly No Fabrication)
# =========================================================================
@pytest.mark.asyncio
async def test_context_assembly_with_missing_data_no_fabrication(
    async_client: AsyncClient,
):
    from app.core.database import get_db

    farmer = await register_farmer(async_client, "Clean Slate Farmer")
    user_id = farmer["user_id"]

    async for session in async_client._transport.app.dependency_overrides[get_db]():
        assembler = ContextAssembler(session)
        assembled = await assembler.assemble(user_id=user_id)

        # Must be strictly False / None
        assert assembled.context_summary["has_profile"] is False
        assert assembled.context_summary["has_crop_recommendation"] is False
        assert assembled.context_summary["has_disease_diagnosis"] is False
        assert assembled.context_summary["has_weather"] is False

        assert assembled.structured_context["farmer_profile"] is None
        assert assembled.structured_context["crop_recommendation"] is None
        assert assembled.structured_context["disease_diagnosis"] is None
        assert assembled.structured_context["weather"] is None

        # Formatted context must state clean slate, NOT invent anything
        assert "No prior farmer profile or diagnostic records found on file." in assembled.formatted_prompt_context
        assert "wheat" not in assembled.formatted_prompt_context
        assert "rice" not in assembled.formatted_prompt_context
        break


# =========================================================================
# 7. Provider Success
# =========================================================================
@pytest.mark.asyncio
async def test_provider_success(async_client: AsyncClient):
    farmer = await register_farmer(async_client, "Successful Farmer")
    mock_provider = MockAdvisoryProvider(
        name="test_ai",
        status=AdvisoryProviderStatus.SUCCESS,
        content="Rotate with legumes to restore nitrogen balance naturally.",
    )
    default_provider_router.set_override_provider(mock_provider)

    try:
        conv_res = await async_client.post(
            "/api/v1/advisory/conversations",
            json={"title": "Soil rotation advice"},
            headers=farmer["headers"],
        )
        conv_id = conv_res.json()["data"]["id"]

        msg_res = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_id}/messages",
            json={"message_text": "How can I improve nitrogen naturally?"},
            headers=farmer["headers"],
        )
        assert msg_res.status_code == 200
        data = msg_res.json()["data"]
        assert data["provider_status"] == AdvisoryProviderStatus.SUCCESS
        assert data["provider_name"] == "test_ai"
        assert "Rotate with legumes" in data["assistant_message"]["message_text"]
    finally:
        default_provider_router.set_override_provider(None)


# =========================================================================
# 8. Provider Unavailable (When no LLM keys are configured)
# =========================================================================
@pytest.mark.asyncio
async def test_provider_unavailable(async_client: AsyncClient):
    farmer = await register_farmer(async_client, "Unconfigured Farmer")
    unconfigured_provider = UnconfiguredProvider()
    default_provider_router.set_override_provider(unconfigured_provider)

    try:
        conv_res = await async_client.post(
            "/api/v1/advisory/conversations",
            json={"title": "Test Unconfigured"},
            headers=farmer["headers"],
        )
        conv_id = conv_res.json()["data"]["id"]

        msg_res = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_id}/messages",
            json={"message_text": "What fertilizer should I use?"},
            headers=farmer["headers"],
        )
        assert msg_res.status_code == 200
        data = msg_res.json()["data"]
        assert data["provider_status"] == AdvisoryProviderStatus.PROVIDER_UNAVAILABLE
        assert "unconfigured" in data["provider_name"]
        # Clear explanation returned to the farmer without crashing or fabricating
        assert "unconfigured" in data["assistant_message"]["message_text"].lower()
    finally:
        default_provider_router.set_override_provider(None)


# =========================================================================
# 9. Provider Timeout and Failure
# =========================================================================
@pytest.mark.asyncio
async def test_provider_timeout_and_failure(async_client: AsyncClient):
    farmer = await register_farmer(async_client, "Timeout Farmer")

    # Timeout
    timeout_provider = MockAdvisoryProvider(
        name="timeout_provider",
        should_timeout=True,
    )
    default_provider_router.set_override_provider(timeout_provider)

    try:
        conv_res = await async_client.post(
            "/api/v1/advisory/conversations",
            json={"title": "Test Timeout"},
            headers=farmer["headers"],
        )
        conv_id = conv_res.json()["data"]["id"]

        msg_res = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_id}/messages",
            json={"message_text": "Can you advise on pest control?"},
            headers=farmer["headers"],
        )
        assert msg_res.status_code == 200
        data = msg_res.json()["data"]
        assert data["provider_status"] == AdvisoryProviderStatus.PROVIDER_TIMEOUT
        assert "timed out" in data["assistant_message"]["message_text"]

        # Failure / Error
        error_provider = MockAdvisoryProvider(
            name="error_provider",
            status=AdvisoryProviderStatus.PROVIDER_ERROR,
            content="An internal provider error occurred.",
            error_message="API Gateway 502",
        )
        default_provider_router.set_override_provider(error_provider)

        msg2_res = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_id}/messages",
            json={"message_text": "Please try again."},
            headers=farmer["headers"],
        )
        assert msg2_res.status_code == 200
        data2 = msg2_res.json()["data"]
        assert data2["provider_status"] == AdvisoryProviderStatus.PROVIDER_ERROR
    finally:
        default_provider_router.set_override_provider(None)


# =========================================================================
# 10. Safety and Uncertainty Handling
# =========================================================================
@pytest.mark.asyncio
async def test_safety_and_uncertainty_handling(async_client: AsyncClient):
    farmer = await register_farmer(async_client, "Safety Farmer")
    mock_provider = MockAdvisoryProvider(
        name="safety_ai",
        content="Consider spraying insecticides or fungicides as needed.",
    )
    default_provider_router.set_override_provider(mock_provider)

    try:
        conv_res = await async_client.post(
            "/api/v1/advisory/conversations",
            json={"title": "Safety Test"},
            headers=farmer["headers"],
        )
        conv_id = conv_res.json()["data"]["id"]

        # Case A: Chemical safety triggered
        msg_res = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_id}/messages",
            json={"message_text": "What chemical pesticide spray dosage should I apply?"},
            headers=farmer["headers"],
        )
        assert msg_res.status_code == 200
        disclaimers = msg_res.json()["data"]["safety_disclaimers"]
        # Must contain Chemical Safety Notice
        assert any("Chemical Safety Notice" in d for d in disclaimers)
        assert any("KVK" in d for d in disclaimers)

        # Case B: Visual disease diagnosis encouragement
        msg_res2 = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_id}/messages",
            json={
                "message_text": "My wheat leaves have brown spots, diagnose what disease it is"
            },
            headers=farmer["headers"],
        )
        assert msg_res2.status_code == 200
        disclaimers2 = msg_res2.json()["data"]["safety_disclaimers"]
        # Must encourage uploading leaf photo via Disease Detection
        assert any("Disease Detection" in d for d in disclaimers2)

        # Case C: Insufficient context for vague queries
        msg_res3 = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_id}/messages",
            json={"message_text": "help me"},
            headers=farmer["headers"],
        )
        assert msg_res3.status_code == 200
        data3 = msg_res3.json()["data"]
        assert data3["provider_status"] == AdvisoryProviderStatus.INSUFFICIENT_CONTEXT
    finally:
        default_provider_router.set_override_provider(None)


# =========================================================================
# 11. Conversation Retrieval and Deletion
# =========================================================================
@pytest.mark.asyncio
async def test_conversation_retrieval_and_deletion(async_client: AsyncClient):
    farmer = await register_farmer(async_client, "Lifecycle Farmer")

    # Create two conversations
    c1 = await async_client.post(
        "/api/v1/advisory/conversations",
        json={"title": "Session 1"},
        headers=farmer["headers"],
    )
    c1_id = c1.json()["data"]["id"]

    c2 = await async_client.post(
        "/api/v1/advisory/conversations",
        json={"title": "Session 2"},
        headers=farmer["headers"],
    )
    c2_id = c2.json()["data"]["id"]

    # List conversations
    list_res = await async_client.get(
        "/api/v1/advisory/conversations",
        headers=farmer["headers"],
    )
    assert list_res.status_code == 200
    ids = [c["id"] for c in list_res.json()["data"]]
    assert c1_id in ids
    assert c2_id in ids

    # Delete conversation 1
    del_res = await async_client.delete(
        f"/api/v1/advisory/conversations/{c1_id}",
        headers=farmer["headers"],
    )
    assert del_res.status_code == 200
    assert del_res.json()["data"] is True

    # Conversation 1 should now be 404
    get_res = await async_client.get(
        f"/api/v1/advisory/conversations/{c1_id}",
        headers=farmer["headers"],
    )
    assert get_res.status_code == 404
