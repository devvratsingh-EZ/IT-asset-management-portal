"""Authentication repository using SQLAlchemy ORM."""
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository
from app.db.models import AuthData
from datetime import datetime, timezone


logger = logging.getLogger('db.auth_repository')


class AuthRepository(BaseRepository[AuthData]):
    """Repository for authentication operations using SQLAlchemy ORM."""
    
    def __init__(self, session: Session):
        super().__init__(AuthData, session)
    
    def verify_user(self, username: str, password: str) -> Optional[dict]:
        """Verify user credentials against the AuthData table."""
        logger.info(f"AUTH REQUEST: Verifying user '{username}'")
        
        stmt = select(AuthData).where(
            AuthData.username == username,
            AuthData.password == password
        )
        user = self.session.scalars(stmt).first()
        
        if user:
            logger.info(f"AUTH REQUEST: User '{username}' authenticated successfully")
            return {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email
            }
        
        logger.warning(f"AUTH REQUEST: Authentication failed for user '{username}'")
        return None
    
    # ADD these methods inside AuthRepository class (after verify_user method):

    def update_refresh_token(self, user_id: int, refresh_token: str, expires_at: datetime) -> bool:
        """Store refresh token in database."""
        try:
            stmt = select(AuthData).where(AuthData.id == user_id)
            user = self.session.scalars(stmt).first()
            if user:
                user.refresh_token = refresh_token
                user.refresh_token_expires_at = expires_at
                self.session.commit()
                logger.info(f"Refresh token updated for user_id={user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update refresh token: {e}")
            self.session.rollback()
            return False

    def validate_refresh_token(self, refresh_token: str) -> Optional[dict]:
        """Validate refresh token and return user if valid."""
        stmt = select(AuthData).where(
            AuthData.refresh_token == refresh_token
        )
        user = self.session.scalars(stmt).first()
        
        if not user:
            logger.warning("Refresh token not found in database")
            return None
        
        if user.refresh_token_expires_at is None:
            logger.warning("Refresh token has no expiry set")
            return None
            
        # Handle timezone-aware comparison
        expires_at = user.refresh_token_expires_at
        now = datetime.now(timezone.utc) if expires_at.tzinfo else datetime.utcnow()
        
        if expires_at < now:
            logger.warning(f"Refresh token expired for user_id={user.id}")
            return None
        
        logger.info(f"Refresh token validated for user_id={user.id}")
        return {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email
        }

    def invalidate_refresh_token(self, user_id: int) -> bool:
        """Invalidate refresh token (logout)."""
        try:
            stmt = select(AuthData).where(AuthData.id == user_id)
            user = self.session.scalars(stmt).first()
            if user:
                user.refresh_token = None
                user.refresh_token_expires_at = None
                self.session.commit()
                logger.info(f"Refresh token invalidated for user_id={user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to invalidate refresh token: {e}")
            self.session.rollback()
            return False