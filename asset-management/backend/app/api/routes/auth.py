"""
Authentication routes with access + refresh token support.

SECURITY ARCHITECTURE:
- Access Tokens: Short-lived (15 min), stored in-memory, sent via Authorization header
- Refresh Tokens: Long-lived (24 hrs), stored in HttpOnly cookie, never exposed to JavaScript
- HTTPS: Required in production (set DEBUG=False in .env)
- CSRF Protection: SameSite=Strict on all cookies
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, Response, Request, Cookie
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.models.requests import LoginRequest
from app.models.responses import LoginResponse, TokenValidationResponse, RefreshResponse
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.dependencies import security
from app.config import settings

logger = logging.getLogger('routes.auth')
router = APIRouter()

REFRESH_COOKIE_NAME = "refresh_token"
COOKIE_MAX_AGE = 24 * 60 * 60  # 24 hours in seconds


def set_refresh_cookie(response: Response, refresh_token: str):
    """
    Set HttpOnly cookie for refresh token with production-grade security.
    
    Security Features:
    - HttpOnly: Prevents XSS attacks (JavaScript cannot access this cookie)
    - Secure: Cookie only sent over HTTPS (prevents MITM attacks)
    - SameSite=Strict: Prevents CSRF attacks (cookie not sent to cross-site requests)
    - Max-Age: Cookie expires after 24 hours
    - Path: Cookie sent to all /api/* endpoints
    
    Environment-based Security:
    - Development (DEBUG=True): secure=False (HTTP allowed for local testing)
    - Production (DEBUG=False): secure=True (HTTPS required - set in .env)
    """
    is_production = not settings.DEBUG
    
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=is_production,  # True in production (HTTPS only), False in development
        samesite="strict",  # Strict CSRF protection
        max_age=COOKIE_MAX_AGE,
        path="/api"  # ← Changed from "/api/auth" to "/api" so it covers all /api/* routes
    )
    
    if is_production:
        logger.warning(f"[auth.py:40] PRODUCTION: Refresh cookie set with secure=True (HTTPS required)")
    else:
        logger.info(f"[auth.py:40] DEVELOPMENT: Refresh cookie set with secure=False (HTTP allowed)")


def clear_refresh_cookie(response: Response):
    """Clear refresh token cookie."""
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path="/api"  # ← Match the path used in set_refresh_cookie
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Authenticate and return access token + set refresh cookie."""
    logger.info(f"LOGIN REQUEST: User '{request.username}'")
    
    auth_service = AuthService(db)
    result = auth_service.authenticate(request.username, request.password)
    
    if result:
        # Set refresh token in HttpOnly cookie
        set_refresh_cookie(response, result["refresh_token"])
        
        # Return access token in response body (not refresh token)
        return LoginResponse(
            success=True,
            message=result["message"],
            token=result["access_token"],
            username=result["username"],
            full_name=result["full_name"],
            expires_at=result["expires_at"]
        )
    
    logger.warning(f"LOGIN FAILED: User '{request.username}'")
    raise HTTPException(status_code=401, detail="Invalid username or password")


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: Optional[str] = Cookie(None, alias=REFRESH_COOKIE_NAME)
):
    """Refresh access token using refresh token from cookie."""
    # Debug: Log all cookies received
    logger.info(f"[auth.py:95] REFRESH REQUEST - Cookies: {request.cookies}")
    logger.info(f"[auth.py:96] REFRESH REQUEST - Cookie param: {refresh_token}")
    
    if not refresh_token:
        logger.warning(f"[auth.py:98] REFRESH: No refresh token cookie present. Cookies received: {dict(request.cookies)}")
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    auth_service = AuthService(db)
    result = auth_service.refresh_tokens(refresh_token)
    
    if result:
        # Set new refresh token cookie (rotation)
        set_refresh_cookie(response, result["refresh_token"])
        
        return RefreshResponse(
            success=True,
            access_token=result["access_token"],
            expires_at=result["expires_at"],
            username=result.get("username"),
            full_name=result.get("full_name")
        )
    
    # Clear invalid cookie
    clear_refresh_cookie(response)
    logger.warning("REFRESH: Invalid or expired refresh token")
    raise HTTPException(status_code=401, detail="Refresh token expired")


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: Optional[str] = Cookie(None, alias=REFRESH_COOKIE_NAME)
):
    """Logout and invalidate refresh token (no auth required - uses cookie)."""
    # Invalidate refresh token in DB if present
    if refresh_token:
        auth_service = AuthService(db)
        user = auth_service.validate_refresh_for_logout(refresh_token)
        if user:
            auth_service.logout(user['id'])
            logger.info(f"LOGOUT: Invalidated refresh token for user_id={user['id']}")
    
    # Always clear cookie
    clear_refresh_cookie(response)
    logger.info("LOGOUT: Refresh cookie cleared")
    return {"success": True, "message": "Logged out successfully"}


@router.get("/verify", response_model=TokenValidationResponse)
async def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify if access token is still valid."""
    auth_service = AuthService(session=None)
    payload = auth_service.verify_token(credentials.credentials)
    
    if payload:
        return TokenValidationResponse(
            valid=True,
            username=payload.get('username'),
            full_name=payload.get('full_name'),
            message="Token is valid"
        )
    
    return TokenValidationResponse(valid=False, message="Token expired or invalid")