"""Asset repository."""
import logging
from datetime import datetime
from mysql.connector import Error

from app.db.repositories.base import BaseRepository
from app.db.connection import get_connection

logger = logging.getLogger('db.asset_repository')


class AssetRepository(BaseRepository):
    """Repository for asset operations."""
    
    def get_types(self) -> list:
        """Get all asset types."""
        logger.info("FETCH: Getting all asset types")
        return self._execute_query("SELECT id, type_name FROM AssetTypes ORDER BY type_name") or []
    
    def get_all_specifications(self) -> dict:
        """Get all specifications grouped by asset type."""
        logger.info("FETCH: Getting all specifications")
        
        rows = self._execute_query("""
            SELECT t.type_name, s.field_key, s.field_label, s.placeholder
            FROM AssetSpecifications s
            JOIN AssetTypes t ON s.asset_type_id = t.id
            ORDER BY t.type_name, s.id
        """)
        
        if not rows:
            return {}
        
        result = {}
        for row in rows:
            type_name = row['type_name']
            if type_name not in result:
                result[type_name] = {'fields': []}
            result[type_name]['fields'].append({
                'key': row['field_key'],
                'label': row['field_label'],
                'placeholder': row['placeholder']
            })
        
        return result
    
    def get_specifications_for_type(self, type_name: str) -> list:
        """Get specification fields for a given asset type."""
        logger.info(f"FETCH: Getting specifications for type '{type_name}'")
        
        return self._execute_query("""
            SELECT s.field_key, s.field_label, s.placeholder
            FROM AssetSpecifications s
            JOIN AssetTypes t ON s.asset_type_id = t.id
            WHERE t.type_name = %s
            ORDER BY s.id
        """, (type_name,)) or []
    
    def get_all(self) -> dict:
        """Get all assets."""
        logger.info("FETCH: Getting all assets")
        connection = get_connection()
        if not connection:
            return {}
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT AssetId, SerialNo, AssetType, Brand, Model,
                       DateOfPurchase, ProductCost, GST, WarrantyExpiry,
                       AssignedTo, RepairStatus
                FROM AssetData ORDER BY AssetId
            """)
            assets = cursor.fetchall()
            
            result = {}
            for asset in assets:
                asset_id = asset['AssetId']
                
                cursor.execute("""
                    SELECT SpecFieldName, SpecFieldValue
                    FROM SpecData WHERE AssetId = %s
                """, (asset_id,))
                specs = cursor.fetchall()
                
                specifications = {spec['SpecFieldName']: spec['SpecFieldValue'] for spec in specs}
                specifications['brand'] = asset['Brand']
                specifications['model'] = asset['Model']
                
                result[asset_id] = {
                    'assetId': asset_id,
                    'serialNumber': asset['SerialNo'],
                    'assetType': asset['AssetType'],
                    'specifications': specifications,
                    'assignedTo': asset['AssignedTo'],
                    'repairStatus': bool(asset['RepairStatus']),
                    'warrantyExpiry': asset['WarrantyExpiry']
                }
            
            logger.info(f"FETCH: Retrieved {len(result)} assets")
            return result
            
        except Error as e:
            logger.error(f"FETCH: Error getting assets: {e}")
            return {}
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_by_id(self, asset_id: str) -> dict:
        """Get a single asset by ID."""
        logger.info(f"FETCH: Getting asset '{asset_id}'")
        connection = get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT AssetId, SerialNo, AssetType, Brand, Model,
                       DateOfPurchase, ProductCost, GST, WarrantyExpiry,
                       AssignedTo, RepairStatus
                FROM AssetData WHERE AssetId = %s
            """, (asset_id,))
            asset = cursor.fetchone()
            
            if not asset:
                return None
            
            cursor.execute("""
                SELECT SpecFieldName, SpecFieldValue
                FROM SpecData WHERE AssetId = %s
            """, (asset_id,))
            specs = cursor.fetchall()
            
            specifications = {spec['SpecFieldName']: spec['SpecFieldValue'] for spec in specs}
            specifications['brand'] = asset['Brand']
            specifications['model'] = asset['Model']
            
            return {
                'assetId': asset['AssetId'],
                'serialNumber': asset['SerialNo'],
                'assetType': asset['AssetType'],
                'specifications': specifications,
                'assignedTo': asset['AssignedTo'],
                'repairStatus': bool(asset['RepairStatus']),
                'warrantyExpiry': asset['WarrantyExpiry']
            }
            
        except Error as e:
            logger.error(f"FETCH: Error getting asset '{asset_id}': {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_assignment_history(self, asset_id: str) -> list:
        """Get assignment history for an asset."""
        logger.info(f"FETCH: Getting assignment history for '{asset_id}'")
        
        rows = self._execute_query("""
            SELECT EmployeeId, EmployeeName, AssignedOn, ReturnedOn, IsActive
            FROM AssignmentHistory
            WHERE AssetId = %s
            ORDER BY AssignedOn DESC
        """, (asset_id,))
        
        if not rows:
            return []
        
        return [{
            'employeeId': row['EmployeeId'],
            'employeeName': row['EmployeeName'],
            'assignedOn': row['AssignedOn'].strftime('%Y-%m-%d') if row['AssignedOn'] else None,
            'returnedOn': 'Active' if row['IsActive'] else (row['ReturnedOn'].strftime('%Y-%m-%d') if row['ReturnedOn'] else None)
        } for row in rows]
    
    def get_all_assignment_history(self) -> dict:
        """Get all assignment history grouped by asset ID."""
        logger.info("FETCH: Getting all assignment history")
        
        rows = self._execute_query("""
            SELECT AssetId, EmployeeId, EmployeeName, AssignedOn, ReturnedOn, IsActive
            FROM AssignmentHistory
            ORDER BY AssetId, AssignedOn DESC
        """)
        
        if not rows:
            return {}
        
        result = {}
        for row in rows:
            asset_id = row['AssetId']
            if asset_id not in result:
                result[asset_id] = []
            
            result[asset_id].append({
                'employeeId': row['EmployeeId'],
                'employeeName': row['EmployeeName'],
                'assignedOn': row['AssignedOn'].strftime('%Y-%m-%d') if row['AssignedOn'] else None,
                'returnedOn': 'Active' if row['IsActive'] else (row['ReturnedOn'].strftime('%Y-%m-%d') if row['ReturnedOn'] else None)
            })
        
        return result
    
    def create(self, asset_data: dict, specifications: dict) -> dict:
        """Create a new asset with specifications."""
        logger.info(f"CREATE: Starting asset creation for serial '{asset_data.get('serialNumber')}'")
        connection = get_connection()
        if not connection:
            raise Exception("Database connection failed")
        
        try:
            cursor = connection.cursor(dictionary=True)
            connection.start_transaction()
            
            # Generate Asset ID
            cursor.execute("UPDATE AssetIdCounter SET current_value = current_value + 1 WHERE id = 1")
            cursor.execute("SELECT current_value FROM AssetIdCounter WHERE id = 1")
            asset_id = f"AST_{cursor.fetchone()['current_value']}"
            
            logger.info(f"CREATE: Generated Asset ID '{asset_id}'")
            
            # Parse dates
            purchase_date = asset_data.get('purchaseDate')
            warranty_expiry = asset_data.get('warrantyExpiry')
            
            if isinstance(purchase_date, str) and purchase_date:
                purchase_date = datetime.fromisoformat(purchase_date.replace('Z', '+00:00')).date()
            if isinstance(warranty_expiry, str) and warranty_expiry:
                warranty_expiry = datetime.fromisoformat(warranty_expiry.replace('Z', '+00:00')).date()
            
            assigned_to = asset_data.get('assignedTo') or None
            
            # Insert asset
            cursor.execute("""
                INSERT INTO AssetData (
                    AssetId, SerialNo, AssetType, Brand, Model,
                    DateOfPurchase, ProductCost, GST, WarrantyExpiry,
                    AssignedTo, RepairStatus,
                    AssetImagePath, PurchaseReceiptsPath, WarrantyCardPath
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                asset_id, asset_data.get('serialNumber'), asset_data.get('assetType'),
                asset_data.get('brand'), asset_data.get('model'), purchase_date,
                asset_data.get('purchaseCost', 0), asset_data.get('gstPaid', 0),
                warranty_expiry, assigned_to, asset_data.get('repairStatus', False),
                "s3://dummy-bucket/assets/images/sample.jpg",
                "s3://dummy-bucket/assets/receipts/sample.pdf",
                "s3://dummy-bucket/assets/warranty/sample.pdf"
            ))
            
            # Get field mapping
            cursor.execute("""
                SELECT s.field_key, s.field_label
                FROM AssetSpecifications s
                JOIN AssetTypes t ON s.asset_type_id = t.id
                WHERE t.type_name = %s
            """, (asset_data.get('assetType'),))
            field_mapping = {row['field_key']: row['field_label'] for row in cursor.fetchall()}
            
            # Insert specifications
            for field_key, field_value in specifications.items():
                if field_value:
                    cursor.execute("""
                        INSERT INTO SpecData (AssetId, AssetTypeName, SpecFieldName, SpecFieldValue)
                        VALUES (%s, %s, %s, %s)
                    """, (asset_id, asset_data.get('assetType'), field_mapping.get(field_key, field_key), field_value))
            
            # Create assignment history if assigned
            if assigned_to:
                cursor.execute("SELECT Name FROM PeopleData WHERE NameId = %s", (assigned_to,))
                emp_result = cursor.fetchone()
                emp_name = emp_result['Name'] if emp_result else assigned_to
                
                cursor.execute("""
                    INSERT INTO AssignmentHistory (AssetId, EmployeeId, EmployeeName, AssignedOn, IsActive)
                    VALUES (%s, %s, %s, %s, TRUE)
                """, (asset_id, assigned_to, emp_name, datetime.now().date()))
            
            connection.commit()
            logger.info(f"CREATE: Successfully created asset '{asset_id}'")
            
            return {'success': True, 'assetId': asset_id, 'message': f'Asset {asset_id} created successfully'}
            
        except Error as e:
            connection.rollback()
            logger.error(f"CREATE: Error - {e}")
            raise
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def update_assignment(self, asset_id: str, new_employee_id: str, repair_status: bool) -> dict:
        """Update asset assignment and repair status."""
        logger.info(f"UPDATE: Updating assignment for '{asset_id}'")
        connection = get_connection()
        if not connection:
            raise Exception("Database connection failed")
        
        try:
            cursor = connection.cursor(dictionary=True)
            connection.start_transaction()
            
            cursor.execute("SELECT AssignedTo FROM AssetData WHERE AssetId = %s", (asset_id,))
            current = cursor.fetchone()
            
            if not current:
                raise Exception(f"Asset {asset_id} not found")
            
            old_employee_id = current['AssignedTo']
            
            if old_employee_id != new_employee_id:
                if old_employee_id:
                    cursor.execute("""
                        UPDATE AssignmentHistory 
                        SET ReturnedOn = %s, IsActive = FALSE
                        WHERE AssetId = %s AND EmployeeId = %s AND IsActive = TRUE
                    """, (datetime.now().date(), asset_id, old_employee_id))
                
                if new_employee_id:
                    cursor.execute("SELECT Name FROM PeopleData WHERE NameId = %s", (new_employee_id,))
                    emp_result = cursor.fetchone()
                    emp_name = emp_result['Name'] if emp_result else new_employee_id
                    
                    cursor.execute("""
                        INSERT INTO AssignmentHistory (AssetId, EmployeeId, EmployeeName, AssignedOn, IsActive)
                        VALUES (%s, %s, %s, %s, TRUE)
                    """, (asset_id, new_employee_id, emp_name, datetime.now().date()))
            
            cursor.execute("""
                UPDATE AssetData SET AssignedTo = %s, RepairStatus = %s WHERE AssetId = %s
            """, (new_employee_id or None, repair_status, asset_id))
            
            connection.commit()
            logger.info(f"UPDATE: Successfully updated '{asset_id}'")
            return {'success': True, 'message': f'Asset {asset_id} updated successfully'}
            
        except Error as e:
            connection.rollback()
            logger.error(f"UPDATE: Error - {e}")
            raise
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def delete_bulk(self, asset_ids: list) -> dict:
        """Delete multiple assets by their IDs."""
        logger.info(f"DELETE: Deleting {len(asset_ids)} assets")
        connection = get_connection()
        if not connection:
            raise Exception("Database connection failed")
        
        try:
            cursor = connection.cursor()
            connection.start_transaction()
            
            format_strings = ','.join(['%s'] * len(asset_ids))
            
            cursor.execute(f"DELETE FROM SpecData WHERE AssetId IN ({format_strings})", tuple(asset_ids))
            cursor.execute(f"DELETE FROM AssignmentHistory WHERE AssetId IN ({format_strings})", tuple(asset_ids))
            cursor.execute(f"DELETE FROM AssetData WHERE AssetId IN ({format_strings})", tuple(asset_ids))
            deleted_count = cursor.rowcount
            
            connection.commit()
            logger.info(f"DELETE: Successfully deleted {deleted_count} assets")
            
            return {'success': True, 'deletedCount': deleted_count, 'message': f'Successfully deleted {deleted_count} asset(s)'}
            
        except Error as e:
            connection.rollback()
            logger.error(f"DELETE: Error - {e}")
            raise
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()