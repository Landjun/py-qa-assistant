"""从用户消息和对话历史中提取课节编号。"""
import re

_CN_DIGIT: dict[str, int] = {
    '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
    '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
}


def _cn_to_int(s: str) -> int | None:
    """中文/阿拉伯数字字符串 → 整数（1-48），无法解析返回 None。"""
    s = s.strip()
    if not s:
        return None
    if s.isdigit():
        n = int(s)
        return n if 1 <= n <= 48 else None

    # 十 / 二十四 / 三十八 …
    if '十' in s:
        idx = s.index('十')
        tens_s = s[:idx]
        ones_s = s[idx + 1:]
        tens = _CN_DIGIT.get(tens_s, 1) if tens_s else 1  # "十" alone ≡ 1×10
        ones = _CN_DIGIT.get(ones_s, 0) if ones_s else 0
        n = tens * 10 + ones
    elif len(s) == 1:
        n = _CN_DIGIT.get(s, -1)
    else:
        return None

    return n if 1 <= n <= 48 else None


_NUM = r'([零一二三四五六七八九十]+|\d+)'

_EXPLICIT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r'第\s*' + _NUM + r'\s*[节讲课]', re.IGNORECASE),
    re.compile(r'(\d+)\s*节课?'),
    re.compile(r'[Ll]esson\s*(\d+)', re.IGNORECASE),
    re.compile(r'\b[Ll](\d{1,2})\b'),
]

_PREV_RE = re.compile(r'上[一]?[节课堂]|上节课')
_THIS_RE = re.compile(r'这[节课堂]|本节|这节课|当前课')


def _extract_explicit(text: str) -> int | None:
    """从单段文本提取首个明确节次。"""
    for pat in _EXPLICIT_PATTERNS:
        for m in pat.finditer(text):
            n = _cn_to_int(m.group(1))
            if n is not None:
                return n
    return None


def _last_lesson_in_history(history: str) -> int | None:
    """扫描历史对话，返回最后一次明确提到的节次。"""
    last: int | None = None
    for pat in _EXPLICIT_PATTERNS:
        for m in pat.finditer(history):
            n = _cn_to_int(m.group(1))
            if n is not None:
                last = n
    return last


def extract_lesson_no(message: str, history_text: str = "") -> int | None:
    """
    从用户消息（+对话历史）解析课节编号。

    1. 消息含明确节次（第12节 / lesson 12 / 十二节 …）→ 直接返回。
    2. 消息含「上节课/上一节」→ 历史最近节次 - 1（最小为 1）。
    3. 消息含「这节课/本节」→ 历史最近节次。
    4. 无法识别 → None。
    """
    n = _extract_explicit(message)
    if n is not None:
        return n

    last = _last_lesson_in_history(history_text)

    if _PREV_RE.search(message):
        if last is not None:
            return max(1, last - 1)
        return None

    if _THIS_RE.search(message):
        return last

    return None
