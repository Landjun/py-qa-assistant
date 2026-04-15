from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.crud import asset as asset_crud
from app.schemas.asset import AssetCreate, AssetOut, AssetUpdate

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("")
def list_assets(db: Session = Depends(get_db)):
    rows = asset_crud.list_assets(db)
    return success_response([AssetOut.model_validate(x).model_dump() for x in rows])


@router.post("")
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    row = asset_crud.create_asset(db, payload)
    return success_response(AssetOut.model_validate(row).model_dump(), "asset created")


@router.put("/{asset_id}")
def update_asset(asset_id: int, payload: AssetUpdate, db: Session = Depends(get_db)):
    row = asset_crud.get_asset(db, asset_id)
    if not row:
        raise HTTPException(status_code=404, detail="asset not found")
    updated = asset_crud.update_asset(db, row, payload)
    return success_response(AssetOut.model_validate(updated).model_dump(), "asset updated")


@router.delete("/{asset_id}")
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    row = asset_crud.get_asset(db, asset_id)
    if not row:
        raise HTTPException(status_code=404, detail="asset not found")
    asset_crud.delete_asset(db, row)
    return success_response(None, "asset deleted")
