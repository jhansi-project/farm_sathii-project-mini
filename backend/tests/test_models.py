import uuid
from decimal import Decimal
import pytest

from app.models import (
    Base,
    User,
    FarmerProfile,
    CropRecommendation,
    DiseaseDiagnosis,
    AdvisoryConversation,
    AdvisoryMessage,
    WeatherCache,
)


def test_model_tables_metadata():
    """Verify that all 7 required entities are properly registered in Base.metadata."""
    table_names = Base.metadata.tables.keys()
    assert "users" in table_names
    assert "farmer_profiles" in table_names
    assert "crop_recommendations" in table_names
    assert "disease_diagnoses" in table_names
    assert "advisory_conversations" in table_names
    assert "advisory_messages" in table_names
    assert "weather_cache" in table_names


def test_user_model_attributes():
    user = User(
        phone="+919876543210",
        email="farmer@example.com",
        password_hash="argon2id$hashed",
        full_name="Ramesh Kumar",
        is_active=True,
    )
    assert user.full_name == "Ramesh Kumar"
    assert user.phone == "+919876543210"
    assert user.email == "farmer@example.com"
    assert user.is_active is True
    assert "Ramesh Kumar" in repr(user)


def test_farmer_profile_attributes():
    user_id = uuid.uuid4()
    profile = FarmerProfile(
        user_id=user_id,
        preferred_language="hi",
        state="Maharashtra",
        district="Pune",
        land_size_acres=Decimal("4.5"),
        soil_type="Clay Loam",
    )
    assert profile.user_id == user_id
    assert profile.preferred_language == "hi"
    assert profile.state == "Maharashtra"
    assert profile.land_size_acres == Decimal("4.5")
    assert "hi" in repr(profile)


def test_crop_recommendation_attributes():
    crop_rec = CropRecommendation(
        nitrogen=Decimal("90.0"),
        phosphorus=Decimal("42.0"),
        potassium=Decimal("43.0"),
        temperature=Decimal("20.8"),
        humidity=Decimal("82.0"),
        ph=Decimal("6.5"),
        rainfall=Decimal("202.9"),
        recommended_crop="rice",
        top_predictions=[{"crop": "rice", "probability": 0.98}],
        model_version="rf_v1.0",
    )
    assert crop_rec.recommended_crop == "rice"
    assert crop_rec.nitrogen == Decimal("90.0")
    assert crop_rec.model_version == "rf_v1.0"
    assert "rice" in repr(crop_rec)


def test_disease_diagnosis_attributes():
    diag = DiseaseDiagnosis(
        original_image_path="storage/uploads/leaf_01.jpg",
        predicted_condition="Early Blight",
        confidence=Decimal("0.8920"),
        model_version="vision_v1.0",
        is_confident=True,
        management_guidance={"sanitation": "Prune lower leaves"},
    )
    assert diag.predicted_condition == "Early Blight"
    assert diag.confidence == Decimal("0.8920")
    assert diag.is_confident is True
    assert "Early Blight" in repr(diag)


def test_advisory_conversation_attributes():
    conv = AdvisoryConversation(
        user_id=uuid.uuid4(),
        title="Wheat irrigation inquiry",
        language="en",
    )
    assert conv.title == "Wheat irrigation inquiry"
    assert conv.language == "en"
    assert "Wheat irrigation" in repr(conv)


def test_weather_cache_attributes():
    cache = WeatherCache(
        cache_key="18.52_73.85",
        latitude=Decimal("18.520000"),
        longitude=Decimal("73.850000"),
        current_conditions={"temp": 28.5, "humidity": 65},
        forecast_daily={"max_temp": 32.0, "rain_prob": 10},
    )
    assert cache.cache_key == "18.52_73.85"
    assert cache.latitude == Decimal("18.520000")
    assert cache.current_conditions["temp"] == 28.5
