"""Asset service."""
import logging
from datetime import datetime

from app.db.repositories.asset_repository import AssetRepository

logger = logging.getLogger('services.asset')


class AssetService:
    """Handles asset business logic."""
    
    def __init__(self):
        self.asset_repo = AssetRepository()
    
    def create_asset(self, asset_data: dict, specifications: dict) -> dict:
        """Create a new asset with specifications."""
        logger.info(f"Creating asset: serial='{asset_data.get('serialNumber')}'")
        return self.asset_repo.create(asset_data, specifications)
    
    def update_assignment(self, asset_id: str, new_employee_id: str, repair_status: bool) -> dict:
        """Update asset assignment and repair status."""
        logger.info(f"Updating assignment for '{asset_id}'")
        return self.asset_repo.update_assignment(asset_id, new_employee_id, repair_status)