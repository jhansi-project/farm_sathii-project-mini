import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

EXPECTED_TABLES = [
    "users",
    "farmer_profiles",
    "crop_recommendations",
    "disease_diagnoses",
    "advisory_conversations",
    "advisory_messages",
    "weather_cache",
]

async def verify_tables():
    engine = create_async_engine(settings.DATABASE_URL)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' ORDER BY table_name;"
                )
            )
            tables = [row[0] for row in result.fetchall()]
            print("Found public tables in PostgreSQL 18:")
            for t in tables:
                print(f"  - {t}")
            
            missing = [t for t in EXPECTED_TABLES if t not in tables]
            if missing:
                print(f"FAILED: Missing expected tables: {missing}")
                return False
            else:
                print(f"SUCCESS: All {len(EXPECTED_TABLES)} required FarmSathi tables are present!")
                return True
    except Exception as e:
        print(f"Verification error: {type(e).__name__}: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify_tables())
