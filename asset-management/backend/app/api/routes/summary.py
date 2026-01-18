"""Summary routes."""
from fastapi import APIRouter

from app.db.repositories.summary_repository import SummaryRepository
from app.db.connection import test_connection

router = APIRouter()
summary_repo = SummaryRepository()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    db_status = "connected" if test_connection() else "disconnected"
    return {"status": "healthy", "database": db_status}


@router.get("/summary")
async def get_summary():
    """Get summary data from SummaryData view."""
    data = summary_repo.get_summary_data()
    return {"success": True, "data": data}