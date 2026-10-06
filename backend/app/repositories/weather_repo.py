from datetime import datetime, timezone, timedelta
from typing import Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weather_cache import WeatherCache
from app.repositories.base import BaseRepository


class WeatherCacheRepository(BaseRepository[WeatherCache]):
    def __init__(self, session: AsyncSession):
        super().__init__(WeatherCache, session)

    async def get_valid_cache(self, cache_key: str) -> Optional[WeatherCache]:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(WeatherCache).where(
                WeatherCache.cache_key == cache_key,
                WeatherCache.expires_at > now,
            )
        )
        return result.scalars().first()

    async def get_by_key(self, cache_key: str) -> Optional[WeatherCache]:
        result = await self.session.execute(
            select(WeatherCache).where(WeatherCache.cache_key == cache_key)
        )
        return result.scalars().first()

    async def upsert_cache(
        self,
        cache_key: str,
        latitude,
        longitude,
        current_conditions: dict,
        forecast_daily: Any,
        expires_at: Optional[datetime] = None,
        ttl_minutes: int = 30,
    ) -> WeatherCache:
        now = datetime.now(timezone.utc)
        if expires_at is None:
            expires_at = now + timedelta(minutes=ttl_minutes)

        entry = await self.get_by_key(cache_key)

        if entry:
            entry.latitude = latitude
            entry.longitude = longitude
            entry.current_conditions = current_conditions
            entry.forecast_daily = forecast_daily
            entry.fetched_at = now
            entry.expires_at = expires_at
        else:
            entry = WeatherCache(
                cache_key=cache_key,
                latitude=latitude,
                longitude=longitude,
                current_conditions=current_conditions,
                forecast_daily=forecast_daily,
                fetched_at=now,
                expires_at=expires_at,
            )
            self.session.add(entry)
        await self.session.flush()
        await self.session.refresh(entry)
        return entry

