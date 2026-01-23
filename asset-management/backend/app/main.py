"""FastAPI application initialization."""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.router import api_router
from app.api.routes.frontend import router as frontend_router
from app.db.init_db import init_database
from app.db.session import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('main')

FRONTEND_DIST_ABS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', settings.FRONTEND_DIST_PATH)
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("\n" + "=" * 50)
    print("Starting IT Asset Management Server")
    print("=" * 50)
    
    print("\nInitializing Database...")
    if init_database():
        print("Database ready!")
        print(f"Connection pool: pool_size=5, max_overflow=10")
    else:
        print("Database initialization failed - running in offline mode")
    
    print(f"\nFrontend path: {FRONTEND_DIST_ABS}")
    print(f"JWT Expiry: {settings.JWT_EXPIRY_HOURS} hours")
    print("=" * 50 + "\n")
    
    yield
    
    # Cleanup: dispose connection pool on shutdown
    print("Disposing database connection pool...")
    db_manager.dispose()
    print("Server shutting down...")


app = FastAPI(
    title="IT Asset Management API",
    description="Backend API for IT Asset Management System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
assets_path = os.path.join(FRONTEND_DIST_ABS, 'assets')
if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

# Include routers
app.include_router(api_router, prefix="/api")
app.include_router(frontend_router)