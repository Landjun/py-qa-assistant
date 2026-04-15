"""AI analysis service with mock + future LLM extension points."""
from __future__ import annotations

import json
from datetime import datetime

from app.core.config import settings
from app.models.enums import StageEnum


class AIService:
    """Encapsulates AI analysis logic.

    Default mode uses mock rules. Future mode can call real LLM HTTP API.
    """

    def __init__(self, mode: str = "mock"):
        self.mode = mode

    def analyze_chat(self, *, student_name: str, chat_content: str, chat_record_id: int | None = None) -> dict:
        if self.mode == "llm":
            result = self.analyze_chat_with_llm(student_name=student_name, chat_content=chat_content)
        else:
            result = self.analyze_chat_with_mock(student_name=student_name, chat_content=chat_content)

        result["chat_record_id"] = chat_record_id
        return result

    def analyze_chat_with_mock(self, *, student_name: str, chat_content: str) -> dict:
        """Keyword-rule mock analysis.

        Output fields are fixed for business operation judgment.
        """
        content = chat_content or ""
        stage = StageEnum.已联系.value
        main_need = "结课后持续提升能力"
        core_concerns = "时间安排与学习效果"
        interest_direction = "实战应用"
        risk_points = "若无持续跟进，可能沉默"
        recommended_course = "进阶实战营"
        recommended_action = "48小时内发起一次定向跟进"
        tags: list[str] = ["结课经营", "待跟进"]

        if any(k in content for k in ["赚钱", "副业", "变现"]):
            stage = StageEnum.有兴趣.value
            main_need = "通过AI副业方向实现收入增长"
            interest_direction = "AI副业导向"
            recommended_course = "AI副业变现实战营"
            recommended_action = "发送副业案例并邀请参加说明会"
            tags.append("AI副业导向")

        if any(k in content for k in ["学不会", "零基础", "怕跟不上"]):
            core_concerns = "担心学习门槛高，害怕学不会"
            risk_points = "学习信心不足，若不分层引导易流失"
            recommended_action = "先提供零基础路径与成功案例，降低门槛"
            tags.append("学习顾虑")

        if any(k in content for k in ["价格", "太贵", "预算"]):
            core_concerns = "预算敏感，关注投入产出比"
            risk_points = "价格因素导致决策延迟"
            tags.append("价格敏感")

        if any(k in content for k in ["报名", "什么时候开课", "我想参加"]):
            stage = StageEnum.高意向.value
            recommended_action = "立即安排顾问1v1沟通并推进成交"
            tags.append("高意向")

        summary = f"Mock分析：学员{student_name}阶段为{stage}，需求聚焦“{main_need}”，建议动作：{recommended_action}。"

        raw_payload = {
            "engine": "mock-rule-v2",
            "generated_at": datetime.utcnow().isoformat(),
            "source_text": content,
            "mode": "mock",
        }

        return {
            "stage": stage,
            "main_need": main_need,
            "core_concerns": core_concerns,
            "interest_direction": interest_direction,
            "risk_points": risk_points,
            "recommended_course": recommended_course,
            "recommended_action": recommended_action,
            "tags": tags,
            "summary": summary,
            "tags_json": json.dumps(tags, ensure_ascii=False),
            "raw_json": json.dumps(raw_payload, ensure_ascii=False),
        }

    def analyze_chat_with_llm(self, *, student_name: str, chat_content: str) -> dict:
        """Reserved for future real LLM API call.

        Keep output structure fully aligned with mock output.
        """
        # TODO: Replace with real HTTP request to model provider.
        # Return schema must remain stable for downstream CRUD/API.
        fallback = self.analyze_chat_with_mock(student_name=student_name, chat_content=chat_content)
        fallback["raw_json"] = json.dumps(
            {
                "engine": "llm-placeholder",
                "message": "LLM integration not enabled; fallback to mock output",
                "generated_at": datetime.utcnow().isoformat(),
            },
            ensure_ascii=False,
        )
        return fallback


ai_service = AIService(mode=settings.ai_mode)
