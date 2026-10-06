import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import DateTime, ForeignKey, JSON, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class CropRecommendation(Base):
    __tablename__ = "crop_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # 7 Soil & Climate Features
    nitrogen: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    phosphorus: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    potassium: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    temperature: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    humidity: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    ph: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    rainfall: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)

    # Model Output
    recommended_crop: Mapped[str] = mapped_column(String(50), nullable=False)
    top_predictions: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationship
    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="crop_recommendations"
    )

    def __repr__(self) -> str:
        return f"<CropRecommendation crop={self.recommended_crop} at={self.created_at}>"
