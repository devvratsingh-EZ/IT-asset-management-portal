"""Employee routes."""
from fastapi import APIRouter, HTTPException

from app.db.repositories.employee_repository import EmployeeRepository

router = APIRouter()
employee_repo = EmployeeRepository()


@router.get("")
async def get_employees():
    """Get all employees."""
    employees = employee_repo.get_all()
    return {"success": True, "data": employees}


@router.get("/{employee_id}")
async def get_employee(employee_id: str):
    """Get a single employee by ID."""
    employee = employee_repo.get_by_id(employee_id)
    if employee:
        return {"success": True, "data": employee}
    raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")