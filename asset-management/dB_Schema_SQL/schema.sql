CREATE TABLE AuthData (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );



CREATE TABLE AssetTypes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type_name VARCHAR(100) UNIQUE NOT NULL
        );



CREATE TABLE AssetSpecifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            asset_type_id INT NOT NULL,
            field_key VARCHAR(50) NOT NULL,
            field_label VARCHAR(100) NOT NULL,
            placeholder VARCHAR(255),
            FOREIGN KEY (asset_type_id) REFERENCES AssetTypes(id) ON DELETE CASCADE,
            UNIQUE KEY unique_type_field (asset_type_id, field_key)
        );


CREATE TABLE PeopleData(
			NameId VARCHAR(250) PRIMARY KEY NOT NULL,
            Name VARCHAR(250),
            Department VARCHAR(50),
            Email VARCHAR(250)
);


CREATE TABLE AssetData(
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
            RepairStatus VARCHAR(10),
            AssetImagePath VARCHAR (250),
            PuchaseReceiptsPath VARCHAR(250),
            WarrantyCardPath VARCHAR(250),
            CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			FOREIGN KEY (AssignedTo) REFERENCES PeopleData (NameId) ON DELETE SET NULL,
            CONSTRAINT unique_serial_brand_type UNIQUE (SerialNo, Brand, AssetType)
);


CREATE TABLE SpecData(
			ID INT PRIMARY KEY AUTO_INCREMENT,
			AssetId VARCHAR (100),
            AssetTypeName VARCHAR(100),
            SpecFieldName VARCHAR (150),
            SpecFieldValue VARCHAR(250),
            FOREIGN KEY (AssetId) REFERENCES AssetData (AssetId) ON DELETE CASCADE
);


CREATE TABLE AssetIdCounter (
            id INT PRIMARY KEY DEFAULT 1,
            current_value INT NOT NULL DEFAULT 1000,
            CONSTRAINT single_row CHECK (id = 1)
        );

CREATE TABLE AssignmentHistory (
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
        );
