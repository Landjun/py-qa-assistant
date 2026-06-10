"""Markdown 文档分块服务。

分块规则：
- 按标题层级（#, ##, ###…）划分 chunk。
- 记录 title_path，例如 "Python基础 > for循环"。
- 单个 chunk 超过 MAX_CHARS 时按段落继续切分。
- 每个 chunk 目标在 MIN_CHARS ~ MAX_CHARS 之间。
"""
import re
from dataclasses import dataclass, field

MIN_CHARS = 30    # 过短的 chunk 不单独保存（合并到下一个）
MAX_CHARS = 800   # 超过此长度按段落切分


@dataclass
class Chunk:
    title_path: str
    content: str
    char_count: int = field(init=False)

    def __post_init__(self) -> None:
        self.char_count = len(self.content)


def _build_path(headings: dict[int, str]) -> str:
    parts = [headings[lvl] for lvl in sorted(headings) if headings.get(lvl)]
    return " > ".join(parts) if parts else "文档"


def _split_by_paragraphs(title_path: str, text: str) -> list[Chunk]:
    """把超长 chunk 按段落（双换行）拆分，尽量保持每段 ≤ MAX_CHARS。"""
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    chunks: list[Chunk] = []
    buf: list[str] = []
    buf_len = 0

    for para in paragraphs:
        if buf and buf_len + len(para) + 2 > MAX_CHARS:
            content = "\n\n".join(buf)
            if len(content) >= MIN_CHARS:
                chunks.append(Chunk(title_path=title_path, content=content))
            buf, buf_len = [para], len(para)
        else:
            buf.append(para)
            buf_len += len(para) + 2

    if buf:
        content = "\n\n".join(buf)
        if len(content) >= MIN_CHARS:
            chunks.append(Chunk(title_path=title_path, content=content))

    return chunks


def _flush(title_path: str, lines: list[str]) -> list[Chunk]:
    """把当前行缓冲区变成 chunk（可能进一步按段落拆分）。"""
    text = "\n".join(lines).strip()
    if len(text) < MIN_CHARS:
        return []
    if len(text) <= MAX_CHARS:
        return [Chunk(title_path=title_path, content=text)]
    return _split_by_paragraphs(title_path, text)


def chunk_markdown(text: str) -> list[Chunk]:
    """解析 Markdown 文本，返回 Chunk 列表。"""
    headings: dict[int, str] = {}
    buf: list[str] = []
    chunks: list[Chunk] = []

    heading_re = re.compile(r"^(#{1,6})\s+(.+)")

    for line in text.splitlines():
        m = heading_re.match(line)
        if m:
            # 遇到新标题：先 flush 当前缓冲区
            flushed = _flush(_build_path(headings), buf)
            chunks.extend(flushed)
            buf = []

            level = len(m.group(1))
            title = m.group(2).strip()
            headings[level] = title
            # 清除更深层的标题（防止路径残留）
            for lvl in [k for k in headings if k > level]:
                del headings[lvl]
        else:
            buf.append(line)

    # 文档末尾剩余内容
    chunks.extend(_flush(_build_path(headings), buf))

    return chunks
