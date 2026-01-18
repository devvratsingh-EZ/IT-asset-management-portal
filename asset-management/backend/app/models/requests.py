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
    purchaseCost: float = 0
    gstPaid: float = 0
    warrantyExpiry: Optional[str] = None
    assignedTo: Optional[str] = None
    repairStatus: bool = False


class AssetUpdateRequest(BaseModel):
    assignedTo: Optional[str] = None
    repairStatus: bool = False


class BulkDeleteRequest(BaseModel):
    assetIds: List[str]