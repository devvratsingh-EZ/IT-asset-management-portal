"""Database initialization using SQLAlchemy."""
import logging
from sqlalchemy import text

from app.config import settings
from app.db.session import db_manager
from app.db.models import Base, AssetIdCounter

logger = logging.getLogger('db.init')


def init_database() -> bool:
    """Initialize the database and create required tables using SQLAlchemy."""
    logger.info("Initializing database with SQLAlchemy...")
    
    try:
        engine = db_manager.engine
        
        # Create all tables defined in models
        Base.metadata.create_all(bind=engine)
        logger.info("All tables created/verified")
        
        # Initialize AssetIdCounter if empty
        with db_manager.session_scope() as session:
            counter = session.get(AssetIdCounter, 1)
            if not counter:
                counter = AssetIdCounter(id=1, current_value=1000)
                session.add(counter)
                logger.info("AssetIdCounter initialized")
            
            # Create the SummaryData view
            session.execute(text("""
                CREATE OR REPLACE VIEW SummaryData AS
                SELECT
                    a.AssetType,
                    COALESCE(p.Department, 'Not Assigned') AS Department,
                    a.Brand,
                    a.Model,
                    COUNT(*) AS Count
                FROM AssetData a
                LEFT JOIN PeopleData p ON a.AssignedTo = p.NameId
                GROUP BY a.AssetType, Department, a.Brand, a.Model
                ORDER BY a.AssetType
            """))
            logger.info("View 'SummaryData' ensured")
        
        logger.info("Database initialization complete")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False