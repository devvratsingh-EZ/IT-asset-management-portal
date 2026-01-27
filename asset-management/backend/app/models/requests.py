"""Request models."""
from typing import Optional, Dict, List
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class AssetCreateRequest(BaseModel):
    serialNumber: str
    assetType: str
    brand: str
    model: str
    specifications: Dict[str, str] = {}
    purchaseDate: Optional[str] = None
    purchaseCost: Optional[float] = 0
    leaseCost: Optional[float] = 0
    gstPaid: float = 0
    warrantyExpiry: Optional[str] = None
    leaseExpiry: Optional[str] = None
    assignedTo: Optional[str] = None
    repairStatus: bool = False
    isRental: bool = False
    isTempAsset: bool = False


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