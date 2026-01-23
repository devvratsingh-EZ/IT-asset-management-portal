"""Asset routes."""
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models.requests import AssetCreateRequest, AssetUpdateRequest, BulkDeleteRequest
from app.db.session import get_db
from app.db.repositories.asset_repository import AssetRepository
from app.dependencies import get_current_user

logger = logging.getLogger('routes.assets')
router = APIRouter()


@router.get("")
async def get_assets(
    _current_user: dict = Depends(get_current_user),  # pylance: disable=unused-argument
    db: Session = Depends(get_db)
):
    """Get all assets."""
    repo = AssetRepository(db)
    assets = repo.get_all()
    return {"success": True, "data": assets}


@router.get("/asset-types")
async def get_asset_types(
    _current_user: dict = Depends(get_current_user),  # pylance: disable=unused-argument
    db: Session = Depends(get_db)
):
    """Get all asset types."""
    repo = AssetRepository(db)
    types = repo.get_types()
    if types:
        return {"success": True, "data": [t['type_name'] for t in types]}
    return {
        "success": True,
        "data": ["Laptop", "Desktop", "Monitor", "Keyboard", "Mouse", "Printer",
                 "Scanner", "Server", "Router", "Switch", "UPS", "Projector",
                 "Tablet", "Mobile Phone", "Headset", "Webcam", "External Hard Drive", "Other"],
        "source": "fallback"
    }


@router.get("/specifications")
async def get_all_specifications(
    _current_user: dict = Depends(get_current_user),  # pylance: disable=unused-argument
    db: Session = Depends(get_db)
):
    """Get all specifications grouped by asset type."""
    repo = AssetRepository(db)
    specs = repo.get_all_specifications()
    if specs:
        return {"success": True, "data": specs}
    return {"success": False, "data": {}, "message": "Database unavailable"}


@router.get("/specifications/{type_name}")
async def get_specifications_for_type(
    type_name: str,
    _current_user: dict = Depends(get_current_user),  # pylance: disable=unused-argument
    db: Session = Depends(get_db)
):
    """Get specifications for a specific asset type."""
    repo = AssetRepository(db)
    specs = repo.get_specifications_for_type(type_name)
    if specs:
        return {
            "success": True,
            "data": {"fields": [{"key": s['field_key'], "label": s['field_label'], "placeholder": s['placeholder']} for s in specs]}
        }
    return {"success": False, "data": {"fields": []}, "message": f"No specifications found for {type_name}"}


@router.get("/assignment-history")
async def get_all_history(
    _current_user: dict = Depends(get_current_user),  # pylance: disable=unused-argument
    db: Session = Depends(get_db)
):
    """Get all assignment history grouped by asset."""
    repo = AssetRepository(db)
    history = repo.get_all_assignment_history()
    return {"success": True, "data": history}


@router.get("/assignment-history/{asset_id}")
async def get_history(
    asset_id: str,
    _current_user: dict = Depends(get_current_user),  # pylance: disable=unused-argument
    db: Session = Depends(get_db)
):
    """Get assignment history for a specific asset."""
    repo = AssetRepository(db)
    history = repo.get_assignment_history(asset_id)
    return {"success": True, "data": history}


@router.get("/{asset_id}")
async def get_asset(
    asset_id: str,
    _current_user: dict = Depends(get_current_user),  # pylance: disable=unused-argument
    db: Session = Depends(get_db)
):
    """Get a single asset by ID."""
    repo = AssetRepository(db)
    asset = repo.get_by_id(asset_id)
    if asset:
        return {"success": True, "data": asset}
    raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")


@router.post("")
async def create_asset(
    request: AssetCreateRequest,
    _current_user: dict = Depends(get_current_user),  # pylance: disable=unused-argument
    db: Session = Depends(get_db)
):
    """Create a new asset."""
    logger.info(f"CREATE ASSET: Serial='{request.serialNumber}', Type='{request.assetType}'")
    
    try:
        repo = AssetRepository(db)
        result = repo.create(
            asset_data=request.model_dump(),
            specifications=request.specifications
        )
        logger.info(result)
        return result
    except Exception as e:
        logger.error(f"CREATE ASSET: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{asset_id}")
async def update_asset(
    asset_id: str,
    request: AssetUpdateRequest,
    _current_user: dict = Depends(get_current_user),  # pylance: disable=unused-argument
    db: Session = Depends(get_db)
):
    """Update asset assignment and repair status."""
    logger.info(f"UPDATE ASSET: '{asset_id}'")
    
    try:
        repo = AssetRepository(db)
        result = repo.update_assignment(
            asset_id=asset_id,
            new_employee_id=request.assignedTo,
            repair_status=request.repairStatus
        )
        return result
    except Exception as e:
        logger.error(f"UPDATE ASSET: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/bulk-delete")
async def bulk_delete_assets(
    request: BulkDeleteRequest,
    _current_user: dict = Depends(get_current_user),  # pylance: disable=unused-argument
    db: Session = Depends(get_db)
):
    """Delete multiple assets by IDs."""
    logger.info(f"BULK DELETE: {len(request.assetIds)} assets")
    try:
        repo = AssetRepository(db)
        result = repo.delete_bulk(request.assetIds)
        return result
    except Exception as e:
        logger.error(f"BULK DELETE: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))