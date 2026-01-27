"""Request models."""
from typing import Optional, Dict, List
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class AssetCreateRequest(BaseModel):
    assetType: str
    serialNumber: str
    brand: str
    model: str
    specifications: dict = {}
    purchaseDate: Optional[str] = None
    purchaseCost: Optional[float] = None
    gstPaid: Optional[float] = None
    warrantyExpiry: Optional[str] = None
    leaseCost: Optional[float] = None
    leaseExpiry: Optional[str] = None
    isRental: bool = False
    assignedTo: Optional[str] = None
    repairStatus: bool = False


class AssetUpdateRequest(BaseModel):
    assignedTo: Optional[str] = None
    repairStatus: bool = False


class BulkDeleteRequest(BaseModel):
    assetIds: List[str]

class BrandModelCreateRequest(BaseModel):
    brandName: str
    modelName: str

class RepairStartRequest(BaseModel):
    assetId: str
    repairDetails: str
    tempAssetId: Optional[str] = None


class RepairEndRequest(BaseModel):
    assetId: str