"""知识库检索接口。"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services import retrieval_service

router = APIRouter(prefix="/api/retrieval", tags=["retrieval"])


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=3, ge=1, le=20)
    score: float = Field(default=0.5, ge=0.0, le=1.0)


class RetrievalResultOut(BaseModel):
    content: str
    source: str
    document_id: int
    chunk_id: int
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[RetrievalResultOut]
    duration_ms: int


@router.post("/search", response_model=SearchResponse)
async def search(
    req: SearchRequest,
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """语义检索，返回最相似的 top_k 条知识库片段。"""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query 不能为空")
    try:
        results, duration_ms = await retrieval_service.search(
            db, req.query, req.top_k, req.score
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return SearchResponse(
        query=req.query,
        results=[
            RetrievalResultOut(
                content=r.content,
                source=r.source,
                document_id=r.document_id,
                chunk_id=r.chunk_id,
                score=r.score,
            )
            for r in results
        ],
        duration_ms=duration_ms,
    )
