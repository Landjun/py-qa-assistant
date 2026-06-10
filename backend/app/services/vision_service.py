"""视觉理解服务：调用 DashScope qwen-vl-max 把图片转为文字描述。"""
import base64
import json
import logging
import re
import time

from openai import APIConnectionError, APIError, AsyncOpenAI, AuthenticationError

from app.core.config import settings

logger = logging.getLogger("app.services.vision")

_MAX_BYTES = 5 * 1024 * 1024  # 5 MB

_VISION_SYSTEM = """\
你是图片内容理解助手，专门识别 Python 学习者发来的截图。
请仔细分析图片中的所有文字和内容，返回 JSON，不得包含其他文本：

{
  "image_type": "报错截图|代码截图|IDE界面|安装界面|其他",
  "ocr_text": "图中所有关键文字、报错信息、代码，尽量逐字转录，不同区域用换行分隔",
  "summary": "一句中文概括图片内容（不超过50字）",
  "detected_error": "识别到的报错类型名称，如 ModuleNotFoundError，没有报错则为空字符串"
}"""


def _detect_mime(raw: bytes) -> str:
    """通过 magic bytes 识别图片 MIME 类型。"""
    if raw[:4] == b"\x89PNG":
        return "image/png"
    if raw[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    return ""


def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    m = re.search(r"\{[\s\S]+\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return {"image_type": "其他", "ocr_text": text[:500], "summary": "内容识别失败", "detected_error": ""}


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.dashscope_api_key,
        base_url=settings.dashscope_base_url,
    )


async def describe_image(image_base64: str, user_hint: str = "", log_ctx=None) -> dict:
    """
    调用 qwen-vl-max 理解图片内容。

    Returns:
        dict: {image_type, ocr_text, summary, detected_error}
    Raises:
        ValueError: 图片格式/大小不合规，或未配置 API Key
        RuntimeError: API 调用失败
    """
    if not settings.dashscope_api_key:
        raise ValueError(
            "DASHSCOPE_API_KEY 未配置，无法使用图片理解功能，请在服务器 .env 中添加该配置"
        )

    try:
        raw = base64.b64decode(image_base64)
    except Exception as e:
        raise ValueError(f"图片 base64 解码失败: {e}") from e

    size_mb = len(raw) / 1024 / 1024
    if len(raw) > _MAX_BYTES:
        raise ValueError(f"图片大小 {size_mb:.1f}MB 超过 5MB 限制，请压缩后重试")

    mime = _detect_mime(raw)
    if not mime:
        raise ValueError("不支持的图片格式，请使用 PNG / JPG / WebP")

    data_url = f"data:{mime};base64,{image_base64}"
    hint_extra = f"\n\n用户补充说明：{user_hint}" if user_hint else ""

    t0 = time.monotonic()
    input_data = {"model": settings.vision_model, "mime": mime, "size_bytes": len(raw)}

    def _log(output_data: dict, status: str, error_message: str = "") -> None:
        if log_ctx is None:
            return
        from app.services.qa_log_service import LogStep
        log_ctx.add_step(LogStep(
            step_name="image_understanding",
            service_name="dashscope_vision",
            input_data=input_data,
            output_data=output_data,
            duration_ms=int((time.monotonic() - t0) * 1000),
            status=status,
            error_message=error_message,
        ))

    try:
        client = _get_client()
        response = await client.chat.completions.create(
            model=settings.vision_model,
            messages=[
                {"role": "system", "content": _VISION_SYSTEM},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_url}},
                        {"type": "text", "text": f"请分析这张图片。{hint_extra}"},
                    ],
                },
            ],
            max_tokens=1024,
        )
        raw_text = response.choices[0].message.content or ""
        logger.info("Vision 响应: %s", raw_text[:200])
        parsed = _extract_json(raw_text)
        _log(
            {
                "image_type": parsed.get("image_type"),
                "detected_error": parsed.get("detected_error"),
                "ocr_preview": parsed.get("ocr_text", "")[:200],
            },
            "SUCCESS",
        )
        return parsed

    except AuthenticationError as e:
        _log({}, "FAILED", str(e))
        raise RuntimeError("DashScope API Key 无效，请检查 .env 中 DASHSCOPE_API_KEY") from e
    except APIConnectionError as e:
        _log({}, "FAILED", str(e))
        raise RuntimeError(f"无法连接 DashScope，请检查网络: {e}") from e
    except APIError as e:
        _log({}, "FAILED", str(e))
        raise RuntimeError(f"DashScope Vision API 错误: {e}") from e
