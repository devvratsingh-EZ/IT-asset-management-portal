"""
Database connection management.
This module now wraps the SQLAlchemy session manager for backwards compatibility.
"""
import logging
from contextlib import contextmanager

from app.db.session import db_manager, get_db

logger = logging.getLogger('db.connection')


def get_connection(with_database: bool = True):
    """
    Legacy function - now returns SQLAlchemy session.
    Maintained for backwards compatibility during migration.
    
    Note: with_database parameter is ignored as SQLAlchemy
    always connects to the configured database.
    """
    logger.warning(
        "get_connection() is deprecated. Use db_manager.get_session() or "
        "the get_db dependency instead."
    )
    return db_manager.get_session()


@contextmanager
def get_db_cursor(dictionary: bool = True):
    """
    Legacy context manager - now uses SQLAlchemy session.
    Maintained for backwards compatibility.
    """
    logger.warning(
        "get_db_cursor() is deprecated. Use db_manager.session_scope() instead."
    )
    with db_manager.session_scope() as session:
        yield session, session


def test_connection() -> bool:
    """Test if database connection is working."""
    return db_manager.test_connection()