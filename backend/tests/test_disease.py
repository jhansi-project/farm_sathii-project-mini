import io
import uuid
from pathlib import Path
import pytest
from PIL import Image
from httpx import AsyncClient

from app.services.disease_service import disease_service


def create_test_image_bytes(format: str = "JPEG", size=(224, 224), color=(34, 139, 34)) -> bytes:
    """Helper to generate a real in-memory image for test suites."""
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()


@pytest.mark.asyncio
async def test_guest_disease_diagnosis_valid_image(async_client: AsyncClient):
    """Guest user can upload a valid image and receive real MobileNetV3-Large inference without DB persistence."""
    img_bytes = create_test_image_bytes(format="JPEG")
    files = {"file": ("leaf_sample.jpg", img_bytes, "image/jpeg")}

    response = await async_client.post("/api/v1/diseases/diagnose", files=files)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]

    # Verify real inference contract
    assert "predicted_condition" in data
    assert data["predicted_condition"] in disease_service.load_classes()
    assert data["crop"] != ""
    assert data["condition"] != ""
    assert data["display_name"] != ""
    assert isinstance(data["confidence"], float)
    assert 0.0 <= data["confidence"] <= 1.0
    assert isinstance(data["is_confident"], bool)
    assert data["model_version"] == "farmsathi_disease_mobilenetv3_v1.0"

    # Guest user persistence contract
    assert data["is_saved"] is False
    assert data["id"] is None
    assert data["created_at"] is None

    # Top predictions contract
    assert len(data["top_predictions"]) >= 1
    assert data["top_predictions"][0]["raw_class"] == data["predicted_condition"]

    # Cultural guidance contract (non-chemical)
    guidance = data["management_guidance"]
    assert len(guidance["cultural_practices"]) > 0
    assert len(guidance["sanitation"]) > 0
    assert "Krishi Vigyan Kendra" in guidance["disclaimer"] or "extension" in guidance["disclaimer"].lower()


@pytest.mark.asyncio
async def test_real_dataset_image_inference(async_client: AsyncClient):
    """Verifies inference on an actual held-out test sample from the dataset if available."""
    dataset_candidates = list(Path("ml/datasets/crop_diseases").glob("**/*.jpg"))
    if not dataset_candidates:
        pytest.skip("Dataset directory not present in workspace")

    sample_img_path = dataset_candidates[0]
    with open(sample_img_path, "rb") as f:
        file_bytes = f.read()

    files = {"file": (sample_img_path.name, file_bytes, "image/jpeg")}
    response = await async_client.post("/api/v1/diseases/diagnose", files=files)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["predicted_condition"] in disease_service.load_classes()
    assert data["confidence"] > 0.5


