"""DashScope text-embedding-v4 调用封装（OpenAI-compatible 接口）。

- 每批最多 BATCH_SIZE 条文本
- 向量维度 1024
- DASHSCOPE_API_KEY 未配置时给出明确错误
"""
import logging

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger("app.services.embedding")

BATCH_SIZE = 10
DIMENSION = 1024


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.dashscope_api_key,
        base_url=settings.dashscope_base_url,
    )


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """批量获取文本向量，返回与输入等长的 float 列表。

    Raises:
        ValueError: DASHSCOPE_API_KEY 未配置。
        RuntimeError: API 调用失败。
    """
    if not settings.dashscope_api_key:
        raise ValueError("DASHSCOPE_API_KEY 未配置，请检查 .env 文件中的 DASHSCOPE_API_KEY")

    client = _get_client()
    all_vectors: list[list[float]] = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        logger.info(
            "Embedding 批次 %d/%d，本批 %d 条",
            i // BATCH_SIZE + 1,
            (len(texts) - 1) // BATCH_SIZE + 1,
            len(batch),
        )
        try:
            response = await client.embeddings.create(
                model=settings.embedding_model,
                input=batch,
                encoding_format="float",
                # dimensions 参数：text-embedding-v4 默认 1024，兼容不支持该参数的版本
                extra_body={"dimension": DIMENSION},
            )
        except Exception as e:
            logger.error("DashScope Embedding 调用失败: %s", e)
            raise RuntimeError(f"Embedding 调用失败: {e}") from e

        # 按 index 排序，保证与输入顺序一致
        sorted_data = sorted(response.data, key=lambda d: d.index)
        all_vectors.extend(d.embedding for d in sorted_data)

    logger.info("Embedding 完成，共 %d 个向量，维度=%d", len(all_vectors), DIMENSION)
    return all_vectors
