"""Employee repository using SQLAlchemy ORM."""
import logging
from typing import Optional, Dict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository
from app.db.models import PeopleData

logger = logging.getLogger('db.employee_repository')


class EmployeeRepository(BaseRepository[PeopleData]):
    """Repository for employee operations using SQLAlchemy ORM."""
    
    def __init__(self, session: Session):
        super().__init__(PeopleData, session)
    
    def get_all(self) -> Dict[str, dict]:
        """Get all employees."""
        logger.info("FETCH: Getting all employees")
        
        stmt = select(PeopleData).order_by(PeopleData.Name)
        employees = self.session.scalars(stmt).all()
        
        result = {
            emp.NameId: {
                'name': emp.Name,
                'department': emp.Department,
                'email': emp.Email
            }
            for emp in employees
        }
        
        logger.info(f"FETCH: Retrieved {len(result)} employees")
        return result
    
    def get_by_id(self, employee_id: str) -> Optional[dict]:
        """Get a single employee by ID."""
        logger.info(f"FETCH: Getting employee '{employee_id}'")
        
        employee = self.session.get(PeopleData, employee_id)
        
        if employee:
            return {
                'name': employee.Name,
                'department': employee.Department,
                'email': employee.Email
            }
        return None