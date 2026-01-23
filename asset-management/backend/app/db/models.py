from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Float, Boolean, Date, Text,
    ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import TIMESTAMP, TINYINT
from datetime import datetime, date, timezone



class Base(DeclarativeBase):
    pass


class AuthData(Base):
    __tablename__ = "authdata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Refresh token fields
    refresh_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    refresh_token_expires_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=True
    )


class AssetType(Base):
    __tablename__ = "assettypes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    specifications: Mapped[List["AssetSpecification"]] = relationship(
        back_populates="asset_type", cascade="all, delete-orphan"
    )


class BrandData(Base):
    __tablename__ = "branddata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brand_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)


class AssetSpecification(Base):
    __tablename__ = "assetspecifications"
    __table_args__ = (
        UniqueConstraint('asset_type_id', 'field_key', name='unique_type_field'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_type_id: Mapped[int] = mapped_column(ForeignKey("assettypes.id", ondelete="CASCADE"), nullable=False)
    field_key: Mapped[str] = mapped_column(String(50), nullable=False)
    field_label: Mapped[str] = mapped_column(String(100), nullable=False)
    placeholder: Mapped[Optional[str]] = mapped_column(String(255))

    asset_type: Mapped["AssetType"] = relationship(back_populates="specifications")


class PeopleData(Base):
    __tablename__ = "peopledata"

    NameId: Mapped[str] = mapped_column(String(250), primary_key=True)
    Name: Mapped[Optional[str]] = mapped_column(String(250))
    Department: Mapped[Optional[str]] = mapped_column(String(50))
    Email: Mapped[Optional[str]] = mapped_column(String(250))

    assigned_assets: Mapped[List["AssetData"]] = relationship(back_populates="assigned_employee")
    assignment_history: Mapped[List["AssignmentHistory"]] = relationship(back_populates="employee")


class AssetData(Base):
    __tablename__ = "assetdata"
    __table_args__ = (
        UniqueConstraint('SerialNo', 'Brand', 'AssetType', name='unique_serial_brand_type'),
    )

    AssetId: Mapped[str] = mapped_column(String(100), primary_key=True)
    SerialNo: Mapped[Optional[str]] = mapped_column(String(150))
    AssetType: Mapped[Optional[str]] = mapped_column(String(150))
    Brand: Mapped[Optional[str]] = mapped_column(String(150))
    Model: Mapped[Optional[str]] = mapped_column(String(200))
    DateOfPurchase: Mapped[Optional[date]] = mapped_column(Date)
    ProductCost: Mapped[Optional[float]] = mapped_column(Float)
    GST: Mapped[Optional[float]] = mapped_column(Float)
    WarrantyExpiry: Mapped[Optional[date]] = mapped_column(Date)

    AssignedTo: Mapped[Optional[str]] = mapped_column(
        ForeignKey("peopledata.NameId", ondelete="SET NULL")
    )

    RepairStatus: Mapped[bool] = mapped_column(TINYINT(1), nullable=False, default=0)
    IsTempAsset: Mapped[bool] = mapped_column(TINYINT(1), nullable=False, default=0)

    AssetImagePath: Mapped[Optional[str]] = mapped_column(String(250))
    PurchaseReceiptsPath: Mapped[Optional[str]] = mapped_column(String(250))
    WarrantyCardPath: Mapped[Optional[str]] = mapped_column(String(250))

    CreatedAt: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=True
    )
    UpdatedAt: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=True
    )

    assigned_employee: Mapped[Optional["PeopleData"]] = relationship(back_populates="assigned_assets")
    spec_data: Mapped[List["SpecData"]] = relationship(back_populates="asset", cascade="all, delete-orphan")
    assignment_history: Mapped[List["AssignmentHistory"]] = relationship(back_populates="asset", cascade="all, delete-orphan")


class SpecData(Base):
    __tablename__ = "specdata"

    ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    AssetId: Mapped[Optional[str]] = mapped_column(ForeignKey("assetdata.AssetId", ondelete="CASCADE"))
    AssetTypeName: Mapped[Optional[str]] = mapped_column(String(100))
    SpecFieldName: Mapped[Optional[str]] = mapped_column(String(150))
    SpecFieldValue: Mapped[Optional[str]] = mapped_column(String(250))

    asset: Mapped[Optional["AssetData"]] = relationship(back_populates="spec_data")


class AssetIdCounter(Base):
    __tablename__ = "assetidcounter"
    __table_args__ = (CheckConstraint('id = 1', name='single_row'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    current_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)


class AssignmentHistory(Base):
    __tablename__ = "assignmenthistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    AssetId: Mapped[str] = mapped_column(ForeignKey("assetdata.AssetId", ondelete="CASCADE"), nullable=False)
    EmployeeId: Mapped[str] = mapped_column(ForeignKey("peopledata.NameId", ondelete="CASCADE"), nullable=False)
    EmployeeName: Mapped[Optional[str]] = mapped_column(String(250))
    AssignedOn: Mapped[date] = mapped_column(Date, nullable=False)
    ReturnedOn: Mapped[Optional[date]] = mapped_column(Date)

    IsActive: Mapped[bool] = mapped_column(TINYINT(1), nullable=True, default=1)

    CreatedAt: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=True
    )

    asset: Mapped["AssetData"] = relationship(back_populates="assignment_history")
    employee: Mapped["PeopleData"] = relationship(back_populates="assignment_history")


class RepairStatusTracker(Base):
    __tablename__ = "repairstatustracker"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    AssetId: Mapped[str] = mapped_column(ForeignKey("assetdata.AssetId", ondelete="CASCADE"), nullable=False)
    TempAssetId: Mapped[str] = mapped_column(ForeignKey("assetdata.AssetId", ondelete="CASCADE"), nullable=False)

    RepairStartTimestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=False
    )
    RepairEndTimestamp: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    RepairDetails: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint("AssetId <> TempAssetId", name="chk_assetid_tempid_not_same"),
    )
