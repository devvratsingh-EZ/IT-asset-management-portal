"""
Database session management with SQLAlchemy.
Implements Singleton pattern with connection pooling.
"""
import logging
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.config import settings

logger = logging.getLogger('db.session')


class DatabaseManager:
    """
    Singleton Database Manager with connection pooling.
    
    Ensures only one engine instance exists throughout the application lifecycle.
    Uses QueuePool for efficient connection management.
    """
    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._init_engine()

    def _init_engine(self):
        """Initialize the SQLAlchemy engine with connection pooling."""
        database_url = (
            f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASSWORD}"
            f"@{settings.DB_HOST}/{settings.DB_NAME}"
        )
        
        self._engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=5,              # Maintain 5 connections in pool
            max_overflow=10,          # Allow up to 10 additional connections
            pool_timeout=30,          # Wait 30s for connection before timeout
            pool_recycle=1800,        # Recycle connections after 30 minutes
            pool_pre_ping=True,       # Verify connection health before use
            echo=settings.DEBUG,      # Log SQL in debug mode
        )
        
        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        
        logger.info(
            f"Database engine initialized with connection pool "
            f"(pool_size=5, max_overflow=10)"
        )

    @property
    def engine(self):
        """Get the SQLAlchemy engine."""
        return self._engine

    @property
    def session_factory(self):
        """Get the session factory."""
        return self._session_factory

    def get_session(self) -> Session:
        """Create a new session from the pool."""
        return self._session_factory()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.
        Automatically handles commit/rollback and connection return to pool.
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def test_connection(self) -> bool:
        """Test database connectivity."""
        try:
            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database connection test: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"Database connection test: FAILED - {e}")
            return False

    def dispose(self):
        """Dispose of the connection pool (for shutdown)."""
        if self._engine:
            self._engine.dispose()
            logger.info("Database connection pool disposed")


# Global singleton instance
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    
    Usage in routes:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()