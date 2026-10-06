import base64
import io
import uuid
import pytest
from httpx import AsyncClient
from PIL import Image

from app.schemas.advisory import AdvisoryProviderStatus
from tests.test_advisory import register_farmer


def create_sample_leaf_image_base64() -> str:
    """Creates a synthetic small leaf-like image for testing."""
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


@pytest.mark.asyncio
async def test_all_12_advisory_scenarios(async_client: AsyncClient):
    farmer = await register_farmer(async_client, name="Krishnamurthy")

    # Create conversation
    conv_res = await async_client.post(
        "/api/v1/advisory/conversations",
        json={"title": "Agronomic Scenarios Test", "language": "en"},
        headers=farmer["headers"],
    )
    assert conv_res.status_code == 201
    conv_id = conv_res.json()["data"]["id"]

    # -------------------------------------------------------------
    # Scenario 1: "Why are my tomato flowers falling?"
    # -------------------------------------------------------------
    res1 = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={"message_text": "Why are my tomato flowers falling?"},
        headers=farmer["headers"],
    )
    assert res1.status_code == 200
    msg1 = res1.json()["data"]["assistant_message"]["message_text"]
    status1 = res1.json()["data"]["provider_status"]
    assert "Welcome to FarmSathi Agricultural Advisory" not in msg1
    assert any(term in msg1.lower() for term in ["flower", "blossom", "temperature", "boron", "planofix"])
    assert status1 == AdvisoryProviderStatus.SUCCESS

    # -------------------------------------------------------------
    # Scenario 2: "Why is my paddy not growing properly?"
    # -------------------------------------------------------------
    res2 = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={"message_text": "Why is my paddy not growing properly?"},
        headers=farmer["headers"],
    )
    assert res2.status_code == 200
    msg2 = res2.json()["data"]["assistant_message"]["message_text"]
    status2 = res2.json()["data"]["provider_status"]
    assert "Welcome to FarmSathi Agricultural Advisory" not in msg2
    assert any(term in msg2.lower() for term in ["growth", "root", "nitrogen", "nutrient", "stunted"])
    assert status2 == AdvisoryProviderStatus.SUCCESS

    # -------------------------------------------------------------
    # Scenario 3: "When should I irrigate my crop?"
    # -------------------------------------------------------------
    res3 = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={"message_text": "When should I irrigate my crop?"},
        headers=farmer["headers"],
    )
    assert res3.status_code == 200
    msg3 = res3.json()["data"]["assistant_message"]["message_text"]
    status3 = res3.json()["data"]["provider_status"]
    assert "Welcome to FarmSathi Agricultural Advisory" not in msg3
    assert any(term in msg3.lower() for term in ["irrigate", "moisture", "root-zone", "watering"])
    assert status3 == AdvisoryProviderStatus.SUCCESS

    # -------------------------------------------------------------
    # Scenario 4: "How can I improve seed germination?"
    # -------------------------------------------------------------
    res4 = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={"message_text": "How can I improve seed germination?"},
        headers=farmer["headers"],
    )
    assert res4.status_code == 200
    msg4 = res4.json()["data"]["assistant_message"]["message_text"]
    status4 = res4.json()["data"]["provider_status"]
    assert "Welcome to FarmSathi Agricultural Advisory" not in msg4
    assert any(term in msg4.lower() for term in ["germination", "seed treatment", "thiram", "trichoderma", "depth"])
    assert status4 == AdvisoryProviderStatus.SUCCESS

    # -------------------------------------------------------------
    # Scenario 5: "Why are my crop leaves turning yellow?"
    # -------------------------------------------------------------
    res5 = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={"message_text": "Why are my crop leaves turning yellow?"},
        headers=farmer["headers"],
    )
    assert res5.status_code == 200
    msg5 = res5.json()["data"]["assistant_message"]["message_text"]
    status5 = res5.json()["data"]["provider_status"]
    assert "Welcome to FarmSathi Agricultural Advisory" not in msg5
    assert any(term in msg5.lower() for term in ["yellow", "nitrogen", "zinc", "khaira", "waterlog"])
    assert status5 == AdvisoryProviderStatus.SUCCESS

    # -------------------------------------------------------------
    # Scenario 6: "What should I do after sowing?"
    # -------------------------------------------------------------
    res6 = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={"message_text": "What should I do after sowing?"},
        headers=farmer["headers"],
    )
    assert res6.status_code == 200
    msg6 = res6.json()["data"]["assistant_message"]["message_text"]
    status6 = res6.json()["data"]["provider_status"]
    assert "Welcome to FarmSathi Agricultural Advisory" not in msg6
    assert any(term in msg6.lower() for term in ["sowing", "irrigation", "crust", "weed", "gap filling"])
    assert status6 == AdvisoryProviderStatus.SUCCESS

    # -------------------------------------------------------------
    # Scenario 7: "Will it rain tomorrow?"
    # -------------------------------------------------------------
    res7 = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={"message_text": "Will it rain tomorrow?"},
        headers=farmer["headers"],
    )
    assert res7.status_code == 200
    msg7 = res7.json()["data"]["assistant_message"]["message_text"]
    assert "Welcome to FarmSathi Agricultural Advisory" not in msg7
    assert any(term in msg7.lower() for term in ["rain", "tomorrow", "forecast", "weather"])

    # -------------------------------------------------------------
    # Scenario 8: Crop recommendation question with N, P, K, pH, rainfall
    # -------------------------------------------------------------
    res8 = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={"message_text": "Recommend crop for N=90, P=42, K=43, ph=6.5, rainfall=200"},
        headers=farmer["headers"],
    )
    assert res8.status_code == 200
    msg8 = res8.json()["data"]["assistant_message"]["message_text"]
    status8 = res8.json()["data"]["provider_status"]
    assert "Welcome to FarmSathi Agricultural Advisory" not in msg8
    assert "Random Forest" in msg8 or "Recommended Crop" in msg8
    assert status8 == AdvisoryProviderStatus.SUCCESS

    # -------------------------------------------------------------
    # Scenario 9: Attached crop image + "Can you tell me what is the problem in the leaf image?"
    # -------------------------------------------------------------
    leaf_b64 = create_sample_leaf_image_base64()
    res9 = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={
            "message_text": "Can you tell me what is the problem in the leaf image?",
            "image_base64": leaf_b64,
            "image_content_type": "image/jpeg",
        },
        headers=farmer["headers"],
    )
    assert res9.status_code == 200
    msg9 = res9.json()["data"]["assistant_message"]["message_text"]
    status9 = res9.json()["data"]["provider_status"]
    assert "Welcome to FarmSathi Agricultural Advisory" not in msg9
    # Must run MobileNetV3 analysis and return condition/confidence/assessment
    assert any(term in msg9 for term in ["MobileNetV3", "Diagnosed Condition", "Assessment", "Healthy", "Confidence"])
    assert status9 in [AdvisoryProviderStatus.SUCCESS, AdvisoryProviderStatus.INSUFFICIENT_CONTEXT]

    # -------------------------------------------------------------
    # Scenario 10: "What crops will grow in the location of Bowrampet village located in Dundigal?"
    # -------------------------------------------------------------
    res10 = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={"message_text": "What crops will grow in the location of Bowrampet village located in Dundigal?"},
        headers=farmer["headers"],
    )
    assert res10.status_code == 200
    msg10 = res10.json()["data"]["assistant_message"]["message_text"]
    status10 = res10.json()["data"]["provider_status"]
    assert "Welcome to FarmSathi Agricultural Advisory" not in msg10
    # Must acknowledge location or Dundigal / Bowrampet
    assert any(term in msg10.lower() for term in ["bowrampet", "dundigal", "telangana", "location"])
    # Must explain missing soil parameters
    assert any(term in msg10 for term in ["Nitrogen", "Phosphorus", "Potassium", "pH"])
    # Status must be INSUFFICIENT_CONTEXT because soil test parameters are required
    assert status10 == AdvisoryProviderStatus.INSUFFICIENT_CONTEXT

    # -------------------------------------------------------------
    # Scenario 11: Synonyms and phrasing variations
    # -------------------------------------------------------------
    # Flower drop variation
    res11a = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={"message_text": "Tomato flower drop problem"},
        headers=farmer["headers"],
    )
    assert res11a.status_code == 200
    msg11a = res11a.json()["data"]["assistant_message"]["message_text"]
    assert "flower" in msg11a.lower() or "blossom" in msg11a.lower()

    # Irrigation variation
    res11b = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={"message_text": "When to water plants?"},
        headers=farmer["headers"],
    )
    assert res11b.status_code == 200
    msg11b = res11b.json()["data"]["assistant_message"]["message_text"]
    assert "moisture" in msg11b.lower() or "irrigation" in msg11b.lower()

    # -------------------------------------------------------------
    # Scenario 12: Previously unseen agricultural question
    # -------------------------------------------------------------
    res12 = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id}/messages",
        json={"message_text": "How do I maintain overall organic soil biodiversity in my farmland?"},
        headers=farmer["headers"],
    )
    assert res12.status_code == 200
    msg12 = res12.json()["data"]["assistant_message"]["message_text"]
    status12 = res12.json()["data"]["provider_status"]
    assert "Welcome to FarmSathi Agricultural Advisory" not in msg12
    assert "Integrated Field Management" in msg12 or "Root-Zone" in msg12
    assert status12 == AdvisoryProviderStatus.SUCCESS


