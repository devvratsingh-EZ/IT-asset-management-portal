"""Response models."""
from typing import Optional
from pydantic import BaseModel


class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    expires_at: Optional[str] = None


class TokenValidationResponse(BaseModel):
    valid: bool
    username: Optional[str] = None
    full_name: Optional[str] = None
    message: Optional[str] = None