"""Markdown 文档分块服务。

分块规则：
- 按标题层级（#, ##, ###…）划分 chunk。
- 记录 title_path，例如 "Python基础 > for循环"。
- 单个 chunk 超过 MAX_CHARS 时按段落继续切分。
- 每个 chunk 目标在 MIN_CHARS ~ MAX_CHARS 之间。
- 解析 ![](faq-images/xxx.png) 形式的图片引用存入 image_path。
"""
import re
from dataclasses import dataclass, field

MIN_CHARS = 30    # 过短的 chunk 不单独保存（合并到下一个）
MAX_CHARS = 800   # 超过此长度按段落切分

_IMG_RE = re.compile(r"!\[.*?\]\((faq-images/[^)]+)\)")


@dataclass
class Chunk:
    title_path: str
    content: str
    image_path: str | None = None
    char_count: int = field(init=False)

    def __post_init__(self) -> None:
        self.char_count = len(self.content)


def _build_path(headings: dict[int, str]) -> str:
    parts = [headings[lvl] for lvl in sorted(headings) if headings.get(lvl)]
    return " > ".join(parts) if parts else "文档"


def _extract_image(lines: list[str]) -> tuple[str | None, list[str]]:
    """从行列表中提取第一个 faq-images 图片路径，返回 (image_path, 去掉图片行的剩余行)。"""
    img_path: str | None = None
    cleaned: list[str] = []
    for line in lines:
        m = _IMG_RE.search(line)
        if m:
            if img_path is None:
                img_path = m.group(1)
            # 图片行本身不放入 content（避免向量化时引入无意义 markdown 语法）
        else:
            cleaned.append(line)
    return img_path, cleaned


def _split_by_paragraphs(title_path: str, text: str, image_path: str | None = None) -> list[Chunk]:
    """把超长 chunk 按段落（双换行）拆分，第一个子 chunk 继承 image_path。"""
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    chunks: list[Chunk] = []
    buf: list[str] = []
    buf_len = 0

    for para in paragraphs:
        if buf and buf_len + len(para) + 2 > MAX_CHARS:
            content = "\n\n".join(buf)
            if len(content) >= MIN_CHARS:
                img = image_path if not chunks else None  # 只有第一个子 chunk 继承图片
                chunks.append(Chunk(title_path=title_path, content=content, image_path=img))
            buf, buf_len = [para], len(para)
        else:
            buf.append(para)
            buf_len += len(para) + 2

    if buf:
        content = "\n\n".join(buf)
        if len(content) >= MIN_CHARS:
            img = image_path if not chunks else None
            chunks.append(Chunk(title_path=title_path, content=content, image_path=img))

    return chunks


def _flush(title_path: str, lines: list[str]) -> list[Chunk]:
    """把当前行缓冲区变成 chunk，提取图片路径，按需按段落拆分。"""
    img_path, clean_lines = _extract_image(lines)
    text = "\n".join(clean_lines).strip()
    if len(text) < MIN_CHARS:
        return []
    if len(text) <= MAX_CHARS:
        return [Chunk(title_path=title_path, content=text, image_path=img_path)]
    return _split_by_paragraphs(title_path, text, image_path=img_path)


def chunk_markdown(text: str) -> list[Chunk]:
    """解析 Markdown 文本，返回 Chunk 列表（含 image_path）。"""
    headings: dict[int, str] = {}
    buf: list[str] = []
    chunks: list[Chunk] = []

    heading_re = re.compile(r"^(#{1,6})\s+(.+)")

    for line in text.splitlines():
        m = heading_re.match(line)
        if m:
            flushed = _flush(_build_path(headings), buf)
            chunks.extend(flushed)
            buf = []

            level = len(m.group(1))
            title = m.group(2).strip()
            headings[level] = title
            for lvl in [k for k in headings if k > level]:
                del headings[lvl]
        else:
            buf.append(line)

    chunks.extend(_flush(_build_path(headings), buf))

    return chunks
