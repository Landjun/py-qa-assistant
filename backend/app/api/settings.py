"""系统设置 & 状态接口。"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_db
from app.services import document_service, faiss_service

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SystemStatus(BaseModel):
    document_count: int
    chunk_count: int
    faiss_vector_count: int
    deepseek_configured: bool
    dashscope_configured: bool
    deepseek_model: str
    embedding_model: str
    rerank_model: str


@router.get("/status", response_model=SystemStatus)
async def get_status(db: AsyncSession = Depends(get_db)) -> SystemStatus:
    """返回系统当前状态：文档数、分块数、向量数、模型配置。"""
    doc_count = await document_service.get_document_count(db)
    chunk_count = await document_service.get_chunk_count(db)
    vector_count = faiss_service.get_vector_count()

    return SystemStatus(
        document_count=doc_count,
        chunk_count=chunk_count,
        faiss_vector_count=vector_count,
        deepseek_configured=bool(settings.deepseek_api_key),
        dashscope_configured=bool(settings.dashscope_api_key),
        deepseek_model=settings.deepseek_model,
        embedding_model=settings.embedding_model,
        rerank_model=settings.rerank_model,
    )
