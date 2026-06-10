"""意图识别服务：基于 DeepSeek 对用户消息进行意图分类和指代消解。"""
import json
import logging
import re
import time
from dataclasses import dataclass

from openai import APIConnectionError, APIError, AsyncOpenAI, AuthenticationError

from app.core.config import settings
from app.models.conversation import Message

logger = logging.getLogger("app.services.intent")

VALID_INTENTS = {"PYTHON_QA", "BUG_HELP", "FEEDBACK", "CHAT"}


@dataclass
class IntentResult:
    confidence: float
    intent: str
    resolved_question: str
    reason: str


def format_history(messages: list[Message]) -> str:
    """将最近 6 条消息格式化为意图识别上下文。"""
    if not messages:
        return "（无历史记录）"
    lines: list[str] = []
    for m in messages[-6:]:
        role = "用户" if m.role == "user" else "助手"
        text = m.content[:100] + "…" if len(m.content) > 100 else m.content
        lines.append(f"{role}: {text}")
    return "\n".join(lines)


_INTENT_SYSTEM = """\
你是 Python 学习答疑客服系统的专业意图识别器。
你的输出将直接用于自动路由和客服决策，请严格遵循规则，不得自由发挥。

## 总体目标

基于【对话历史】和【用户最新消息】，完成：

1. 指代消解
2. 意图识别

## 任务一：指代消解

结合【对话历史】，对【用户最新消息】中的指代性表达进行消解，生成一条单句、语义完整、无模糊指代的用户问题。

规则：
1. 必须结合对话历史。
2. 如果用户问题已经明确，不要强行改写。
3. 不得引入对话中不存在的新信息。
4. 输出必须是完整问题句。

## 任务二：意图识别

分类到以下四类之一：

1. PYTHON_QA：
- Python 基础概念
- Python 语法
- 变量、数据类型、列表、字典、元组、集合
- 条件判断、循环、函数、类、模块
- 文件读写、JSON、CSV、正则、时间处理
- requests、FastAPI、Flask、爬虫基础
- uv、虚拟环境、包管理
- pip 安装、pip 太慢、pip 换源、国内镜像、清华源、阿里源
- Python 安装、PATH 配置、Add to PATH、环境变量
- PyCharm 使用、创建项目、选择解释器、配置虚拟环境
- "这个知识点怎么理解"
- "这个代码是什么意思"
- "帮我讲懂这个 Python 概念"

2. BUG_HELP：
- 用户贴出 Python 报错
- 用户说代码运行不了
- 用户问如何解决异常
- SyntaxError、IndentationError、ModuleNotFoundError、TypeError、ValueError
- ImportError、FileNotFoundError、KeyError、IndexError、JSONDecodeError

3. FEEDBACK：
- 用户反馈当前答疑系统不好用
- 用户希望增加功能
- 页面打不开、按钮点不了、回答不准、检索不到、上传失败

4. CHAT：
- 不属于以上三类
- 问候、寒暄、情绪表达、无意义输入"""


def _build_user_msg(history_text: str, question: str) -> str:
    return f"""【对话历史】
{history_text}

【用户最新消息】
{question}

输出 JSON，不得包含其他文本：

{{
  "confidence": 0.0,
  "intent": "PYTHON_QA | BUG_HELP | FEEDBACK | CHAT",
  "resolved_question": "指代消解后的明确问题",
  "reason": "简要分类理由"
}}"""


def _log_step(log_ctx, input_data: dict, output_data: dict, t0: float, status: str, error_message: str = "") -> None:
    if log_ctx is None:
        return
    from app.services.qa_log_service import LogStep
    log_ctx.add_step(LogStep(
        step_name="intent_recognition",
        service_name="deepseek",
        input_data=input_data,
        output_data=output_data,
        duration_ms=int((time.monotonic() - t0) * 1000),
        status=status,
        error_message=error_message,
    ))


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
    raise ValueError(f"无法解析意图 JSON: {text[:200]}")


async def recognize_intent(history_text: str, question: str, log_ctx=None) -> IntentResult:
    """调用 DeepSeek 进行意图识别，失败时调用方应降级。"""
    t0 = time.monotonic()
    input_data = {"question": question[:200], "history_len": len(history_text)}

    if not settings.deepseek_api_key:
        _log_step(log_ctx, input_data, {}, t0, "FAILED", "DEEPSEEK_API_KEY 未配置")
        raise ValueError("DEEPSEEK_API_KEY 未配置")

    client = AsyncOpenAI(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url)
    user_msg = _build_user_msg(history_text, question)
    logger.info("意图识别: question='%s'", question[:60])

    try:
        response = await client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": _INTENT_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.1,
            max_tokens=300,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or ""
        obj = _extract_json(raw)
    except (AuthenticationError, APIConnectionError, APIError) as e:
        _log_step(log_ctx, input_data, {}, t0, "FAILED", str(e))
        raise RuntimeError(str(e)) from e
    except ValueError:
        logger.warning("意图 JSON 解析失败，降级 PYTHON_QA")
        result = IntentResult(confidence=0.5, intent="PYTHON_QA", resolved_question=question, reason="解析失败")
        _log_step(log_ctx, input_data, {"intent": "PYTHON_QA", "fallback": True}, t0, "SUCCESS")
        return result

    intent = obj.get("intent", "PYTHON_QA")
    if intent not in VALID_INTENTS:
        intent = "PYTHON_QA"

    result = IntentResult(
        confidence=float(obj.get("confidence", 0.5)),
        intent=intent,
        resolved_question=str(obj.get("resolved_question", question)) or question,
        reason=str(obj.get("reason", "")),
    )
    _log_step(log_ctx, input_data,
              {"intent": result.intent, "confidence": result.confidence, "reason": result.reason[:100]},
              t0, "SUCCESS")
    logger.info("意图: %s  confidence=%.2f  reason='%s'", result.intent, result.confidence, result.reason)
    return result
