"""Employee repository."""
import logging

from app.db.repositories.base import BaseRepository

logger = logging.getLogger('db.employee_repository')


class EmployeeRepository(BaseRepository):
    """Repository for employee operations."""
    
    def get_all(self) -> dict:
        """Get all employees."""
        logger.info("FETCH: Getting all employees")
        
        rows = self._execute_query("""
            SELECT NameId, Name, Department, Email
            FROM PeopleData
            ORDER BY Name
        """)
        
        if not rows:
            return {}
        
        result = {}
        for row in rows:
            result[row['NameId']] = {
                'name': row['Name'],
                'department': row['Department'],
                'email': row['Email']
            }
        
        logger.info(f"FETCH: Retrieved {len(result)} employees")
        return result
    
    def get_by_id(self, employee_id: str) -> dict:
        """Get a single employee by ID."""
        logger.info(f"FETCH: Getting employee '{employee_id}'")
        
        row = self._execute_query("""
            SELECT NameId, Name, Department, Email
            FROM PeopleData
            WHERE NameId = %s
        """, (employee_id,), fetch_one=True)
        
        if row:
            return {
                'name': row['Name'],
                'department': row['Department'],
                'email': row['Email']
            }
        return None