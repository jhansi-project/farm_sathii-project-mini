import uuid
from decimal import Decimal
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.models import User, FarmerProfile, CropRecommendation, WeatherCache


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_live_postgres_connection(db_session: AsyncSession):
    """Verify live async query execution on PostgreSQL 18 farmsathi_v2_db."""
    result = await db_session.execute(text("SELECT current_database();"))
    db_name = result.scalar()
    assert db_name == "farmsathi_v2_db"


@pytest.mark.asyncio
async def test_live_postgres_crud_and_cascade(db_session: AsyncSession):
    """Verify entity creation and cascade cleanup directly on PostgreSQL 18."""
    # 1. Create a user
    test_user_id = uuid.uuid4()
    unique_phone = f"+9199{uuid.uuid4().hex[:8]}"
    user = User(
        id=test_user_id,
        phone=unique_phone,
        email=f"test_{unique_phone[3:]}@example.com",
        password_hash="argon2id$testhash",
        full_name="Integration Test Farmer",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # 2. Add profile
    profile = FarmerProfile(
        user_id=test_user_id,
        preferred_language="hi",
        state="Maharashtra",
        district="Nashik",
        land_size_acres=Decimal("5.00"),
        soil_type="Black Soil",
    )
    db_session.add(profile)
    await db_session.flush()

    # 3. Add crop recommendation
    crop_rec = CropRecommendation(
        user_id=test_user_id,
        nitrogen=Decimal("85.00"),
        phosphorus=Decimal("40.00"),
        potassium=Decimal("45.00"),
        temperature=Decimal("25.50"),
        humidity=Decimal("78.00"),
        ph=Decimal("6.80"),
        rainfall=Decimal("180.00"),
        recommended_crop="cotton",
        top_predictions=[{"crop": "cotton", "probability": 0.95}],
        model_version="rf_v1.0",
    )
    db_session.add(crop_rec)
    await db_session.flush()

    # Verify relationships & persistence
    res = await db_session.get(User, test_user_id)
    assert res is not None
    assert res.full_name == "Integration Test Farmer"

    # 4. Clean up test record (cascade delete)
    await db_session.delete(user)
    await db_session.commit()

    # Verify deleted
    deleted_user = await db_session.get(User, test_user_id)
    assert deleted_user is None
