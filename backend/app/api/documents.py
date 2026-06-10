"""文档管理接口。"""
import email.header
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.services import document_service
from app.services.auth_service import require_roles

_admin_only = require_roles("admin")
_admin_teacher = require_roles("admin", "teacher")


def _decode_filename(raw: str) -> str:
    """解码 RFC 2047 MIME 编码的文件名（PowerShell HttpClient 上传时会产生此格式）。"""
    parts = email.header.decode_header(raw)
    decoded = ""
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded += part.decode(charset or "utf-8", errors="replace")
        else:
            decoded += part
    return decoded

logger = logging.getLogger("app.api.documents")
router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_TYPES = {"text/markdown", "text/plain", "text/x-markdown"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


# ─── 响应模型 ────────────────────────────────────────────────────────────────

class ChunkOut(BaseModel):
    id: int
    document_id: int
    faiss_id: int | None
    title_path: str
    content: str
    char_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentOut(BaseModel):
    id: int
    filename: str
    title: str
    file_type: str
    status: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── 接口 ────────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_admin_only),
) -> DocumentOut:
    """上传 Markdown 文件，自动分块入库。"""
    # 文件大小检查（先读全部内容）
    raw = await file.read()
    if len(raw) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"文件超过 5MB 限制")

    # 解码
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="文件编码必须为 UTF-8")

    filename = _decode_filename(file.filename or "unknown.md")
    title = filename.rsplit(".", 1)[0]  # 去掉扩展名作为 title

    logger.info("上传文档: %s (%d bytes)", filename, len(raw))
    try:
        doc = await document_service.create_document(db, filename, title, text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return DocumentOut.model_validate(doc)


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_admin_teacher),
) -> list[DocumentOut]:
    """获取所有文档列表（admin/teacher）。"""
    docs = await document_service.list_documents(db)
    return [DocumentOut.model_validate(d) for d in docs]


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_admin_teacher),
) -> DocumentOut:
    """获取单个文档详情（admin/teacher）。"""
    doc = await document_service.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return DocumentOut.model_validate(doc)


@router.get("/{document_id}/chunks", response_model=list[ChunkOut])
async def get_chunks(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_admin_teacher),
) -> list[ChunkOut]:
    """获取文档的所有分块（admin/teacher）。"""
    doc = await document_service.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    chunks = await document_service.get_chunks(db, document_id)
    return [ChunkOut.model_validate(c) for c in chunks]


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(_admin_only),
) -> None:
    """删除文档及其所有分块（admin only）。"""
    ok = await document_service.delete_document(db, document_id)
    if not ok:
        raise HTTPException(status_code=404, detail="文档不存在")
