import base64
import io
import uuid
import pytest
from httpx import AsyncClient
from PIL import Image

from app.schemas.advisory import AdvisoryProviderStatus
from app.services.advisory.providers.mock_provider import MockAdvisoryProvider
from app.services.advisory.providers.router import default_provider_router


async def register_farmer(client: AsyncClient, name: str = "Advisory Farmer") -> dict:
    unique_phone = f"+9199{uuid.uuid4().hex[:8]}"
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
    data = res.json()["data"]
    token = data["access_token"]
    user_id = data["user"]["id"]
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "user_id": uuid.UUID(user_id),
        "token": token,
    }


def create_test_image_b64(fmt: str = "JPEG", size=(50, 50), color="green") -> str:
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# =========================================================================
# 1. Multilingual Question Tests
# =========================================================================

@pytest.mark.asyncio
async def test_multilingual_supported_languages(async_client: AsyncClient):
    mock = MockAdvisoryProvider(
        content="వరి పంట ఆకుల పసుపు సమస్యకు సలహా: తగినంత నత్రజని అందించండి.",
        supports_multilingual=True,
    )
    default_provider_router.set_override_provider(mock)

    try:
        farmer = await register_farmer(async_client, "Venkat Rao")

        # 1. Create conversation in Telugu ('te')
        conv_res = await async_client.post(
            "/api/v1/advisory/conversations",
            json={"title": "వరి పంట సలహా", "language": "te"},
            headers=farmer["headers"],
        )
        assert conv_res.status_code == 201
        conv_data = conv_res.json()["data"]
        assert conv_data["language"] == "te"
        conv_id = conv_data["id"]

        # 2. Send Telugu question
        msg_res = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_id}/messages",
            json={
                "message_text": "నా వరి ఆకులు పసుపు రంగులోకి మారుతున్నాయి. ఏమి చేయాలి?",
                "language": "te",
            },
            headers=farmer["headers"],
        )
        assert msg_res.status_code == 200
        msg_data = msg_res.json()["data"]
        assert msg_data["provider_status"] == AdvisoryProviderStatus.SUCCESS.value
        assert mock.last_received_request is not None
        assert mock.last_received_request.language == "te"

        # 3. Hindi ('hi') question
        msg_res_hi = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_id}/messages",
            json={
                "message_text": "गेहूं की पत्तियां पीली हो रही हैं, क्या करें?",
                "language": "hi",
            },
            headers=farmer["headers"],
        )
        assert msg_res_hi.status_code == 200
        assert mock.last_received_request.language == "hi"

    finally:
        default_provider_router.set_override_provider(None)


@pytest.mark.asyncio
async def test_multilingual_unsupported_language_rejected(async_client: AsyncClient):
    farmer = await register_farmer(async_client, "Language Tester")

    # Creating conversation with unsupported language
    conv_res = await async_client.post(
        "/api/v1/advisory/conversations",
        json={"title": "Test", "language": "unsupported_lang"},
        headers=farmer["headers"],
    )
    assert conv_res.status_code == 422

    # Creating valid conversation first
    valid_conv = await async_client.post(
        "/api/v1/advisory/conversations",
        json={"title": "Valid Conv", "language": "en"},
        headers=farmer["headers"],
    )
    assert valid_conv.status_code == 201
    conv_id = valid_conv.json()["data"]["id"]

    # Sending message with unsupported language
    msg_res = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={"message_text": "What fertilizer for wheat?", "language": "xyz"},
        headers=farmer["headers"],
    )
    assert msg_res.status_code == 422


# =========================================================================
# 2. Image-Based Advisory Tests
# =========================================================================

