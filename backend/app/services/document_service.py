"""文档 & 分块 CRUD 服务层（含向量化 + FAISS 管理）。"""
import logging

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentChunk
from app.services import embedding_service, faiss_service
from app.services.chunker_service import chunk_markdown

logger = logging.getLogger("app.services.document")


async def create_document(
    db: AsyncSession,
    filename: str,
    title: str,
    content: str,
    file_type: str = "markdown",
) -> Document:
    """保存文档，完成分块 → 向量化 → FAISS 入库。"""
    doc = Document(filename=filename, title=title, file_type=file_type, status="processing")
    db.add(doc)
    await db.flush()  # 获取 doc.id

    # 1. 分块
    chunks = chunk_markdown(content)
    logger.info("文档 '%s' 分块: %d 个 chunk", filename, len(chunks))

    chunk_records: list[DocumentChunk] = []
    for chunk in chunks:
        rec = DocumentChunk(
            document_id=doc.id,
            title_path=chunk.title_path,
            content=chunk.content,
            char_count=chunk.char_count,
            image_path=chunk.image_path,
        )
        db.add(rec)
        chunk_records.append(rec)

    doc.chunk_count = len(chunks)
    await db.flush()  # 获取每个 chunk 的 id

    # 2. 向量化（每批 10 条）
    texts = [c.content for c in chunk_records]
    vectors = await embedding_service.embed_texts(texts)

    # 3. 写入 FAISS & 保存 embedding 到 SQLite
    chunk_ids = [c.id for c in chunk_records]
    await faiss_service.add_vectors(vectors, chunk_ids)

    for rec, vec in zip(chunk_records, vectors):
        rec.faiss_id = rec.id  # faiss_id 与 chunk.id 保持一致
        rec.embedding = np.array(vec, dtype=np.float32).tobytes()

    doc.status = "ready"
    await db.commit()
    await db.refresh(doc)
    logger.info("文档 '%s' 向量化完成，FAISS 向量数=%d", filename, faiss_service.get_vector_count())
    return doc


async def list_documents(db: AsyncSession) -> list[Document]:
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return list(result.scalars().all())


async def get_document(db: AsyncSession, document_id: int) -> Document | None:
    return await db.get(Document, document_id)


async def get_chunks(db: AsyncSession, document_id: int) -> list[DocumentChunk]:
    result = await db.execute(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.id.asc())
    )
    return list(result.scalars().all())


async def delete_document(db: AsyncSession, document_id: int) -> bool:
    """删除文档（cascade 删除 chunks），然后从 SQLite 中读取剩余 chunk 的 embedding 重建 FAISS。"""
    doc = await db.get(Document, document_id)
    if not doc:
        return False

    await db.delete(doc)
    await db.commit()

    # 重建 FAISS：读取所有剩余 chunk 的 embedding
    result = await db.execute(
        select(DocumentChunk).where(DocumentChunk.embedding.is_not(None))
    )
    remaining = list(result.scalars().all())

    vectors = [
        np.frombuffer(c.embedding, dtype=np.float32).tolist()  # type: ignore[arg-type]
        for c in remaining
        if c.embedding
    ]
    ids = [c.id for c in remaining if c.embedding]

    await faiss_service.rebuild_from_embeddings(vectors, ids)
    logger.info(
        "文档 %d 删除后 FAISS 重建完成，剩余向量=%d", document_id, faiss_service.get_vector_count()
    )
    return True


async def get_document_count(db: AsyncSession) -> int:
    from sqlalchemy import func
    result = await db.execute(select(func.count()).select_from(Document))
    return result.scalar_one()


async def get_chunk_count(db: AsyncSession) -> int:
    from sqlalchemy import func
    result = await db.execute(select(func.count()).select_from(DocumentChunk))
    return result.scalar_one()
