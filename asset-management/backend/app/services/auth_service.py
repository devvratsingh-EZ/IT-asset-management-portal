"""Authentication service with access + refresh token support."""
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.db.repositories.auth_repository import AuthRepository

logger = logging.getLogger('services.auth')


class AuthService:
    """Handles authentication logic with access and refresh tokens."""
    
    FALLBACK_USERS = {"itadmin": "pass123", "techlead": "admin456"}
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session
    
    def create_access_token(self, data: dict) -> Tuple[str, datetime]:
        """Create short-lived JWT access token (15 min)."""
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = data.copy()
        to_encode.update({"exp": expires_at, "type": "access"})
        token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        logger.info(f"Access token created for user '{data.get('username')}', expires at {expires_at}")
        return token, expires_at
    
    def create_refresh_token(self) -> Tuple[str, datetime]:
        """Create secure random refresh token (24 hours)."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)
        return token, expires_at
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT access token and return payload."""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            if payload.get('type') != 'access':
                logger.warning("Token is not an access token")
                return None
            logger.info(f"Access token verified for user '{payload.get('username')}'")
            return payload
        except JWTError as e:
            logger.warning(f"Access token verification failed - {str(e)}")
            return None
    
    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """Authenticate user and return tokens."""
        user = None
        user_id = 0
        full_name = username
        
        # Try database authentication
        if self.session:
            auth_repo = AuthRepository(self.session)
            user = auth_repo.verify_user(username, password)
            if user:
                user_id = user['id']
                full_name = user.get('full_name', username)
        
        # Fallback for development
        if not user and self.FALLBACK_USERS.get(username) == password:
            user = {'username': username}
            user_id = 0
            full_name = "IT Administrator" if username == "itadmin" else username
        
        if not user:
            return None
        
        # Create access token
        access_token, access_expires = self.create_access_token({
            "username": username,
            "full_name": full_name,
            "user_id": user_id
        })
        
        # Create refresh token
        refresh_token, refresh_expires = self.create_refresh_token()
        
        # Store refresh token in DB (skip for fallback users)
        if self.session and user_id > 0:
            auth_repo = AuthRepository(self.session)
            auth_repo.update_refresh_token(user_id, refresh_token, refresh_expires)
        
        return {
            "success": True,
            "message": "Login successful",
            "access_token": access_token,
            "username": username,
            "full_name": full_name,
            "expires_at": access_expires.isoformat(),
            "refresh_token": refresh_token,
            "refresh_expires_at": refresh_expires.isoformat()
        }
    
    def refresh_tokens(self, refresh_token: str) -> Optional[dict]:
        """Validate refresh token and issue new token pair."""
        if not self.session:
            logger.error("No database session for refresh token validation")
            return None
        
        auth_repo = AuthRepository(self.session)
        user = auth_repo.validate_refresh_token(refresh_token)
        
        if not user:
            return None
        
        # Create new access token
        access_token, access_expires = self.create_access_token({
            "username": user['username'],
            "full_name": user.get('full_name', user['username']),
            "user_id": user['id']
        })
        
        # Rotate refresh token
        new_refresh_token, refresh_expires = self.create_refresh_token()
        auth_repo.update_refresh_token(user['id'], new_refresh_token, refresh_expires)
        
        return {
            "success": True,
            "access_token": access_token,
            "expires_at": access_expires.isoformat(),
            "refresh_token": new_refresh_token,
            "refresh_expires_at": refresh_expires.isoformat()
        }
    
    def logout(self, user_id: int) -> bool:
        """Invalidate refresh token on logout."""
        if not self.session or user_id <= 0:
            return True  # Fallback users don't have DB tokens
        
        auth_repo = AuthRepository(self.session)
        return auth_repo.invalidate_refresh_token(user_id)
    

    def validate_refresh_for_logout(self, refresh_token: str) -> Optional[dict]:
        """Validate refresh token for logout (just returns user info if valid)."""
        if not self.session:
            return None
        
        auth_repo = AuthRepository(self.session)
        return auth_repo.validate_refresh_token(refresh_token)