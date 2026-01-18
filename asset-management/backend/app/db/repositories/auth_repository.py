"""Authentication repository."""
import logging
from mysql.connector import Error

from app.db.repositories.base import BaseRepository

logger = logging.getLogger('db.auth_repository')


class AuthRepository(BaseRepository):
    """Repository for authentication operations."""
    
    def verify_user(self, username: str, password: str) -> dict:
        """Verify user credentials against the AuthData table."""
        logger.info(f"AUTH REQUEST: Verifying user '{username}'")
        
        query = """
        SELECT id, username, full_name, email
        FROM AuthData
        WHERE username = %s AND password = %s
        """
        user = self._execute_query(query, (username, password), fetch_one=True)
        
        if user:
            logger.info(f"AUTH REQUEST: User '{username}' authenticated successfully")
        else:
            logger.warning(f"AUTH REQUEST: Authentication failed for user '{username}'")
        
        return user