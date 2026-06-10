"""统一异常处理基础结构。

- AppException: 业务异常基类，带 code / message / status_code。
- register_exception_handlers: 注册到 FastAPI，统一响应体格式：
    {"code": <str>, "message": <str>, "detail": <any|null>}
后续业务层只需 `raise AppException(...)` 或其子类即可。
"""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app")


class AppException(Exception):
    """业务异常基类。"""

    code: str = "app_error"
    status_code: int = 400

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        status_code: int | None = None,
        detail=None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        self.detail = detail


class NotFoundError(AppException):
    code = "not_found"
    status_code = 404


class ExternalServiceError(AppException):
    """外部模型 / 第三方服务调用失败（预留给 services 层）。"""

    code = "external_service_error"
    status_code = 502


def _error_body(code: str, message: str, detail=None) -> dict:
    return {"code": code, "message": message, "detail": detail}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def _handle_app_exception(request: Request, exc: AppException):
        logger.warning("AppException: %s - %s", exc.code, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, exc.detail),
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation_error(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=_error_body("validation_error", "请求参数校验失败", exc.errors()),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _handle_http_exception(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body("http_error", str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content=_error_body("internal_error", "服务器内部错误"),
        )
