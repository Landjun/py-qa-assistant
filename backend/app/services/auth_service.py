"""认证服务：密码哈希、JWT 签发与验证、当前用户依赖。"""
import logging

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_db

logger = logging.getLogger("app.services.auth")

_bearer = HTTPBearer(auto_error=False)


# ─── 密码 ────────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


# ─── JWT ─────────────────────────────────────────────────────────────────────

from datetime import datetime, timedelta, timezone


def create_access_token(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


# ─── FastAPI 依赖 ─────────────────────────────────────────────────────────────

def require_roles(*roles: str):
    """返回一个 FastAPI 依赖，校验当前用户 role 是否在允许列表内，否则抛 403。

    用法：Depends(require_roles("admin", "teacher"))
    """
    from typing import Callable

    async def _check(current_user=Depends(get_current_user)) -> "User":  # type: ignore[name-defined]
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"无权限访问，需要角色：{' 或 '.join(roles)}",
            )
        return current_user

    return _check


async def get_optional_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> int | None:
    """从 Bearer token 中提取 user_id；token 缺失 / 无效时返回 None（不抛异常）。"""
    if credentials is None:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        return int(payload["sub"])
    except Exception:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
):
    """验证 Bearer token，返回 User 实例；未登录 / token 无效时抛出 401。"""
    from app.models.user import User  # 延迟导入避免循环

    if credentials is None:
        raise HTTPException(status_code=401, detail="未登录，请先登录")
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    except Exception:
        raise HTTPException(status_code=401, detail="无效的 token，请重新登录")

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在，请重新登录")
    return user
