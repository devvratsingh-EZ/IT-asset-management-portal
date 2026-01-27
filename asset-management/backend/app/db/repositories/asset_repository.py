"""Asset repository using SQLAlchemy ORM."""
import logging
from datetime import datetime
from typing import Optional, Dict, List

from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session, joinedload

from app.db.repositories.base import BaseRepository
from app.db.models import (
    AssetData, AssetType, AssetSpecification, SpecData,
    AssignmentHistory, PeopleData, AssetIdCounter, BrandData, RepairStatusTracker
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
    
    # Add these new methods to the AssetRepository class

    def get_brands(self) -> List[dict]:
        """Get all unique asset brands."""
        logger.info("FETCH: Getting all unique asset brands")
        stmt = select(BrandData.brand_name).distinct().order_by(BrandData.brand_name)
        brands = self.session.scalars(stmt).all()
        return [{"brand_name": b} for b in brands]

    def get_models(self) -> List[dict]:
        """Get all asset models with their brands."""
        logger.info("FETCH: Getting all asset models")
        stmt = select(BrandData).order_by(BrandData.brand_name, BrandData.model_name)
        models = self.session.scalars(stmt).all()
        return [{"id": m.id, "brand_name": m.brand_name, "model_name": m.model_name} for m in models]

    def get_models_by_brand(self, brand_name: str) -> List[dict]:
        """Get models filtered by brand name."""
        logger.info(f"FETCH: Getting models for brand '{brand_name}'")
        stmt = select(BrandData).where(BrandData.brand_name == brand_name).order_by(BrandData.model_name)
        models = self.session.scalars(stmt).all()
        return [{"id": m.id, "model_name": m.model_name} for m in models]

    def get_brands_by_model(self, model_name: str) -> List[dict]:
        """Get brands filtered by model name."""
        logger.info(f"FETCH: Getting brands for model '{model_name}'")
        stmt = select(BrandData).where(BrandData.model_name == model_name).order_by(BrandData.brand_name)
        brands = self.session.scalars(stmt).all()
        return [{"id": b.id, "brand_name": b.brand_name} for b in brands]

    def create_brand_model(self, brand_name: str, model_name: str) -> dict:
        """Create a new brand-model entry."""
        logger.info(f"CREATE: Adding brand '{brand_name}' with model '{model_name}'")
        try:
            # Check if combination already exists
            stmt = select(BrandData).where(
                BrandData.brand_name == brand_name,
                BrandData.model_name == model_name
            )
            existing = self.session.scalars(stmt).first()
            if existing:
                logger.info(f"CREATE: Brand-model combination already exists (id={existing.id})")
                return {"success": True, "id": existing.id, "message": "Brand-model combination already exists"}
            
            new_entry = BrandData(brand_name=brand_name, model_name=model_name)
            self.session.add(new_entry)
            self.session.commit()
            logger.info(f"CREATE: Successfully added brand-model (id={new_entry.id})")
            return {"success": True, "id": new_entry.id, "message": "Brand-model added successfully"}
        except Exception as e:
            self.session.rollback()
            logger.error(f"CREATE: Error adding brand-model - {e}")
            raise
    
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
                'isTempAsset': bool(asset.IsTempAsset),
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
            'isTempAsset': bool(asset.IsTempAsset),
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

    def get_available_temp_assets(self, asset_type: str, exclude_asset_id: str) -> List[dict]:
        """Get unassigned assets of same type for temp assignment."""
        logger.info(f"FETCH: Getting available temp assets for type '{asset_type}'")
        stmt = (
            select(AssetData)
            .where(AssetData.AssetType == asset_type)
            .where(AssetData.AssignedTo == None)
            .where(AssetData.AssetId != exclude_asset_id)
            .where(AssetData.RepairStatus == False)
            .where(AssetData.IsTempAsset == False)
            .order_by(AssetData.AssetId)
        )
        assets = self.session.scalars(stmt).all()
        return [{"assetId": a.AssetId, "serialNumber": a.SerialNo} for a in assets]

def get_active_repair(self, asset_id: str) -> Optional[dict]:
    """Get active repair record for an asset."""
    logger.info(f"FETCH: Getting active repair for '{asset_id}'")
    stmt = (
        select(RepairStatusTracker)
        .where(RepairStatusTracker.AssetId == asset_id)
        .where(RepairStatusTracker.RepairEndTimestamp == None)
    )
    repair = self.session.scalars(stmt).first()
    if not repair:
        return None
    return {
        'id': repair.id,
        'assetId': repair.AssetId,
        'tempAssetId': repair.TempAssetId,
        'repairDetails': repair.RepairDetails,
        'repairStartTimestamp': repair.RepairStartTimestamp.isoformat() if repair.RepairStartTimestamp else None
    }

def start_repair(self, asset_id: str, repair_details: str, temp_asset_id: Optional[str] = None) -> dict:
    """Start repair for an asset."""
    logger.info(f"REPAIR START: Asset '{asset_id}', TempAsset='{temp_asset_id}'")
    try:
        asset = self.session.get(AssetData, asset_id)
        if not asset:
            raise Exception(f"Asset {asset_id} not found")
        
        current_employee_id = asset.AssignedTo
        
        # Set asset under repair
        asset.RepairStatus = True
        
        # Handle temp asset assignment if employee is assigned and temp asset provided
        if current_employee_id and temp_asset_id:
            temp_asset = self.session.get(AssetData, temp_asset_id)
            if not temp_asset:
                raise Exception(f"Temp asset {temp_asset_id} not found")
            
            # Mark temp asset
            temp_asset.IsTempAsset = True
            temp_asset.AssignedTo = current_employee_id
            
            # Create assignment history for temp asset
            employee = self.session.get(PeopleData, current_employee_id)
            emp_name = employee.Name if employee else current_employee_id
            
            history = AssignmentHistory(
                AssetId=temp_asset_id,
                EmployeeId=current_employee_id,
                EmployeeName=emp_name,
                AssignedOn=datetime.now().date(),
                IsActive=True
            )
            self.session.add(history)
        
        # Create repair tracker record
        repair_record = RepairStatusTracker(
            AssetId=asset_id,
            TempAssetId=temp_asset_id if temp_asset_id else asset_id,  # Use same ID if no temp
            RepairDetails=repair_details
        )
        self.session.add(repair_record)
        
        self.session.commit()
        logger.info(f"REPAIR START: Successfully started repair for '{asset_id}'")
        return {'success': True, 'message': f'Repair started for {asset_id}'}
        
    except Exception as e:
        self.session.rollback()
        logger.error(f"REPAIR START: Error - {e}")
        raise

def end_repair(self, asset_id: str) -> dict:
    """End repair for an asset."""
    logger.info(f"REPAIR END: Asset '{asset_id}'")
    try:
        asset = self.session.get(AssetData, asset_id)
        if not asset:
            raise Exception(f"Asset {asset_id} not found")
        
        # Get active repair record
        stmt = (
            select(RepairStatusTracker)
            .where(RepairStatusTracker.AssetId == asset_id)
            .where(RepairStatusTracker.RepairEndTimestamp == None)
        )
        repair = self.session.scalars(stmt).first()
        
        if not repair:
            raise Exception(f"No active repair found for {asset_id}")
        
        # Handle temp asset if exists and is different from main asset
        if repair.TempAssetId and repair.TempAssetId != asset_id:
            temp_asset = self.session.get(AssetData, repair.TempAssetId)
            if temp_asset and temp_asset.IsTempAsset:
                # Close temp asset assignment
                if temp_asset.AssignedTo:
                    stmt = (
                        update(AssignmentHistory)
                        .where(AssignmentHistory.AssetId == repair.TempAssetId)
                        .where(AssignmentHistory.IsActive == True)
                        .values(ReturnedOn=datetime.now().date(), IsActive=False)
                    )
                    self.session.execute(stmt)
                
                # Reset temp asset
                temp_asset.IsTempAsset = False
                temp_asset.AssignedTo = None
        
        # End repair
        repair.RepairEndTimestamp = datetime.now()
        asset.RepairStatus = False
        
        self.session.commit()
        logger.info(f"REPAIR END: Successfully ended repair for '{asset_id}'")
        return {'success': True, 'message': f'Repair ended for {asset_id}'}
        
    except Exception as e:
        self.session.rollback()
        logger.error(f"REPAIR END: Error - {e}")
        raise