@pytest.mark.asyncio
async def test_authenticated_diagnosis_persistence_and_history(async_client: AsyncClient):
    """Authenticated user diagnosis is saved to PostgreSQL and retrieved in history."""
    phone = f"+9197{uuid.uuid4().hex[:8]}"
    reg_payload = {
        "phone": phone,
        "password": "Password123!",
        "full_name": "Test Disease Farmer",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201

    access_token = reg_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    img_bytes = create_test_image_bytes(format="PNG", size=(256, 256))
    files = {"file": ("healthy_leaf.png", img_bytes, "image/png")}

    diag_res = await async_client.post("/api/v1/diseases/diagnose", files=files, headers=headers)
    assert diag_res.status_code == 200
    diag_data = diag_res.json()["data"]
    assert diag_data["is_saved"] is True
    assert diag_data["id"] is not None
    diagnosis_id = diag_data["id"]

    # Fetch history
    hist_res = await async_client.get("/api/v1/diseases/history", headers=headers)
    assert hist_res.status_code == 200
    hist_data = hist_res.json()["data"]
    assert len(hist_data) >= 1

    matched = next((item for item in hist_data if item["id"] == diagnosis_id), None)
    assert matched is not None
    assert matched["predicted_condition"] == diag_data["predicted_condition"]
    assert matched["display_name"] == diag_data["display_name"]
    assert matched["is_confident"] == diag_data["is_confident"]
    assert "management_guidance" in matched


@pytest.mark.asyncio
async def test_invalid_file_type_rejected(async_client: AsyncClient):
    """Non-image files like text/pdf are rejected with 400 Bad Request."""
    files = {"file": ("document.txt", b"This is a text document, not an image.", "text/plain")}
    response = await async_client.post("/api/v1/diseases/diagnose", files=files)
    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["detail"] or "Unsupported file type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_corrupted_image_rejected(async_client: AsyncClient):
    """Corrupted image bytes disguised with image extension are rejected with 400."""
    files = {"file": ("broken.jpg", b"corrupted random data not an image", "image/jpeg")}
    response = await async_client.post("/api/v1/diseases/diagnose", files=files)
    assert response.status_code == 400
    assert "Invalid or corrupted image" in response.json()["detail"]


@pytest.mark.asyncio
async def test_oversized_upload_rejected(async_client: AsyncClient):
    """Files exceeding 10 MB limit are rejected with 400 Bad Request."""
    # 10 MB + 1024 bytes
    fake_oversized_bytes = b"0" * (10 * 1024 * 1024 + 1024)
    files = {"file": ("giant_image.jpg", fake_oversized_bytes, "image/jpeg")}
    response = await async_client.post("/api/v1/diseases/diagnose", files=files)
    assert response.status_code == 400
    assert "exceeds maximum allowed size" in response.json()["detail"]


@pytest.mark.asyncio
async def test_model_loading_failure_returns_503(async_client: AsyncClient):
    """When model checkpoint is unavailable or cannot load, returns structured 503 error."""
    try:
        disease_service.set_model_path_override("ml/models/non_existent_disease_model.pth")
        img_bytes = create_test_image_bytes(format="JPEG")
        files = {"file": ("test_leaf.jpg", img_bytes, "image/jpeg")}

        response = await async_client.post("/api/v1/diseases/diagnose", files=files)
        assert response.status_code == 503
        data = response.json()
        assert "unavailable" in str(data).lower()
    finally:
        disease_service.set_model_path_override(None)


@pytest.mark.asyncio
async def test_disease_model_metrics_endpoint(async_client: AsyncClient):
    """Model evaluation metrics endpoint returns the held-out test evaluation reference."""
    response = await async_client.get("/api/v1/diseases/model-metrics")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["architecture"] == "MobileNetV3-Large"
    assert data["num_classes"] == 17
    assert data["test_samples"] == 2010
    assert data["accuracy"] == 0.9592
    assert data["model_size_mb"] == 16.31


@pytest.mark.asyncio
async def test_unsuitable_non_crop_image_rejected_from_diagnosis(async_client: AsyncClient):
    """Clearly unrelated non-crop images (such as a person, room, or wall) must be flagged as unsuitable."""
    wall_bytes = create_test_image_bytes(format="JPEG", size=(320, 240), color=(235, 230, 215))
    files = {"file": ("indoor_wall.jpg", wall_bytes, "image/jpeg")}
    response = await async_client.post("/api/v1/diseases/diagnose", files=files)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["is_suitable"] is False
    assert data["suitability_message"] is not None


@pytest.mark.asyncio
async def test_person_image_rejected_from_diagnosis(async_client: AsyncClient):
    """Verifies that an image of a person (like the webcam selfie upload) is flagged as unsuitable."""
    person_path = Path("storage/uploads/diseases/c3a004bda3964781.jpg")
    if not person_path.exists():
        pytest.skip("Captured test person image not found in storage")

    with open(person_path, "rb") as f:
        file_bytes = f.read()

    files = {"file": ("captured_person.jpg", file_bytes, "image/jpeg")}
    response = await async_client.post("/api/v1/diseases/diagnose", files=files)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["is_suitable"] is False
    assert data["suitability_message"] is not None

