"""Summary routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db, db_manager
from app.db.repositories.summary_repository import SummaryRepository
from app.dependencies import get_current_user

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    db_status = "connected" if db_manager.test_connection() else "disconnected"
    return {"status": "healthy", "database": db_status}


@router.get("/summary")
async def get_summary(
    _current_user: dict = Depends(get_current_user),  # pylance: disable=unused-argument
    db: Session = Depends(get_db)
):
    """Get summary data from SummaryData view."""
    repo = SummaryRepository(db)
    data = repo.get_summary_data()
    return {"success": True, "data": data}