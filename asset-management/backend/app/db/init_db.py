"""Database initialization."""
import logging
from mysql.connector import Error

from app.config import settings
from app.db.connection import get_connection

logger = logging.getLogger('db.init')


def init_database() -> bool:
    """Initialize the database and create required tables."""
    logger.info("Initializing database...")
    connection = get_connection(with_database=False)
    if not connection:
        logger.error("Failed to connect to MySQL server")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME}")
        logger.info(f"Database '{settings.DB_NAME}' ensured")
        cursor.execute(f"USE {settings.DB_NAME}")
        
        # Create tables
        _create_tables(cursor)
        
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


def _create_tables(cursor):
    """Create all required tables."""
    
    # AuthData
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS AuthData (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )""")
    logger.info("Table 'AuthData' ensured")
    
    # AssetTypes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS AssetTypes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        type_name VARCHAR(100) UNIQUE NOT NULL
    )""")
    logger.info("Table 'AssetTypes' ensured")
    
    # AssetSpecifications
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS AssetSpecifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            asset_type_id INT NOT NULL,
            field_key VARCHAR(50) NOT NULL,
            field_label VARCHAR(100) NOT NULL,
            placeholder VARCHAR(255),
            FOREIGN KEY (asset_type_id) REFERENCES AssetTypes(id) ON DELETE CASCADE,
            UNIQUE KEY unique_type_field (asset_type_id, field_key)
    )""")
    logger.info("Table 'AssetSpecifications' ensured")
    
    # PeopleData
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS PeopleData (
			NameId VARCHAR(250) PRIMARY KEY NOT NULL,
            Name VARCHAR(250),
            Department VARCHAR(50),
            Email VARCHAR(250)
    )""")
    logger.info("Table 'PeopleData' ensured")
    
    # AssetData
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS AssetData (
			AssetId VARCHAR(100) PRIMARY KEY NOT NULL,
            SerialNo VARCHAR(150),
            AssetType VARCHAR(150),
            Brand VARCHAR(150),
            Model VARCHAR(200),
            DateOfPurchase DATE,
            ProductCost FLOAT,
            GST FLOAT,
            WarrantyExpiry DATE,
            AssignedTo VARCHAR(250),
            RepairStatus BOOL NOT NULL DEFAULT 0,
            IsTempStatus BOOL NOT NULL DEFAULT 0,
            AssetImagePath VARCHAR (250),
            PuchaseReceiptsPath VARCHAR(250),
            WarrantyCardPath VARCHAR(250),
            CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			FOREIGN KEY (AssignedTo) REFERENCES PeopleData (NameId) ON DELETE SET NULL,
            CONSTRAINT unique_serial_brand_type UNIQUE (SerialNo, Brand, AssetType)
    )""")
    logger.info("Table 'AssetData' ensured")
    
    # SpecData
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SpecData (
			ID INT PRIMARY KEY AUTO_INCREMENT,
			AssetId VARCHAR (100),
            AssetTypeName VARCHAR(100),
            SpecFieldName VARCHAR (150),
            SpecFieldValue VARCHAR(250),
            FOREIGN KEY (AssetId) REFERENCES AssetData (AssetId) ON DELETE CASCADE
    )""")
    logger.info("Table 'SpecData' ensured")
    
    # AssetIdCounter
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS AssetIdCounter (
            id INT PRIMARY KEY DEFAULT 1,
            current_value INT NOT NULL DEFAULT 1000,
            CONSTRAINT single_row CHECK (id = 1)
    )""")
    cursor.execute("INSERT IGNORE INTO AssetIdCounter (id, current_value) VALUES (1, 1000)")
    logger.info("Table 'AssetIdCounter' ensured")
    
    # AssignmentHistory
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
    )""")
    logger.info("Table 'AssignmentHistory' ensured")
    
    # SummaryData view
    cursor.execute("""
    CREATE OR REPLACE VIEW SummaryData AS
                SELECT
                    a.AssetType,
                    COALESCE(p.Department, 'Not Assigned') AS Department,
                    a.Brand,
                    a.Model,
                    COUNT(*) AS Count
                FROM AssetData a
                LEFT JOIN PeopleData p 
                    ON a.AssignedTo = p.NameId
                GROUP BY 
                    a.AssetType,
                    Department,
                    a.Brand,
                    a.Model
                ORDER BY a.AssetType
    """)
    logger.info("View 'SummaryData' ensured")