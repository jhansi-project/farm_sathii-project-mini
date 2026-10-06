import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class DiseaseDiagnosis(Base):
    __tablename__ = "disease_diagnoses"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    original_image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    predicted_condition: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4), nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    is_confident: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # General crop disease management guidance (non-chemical cultural practices & disclaimers)
    management_guidance: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationship
    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="disease_diagnoses"
    )

    def __repr__(self) -> str:
        return f"<DiseaseDiagnosis condition={self.predicted_condition} confident={self.is_confident}>"
