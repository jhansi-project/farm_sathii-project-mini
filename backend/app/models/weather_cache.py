from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List
from sqlalchemy import DateTime, JSON, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class WeatherCache(Base):
    __tablename__ = "weather_cache"

    cache_key: Mapped[str] = mapped_column(String(100), primary_key=True)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)

    # Verified weather observation metrics & forecast
    current_conditions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    forecast_daily: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)

    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<WeatherCache key={self.cache_key} expires={self.expires_at}>"
