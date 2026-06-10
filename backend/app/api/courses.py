"""课程 / 课节 / 课节资源 API。

权限：
  - 写操作（创建/上传/删除/更新）→ admin only
  - 读操作（列表/详情/下载）→ 所有已登录角色
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.services import course_service
from app.services.auth_service import get_current_user, require_roles

logger = logging.getLogger("app.api.courses")
router = APIRouter(tags=["courses"])

_admin = require_roles("admin")
_any = get_current_user  # 任意已登录用户

MAX_ASSET_BYTES = 50 * 1024 * 1024  # 50 MB


# ─── 响应模型 ─────────────────────────────────────────────────────────────────

class CourseOut(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    lesson_count: int = 0

    model_config = {"from_attributes": True}


class LessonOut(BaseModel):
    id: int
    course_id: int
    lesson_no: int
    title: str
    summary: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LessonAssetOut(BaseModel):
    id: int
    lesson_id: int
    asset_type: str
    filename: str
    file_path: str
    file_type: str
    size_bytes: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── 请求模型 ─────────────────────────────────────────────────────────────────

class CourseCreate(BaseModel):
    name: str
    description: str = ""


class LessonCreate(BaseModel):
    lesson_no: int
    title: str
    summary: str | None = None


class LessonUpdate(BaseModel):
    title: str | None = None
    summary: str | None = None


# ─── 课程接口 ─────────────────────────────────────────────────────────────────

@router.get("/api/courses", response_model=list[CourseOut])
async def list_courses(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_any),
) -> list[CourseOut]:
    courses = await course_service.list_courses(db)
    result = []
    for c in courses:
        lessons = await course_service.list_lessons(db, c.id)
        out = CourseOut.model_validate(c)
        out.lesson_count = len(lessons)
        result.append(out)
    return result


@router.post("/api/courses", response_model=CourseOut, status_code=201)
async def create_course(
    body: CourseCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_admin),
) -> CourseOut:
    course = await course_service.create_course(db, body.name, body.description)
    return CourseOut.model_validate(course)


@router.post("/api/courses/init-48", response_model=CourseOut, status_code=201)
async def init_48(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_admin),
) -> CourseOut:
    """幂等：一次性建好 1 门课 + 48 个占位课节。已存在则返回现有课程。"""
    course = await course_service.init_48_lessons(db)
    lessons = await course_service.list_lessons(db, course.id)
    out = CourseOut.model_validate(course)
    out.lesson_count = len(lessons)
    return out


# ─── 课节接口 ─────────────────────────────────────────────────────────────────

@router.get("/api/courses/{course_id}/lessons", response_model=list[LessonOut])
async def list_lessons(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_any),
) -> list[LessonOut]:
    course = await course_service.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    lessons = await course_service.list_lessons(db, course_id)
    return [LessonOut.model_validate(l) for l in lessons]


@router.post("/api/courses/{course_id}/lessons", response_model=LessonOut, status_code=201)
async def create_lesson(
    course_id: int,
    body: LessonCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_admin),
) -> LessonOut:
    course = await course_service.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    try:
        lesson = await course_service.create_lesson(db, course_id, body.lesson_no, body.title, body.summary)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建课节失败: {e}")
    return LessonOut.model_validate(lesson)


@router.get("/api/lessons/{lesson_id}", response_model=LessonOut)
async def get_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_any),
) -> LessonOut:
    lesson = await course_service.get_lesson(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="课节不存在")
    return LessonOut.model_validate(lesson)


@router.patch("/api/lessons/{lesson_id}", response_model=LessonOut)
async def update_lesson(
    lesson_id: int,
    body: LessonUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_admin),
) -> LessonOut:
    lesson = await course_service.update_lesson(db, lesson_id, body.title, body.summary)
    if not lesson:
        raise HTTPException(status_code=404, detail="课节不存在")
    return LessonOut.model_validate(lesson)


# ─── 课节资源接口 ─────────────────────────────────────────────────────────────

@router.get("/api/lessons/{lesson_id}/assets", response_model=list[LessonAssetOut])
async def list_assets(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_any),
) -> list[LessonAssetOut]:
    lesson = await course_service.get_lesson(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="课节不存在")
    assets = await course_service.list_assets(db, lesson_id)
    return [LessonAssetOut.model_validate(a) for a in assets]


@router.post("/api/lessons/{lesson_id}/assets", response_model=LessonAssetOut, status_code=201)
async def upload_asset(
    lesson_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_admin),
) -> LessonAssetOut:
    """上传课件（PDF/PPT/PPTX）或代码（py/ipynb/txt/zip）到课节。"""
    lesson = await course_service.get_lesson(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="课节不存在")

    data = await file.read()
    if len(data) > MAX_ASSET_BYTES:
        raise HTTPException(status_code=413, detail="文件超过 50MB 限制")

    filename = file.filename or "unknown"
    try:
        asset = await course_service.save_asset(db, lesson, filename, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return LessonAssetOut.model_validate(asset)


@router.delete("/api/assets/{asset_id}", status_code=204)
async def delete_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_admin),
) -> None:
    ok = await course_service.delete_asset(db, asset_id)
    if not ok:
        raise HTTPException(status_code=404, detail="资源不存在")
