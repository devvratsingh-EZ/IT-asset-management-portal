"""Database connection management."""
import logging
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

from app.config import settings

logger = logging.getLogger('db.connection')


def get_connection(with_database: bool = True):
    """Create and return a MySQL database connection."""
    try:
        if with_database:
            connection = mysql.connector.connect(**settings.db_config)
        else:
            config = {k: v for k, v in settings.db_config.items() if k != 'database'}
            connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            logger.debug(f"Connected to MySQL {'database: ' + settings.DB_NAME if with_database else 'server'}")
            return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return None


@contextmanager
def get_db_cursor(dictionary: bool = True):
    """Context manager for database operations."""
    connection = get_connection()
    if not connection:
        yield None, None
        return
    
    try:
        cursor = connection.cursor(dictionary=dictionary)
        yield connection, cursor
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def test_connection() -> bool:
    """Test if database connection is working."""
    connection = get_connection()
    if connection and connection.is_connected():
        logger.debug("Database connection test: SUCCESS")
        connection.close()
        return True
    logger.debug("Database connection test: FAILED")
    return False