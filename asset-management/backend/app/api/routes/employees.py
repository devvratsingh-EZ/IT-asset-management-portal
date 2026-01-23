"""Employee routes."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.repositories.employee_repository import EmployeeRepository
from app.dependencies import get_current_user

router = APIRouter()


@router.get("")
async def get_employees(
    _current_user: dict = Depends(get_current_user),  # pylance: disable=unused-argument
    db: Session = Depends(get_db)
):
    """Get all employees."""
    repo = EmployeeRepository(db)
    employees = repo.get_all()
    return {"success": True, "data": employees}


@router.get("/{employee_id}")
async def get_employee(
    employee_id: str,
    _current_user: dict = Depends(get_current_user),  # pylance: disable=unused-argument
    db: Session = Depends(get_db)
):
    """Get a single employee by ID."""
    repo = EmployeeRepository(db)
    employee = repo.get_by_id(employee_id)
    if employee:
        return {"success": True, "data": employee}
    raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")