"""Main API router combining all route modules."""
from fastapi import APIRouter

from app.api.routes import auth, assets, employees, summary
from app.db.repositories.asset_repository import AssetRepository

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(employees.router, prefix="/employees", tags=["Employees"])
api_router.include_router(summary.router, tags=["Summary"])

# Legacy routes for backward compatibility
asset_repo = AssetRepository()

@api_router.get("/asset-types")
async def get_asset_types_legacy():
    """Get all asset types (legacy route)."""
    types = asset_repo.get_types()
    if types:
        return {"success": True, "data": [t['type_name'] for t in types]}
    return {"success": True, "data": ["Laptop", "Desktop", "Monitor", "Keyboard", "Mouse", "Printer",
             "Scanner", "Server", "Router", "Switch", "UPS", "Projector",
             "Tablet", "Mobile Phone", "Headset", "Webcam", "External Hard Drive", "Other"], "source": "fallback"}

@api_router.get("/asset-specifications")
async def get_all_specs_legacy():
    """Get all specifications (legacy route)."""
    specs = asset_repo.get_all_specifications()
    return {"success": True, "data": specs} if specs else {"success": False, "data": {}}

@api_router.get("/assignment-history")
async def get_all_history_legacy():
    """Get all assignment history (legacy route)."""
    history = asset_repo.get_all_assignment_history()
    return {"success": True, "data": history}

@api_router.get("/assignment-history/{asset_id}")
async def get_history_legacy(asset_id: str):
    """Get assignment history for specific asset (legacy route)."""
    history = asset_repo.get_assignment_history(asset_id)
    return {"success": True, "data": history}