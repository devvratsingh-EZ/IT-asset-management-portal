"""Asset repository using SQLAlchemy ORM."""
import logging
from datetime import datetime
from typing import Optional, Dict, List

from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session, joinedload

from app.db.repositories.base import BaseRepository
from app.db.models import (
    AssetData, AssetType, AssetSpecification, SpecData,
    AssignmentHistory, PeopleData, AssetIdCounter
)

logger = logging.getLogger('db.asset_repository')


class AssetRepository(BaseRepository[AssetData]):
    """Repository for asset operations using SQLAlchemy ORM."""
    
    def __init__(self, session: Session):
        super().__init__(AssetData, session)
    
    def get_types(self) -> List[dict]:
        """Get all asset types."""
        logger.info("FETCH: Getting all asset types")
        stmt = select(AssetType).order_by(AssetType.type_name)
        types = self.session.scalars(stmt).all()
        return [{"id": t.id, "type_name": t.type_name} for t in types]
    
    def get_all_specifications(self) -> Dict[str, dict]:
        """Get all specifications grouped by asset type."""
        logger.info("FETCH: Getting all specifications")
        
        stmt = (
            select(AssetSpecification)
            .join(AssetType)
            .options(joinedload(AssetSpecification.asset_type))
            .order_by(AssetType.type_name, AssetSpecification.id)
        )
        specs = self.session.scalars(stmt).all()
        
        result = {}
        for spec in specs:
            type_name = spec.asset_type.type_name
            if type_name not in result:
                result[type_name] = {'fields': []}
            result[type_name]['fields'].append({
                'key': spec.field_key,
                'label': spec.field_label,
                'placeholder': spec.placeholder
            })
        
        return result
    
    def get_specifications_for_type(self, type_name: str) -> List[dict]:
        """Get specification fields for a given asset type."""
        logger.info(f"FETCH: Getting specifications for type '{type_name}'")
        
        stmt = (
            select(AssetSpecification)
            .join(AssetType)
            .where(AssetType.type_name == type_name)
            .order_by(AssetSpecification.id)
        )
        specs = self.session.scalars(stmt).all()
        
        return [
            {
                'field_key': s.field_key,
                'field_label': s.field_label,
                'placeholder': s.placeholder
            }
            for s in specs
        ]
    
    def get_all(self) -> Dict[str, dict]:
        """Get all assets with their specifications."""
        logger.info("FETCH: Getting all assets")
        
        stmt = (
            select(AssetData)
            .options(joinedload(AssetData.spec_data))
            .order_by(AssetData.AssetId)
        )
        assets = self.session.scalars(stmt).unique().all()
        
        result = {}
        for asset in assets:
            specifications = {
                spec.SpecFieldName: spec.SpecFieldValue 
                for spec in asset.spec_data
            }
            specifications['brand'] = asset.Brand
            specifications['model'] = asset.Model
            
            result[asset.AssetId] = {
                'assetId': asset.AssetId,
                'serialNumber': asset.SerialNo,
                'assetType': asset.AssetType,
                'specifications': specifications,
                'assignedTo': asset.AssignedTo,
                'repairStatus': bool(asset.RepairStatus),
                'warrantyExpiry': asset.WarrantyExpiry
            }
        
        logger.info(f"FETCH: Retrieved {len(result)} assets")
        return result
    
    def get_by_id(self, asset_id: str) -> Optional[dict]:
        """Get a single asset by ID with specifications."""
        logger.info(f"FETCH: Getting asset '{asset_id}'")
        
        stmt = (
            select(AssetData)
            .options(joinedload(AssetData.spec_data))
            .where(AssetData.AssetId == asset_id)
        )
        asset = self.session.scalars(stmt).first()
        
        if not asset:
            return None
        
        specifications = {
            spec.SpecFieldName: spec.SpecFieldValue 
            for spec in asset.spec_data
        }
        specifications['brand'] = asset.Brand
        specifications['model'] = asset.Model
        
        return {
            'assetId': asset.AssetId,
            'serialNumber': asset.SerialNo,
            'assetType': asset.AssetType,
            'specifications': specifications,
            'assignedTo': asset.AssignedTo,
            'repairStatus': bool(asset.RepairStatus),
            'warrantyExpiry': asset.WarrantyExpiry
        }
    
    def get_assignment_history(self, asset_id: str) -> List[dict]:
        """Get assignment history for an asset."""
        logger.info(f"FETCH: Getting assignment history for '{asset_id}'")
        
        stmt = (
            select(AssignmentHistory)
            .where(AssignmentHistory.AssetId == asset_id)
            .order_by(AssignmentHistory.AssignedOn.desc())
        )
        history = self.session.scalars(stmt).all()
        
        return [
            {
                'employeeId': h.EmployeeId,
                'employeeName': h.EmployeeName,
                'assignedOn': h.AssignedOn.strftime('%Y-%m-%d') if h.AssignedOn else None,
                'returnedOn': 'Active' if h.IsActive else (
                    h.ReturnedOn.strftime('%Y-%m-%d') if h.ReturnedOn else None
                )
            }
            for h in history
        ]
    
    def get_all_assignment_history(self) -> Dict[str, List[dict]]:
        """Get all assignment history grouped by asset ID."""
        logger.info("FETCH: Getting all assignment history")
        
        stmt = (
            select(AssignmentHistory)
            .order_by(AssignmentHistory.AssetId, AssignmentHistory.AssignedOn.desc())
        )
        history = self.session.scalars(stmt).all()
        
        result = {}
        for h in history:
            if h.AssetId not in result:
                result[h.AssetId] = []
            result[h.AssetId].append({
                'employeeId': h.EmployeeId,
                'employeeName': h.EmployeeName,
                'assignedOn': h.AssignedOn.strftime('%Y-%m-%d') if h.AssignedOn else None,
                'returnedOn': 'Active' if h.IsActive else (
                    h.ReturnedOn.strftime('%Y-%m-%d') if h.ReturnedOn else None
                )
            })
        
        return result
    
    def create(self, asset_data: dict, specifications: dict) -> dict:
        """Create a new asset with specifications."""
        logger.info(f"CREATE: Starting asset creation for serial '{asset_data.get('serialNumber')}'")
        
        try:
            # Generate Asset ID
            counter = self.session.get(AssetIdCounter, 1)
            if not counter:
                counter = AssetIdCounter(id=1, current_value=1000)
                self.session.add(counter)
            counter.current_value += 1
            asset_id = f"AST_{counter.current_value}"
            
            logger.info(f"CREATE: Generated Asset ID '{asset_id}'")
            
            # Parse dates
            purchase_date = asset_data.get('purchaseDate')
            warranty_expiry = asset_data.get('warrantyExpiry')
            
            if isinstance(purchase_date, str) and purchase_date:
                purchase_date = datetime.fromisoformat(
                    purchase_date.replace('Z', '+00:00')
                ).date()
            if isinstance(warranty_expiry, str) and warranty_expiry:
                warranty_expiry = datetime.fromisoformat(
                    warranty_expiry.replace('Z', '+00:00')
                ).date()
            
            assigned_to = asset_data.get('assignedTo') or None
            
            # Create asset
            asset = AssetData(
                AssetId=asset_id,
                SerialNo=asset_data.get('serialNumber'),
                AssetType=asset_data.get('assetType'),
                Brand=asset_data.get('brand'),
                Model=asset_data.get('model'),
                DateOfPurchase=purchase_date,
                ProductCost=asset_data.get('purchaseCost', 0),
                GST=asset_data.get('gstPaid', 0),
                WarrantyExpiry=warranty_expiry,
                AssignedTo=assigned_to,
                RepairStatus=asset_data.get('repairStatus', False),
                AssetImagePath="s3://dummy-bucket/assets/images/sample.jpg",
                PurchaseReceiptsPath="s3://dummy-bucket/assets/receipts/sample.pdf",
                WarrantyCardPath="s3://dummy-bucket/assets/warranty/sample.pdf"
            )
            self.session.add(asset)
            
            # Get field mapping
            stmt = (
                select(AssetSpecification)
                .join(AssetType)
                .where(AssetType.type_name == asset_data.get('assetType'))
            )
            spec_fields = self.session.scalars(stmt).all()
            field_mapping = {s.field_key: s.field_label for s in spec_fields}
            
            # Insert specifications
            for field_key, field_value in specifications.items():
                if field_value:
                    spec = SpecData(
                        AssetId=asset_id,
                        AssetTypeName=asset_data.get('assetType'),
                        SpecFieldName=field_mapping.get(field_key, field_key),
                        SpecFieldValue=field_value
                    )
                    self.session.add(spec)
            
            # Create assignment history if assigned
            if assigned_to:
                employee = self.session.get(PeopleData, assigned_to)
                emp_name = employee.Name if employee else assigned_to
                
                history = AssignmentHistory(
                    AssetId=asset_id,
                    EmployeeId=assigned_to,
                    EmployeeName=emp_name,
                    AssignedOn=datetime.now().date(),
                    IsActive=True
                )
                self.session.add(history)
            
            self.session.commit()
            logger.info(f"CREATE: Successfully created asset '{asset_id}'")
            
            return {
                'success': True,
                'assetId': asset_id,
                'message': f'Asset {asset_id} created successfully'
            }
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"CREATE: Error - {e}")
            raise
    
    def update_assignment(
        self, asset_id: str, new_employee_id: str, repair_status: bool
    ) -> dict:
        """Update asset assignment and repair status."""
        logger.info(f"UPDATE: Updating assignment for '{asset_id}'")
        
        try:
            asset = self.session.get(AssetData, asset_id)
            if not asset:
                raise Exception(f"Asset {asset_id} not found")
            
            old_employee_id = asset.AssignedTo
            
            if old_employee_id != new_employee_id:
                # Close old assignment
                if old_employee_id:
                    stmt = (
                        update(AssignmentHistory)
                        .where(AssignmentHistory.AssetId == asset_id)
                        .where(AssignmentHistory.EmployeeId == old_employee_id)
                        .where(AssignmentHistory.IsActive == True)
                        .values(ReturnedOn=datetime.now().date(), IsActive=False)
                    )
                    self.session.execute(stmt)
                
                # Create new assignment
                if new_employee_id:
                    employee = self.session.get(PeopleData, new_employee_id)
                    emp_name = employee.Name if employee else new_employee_id
                    
                    history = AssignmentHistory(
                        AssetId=asset_id,
                        EmployeeId=new_employee_id,
                        EmployeeName=emp_name,
                        AssignedOn=datetime.now().date(),
                        IsActive=True
                    )
                    self.session.add(history)
            
            # Update asset
            asset.AssignedTo = new_employee_id or None
            asset.RepairStatus = repair_status
            
            self.session.commit()
            logger.info(f"UPDATE: Successfully updated '{asset_id}'")
            return {'success': True, 'message': f'Asset {asset_id} updated successfully'}
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"UPDATE: Error - {e}")
            raise
    
    def delete_bulk(self, asset_ids: List[str]) -> dict:
        """Delete multiple assets by their IDs."""
        logger.info(f"DELETE: Deleting {len(asset_ids)} assets")
        
        try:
            # SQLAlchemy cascade will handle related records
            stmt = delete(AssetData).where(AssetData.AssetId.in_(asset_ids))
            result = self.session.execute(stmt)
            deleted_count = result.rowcount
            
            self.session.commit()
            logger.info(f"DELETE: Successfully deleted {deleted_count} assets")
            
            return {
                'success': True,
                'deletedCount': deleted_count,
                'message': f'Successfully deleted {deleted_count} asset(s)'
            }
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"DELETE: Error - {e}")
            raise