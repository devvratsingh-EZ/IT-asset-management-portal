"""
Database Utilities for MySQL Connection
Handles database connection, table creation, and queries
"""
import mysql.connector
from mysql.connector import Error
import os
import logging
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('DB_utils')

# Database configuration from environment
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'database': os.getenv('DB_NAME', 'ITAssetData')
}


def get_connection(with_database=True):
    """Create and return a MySQL database connection."""
    try:
        if with_database:
            connection = mysql.connector.connect(**DB_CONFIG)
        else:
            config = {k: v for k, v in DB_CONFIG.items() if k != 'database'}
            connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            logger.debug(f"Connected to MySQL {'database: ' + DB_CONFIG['database'] if with_database else 'server'}")
            return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return None


def init_database():
    """Initialize the database and create required tables."""
    logger.info("Initializing database...")
    connection = get_connection(with_database=False)
    if not connection:
        logger.error("Failed to connect to MySQL server")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        logger.info(f"Database '{DB_CONFIG['database']}' ensured")
        
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Create AuthData table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS AuthData (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        logger.info("Table 'AuthData' ensured")
        
        # Create AssetTypes table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS AssetTypes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type_name VARCHAR(100) UNIQUE NOT NULL
        )
        """)
        logger.info("Table 'AssetTypes' ensured")
        
        # Create AssetSpecifications table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS AssetSpecifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            asset_type_id INT NOT NULL,
            field_key VARCHAR(50) NOT NULL,
            field_label VARCHAR(100) NOT NULL,
            placeholder VARCHAR(255),
            FOREIGN KEY (asset_type_id) REFERENCES AssetTypes(id) ON DELETE CASCADE,
            UNIQUE KEY unique_type_field (asset_type_id, field_key)
        )
        """)
        logger.info("Table 'AssetSpecifications' ensured")
        
        # Create PeopleData table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS PeopleData (
            NameId VARCHAR(250) PRIMARY KEY NOT NULL,
            Name VARCHAR(250),
            Department VARCHAR(50),
            Email VARCHAR(250)
        )
        """)
        logger.info("Table 'PeopleData' ensured")
        
        # Create AssetData table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS AssetData (
            AssetId VARCHAR(100) PRIMARY KEY NOT NULL,
            SerialNo VARCHAR(150),
            AssetType VARCHAR(150),
            Brand VARCHAR(150),
            Model VARCHAR(150),
            DateOfPurchase DATE,
            ProductCost FLOAT,
            GST FLOAT,
            WarrantyExpiry DATE,
            AssignedTo VARCHAR(250) DEFAULT NULL,
            RepairStatus BOOLEAN DEFAULT FALSE,
            AssetImagePath VARCHAR(250),
            PurchaseReceiptsPath VARCHAR(250),
            WarrantyCardPath VARCHAR(250),
            CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (AssignedTo) REFERENCES PeopleData(NameId) ON DELETE SET NULL,
            CONSTRAINT unique_serial_brand_type UNIQUE (SerialNo, Brand, AssetType)
        )
        """)
        logger.info("Table 'AssetData' ensured")
        
        # Create SpecData table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS SpecData (
            ID INT PRIMARY KEY AUTO_INCREMENT,
            AssetId VARCHAR(100),
            AssetTypeName VARCHAR(100),
            SpecFieldName VARCHAR(150),
            SpecFieldValue VARCHAR(250),
            FOREIGN KEY (AssetId) REFERENCES AssetData(AssetId) ON DELETE CASCADE
        )
        """)
        logger.info("Table 'SpecData' ensured")
        
        # Create AssetIdCounter table for scalable ID generation
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS AssetIdCounter (
            id INT PRIMARY KEY DEFAULT 1,
            current_value INT NOT NULL DEFAULT 1000,
            CONSTRAINT single_row CHECK (id = 1)
        )
        """)
        logger.info("Table 'AssetIdCounter' ensured")
        
        # Initialize counter if not exists
        cursor.execute("""
        INSERT IGNORE INTO AssetIdCounter (id, current_value) VALUES (1, 1000)
        """)
        
        # Create AssignmentHistory table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS AssignmentHistory (
            id INT AUTO_INCREMENT PRIMARY KEY,
            AssetId VARCHAR(100) NOT NULL,
            EmployeeId VARCHAR(250) NOT NULL,
            EmployeeName VARCHAR(250),
            AssignedOn DATE NOT NULL,
            ReturnedOn DATE DEFAULT NULL,
            IsActive BOOLEAN DEFAULT TRUE,
            CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (AssetId) REFERENCES AssetData(AssetId) ON DELETE CASCADE,
            FOREIGN KEY (EmployeeId) REFERENCES PeopleData(NameId) ON DELETE CASCADE
        )
        """)
        logger.info("Table 'AssignmentHistory' ensured")
        
        connection.commit()
        logger.info("Database initialization complete")
        return True
        
    except Error as e:
        logger.error(f"Error initializing database: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def verify_user(username: str, password: str) -> dict:
    """Verify user credentials against the AuthData table."""
    logger.info(f"AUTH REQUEST: Verifying user '{username}'")
    connection = get_connection()
    if not connection:
        logger.warning("AUTH REQUEST: Database connection failed, returning None")
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT id, username, full_name, email, is_active
        FROM AuthData
        WHERE username = %s AND password = %s AND is_active = TRUE
        """
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        
        if user:
            logger.info(f"AUTH REQUEST: User '{username}' authenticated successfully")
        else:
            logger.warning(f"AUTH REQUEST: Authentication failed for user '{username}'")
        
        return user
    except Error as e:
        logger.error(f"AUTH REQUEST: Error verifying user: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# ============== Asset Type Functions ==============

def get_asset_types() -> list:
    """Get all asset types."""
    logger.info("FETCH REQUEST: Getting all asset types")
    connection = get_connection()
    if not connection:
        logger.warning("FETCH REQUEST: Database connection failed for asset types")
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, type_name 
            FROM AssetTypes 
            ORDER BY type_name
        """)
        results = cursor.fetchall()
        logger.info(f"FETCH REQUEST: Retrieved {len(results)} asset types from database")
        return results
    except Error as e:
        logger.error(f"FETCH REQUEST: Error fetching asset types: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_specifications_for_type(type_name: str) -> list:
    """Get specification fields for a given asset type."""
    logger.info(f"FETCH REQUEST: Getting specifications for type '{type_name}'")
    connection = get_connection()
    if not connection:
        logger.warning(f"FETCH REQUEST: Database connection failed for specifications of '{type_name}'")
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.field_key, s.field_label, s.placeholder
            FROM AssetSpecifications s
            JOIN AssetTypes t ON s.asset_type_id = t.id
            WHERE t.type_name = %s
            ORDER BY s.id
        """, (type_name,))
        results = cursor.fetchall()
        logger.info(f"FETCH REQUEST: Retrieved {len(results)} specifications for type '{type_name}'")
        return results
    except Error as e:
        logger.error(f"FETCH REQUEST: Error fetching specifications for '{type_name}': {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_all_specifications() -> dict:
    """Get all specifications grouped by asset type."""
    logger.info("FETCH REQUEST: Getting all specifications")
    connection = get_connection()
    if not connection:
        logger.warning("FETCH REQUEST: Database connection failed for all specifications")
        return {}
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.type_name, s.field_key, s.field_label, s.placeholder
            FROM AssetSpecifications s
            JOIN AssetTypes t ON s.asset_type_id = t.id
            ORDER BY t.type_name, s.id
        """)
        rows = cursor.fetchall()
        
        # Group by type_name
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
        
        logger.info(f"FETCH REQUEST: Retrieved specifications for {len(result)} asset types ({len(rows)} total fields)")
        return result
    except Error as e:
        logger.error(f"FETCH REQUEST: Error fetching all specifications: {e}")
        return {}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# ============== People/Employee Functions ==============

def get_all_employees() -> dict:
    """Get all employees from PeopleData table."""
    logger.info("FETCH REQUEST: Getting all employees")
    connection = get_connection()
    if not connection:
        logger.warning("FETCH REQUEST: Database connection failed for employees")
        return {}
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT NameId, Name, Department, Email
            FROM PeopleData
            ORDER BY Name
        """)
        rows = cursor.fetchall()
        
        # Convert to dict format matching frontend expectations
        result = {}
        for row in rows:
            result[row['NameId']] = {
                'name': row['Name'],
                'department': row['Department'],
                'email': row['Email']
            }
        
        logger.info(f"FETCH REQUEST: Retrieved {len(result)} employees from database")
        return result
    except Error as e:
        logger.error(f"FETCH REQUEST: Error fetching employees: {e}")
        return {}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_employee_by_id(employee_id: str) -> dict:
    """Get a single employee by ID."""
    logger.info(f"FETCH REQUEST: Getting employee '{employee_id}'")
    connection = get_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT NameId, Name, Department, Email
            FROM PeopleData
            WHERE NameId = %s
        """, (employee_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                'name': row['Name'],
                'department': row['Department'],
                'email': row['Email']
            }
        return None
    except Error as e:
        logger.error(f"FETCH REQUEST: Error fetching employee '{employee_id}': {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# ============== Asset ID Generation ==============

def generate_asset_id() -> str:
    """
    Generate a unique Asset ID using a counter table.
    
    Strategy: Use a dedicated counter table with atomic increment.
    This is more scalable than scanning the AssetData table because:
    1. Single row update vs full table scan
    2. O(1) operation vs O(n) operation
    3. Works correctly under concurrent inserts
    4. No gaps in sequence (unless transaction rollback)
    """
    logger.info("GENERATE: Creating new Asset ID")
    connection = get_connection()
    if not connection:
        raise Exception("Database connection failed")
    
    try:
        cursor = connection.cursor()
        
        # Atomic increment and fetch using FOR UPDATE to lock the row
        cursor.execute("""
            UPDATE AssetIdCounter 
            SET current_value = current_value + 1 
            WHERE id = 1
        """)
        
        cursor.execute("""
            SELECT current_value FROM AssetIdCounter WHERE id = 1
        """)
        
        result = cursor.fetchone()
        new_id = result[0]
        
        connection.commit()
        
        asset_id = f"AST_{new_id}"
        logger.info(f"GENERATE: Created Asset ID '{asset_id}'")
        return asset_id
        
    except Error as e:
        connection.rollback()
        logger.error(f"GENERATE: Error generating Asset ID: {e}")
        raise
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# ============== Asset CRUD Functions ==============

def create_asset(asset_data: dict, specifications: dict) -> dict:
    """
    Create a new asset with specifications.
    
    This function:
    1. Generates a unique Asset ID
    2. Inserts core asset data into AssetData table
    3. Inserts specifications into SpecData table
    4. Creates assignment history if assigned to someone
    
    All operations are wrapped in a transaction for atomicity.
    """
    logger.info(f"CREATE ASSET: Starting asset creation for serial '{asset_data.get('serialNumber')}'")
    connection = get_connection()
    if not connection:
        raise Exception("Database connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Start transaction
        connection.start_transaction()
        
        # 1. Generate unique Asset ID
        cursor.execute("""
            UPDATE AssetIdCounter 
            SET current_value = current_value + 1 
            WHERE id = 1
        """)
        cursor.execute("SELECT current_value FROM AssetIdCounter WHERE id = 1")
        counter_result = cursor.fetchone()
        asset_id = f"AST_{counter_result['current_value']}"
        
        logger.info(f"CREATE ASSET: Generated Asset ID '{asset_id}'")
        
        # 2. Prepare dummy S3 paths for file uploads
        dummy_image_path = "s3://dummy-bucket/assets/images/sample.jpg"
        dummy_receipt_path = "s3://dummy-bucket/assets/receipts/sample.pdf"
        dummy_warranty_path = "s3://dummy-bucket/assets/warranty/sample.pdf"
        
        # 3. Insert into AssetData table
        insert_asset_query = """
            INSERT INTO AssetData (
                AssetId, SerialNo, AssetType, Brand, Model,
                DateOfPurchase, ProductCost, GST, WarrantyExpiry,
                AssignedTo, RepairStatus,
                AssetImagePath, PurchaseReceiptsPath, WarrantyCardPath
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s
            )
        """
        
        # Handle date conversion
        purchase_date = asset_data.get('purchaseDate')
        warranty_expiry = asset_data.get('warrantyExpiry')
        
        if isinstance(purchase_date, str) and purchase_date:
            purchase_date = datetime.fromisoformat(purchase_date.replace('Z', '+00:00')).date()
        if isinstance(warranty_expiry, str) and warranty_expiry:
            warranty_expiry = datetime.fromisoformat(warranty_expiry.replace('Z', '+00:00')).date()
        
        assigned_to = asset_data.get('assignedTo') or None
        
        cursor.execute(insert_asset_query, (
            asset_id,
            asset_data.get('serialNumber'),
            asset_data.get('assetType'),
            asset_data.get('brand'),
            asset_data.get('model'),
            purchase_date,
            asset_data.get('purchaseCost', 0),
            asset_data.get('gstPaid', 0),
            warranty_expiry,
            assigned_to,
            asset_data.get('repairStatus', False),
            dummy_image_path,
            dummy_receipt_path,
            dummy_warranty_path
        ))
        
        logger.info(f"CREATE ASSET: Inserted core data for '{asset_id}'")
        
        # 4. Insert specifications into SpecData table
        # Get field_label mapping from AssetSpecifications
        asset_type = asset_data.get('assetType')
        
        cursor.execute("""
            SELECT s.field_key, s.field_label
            FROM AssetSpecifications s
            JOIN AssetTypes t ON s.asset_type_id = t.id
            WHERE t.type_name = %s
        """, (asset_type,))
        
        field_mapping = {row['field_key']: row['field_label'] for row in cursor.fetchall()}
        
        # Insert each specification
        insert_spec_query = """
            INSERT INTO SpecData (AssetId, AssetTypeName, SpecFieldName, SpecFieldValue)
            VALUES (%s, %s, %s, %s)
        """
        
        specs_inserted = 0
        for field_key, field_value in specifications.items():
            if field_value:  # Only insert non-empty values
                # Use field_label from mapping, fallback to field_key if not found
                field_label = field_mapping.get(field_key, field_key)
                cursor.execute(insert_spec_query, (
                    asset_id,
                    asset_type,
                    field_label,  # Using field_label as per requirement
                    field_value
                ))
                specs_inserted += 1
        
        logger.info(f"CREATE ASSET: Inserted {specs_inserted} specifications for '{asset_id}'")
        
        # 5. Create assignment history if assigned
        if assigned_to:
            # Get employee name
            cursor.execute("SELECT Name FROM PeopleData WHERE NameId = %s", (assigned_to,))
            emp_result = cursor.fetchone()
            emp_name = emp_result['Name'] if emp_result else assigned_to
            
            cursor.execute("""
                INSERT INTO AssignmentHistory (AssetId, EmployeeId, EmployeeName, AssignedOn, IsActive)
                VALUES (%s, %s, %s, %s, TRUE)
            """, (asset_id, assigned_to, emp_name, datetime.now().date()))
            
            logger.info(f"CREATE ASSET: Created assignment history for '{asset_id}' -> '{assigned_to}'")
        
        # Commit transaction
        connection.commit()
        
        logger.info(f"CREATE ASSET: Successfully created asset '{asset_id}'")
        
        return {
            'success': True,
            'assetId': asset_id,
            'message': f'Asset {asset_id} created successfully'
        }
        
    except Error as e:
        connection.rollback()
        logger.error(f"CREATE ASSET: Error creating asset: {e}")
        raise
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_all_assets() -> dict:
    """Get all assets from database."""
    logger.info("FETCH REQUEST: Getting all assets")
    connection = get_connection()
    if not connection:
        logger.warning("FETCH REQUEST: Database connection failed for assets")
        return {}
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get all assets
        cursor.execute("""
            SELECT 
                AssetId, SerialNo, AssetType, Brand, Model,
                DateOfPurchase, ProductCost, GST, WarrantyExpiry,
                AssignedTo, RepairStatus,
                AssetImagePath, PurchaseReceiptsPath, WarrantyCardPath
            FROM AssetData
            ORDER BY AssetId
        """)
        assets = cursor.fetchall()
        
        result = {}
        for asset in assets:
            asset_id = asset['AssetId']
            
            # Get specifications for this asset
            cursor.execute("""
                SELECT SpecFieldName, SpecFieldValue
                FROM SpecData
                WHERE AssetId = %s
            """, (asset_id,))
            specs = cursor.fetchall()
            
            specifications = {}
            for spec in specs:
                specifications[spec['SpecFieldName']] = spec['SpecFieldValue']
            
            # Add brand and model to specifications for display
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
        
        logger.info(f"FETCH REQUEST: Retrieved {len(result)} assets from database")
        return result
        
    except Error as e:
        logger.error(f"FETCH REQUEST: Error fetching assets: {e}")
        return {}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_asset_by_id(asset_id: str) -> dict:
    """Get a single asset by ID."""
    logger.info(f"FETCH REQUEST: Getting asset '{asset_id}'")
    connection = get_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                AssetId, SerialNo, AssetType, Brand, Model,
                DateOfPurchase, ProductCost, GST, WarrantyExpiry,
                AssignedTo, RepairStatus,
                AssetImagePath, PurchaseReceiptsPath, WarrantyCardPath
            FROM AssetData
            WHERE AssetId = %s
        """, (asset_id,))
        asset = cursor.fetchone()
        
        if not asset:
            return None
        
        # Get specifications
        cursor.execute("""
            SELECT SpecFieldName, SpecFieldValue
            FROM SpecData
            WHERE AssetId = %s
        """, (asset_id,))
        specs = cursor.fetchall()
        
        specifications = {}
        for spec in specs:
            specifications[spec['SpecFieldName']] = spec['SpecFieldValue']
        
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
        logger.error(f"FETCH REQUEST: Error fetching asset '{asset_id}': {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_assignment_history(asset_id: str) -> list:
    """Get assignment history for an asset."""
    logger.info(f"FETCH REQUEST: Getting assignment history for '{asset_id}'")
    connection = get_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                EmployeeId, EmployeeName, AssignedOn, ReturnedOn, IsActive
            FROM AssignmentHistory
            WHERE AssetId = %s
            ORDER BY AssignedOn DESC
        """, (asset_id,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'employeeId': row['EmployeeId'],
                'employeeName': row['EmployeeName'],
                'assignedOn': row['AssignedOn'].strftime('%Y-%m-%d') if row['AssignedOn'] else None,
                'returnedOn': 'Active' if row['IsActive'] else (row['ReturnedOn'].strftime('%Y-%m-%d') if row['ReturnedOn'] else None)
            })
        
        logger.info(f"FETCH REQUEST: Retrieved {len(history)} history records for '{asset_id}'")
        return history
        
    except Error as e:
        logger.error(f"FETCH REQUEST: Error fetching assignment history: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_all_assignment_history() -> dict:
    """Get all assignment history grouped by asset ID."""
    logger.info("FETCH REQUEST: Getting all assignment history")
    connection = get_connection()
    if not connection:
        return {}
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                AssetId, EmployeeId, EmployeeName, AssignedOn, ReturnedOn, IsActive
            FROM AssignmentHistory
            ORDER BY AssetId, AssignedOn DESC
        """)
        
        result = {}
        for row in cursor.fetchall():
            asset_id = row['AssetId']
            if asset_id not in result:
                result[asset_id] = []
            
            result[asset_id].append({
                'employeeId': row['EmployeeId'],
                'employeeName': row['EmployeeName'],
                'assignedOn': row['AssignedOn'].strftime('%Y-%m-%d') if row['AssignedOn'] else None,
                'returnedOn': 'Active' if row['IsActive'] else (row['ReturnedOn'].strftime('%Y-%m-%d') if row['ReturnedOn'] else None)
            })
        
        logger.info(f"FETCH REQUEST: Retrieved assignment history for {len(result)} assets")
        return result
        
    except Error as e:
        logger.error(f"FETCH REQUEST: Error fetching all assignment history: {e}")
        return {}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def update_asset_assignment(asset_id: str, new_employee_id: str, repair_status: bool) -> dict:
    """Update asset assignment and repair status."""
    logger.info(f"UPDATE ASSET: Updating assignment for '{asset_id}'")
    connection = get_connection()
    if not connection:
        raise Exception("Database connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        connection.start_transaction()
        
        # Get current assignment
        cursor.execute("SELECT AssignedTo FROM AssetData WHERE AssetId = %s", (asset_id,))
        current = cursor.fetchone()
        
        if not current:
            raise Exception(f"Asset {asset_id} not found")
        
        old_employee_id = current['AssignedTo']
        
        # If assignment changed
        if old_employee_id != new_employee_id:
            # Close old assignment if exists
            if old_employee_id:
                cursor.execute("""
                    UPDATE AssignmentHistory 
                    SET ReturnedOn = %s, IsActive = FALSE
                    WHERE AssetId = %s AND EmployeeId = %s AND IsActive = TRUE
                """, (datetime.now().date(), asset_id, old_employee_id))
                logger.info(f"UPDATE ASSET: Closed assignment for '{old_employee_id}'")
            
            # Create new assignment if new employee
            if new_employee_id:
                cursor.execute("SELECT Name FROM PeopleData WHERE NameId = %s", (new_employee_id,))
                emp_result = cursor.fetchone()
                emp_name = emp_result['Name'] if emp_result else new_employee_id
                
                cursor.execute("""
                    INSERT INTO AssignmentHistory (AssetId, EmployeeId, EmployeeName, AssignedOn, IsActive)
                    VALUES (%s, %s, %s, %s, TRUE)
                """, (asset_id, new_employee_id, emp_name, datetime.now().date()))
                logger.info(f"UPDATE ASSET: Created assignment for '{new_employee_id}'")
        
        # Update asset record
        cursor.execute("""
            UPDATE AssetData 
            SET AssignedTo = %s, RepairStatus = %s
            WHERE AssetId = %s
        """, (new_employee_id or None, repair_status, asset_id))
        
        connection.commit()
        
        logger.info(f"UPDATE ASSET: Successfully updated '{asset_id}'")
        return {'success': True, 'message': f'Asset {asset_id} updated successfully'}
        
    except Error as e:
        connection.rollback()
        logger.error(f"UPDATE ASSET: Error updating asset: {e}")
        raise
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_summary_data() -> list:
    """Get summary data from SummaryData view."""
    logger.info("FETCH REQUEST: Getting summary data")
    connection = get_connection()
    if not connection:
        logger.warning("FETCH REQUEST: Database connection failed for summary")
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT AssetType, Department, Brand, Model, Count
            FROM SummaryData
            ORDER BY AssetType, Department, Brand, Model
        """)
        results = cursor.fetchall()
        logger.info(f"FETCH REQUEST: Retrieved {len(results)} summary rows")
        return results
    except Error as e:
        logger.error(f"FETCH REQUEST: Error fetching summary data: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def test_connection() -> bool:
    """Test if database connection is working."""
    connection = get_connection()
    if connection and connection.is_connected():
        logger.debug("Database connection test: SUCCESS")
        connection.close()
        return True
    logger.debug("Database connection test: FAILED")
    return False


if __name__ == "__main__":
    logger.info("Running database initialization...")
    if init_database():
        logger.info("Database setup complete!")
    else:
        logger.error("Database setup failed!")