@pytest.mark.asyncio
async def test_valid_image_formats_accepted(async_client: AsyncClient):
    mock = MockAdvisoryProvider(
        content="I observe slight leaf chlorosis in the attached image. Ensure adequate micronutrient balance.",
        supports_images=True,
    )
    default_provider_router.set_override_provider(mock)

    try:
        farmer = await register_farmer(async_client, "Image Farmer")

        conv_res = await async_client.post(
            "/api/v1/advisory/conversations",
            json={"title": "Leaf image consultation"},
            headers=farmer["headers"],
        )
        assert conv_res.status_code == 201
        conv_id = conv_res.json()["data"]["id"]

        # 1. JPEG image
        jpeg_b64 = create_test_image_b64("JPEG", color="yellow")
        res_jpeg = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_id}/messages",
            json={
                "message_text": "Why are my paddy leaves turning yellow as seen in this photo?",
                "image_base64": jpeg_b64,
                "image_content_type": "image/jpeg",
                "image_filename": "paddy_leaf.jpg",
            },
            headers=farmer["headers"],
        )
        assert res_jpeg.status_code == 200
        data_jpeg = res_jpeg.json()["data"]
        assert data_jpeg["provider_status"] == AdvisoryProviderStatus.SUCCESS.value
        assert mock.last_received_request.image_bytes is not None
        assert mock.last_received_request.image_mime_type == "image/jpeg"
        # Verify disclaimers include image advisory notice
        disclaimers = data_jpeg["safety_disclaimers"]
        assert any("Visual Advisory Notice" in d for d in disclaimers)

        # 2. PNG image
        png_b64 = create_test_image_b64("PNG", color="green")
        res_png = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_id}/messages",
            json={
                "message_text": "Are these spots concerning?",
                "image_base64": png_b64,
                "image_content_type": "image/png",
                "image_filename": "leaf_sample.png",
            },
            headers=farmer["headers"],
        )
        assert res_png.status_code == 200
        assert mock.last_received_request.image_mime_type == "image/png"

        # 3. WebP image
        webp_b64 = create_test_image_b64("WEBP", color="brown")
        res_webp = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_id}/messages",
            json={
                "message_text": "What could cause this damage?",
                "image_base64": webp_b64,
                "image_content_type": "image/webp",
                "image_filename": "plant.webp",
            },
            headers=farmer["headers"],
        )
        assert res_webp.status_code == 200
        assert mock.last_received_request.image_mime_type == "image/webp"

    finally:
        default_provider_router.set_override_provider(None)


@pytest.mark.asyncio
async def test_invalid_image_formats_rejected(async_client: AsyncClient):
    farmer = await register_farmer(async_client, "Validation Tester")
    conv_res = await async_client.post(
        "/api/v1/advisory/conversations",
        json={"title": "Validation Conv"},
        headers=farmer["headers"],
    )
    conv_id = conv_res.json()["data"]["id"]

    # Unsupported extension
    valid_b64 = create_test_image_b64("JPEG")
    res_bad_ext = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={
            "message_text": "Examine this file",
            "image_base64": valid_b64,
            "image_content_type": "image/jpeg",
            "image_filename": "danger.exe",
        },
        headers=farmer["headers"],
    )
    assert res_bad_ext.status_code == 400
    assert "Unsupported image file extension" in res_bad_ext.json()["detail"]

    # Unsupported MIME type
    res_bad_mime = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={
            "message_text": "Examine this file",
            "image_base64": valid_b64,
            "image_content_type": "application/pdf",
            "image_filename": "doc.jpg",
        },
        headers=farmer["headers"],
    )
    assert res_bad_mime.status_code == 400
    assert "Unsupported image MIME type" in res_bad_mime.json()["detail"]

    # Corrupted image bytes
    corrupt_b64 = base64.b64encode(b"not an image file content").decode("utf-8")
    res_corrupt = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={
            "message_text": "Examine this file",
            "image_base64": corrupt_b64,
            "image_content_type": "image/jpeg",
            "image_filename": "corrupt.jpg",
        },
        headers=farmer["headers"],
    )
    assert res_corrupt.status_code == 400
    assert "Invalid or corrupted image file" in res_corrupt.json()["detail"]


@pytest.mark.asyncio
async def test_oversized_image_rejected(async_client: AsyncClient):
    farmer = await register_farmer(async_client, "Oversized Tester")
    conv_res = await async_client.post(
        "/api/v1/advisory/conversations",
        json={"title": "Size Conv"},
        headers=farmer["headers"],
    )
    conv_id = conv_res.json()["data"]["id"]

    # Create oversized bytes (> 10MB)
    oversized_bytes = b"0" * (11 * 1024 * 1024)
    oversized_b64 = base64.b64encode(oversized_bytes).decode("utf-8")

    res = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={
            "message_text": "Look at my crop",
            "image_base64": oversized_b64,
            "image_content_type": "image/jpeg",
            "image_filename": "huge.jpg",
        },
        headers=farmer["headers"],
    )
    assert res.status_code == 400
    assert "exceeds maximum allowed size" in res.json()["detail"]


