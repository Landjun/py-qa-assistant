"""FAISS 索引管理（单例 + asyncio.Lock 保证并发安全）。

索引类型：IndexIDMap2(IndexFlatIP) —— 内积相似度，向量写入前 L2 归一化 = 余弦相似度。
删除策略：重建（IndexIDMap2 原理上支持 remove_ids，但重建更可靠）。
"""
import asyncio
import logging
import os

import faiss
import numpy as np

from app.core.config import settings

logger = logging.getLogger("app.services.faiss")

DIMENSION = 1024
_lock = asyncio.Lock()
_index: faiss.Index | None = None


# ─── 内部工具 ────────────────────────────────────────────────────────────────

def _index_path() -> str:
    return settings.faiss_index_path


def _ensure_dir() -> None:
    path = _index_path()
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)


def _load_or_create_sync() -> faiss.Index:
    path = _index_path()
    if os.path.exists(path):
        idx = faiss.read_index(path)
        logger.info("FAISS 索引加载: %s (%d 向量)", path, idx.ntotal)
        return idx
    base = faiss.IndexFlatIP(DIMENSION)
    idx = faiss.IndexIDMap2(base)
    logger.info("FAISS 新索引创建，维度=%d", DIMENSION)
    return idx


def _save_sync(idx: faiss.Index) -> None:
    _ensure_dir()
    faiss.write_index(idx, _index_path())
    logger.info("FAISS 索引已保存: %s (%d 向量)", _index_path(), idx.ntotal)


def _normalize(vectors: list[list[float]]) -> np.ndarray:
    arr = np.array(vectors, dtype=np.float32)
    faiss.normalize_L2(arr)
    return arr


# ─── 公开接口 ────────────────────────────────────────────────────────────────

async def init_index() -> None:
    """应用启动时预加载索引（可选，懒加载也可）。"""
    global _index
    async with _lock:
        _index = await asyncio.to_thread(_load_or_create_sync)


def get_vector_count() -> int:
    global _index
    if _index is None:
        path = _index_path()
        if os.path.exists(path):
            _index = faiss.read_index(path)
        else:
            return 0
    return _index.ntotal


async def add_vectors(vectors: list[list[float]], chunk_ids: list[int]) -> None:
    """添加向量到索引并持久化。chunk_ids 作为 FAISS ID。"""
    if not vectors:
        return

    def _do() -> None:
        global _index
        if _index is None:
            _index = _load_or_create_sync()
        arr = _normalize(vectors)
        ids = np.array(chunk_ids, dtype=np.int64)
        _index.add_with_ids(arr, ids)
        _save_sync(_index)

    async with _lock:
        await asyncio.to_thread(_do)


async def search(query_vector: list[float], top_k: int) -> list[tuple[int, float]]:
    """余弦相似度检索，返回 [(chunk_id, cosine_sim), ...]，已按分数降序。"""

    def _do() -> list[tuple[int, float]]:
        global _index
        if _index is None:
            _index = _load_or_create_sync()
        if _index.ntotal == 0:
            return []
        arr = _normalize([query_vector])
        k = min(top_k, _index.ntotal)
        distances, ids = _index.search(arr, k)
        results: list[tuple[int, float]] = []
        for dist, fid in zip(distances[0], ids[0]):
            if fid == -1:
                continue
            results.append((int(fid), float(dist)))
        return results

    async with _lock:
        return await asyncio.to_thread(_do)


async def rebuild_from_embeddings(
    vectors: list[list[float]], chunk_ids: list[int]
) -> None:
    """重建整个索引（删除文档后调用）。"""

    def _do() -> None:
        global _index
        base = faiss.IndexFlatIP(DIMENSION)
        idx = faiss.IndexIDMap2(base)
        if vectors:
            arr = _normalize(vectors)
            ids = np.array(chunk_ids, dtype=np.int64)
            idx.add_with_ids(arr, ids)
        _index = idx
        _save_sync(idx)

    async with _lock:
        await asyncio.to_thread(_do)
