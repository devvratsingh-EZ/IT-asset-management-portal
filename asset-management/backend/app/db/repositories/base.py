"""Base repository class."""
import logging
from mysql.connector import Error

from app.db.connection import get_connection

logger = logging.getLogger('db.repository')


class BaseRepository:
    """Base class for all repositories."""
    
    def _get_connection(self):
        return get_connection()
    
    def _execute_query(self, query: str, params: tuple = None, fetch_one: bool = False):
        """Execute a query and return results."""
        connection = self._get_connection()
        if not connection:
            logger.error("Failed to get database connection")
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
        except Error as e:
            logger.error(f"Query error: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()