# =========================================================================
# 3. Provider Capability Handling Tests
# =========================================================================

@pytest.mark.asyncio
async def test_provider_without_image_support_returns_structured_limitation(async_client: AsyncClient):
    # Mock provider that does NOT support images
    mock = MockAdvisoryProvider(
        content="I am a text-only advisor.",
        supports_images=False,
    )
    default_provider_router.set_override_provider(mock)

    try:
        farmer = await register_farmer(async_client, "Capability Farmer")
        conv_res = await async_client.post(
            "/api/v1/advisory/conversations",
            json={"title": "Capability Test"},
            headers=farmer["headers"],
        )
        conv_id = conv_res.json()["data"]["id"]

        jpeg_b64 = create_test_image_b64("JPEG")
        res = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_id}/messages",
            json={
                "message_text": "What do you see on these leaves?",
                "image_base64": jpeg_b64,
                "image_content_type": "image/jpeg",
                "image_filename": "leaf.jpg",
            },
            headers=farmer["headers"],
        )
        assert res.status_code == 200
        data = res.json()["data"]
        # Must return structured PROVIDER_UNAVAILABLE instead of inventing an answer
        assert data["provider_status"] == AdvisoryProviderStatus.PROVIDER_UNAVAILABLE.value
        assert "does not support image understanding" in data["assistant_message"]["message_text"]

    finally:
        default_provider_router.set_override_provider(None)


# =========================================================================
# 4. User Isolation & Multi-turn with Images
# =========================================================================

@pytest.mark.asyncio
async def test_user_isolation_with_multimodal_advisory(async_client: AsyncClient):
    mock = MockAdvisoryProvider(content="Advisory advice for Farmer A", supports_images=True)
    default_provider_router.set_override_provider(mock)

    try:
        farmer_a = await register_farmer(async_client, "Farmer A")
        farmer_b = await register_farmer(async_client, "Farmer B")

        # Farmer A creates conversation with initial image question
        jpeg_b64 = create_test_image_b64("JPEG")
        conv_a = await async_client.post(
            "/api/v1/advisory/conversations",
            json={
                "title": "Farmer A Corn Query",
                "initial_message": "Why are my corn tassels drying up?",
                "image_base64": jpeg_b64,
                "image_content_type": "image/jpeg",
            },
            headers=farmer_a["headers"],
        )
        assert conv_a.status_code == 201
        conv_a_id = conv_a.json()["data"]["id"]

        # Farmer B tries to post a message into Farmer A's conversation -> 404
        bad_post = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_a_id}/messages",
            json={"message_text": "Sneaky question"},
            headers=farmer_b["headers"],
        )
        assert bad_post.status_code == 404

        # Farmer B tries to fetch Farmer A's conversation detail -> 404
        bad_get = await async_client.post(
            f"/api/v1/advisory/conversations/{conv_a_id}",
            headers=farmer_b["headers"],
        )
        assert bad_get.status_code in (404, 405)

    finally:
        default_provider_router.set_override_provider(None)


# =========================================================================
# 5. Text-Only Requests Continue Working (Backward Compatibility)
# =========================================================================

@pytest.mark.asyncio
async def test_existing_text_only_advisory_unaffected(async_client: AsyncClient):
    mock = MockAdvisoryProvider(content="Standard text-only agronomic advice.")
    default_provider_router.set_override_provider(mock)

    try:
        farmer = await register_farmer(async_client, "Text Farmer")
        res = await async_client.post(
            "/api/v1/advisory/conversations",
            json={"initial_message": "How often should I irrigate wheat in black cotton soil?"},
            headers=farmer["headers"],
        )
        assert res.status_code == 201
        data = res.json()["data"]
        assert len(data["messages"]) == 2
        assert mock.last_received_request.image_bytes is None
        assert mock.last_received_request.farmer_question == "How often should I irrigate wheat in black cotton soil?"

    finally:
        default_provider_router.set_override_provider(None)
