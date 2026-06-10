"""健康检查接口。"""
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.service_name}
