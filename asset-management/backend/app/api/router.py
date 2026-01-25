"""Main API router combining all route modules."""
from fastapi import APIRouter

from app.api.routes import auth, assets, employees, summary

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(employees.router, prefix="/employees", tags=["Employees"])
api_router.include_router(summary.router, tags=["Summary"])