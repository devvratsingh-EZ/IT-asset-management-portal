"""Shared dependencies for the application."""
import logging
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth_service import AuthService

logger = logging.getLogger('dependencies')
security = HTTPBearer()
auth_service = AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Dependency to get current authenticated user."""
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload