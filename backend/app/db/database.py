"""数据库引擎、会话工厂、Base 定义。"""
import logging
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger("app.db")

from app.core.config import settings

# sqlite:///./data/app.db  →  sqlite+aiosqlite:///./data/app.db
_db_url = settings.database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)

engine = create_async_engine(_db_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖注入：提供一个 async DB 会话。"""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """应用启动时建表（表不存在则创建，已存在则跳过）。"""
    # 延迟导入，保证模型已注册到 Base.metadata
    import app.models.conversation  # noqa: F401
    import app.models.document  # noqa: F401
    import app.models.qa_log  # noqa: F401
    import app.models.user  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # 增量迁移：为旧表追加新列（列已存在时忽略）
        migrations = [
            "ALTER TABLE document_chunks ADD COLUMN embedding BLOB",
            "ALTER TABLE qa_logs ADD COLUMN user_id INTEGER",
            "ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'student'",
        ]
        for sql in migrations:
            try:
                await conn.execute(text(sql))
                logger.info("Migration applied: %s", sql)
            except Exception:
                pass  # 列已存在，跳过


async def seed_db() -> None:
    """从 .env 读取密码，upsert 所有种子账号（密码变化时同步更新）。"""
    import asyncio

    from sqlalchemy import select

    from app.core.config import settings
    from app.models.user import User
    from app.services.auth_service import hash_password

    # 账号定义：(email, 密码, role, 角色说明)
    _ACCOUNTS = [
        ("admin@pyqa.com",    settings.seed_admin_password, "admin",   "管理员"),
        ("test1@pyqa.com",    settings.seed_test_password,  "student", "测试账号1"),
        ("test2@pyqa.com",    settings.seed_test_password,  "student", "测试账号2"),
        ("test3@pyqa.com",    settings.seed_test_password,  "student", "测试账号3"),
        ("test4@pyqa.com",    settings.seed_test_password,  "student", "测试账号4"),
        ("test5@pyqa.com",    settings.seed_test_password,  "student", "测试账号5"),
        ("qa1@pyqa.com",      settings.seed_qa_password,    "teacher", "学院答疑1"),
        ("qa2@pyqa.com",      settings.seed_qa_password,    "teacher", "学院答疑2"),
        ("qa3@pyqa.com",      settings.seed_qa_password,    "teacher", "学院答疑3"),
        ("qa4@pyqa.com",      settings.seed_qa_password,    "teacher", "学院答疑4"),
        ("qa5@pyqa.com",      settings.seed_qa_password,    "teacher", "学院答疑5"),
    ]

    missing_passwords = [
        name for name in ("seed_admin_password", "seed_test_password", "seed_qa_password")
        if not getattr(settings, name)
    ]
    if missing_passwords:
        logger.warning(
            "种子账号跳过：.env 中未配置 %s，请补充后重启服务",
            ", ".join(missing_passwords).upper(),
        )
        return

    async with AsyncSessionLocal() as db:
        for email, password, role, label in _ACCOUNTS:
            pw_hash = await asyncio.to_thread(hash_password, password)
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if user is None:
                db.add(User(email=email, password_hash=pw_hash, role=role))
                logger.info("种子账号创建: %s (%s)", email, label)
            else:
                user.password_hash = pw_hash
                user.role = role
                logger.info("种子账号同步: %s (%s)", email, label)
        await db.commit()
        logger.info(
            "种子账号就绪: 管理员×1 测试×5 学院答疑×5  (共 %d 个)", len(_ACCOUNTS)
        )
