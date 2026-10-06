from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict

from app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str
    timestamp: str


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def check_health() -> HealthResponse:
    """
    Returns system liveness and basic runtime status.
    """
    return HealthResponse(
        success=True,
        data={
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0",
        },
        message="FarmSathi backend service is operational",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
