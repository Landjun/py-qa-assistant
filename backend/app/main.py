"""FastAPI 应用入口。

启动（开发）：
    uv run uvicorn app.main:app --reload
启动（生产，同时托管前端）：
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.conversations import router as conversations_router
from app.api.courses import router as courses_router
from app.api.documents import router as documents_router
from app.api.health import router as health_router
from app.api.logs import router as logs_router
from app.api.retrieval import router as retrieval_router
from app.api.settings import router as settings_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.database import init_db, seed_db
from app.services import faiss_service

# frontend/dist 相对于项目根目录
_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"
# backend/static：FAQ 截图等静态资源
_STATIC = Path(__file__).parent.parent / "static"

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_db()
    await faiss_service.init_index()
    logging.getLogger("app").info("数据库 + FAISS 索引初始化完成")
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.service_name, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(auth_router)
    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(conversations_router)
    app.include_router(courses_router)
    app.include_router(documents_router)
    app.include_router(logs_router)
    app.include_router(retrieval_router)
    app.include_router(settings_router)

    # FAQ 截图等后端静态资源
    if _STATIC.exists():
        app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")

    # 生产模式：托管前端静态文件
    if _DIST.exists():
        app.mount("/assets", StaticFiles(directory=str(_DIST / "assets")), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str) -> FileResponse:
            """所有非 /api 路由返回 index.html（React Router SPA）。"""
            return FileResponse(str(_DIST / "index.html"))

    return app


app = create_app()
