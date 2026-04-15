"""CRUD for assets."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate


def list_assets(db: Session) -> list[Asset]:
    return list(db.scalars(select(Asset).order_by(Asset.updated_at.desc())).all())


def get_asset(db: Session, asset_id: int) -> Asset | None:
    return db.get(Asset, asset_id)


def create_asset(db: Session, payload: AssetCreate) -> Asset:
    obj = Asset(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_asset(db: Session, obj: Asset, payload: AssetUpdate) -> Asset:
    for key, val in payload.model_dump().items():
        setattr(obj, key, val)
    db.commit()
    db.refresh(obj)
    return obj


def delete_asset(db: Session, obj: Asset) -> None:
    db.delete(obj)
    db.commit()
