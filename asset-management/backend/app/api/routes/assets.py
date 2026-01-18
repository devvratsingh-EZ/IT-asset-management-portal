"""Asset routes."""
import logging
from fastapi import APIRouter, HTTPException

from app.models.requests import AssetCreateRequest, AssetUpdateRequest, BulkDeleteRequest
from app.services.asset_service import AssetService
from app.db.repositories.asset_repository import AssetRepository

logger = logging.getLogger('routes.assets')
router = APIRouter()
asset_service = AssetService()
asset_repo = AssetRepository()


@router.get("")
async def get_assets():
    """Get all assets."""
    assets = asset_repo.get_all()
    return {"success": True, "data": assets}


@router.get("/asset-types")
async def get_asset_types():
    """Get all asset types."""
    types = asset_repo.get_types()
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
async def get_all_specifications():
    """Get all specifications grouped by asset type."""
    specs = asset_repo.get_all_specifications()
    if specs:
        return {"success": True, "data": specs}
    return {"success": False, "data": {}, "message": "Database unavailable"}


@router.get("/specifications/{type_name}")
async def get_specifications_for_type(type_name: str):
    """Get specifications for a specific asset type."""
    specs = asset_repo.get_specifications_for_type(type_name)
    if specs:
        return {
            "success": True,
            "data": {"fields": [{"key": s['field_key'], "label": s['field_label'], "placeholder": s['placeholder']} for s in specs]}
        }
    return {"success": False, "data": {"fields": []}, "message": f"No specifications found for {type_name}"}


@router.get("/assignment-history")
async def get_all_history():
    """Get all assignment history grouped by asset."""
    history = asset_repo.get_all_assignment_history()
    return {"success": True, "data": history}


@router.get("/assignment-history/{asset_id}")
async def get_history(asset_id: str):
    """Get assignment history for a specific asset."""
    history = asset_repo.get_assignment_history(asset_id)
    return {"success": True, "data": history}


@router.get("/{asset_id}")
async def get_asset(asset_id: str):
    """Get a single asset by ID."""
    asset = asset_repo.get_by_id(asset_id)
    if asset:
        return {"success": True, "data": asset}
    raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")


@router.post("")
async def create_asset(request: AssetCreateRequest):
    """Create a new asset."""
    logger.info(f"CREATE ASSET: Serial='{request.serialNumber}', Type='{request.assetType}'")
    
    try:
        result = asset_service.create_asset(
            asset_data=request.model_dump(),
            specifications=request.specifications
        )
        return result
    except Exception as e:
        logger.error(f"CREATE ASSET: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{asset_id}")
async def update_asset(asset_id: str, request: AssetUpdateRequest):
    """Update asset assignment and repair status."""
    logger.info(f"UPDATE ASSET: '{asset_id}'")
    
    try:
        result = asset_service.update_assignment(
            asset_id=asset_id,
            new_employee_id=request.assignedTo,
            repair_status=request.repairStatus
        )
        return result
    except Exception as e:
        logger.error(f"UPDATE ASSET: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/bulk-delete")
async def bulk_delete_assets(request: BulkDeleteRequest):
    """Delete multiple assets by IDs."""
    logger.info(f"BULK DELETE: {len(request.assetIds)} assets")
    try:
        result = asset_repo.delete_bulk(request.assetIds)
        return result
    except Exception as e:
        logger.error(f"BULK DELETE: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))