"""Main API router registration."""
from fastapi import APIRouter

from app.api import ai, assets, chat_records, dashboard, follow_ups, profiles, students

api_router = APIRouter()
api_router.include_router(students.router)
api_router.include_router(profiles.router)
api_router.include_router(chat_records.router)
api_router.include_router(ai.router)
api_router.include_router(follow_ups.router)
api_router.include_router(assets.router)
api_router.include_router(dashboard.router)
