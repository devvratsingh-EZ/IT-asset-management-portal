"""Authentication routes."""
import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.models.requests import LoginRequest
from app.models.responses import LoginResponse, TokenValidationResponse
from app.services.auth_service import AuthService
from app.dependencies import security

logger = logging.getLogger('routes.auth')
router = APIRouter()
auth_service = AuthService()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate and return JWT token."""
    logger.info(f"LOGIN REQUEST: User '{request.username}'")
    
    result = auth_service.authenticate(request.username, request.password)
    if result:
        return LoginResponse(**result)
    
    logger.warning(f"LOGIN FAILED: User '{request.username}'")
    raise HTTPException(status_code=401, detail="Invalid username or password")


@router.get("/verify", response_model=TokenValidationResponse)
async def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify if token is still valid."""
    payload = auth_service.verify_token(credentials.credentials)
    
    if payload:
        return TokenValidationResponse(
            valid=True,
            username=payload.get('username'),
            full_name=payload.get('full_name'),
            message="Token is valid"
        )
    
    return TokenValidationResponse(valid=False, message="Token expired or invalid")