"""FastAPI entrypoint for teaching operations after-course CRM."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.errors import AppException
from app.core.response import error_response, success_response
from app.services.seed import seed_data

app = FastAPI(title=settings.app_name, version=settings.app_version)

# CORS for local frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Create tables automatically and initialize seed data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content=error_response(exc.message, exc.code))


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=error_response(str(exc.detail), "HTTP_ERROR"))


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    return JSONResponse(status_code=500, content=error_response(f"internal error: {exc}", "INTERNAL_ERROR"))


@app.get("/")
def health_check():
    return success_response({"service": settings.app_name, "version": settings.app_version})


app.include_router(api_router)
