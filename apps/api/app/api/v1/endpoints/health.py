from typing import Any

from fastapi import APIRouter

from app.core.config import settings
from app.db.session import check_db_health

router = APIRouter()


@router.get("/health", summary="Health check with subsystem verification")
async def health_check() -> dict[str, Any]:
    db_status = await check_db_health()
    return {
        "status": "ok" if db_status.get("connected") else "degraded",
        "service": "pragya-api",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
    }