@pytest.mark.asyncio
async def test_multilingual_advisory_responses(async_client: AsyncClient):
    """Verifies that advisory queries in Telugu and Hindi return native localized responses."""
    farmer = await register_farmer(async_client, name="Lakshman Rao")

    # Telugu conversation
    conv_te = await async_client.post(
        "/api/v1/advisory/conversations",
        json={"title": "తెలుగు వ్యవసాయం", "language": "te"},
        headers=farmer["headers"],
    )
    assert conv_te.status_code == 201
    conv_id_te = conv_te.json()["data"]["id"]

    res_te = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id_te}/messages",
        json={"message_text": "టమాటా పూత రాలిపోతుంది ఎందుకు?", "language": "te"},
        headers=farmer["headers"],
    )
    assert res_te.status_code == 200
    msg_te = res_te.json()["data"]["assistant_message"]["message_text"]
    assert "పూత" in msg_te
    assert "Welcome to FarmSathi" not in msg_te

    # Hindi conversation
    conv_hi = await async_client.post(
        "/api/v1/advisory/conversations",
        json={"title": "बीज अंकुरण", "language": "hi"},
        headers=farmer["headers"],
    )
    assert conv_hi.status_code == 201
    conv_id_hi = conv_hi.json()["data"]["id"]

    res_hi = await async_client.post(
        f"/api/v1/advisory/conversations/{conv_id_hi}/messages",
        json={"message_text": "बीज अंकुरण कैसे सुधारें?", "language": "hi"},
        headers=farmer["headers"],
    )
    assert res_hi.status_code == 200
    msg_hi = res_hi.json()["data"]["assistant_message"]["message_text"]
    assert "अंकुरण" in msg_hi
    assert "Welcome to FarmSathi" not in msg_hi
