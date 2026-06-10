"""课程 / 课节 / 课节资源 CRUD 服务。"""
import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course, Lesson, LessonAsset

logger = logging.getLogger("app.services.course")

# 课程资源存储根目录（相对 backend/static/）
_ASSET_ROOT = Path(__file__).parent.parent.parent / "static" / "course-assets"


# ─── 课程 ─────────────────────────────────────────────────────────────────────

async def create_course(db: AsyncSession, name: str, description: str = "") -> Course:
    course = Course(name=name, description=description)
    db.add(course)
    await db.commit()
    await db.refresh(course)
    logger.info("课程创建: id=%d name=%s", course.id, name)
    return course


async def list_courses(db: AsyncSession) -> list[Course]:
    result = await db.execute(select(Course).order_by(Course.id.asc()))
    return list(result.scalars().all())


async def get_course(db: AsyncSession, course_id: int) -> Course | None:
    return await db.get(Course, course_id)


# ─── 课节 ─────────────────────────────────────────────────────────────────────

async def create_lesson(
    db: AsyncSession,
    course_id: int,
    lesson_no: int,
    title: str,
    summary: str | None = None,
) -> Lesson:
    lesson = Lesson(course_id=course_id, lesson_no=lesson_no, title=title, summary=summary)
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return lesson


async def list_lessons(db: AsyncSession, course_id: int) -> list[Lesson]:
    result = await db.execute(
        select(Lesson).where(Lesson.course_id == course_id).order_by(Lesson.lesson_no.asc())
    )
    return list(result.scalars().all())


async def get_lesson(db: AsyncSession, lesson_id: int) -> Lesson | None:
    return await db.get(Lesson, lesson_id)


async def update_lesson(
    db: AsyncSession,
    lesson_id: int,
    title: str | None = None,
    summary: str | None = None,
) -> Lesson | None:
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        return None
    if title is not None:
        lesson.title = title
    if summary is not None:
        lesson.summary = summary
    await db.commit()
    await db.refresh(lesson)
    return lesson


async def init_48_lessons(db: AsyncSession, course_name: str = "Python 编程入门（共 48 节）") -> Course:
    """幂等：若已存在则返回已有课程，否则创建课程 + 48 个占位课节。"""
    result = await db.execute(select(Course).order_by(Course.id.asc()).limit(1))
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing

    course = Course(name=course_name, description="Python 零基础入门课程，共 48 节。")
    db.add(course)
    await db.flush()

    for i in range(1, 49):
        db.add(Lesson(course_id=course.id, lesson_no=i, title=f"第 {i} 节"))

    await db.commit()
    await db.refresh(course)
    logger.info("init-48 完成: course_id=%d lessons=48", course.id)
    return course


# ─── 课节资源 ──────────────────────────────────────────────────────────────────

SLIDE_EXTS = {"pdf", "ppt", "pptx"}
CODE_EXTS = {"py", "ipynb", "txt", "zip"}


def _infer_asset_type(ext: str) -> str:
    if ext in SLIDE_EXTS:
        return "slide"
    if ext in CODE_EXTS:
        return "code"
    return "other"


async def save_asset(
    db: AsyncSession,
    lesson: Lesson,
    filename: str,
    data: bytes,
) -> LessonAsset:
    """保存文件到 static/course-assets/lesson-{no}/ 并写入数据库。"""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in SLIDE_EXTS | CODE_EXTS:
        raise ValueError(
            f"不支持的文件格式 .{ext}，课件接受 pdf/ppt/pptx，代码接受 py/ipynb/txt/zip"
        )

    asset_type = _infer_asset_type(ext)
    dest_dir = _ASSET_ROOT / f"lesson-{lesson.lesson_no}"
    dest_dir.mkdir(parents=True, exist_ok=True)

    # 同名文件覆盖（追加时间戳可选，这里保持简单）
    dest = dest_dir / filename
    dest.write_bytes(data)

    rel_path = f"course-assets/lesson-{lesson.lesson_no}/{filename}"

    asset = LessonAsset(
        lesson_id=lesson.id,
        asset_type=asset_type,
        filename=filename,
        file_path=rel_path,
        file_type=ext,
        size_bytes=len(data),
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    logger.info("资源上传: lesson=%d type=%s file=%s size=%d", lesson.id, asset_type, filename, len(data))
    return asset


async def list_assets(db: AsyncSession, lesson_id: int) -> list[LessonAsset]:
    result = await db.execute(
        select(LessonAsset).where(LessonAsset.lesson_id == lesson_id).order_by(LessonAsset.id.asc())
    )
    return list(result.scalars().all())


async def get_asset(db: AsyncSession, asset_id: int) -> LessonAsset | None:
    return await db.get(LessonAsset, asset_id)


async def delete_asset(db: AsyncSession, asset_id: int) -> bool:
    asset = await db.get(LessonAsset, asset_id)
    if not asset:
        return False
    # 删除磁盘文件（不存在则跳过）
    disk_path = _ASSET_ROOT.parent / asset.file_path  # static/../file_path → static/file_path
    disk_path = Path(__file__).parent.parent.parent / "static" / asset.file_path
    if disk_path.exists():
        disk_path.unlink()
    await db.delete(asset)
    await db.commit()
    logger.info("资源删除: asset_id=%d file=%s", asset_id, asset.filename)
    return True
