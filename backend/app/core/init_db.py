import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

logger = logging.getLogger("farmsathi.init_db")

async def ensure_database_exists():
    """
    Connects to the default postgres database and creates farmsathi_db if it does not exist.
    """
    url = settings.DATABASE_URL
    # Base URL pointing to default 'postgres' database
    if "/" in url:
        base_url = url.rsplit("/", 1)[0] + "/postgres"
    else:
        base_url = url

    # Connect with isolation_level="AUTOCOMMIT" to allow CREATE DATABASE
    engine = create_async_engine(base_url, isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as conn:
            # Check if farmsathi_v2_db exists
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = 'farmsathi_v2_db'")
            )
            exists = result.scalar() is not None
            if not exists:
                await conn.execute(text("CREATE DATABASE farmsathi_v2_db"))
                print("Created database: farmsathi_v2_db")
            else:
                print("Database farmsathi_v2_db already exists")
    except Exception as e:
        print(f"Database check/creation notice: {type(e).__name__}: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(ensure_database_exists())
