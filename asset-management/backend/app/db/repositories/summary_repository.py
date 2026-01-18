"""Summary repository."""
import logging

from app.db.repositories.base import BaseRepository

logger = logging.getLogger('db.summary_repository')


class SummaryRepository(BaseRepository):
    """Repository for summary operations."""
    
    def get_summary_data(self) -> list:
        """Get summary data from SummaryData view."""
        logger.info("FETCH: Getting summary data")
        
        results = self._execute_query("""
            SELECT AssetType, Department, Brand, Model, Count
            FROM SummaryData
            ORDER BY AssetType, Department, Brand, Model
        """)
        
        logger.info(f"FETCH: Retrieved {len(results) if results else 0} summary rows")
        return results or []