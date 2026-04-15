"""API dependencies."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db


DBSessionDep = Depends(get_db)
