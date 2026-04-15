"""Mock AI service for analysis generation (Phase 1)."""
import json
from datetime import datetime

from app.models.enums import StageEnum


def analyze_student_chats(student_name: str, latest_chat_content: str | None) -> dict:
    """
    Return deterministic mock analysis data.
    This intentionally avoids external model dependencies.
    """
    content = latest_chat_content or "暂无聊天内容"
    is_positive = any(k in content for k in ["想", "了解", "报名", "价格", "课程"])

    stage = StageEnum.高意向.value if is_positive else StageEnum.已联系.value
    result = {
        "stage": stage,
        "main_need": "希望结课后继续提升职业能力",
        "core_concerns": "时间安排与价格投入",
        "interest_direction": "实战项目与求职辅导",
        "risk_points": "若短期未跟进，可能转向其他机构",
        "recommended_course": "进阶实战营",
        "recommended_action": "48小时内完成1次定向沟通并发送案例",
        "tags_json": json.dumps(["复购潜力", "关注价格", "需及时跟进"], ensure_ascii=False),
        "summary": f"Mock分析：学员{student_name}当前处于{stage}阶段，建议尽快推进复购沟通。",
        "raw_json": json.dumps(
            {
                "engine": "mock-ai-v1",
                "generated_at": datetime.utcnow().isoformat(),
                "signal_from_latest_chat": content,
                "positive_signal": is_positive,
            },
            ensure_ascii=False,
        ),
    }
    return result
