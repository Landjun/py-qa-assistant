"""知识库语义检索服务：query → embed → FAISS → SQLite chunk 回查。"""
import time
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentChunk
from app.services import embedding_service, faiss_service


@dataclass
class RetrievalResult:
    content: str
    source: str
    document_id: int
    chunk_id: int
    score: float
    image_path: str | None = None


def _add_log_step(log_ctx, step_name: str, service_name: str, input_data: dict, output_data: dict, t0: float, status: str, error_message: str = "") -> None:
    if log_ctx is None:
        return
    from app.services.qa_log_service import LogStep
    log_ctx.add_step(LogStep(
        step_name=step_name,
        service_name=service_name,
        input_data=input_data,
        output_data=output_data,
        duration_ms=int((time.monotonic() - t0) * 1000),
        status=status,
        error_message=error_message,
    ))


async def search(
    db: AsyncSession,
    query: str,
    top_k: int = 3,
    score_threshold: float = 0.5,
    log_ctx=None,
) -> tuple[list[RetrievalResult], int]:
    """返回 (results, duration_ms)。results 按 score 降序，低于阈值的已过滤。"""
    t0 = time.monotonic()

    if faiss_service.get_vector_count() == 0:
        raise ValueError("知识库为空，请先上传文档并完成向量化")

    # Step 1: query 向量化
    t_embed = time.monotonic()
    try:
        vectors = await embedding_service.embed_texts([query])
        query_vec = vectors[0]
        _add_log_step(log_ctx, "embedding", "dashscope",
                      {"query": query[:200]},
                      {"vector_dim": len(query_vec)},
                      t_embed, "SUCCESS")
    except Exception as e:
        _add_log_step(log_ctx, "embedding", "dashscope",
                      {"query": query[:200]}, {},
                      t_embed, "FAILED", str(e))
        raise

    # Step 2: FAISS 检索 + 分数过滤
    t_faiss = time.monotonic()
    try:
        search_k = min(top_k * 3, faiss_service.get_vector_count())
        raw_results = await faiss_service.search(query_vec, search_k)

        filtered: list[tuple[int, float]] = []
        for chunk_id, raw_score in raw_results:
            norm_score = max(0.0, min(1.0, (raw_score + 1.0) / 2.0))
            if norm_score >= score_threshold:
                filtered.append((chunk_id, norm_score))
        filtered = filtered[:top_k]

        _add_log_step(log_ctx, "faiss_search", "faiss",
                      {"search_k": search_k, "score_threshold": score_threshold},
                      {"raw_count": len(raw_results), "filtered_count": len(filtered)},
                      t_faiss, "SUCCESS")
    except Exception as e:
        _add_log_step(log_ctx, "faiss_search", "faiss", {}, {}, t_faiss, "FAILED", str(e))
        raise

    # Step 3: SQLite 回查 chunk + document 信息
    t_retrieval = time.monotonic()
    results: list[RetrievalResult] = []
    try:
        if filtered:
            chunk_ids = [cid for cid, _ in filtered]
            scores_map = {cid: score for cid, score in filtered}

            stmt = (
                select(DocumentChunk, Document)
                .join(Document, DocumentChunk.document_id == Document.id)
                .where(DocumentChunk.id.in_(chunk_ids))
            )
            rows = (await db.execute(stmt)).all()
            chunk_map = {row.DocumentChunk.id: (row.DocumentChunk, row.Document) for row in rows}

            for cid, score in filtered:
                if cid not in chunk_map:
                    continue
                chunk, doc = chunk_map[cid]
                results.append(RetrievalResult(
                    content=chunk.content,
                    source=doc.title,
                    document_id=doc.id,
                    chunk_id=chunk.id,
                    score=round(score, 4),
                    image_path=chunk.image_path,
                ))

        _add_log_step(log_ctx, "retrieval", "sqlite",
                      {"chunk_ids": [cid for cid, _ in filtered]},
                      {"result_count": len(results),
                       "sources": [r.source for r in results]},
                      t_retrieval, "SUCCESS")
    except Exception as e:
        _add_log_step(log_ctx, "retrieval", "sqlite", {}, {}, t_retrieval, "FAILED", str(e))
        raise

    duration_ms = int((time.monotonic() - t0) * 1000)
    return results, duration_ms
