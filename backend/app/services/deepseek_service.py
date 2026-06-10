"""DeepSeek 调用封装（OpenAI-compatible Chat Completions）。"""
import json
import logging
import re

from openai import AsyncOpenAI, APIConnectionError, APIError, AuthenticationError

from app.core.config import settings
from app.schemas.chat import QAData
from app.services.prompt_service import SYSTEM_PROMPT, build_user_message

logger = logging.getLogger("app.services.deepseek")

_VALID_TYPES = {"概念解释", "代码理解", "报错排查", "作业思路", "环境配置", "其他"}


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
    )


def _extract_json(text: str) -> dict:
    """从 LLM 输出中提取 JSON，兼容 markdown 代码块包裹的情况。"""
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 尝试从 ```json ... ``` 或 ``` ... ``` 中提取
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试找第一个 { ... } 块
    match = re.search(r"\{[\s\S]+\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"无法从 LLM 输出中解析 JSON，原始内容: {text[:200]}")


def _parse_qa_data(raw: str) -> QAData:
    """解析 DeepSeek 返回文本为 QAData，失败时降级保留 answer。"""
    try:
        obj = _extract_json(raw)
        qt = obj.get("question_type", "其他")
        if qt not in _VALID_TYPES:
            qt = "其他"
        return QAData(
            question_type=qt,
            answer=str(obj.get("answer", "")),
            beginner_explanation=str(obj.get("beginner_explanation", "")),
            code_example=str(obj.get("code_example", "")),
            need_more_info=bool(obj.get("need_more_info", False)),
            need_more_info_fields=[str(f) for f in obj.get("need_more_info_fields", [])],
        )
    except Exception as e:
        logger.warning("JSON 解析失败，降级处理: %s", e)
        # 降级：把原始文本作为 answer 返回
        return QAData(question_type="其他", answer=raw)


async def ask_structured(question: str) -> QAData:
    """向 DeepSeek 发送结构化问答请求，返回 QAData。

    Raises:
        ValueError: API Key 未配置。
        RuntimeError: API 调用网络 / 认证失败。
    """
    if not settings.deepseek_api_key:
        raise ValueError("DeepSeek API Key 未配置，请检查 .env 文件中的 DEEPSEEK_API_KEY")

    client = _get_client()
    user_msg = build_user_message(question)
    logger.info("DeepSeek 请求: model=%s len=%d", settings.deepseek_model, len(question))

    try:
        response = await client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,      # 降低随机性，提高 JSON 稳定性
            max_tokens=1500,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or ""
        logger.info("DeepSeek 响应: tokens=%s", response.usage)
        return _parse_qa_data(raw)

    except AuthenticationError as e:
        logger.error("DeepSeek 认证失败: %s", e)
        raise RuntimeError("DeepSeek API Key 无效，请确认密钥是否正确") from e
    except APIConnectionError as e:
        logger.error("DeepSeek 连接失败: %s", e)
        raise RuntimeError(f"无法连接 DeepSeek 服务，请检查网络或 DEEPSEEK_BASE_URL: {e}") from e
    except APIError as e:
        logger.error("DeepSeek API 错误: %s", e)
        raise RuntimeError(f"DeepSeek API 返回错误: {e.message}") from e
