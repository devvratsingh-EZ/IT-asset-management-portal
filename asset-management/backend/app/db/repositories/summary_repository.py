"""Summary repository using SQLAlchemy ORM."""
import logging
from typing import List

from sqlalchemy import select, func, text
from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository
from app.db.models import AssetData, PeopleData

logger = logging.getLogger('db.summary_repository')


class SummaryRepository:
    """Repository for summary operations using SQLAlchemy ORM."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_summary_data(self) -> List[dict]:
        """Get summary data (replaces the SQL View query)."""
        logger.info("FETCH: Getting summary data")
        
        # Query equivalent to the SummaryData view
        stmt = (
            select(
                AssetData.AssetType,
                func.coalesce(PeopleData.Department, 'Not Assigned').label('Department'),
                AssetData.Brand,
                AssetData.Model,
                func.count().label('Count')
            )
            .outerjoin(PeopleData, AssetData.AssignedTo == PeopleData.NameId)
            .group_by(
                AssetData.AssetType,
                func.coalesce(PeopleData.Department, 'Not Assigned'),
                AssetData.Brand,
                AssetData.Model
            )
            .order_by(AssetData.AssetType)
        )
        
        results = self.session.execute(stmt).all()
        
        data = [
            {
                'AssetType': row.AssetType,
                'Department': row.Department,
                'Brand': row.Brand,
                'Model': row.Model,
                'Count': row.Count
            }
            for row in results
        ]
        
        logger.info(f"FETCH: Retrieved {len(data)} summary rows")
        return data