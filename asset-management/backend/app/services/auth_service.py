"""Authentication service."""
import logging
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.config import settings
from app.db.repositories.auth_repository import AuthRepository

logger = logging.getLogger('services.auth')


class AuthService:
    """Handles authentication logic."""
    
    FALLBACK_USERS = {"itadmin": "pass123", "techlead": "admin456"}
    
    def __init__(self):
        self.auth_repo = AuthRepository()
    
    def create_access_token(self, data: dict) -> tuple:
        """Create JWT token with expiration."""
        expires_at = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS)
        to_encode = data.copy()
        to_encode.update({"exp": expires_at})
        token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        logger.info(f"JWT TOKEN: Created for user '{data.get('username')}', expires at {expires_at}")
        return token, expires_at
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            logger.info(f"JWT TOKEN: Verified for user '{payload.get('username')}'")
            return payload
        except JWTError as e:
            logger.warning(f"JWT TOKEN: Verification failed - {str(e)}")
            return None
    
    def authenticate(self, username: str, password: str) -> dict:
        """Authenticate user and return token data."""
        user = self.auth_repo.verify_user(username, password)
        
        if user:
            token, expires_at = self.create_access_token({
                "username": user['username'],
                "full_name": user.get('full_name', user['username']),
                "user_id": user['id']
            })
            return {
                "success": True,
                "message": "Login successful",
                "token": token,
                "username": user['username'],
                "full_name": user.get('full_name', user['username']),
                "expires_at": expires_at.isoformat()
            }
        
        # Fallback for development
        if self.FALLBACK_USERS.get(username) == password:
            full_name = "IT Administrator" if username == "itadmin" else username
            token, expires_at = self.create_access_token({
                "username": username,
                "full_name": full_name,
                "user_id": 0
            })
            return {
                "success": True,
                "message": "Login successful (fallback)",
                "token": token,
                "username": username,
                "full_name": full_name,
                "expires_at": expires_at.isoformat()
            }
        
        return None