from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.common import ORMBase


class AssetBase(BaseModel):
    asset_type: str
    title: str
    scene: Optional[str] = None
    stage: Optional[str] = None
    direction: Optional[str] = None
    content: Optional[str] = None
    link: Optional[str] = None
    description: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(AssetBase):
    pass


class AssetOut(ORMBase, AssetBase):
    id: int
    created_at: datetime
    updated_at: datetime
