from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class StandardResponse(BaseModel, Generic[DataT]):
    """Standard API response envelope for all FarmSathi endpoints."""
    success: bool = True
    data: Optional[DataT] = None
    message: str = "Operation completed successfully"
    errors: Optional[dict] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
