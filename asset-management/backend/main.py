"""
IT Asset Management - FastAPI Backend Server
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
import os
import logging
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()

from DB_utils import (
    init_database, verify_user, test_connection,
    get_asset_types, get_all_specifications, get_specifications_for_type,
    get_all_employees, get_employee_by_id,
    create_asset, get_all_assets, get_asset_by_id,
    get_assignment_history, get_all_assignment_history,
    update_asset_assignment, get_summary_data
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('main')

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.getenv('JWT_EXPIRY_HOURS', 24))

# Security
security = HTTPBearer()

# Frontend path
FRONTEND_DIST_PATH = os.getenv('FRONTEND_DIST_PATH', '../dist')
FRONTEND_DIST_ABS = os.path.abspath(os.path.join(os.path.dirname(__file__), FRONTEND_DIST_PATH))


# ============== Pydantic Models ==============

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    token: str = None
    username: str = None
    full_name: str = None
    expires_at: str = None


class TokenValidationResponse(BaseModel):
    valid: bool
    username: str = None
    full_name: str = None
    message: str = None


class AssetCreateRequest(BaseModel):
    serialNumber: str
    assetType: str
    brand: str
    model: str
    specifications: Dict[str, str] = {}
    purchaseDate: Optional[str] = None
    purchaseCost: float = 0
    gstPaid: float = 0
    warrantyExpiry: Optional[str] = None
    assignedTo: Optional[str] = None
    repairStatus: bool = False


class AssetUpdateRequest(BaseModel):
    assignedTo: Optional[str] = None
    repairStatus: bool = False


# ============== JWT Functions ==============

def create_access_token(data: dict) -> tuple:
    """Create JWT token with expiration."""
    expires_at = datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    to_encode = data.copy()
    to_encode.update({"exp": expires_at})
    token = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    logger.info(f"JWT TOKEN: Created token for user '{data.get('username')}', expires at {expires_at}")
    return token, expires_at


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        logger.info(f"JWT TOKEN: Verified token for user '{payload.get('username')}'")
        return payload
    except JWTError as e:
        logger.warning(f"JWT TOKEN: Verification failed - {str(e)}")
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency to get current authenticated user."""
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


# ============== Lifespan ==============

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "="*50)
    print("Starting IT Asset Management Server")
    print("="*50)
    
    print("\nInitializing Database...")
    if init_database():
        print("Database ready!")
    else:
        print("Database initialization failed - running in offline mode")
    
    print(f"\nFrontend path: {FRONTEND_DIST_ABS}")
    print(f"JWT Expiry: {JWT_EXPIRY_HOURS} hours")
    print("="*50 + "\n")
    
    yield
    print("Server shutting down...")


app = FastAPI(
    title="IT Asset Management API",
    description="Backend API for IT Asset Management System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Health Check ==============

@app.get("/api/health")
async def health_check():
    db_status = "connected" if test_connection() else "disconnected"
    return {"status": "healthy", "database": db_status}


# ============== Auth API Routes ==============

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate and return JWT token."""
    logger.info(f"LOGIN REQUEST: User '{request.username}'")
    
    user = verify_user(request.username, request.password)
    
    if user:
        token, expires_at = create_access_token({
            "username": user['username'],
            "full_name": user.get('full_name', user['username']),
            "user_id": user['id']
        })
        return LoginResponse(
            success=True,
            message="Login successful",
            token=token,
            username=user['username'],
            full_name=user.get('full_name', user['username']),
            expires_at=expires_at.isoformat()
        )
    
    # Fallback for development
    FALLBACK_USERS = {"itadmin": "pass123", "techlead": "admin456"}
    if FALLBACK_USERS.get(request.username) == request.password:
        token, expires_at = create_access_token({
            "username": request.username,
            "full_name": "IT Administrator" if request.username == "itadmin" else request.username,
            "user_id": 0
        })
        return LoginResponse(
            success=True,
            message="Login successful (fallback)",
            token=token,
            username=request.username,
            full_name="IT Administrator" if request.username == "itadmin" else request.username,
            expires_at=expires_at.isoformat()
        )
    
    logger.warning(f"LOGIN FAILED: User '{request.username}'")
    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.get("/api/auth/verify", response_model=TokenValidationResponse)
async def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify if token is still valid."""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload:
        return TokenValidationResponse(
            valid=True,
            username=payload.get('username'),
            full_name=payload.get('full_name'),
            message="Token is valid"
        )
    
    return TokenValidationResponse(valid=False, message="Token expired or invalid")


# ============== Asset Type API Routes ==============

@app.get("/api/asset-types")
async def get_asset_types_api():
    """Get all asset types."""
    types = get_asset_types()
    if types:
        return {"success": True, "data": [t['type_name'] for t in types]}
    # Fallback
    return {
        "success": True,
        "data": ["Laptop", "Desktop", "Monitor", "Keyboard", "Mouse", "Printer",
                 "Scanner", "Server", "Router", "Switch", "UPS", "Projector",
                 "Tablet", "Mobile Phone", "Headset", "Webcam", "External Hard Drive", "Other"],
        "source": "fallback"
    }


@app.get("/api/asset-specifications")
async def get_all_specifications_api():
    """Get all specifications grouped by asset type."""
    specs = get_all_specifications()
    if specs:
        return {"success": True, "data": specs}
    return {"success": False, "data": {}, "message": "Database unavailable"}


@app.get("/api/asset-specifications/{type_name}")
async def get_specifications_for_type_api(type_name: str):
    """Get specifications for a specific asset type."""
    specs = get_specifications_for_type(type_name)
    if specs:
        return {
            "success": True,
            "data": {"fields": [{"key": s['field_key'], "label": s['field_label'], "placeholder": s['placeholder']} for s in specs]}
        }
    return {"success": False, "data": {"fields": []}, "message": f"No specifications found for {type_name}"}


# ============== Employee API Routes ==============

@app.get("/api/employees")
async def get_employees_api():
    """Get all employees from PeopleData table."""
    employees = get_all_employees()
    return {"success": True, "data": employees}


@app.get("/api/employees/{employee_id}")
async def get_employee_api(employee_id: str):
    """Get a single employee by ID."""
    employee = get_employee_by_id(employee_id)
    if employee:
        return {"success": True, "data": employee}
    raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")


# ============== Asset API Routes ==============

@app.get("/api/assets")
async def get_assets_api():
    """Get all assets."""
    assets = get_all_assets()
    return {"success": True, "data": assets}


@app.get("/api/assets/{asset_id}")
async def get_asset_api(asset_id: str):
    """Get a single asset by ID."""
    asset = get_asset_by_id(asset_id)
    if asset:
        return {"success": True, "data": asset}
    raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")


@app.post("/api/assets")
async def create_asset_api(request: AssetCreateRequest):
    """Create a new asset."""
    logger.info(f"CREATE ASSET API: Received request for '{request.serialNumber}'")
    logger.info(f"CREATE ASSET API: Serial='{request.serialNumber}', Type='{request.assetType}'")
    
    try:
        result = create_asset(
            asset_data={
                'serialNumber': request.serialNumber,
                'assetType': request.assetType,
                'brand': request.brand,
                'model': request.model,
                'purchaseDate': request.purchaseDate,
                'purchaseCost': request.purchaseCost,
                'gstPaid': request.gstPaid,
                'warrantyExpiry': request.warrantyExpiry,
                'assignedTo': request.assignedTo,
                'repairStatus': request.repairStatus
            },
            specifications=request.specifications
        )
        return result
    except Exception as e:
        logger.error(f"CREATE ASSET API: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/assets/{asset_id}")
async def update_asset_api(asset_id: str, request: AssetUpdateRequest):
    """Update asset assignment and repair status."""
    logger.info(f"UPDATE ASSET API: Updating '{asset_id}'")
    
    try:
        result = update_asset_assignment(
            asset_id=asset_id,
            new_employee_id=request.assignedTo,
            repair_status=request.repairStatus
        )
        return result
    except Exception as e:
        logger.error(f"UPDATE ASSET API: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Assignment History API Routes ==============

@app.get("/api/assignment-history")
async def get_all_history_api():
    """Get all assignment history grouped by asset."""
    history = get_all_assignment_history()
    return {"success": True, "data": history}


@app.get("/api/assignment-history/{asset_id}")
async def get_history_api(asset_id: str):
    """Get assignment history for a specific asset."""
    history = get_assignment_history(asset_id)
    return {"success": True, "data": history}



# ============== Summary API Routes ==============

@app.get("/api/summary")
async def get_summary_api():
    """Get summary data from SummaryData view."""
    data = get_summary_data()
    return {"success": True, "data": data}



# ============== Frontend Routes ==============

if os.path.exists(os.path.join(FRONTEND_DIST_ABS, 'assets')):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST_ABS, 'assets')), name="assets")


async def serve_frontend():
    index_path = os.path.join(FRONTEND_DIST_ABS, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Frontend not built. Run: npm run build</h1>", status_code=200)


@app.get("/", response_class=HTMLResponse)
async def root():
    return await serve_frontend()

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return await serve_frontend()

@app.get("/asset_addition", response_class=HTMLResponse)
async def asset_addition_page():
    return await serve_frontend()

@app.get("/asset_assignment", response_class=HTMLResponse)
async def asset_assignment_page():
    return await serve_frontend()

@app.get("/summary", response_class=HTMLResponse)
async def summary_page():
    return await serve_frontend()

@app.get("/vite.svg")
async def vite_svg():
    svg_path = os.path.join(FRONTEND_DIST_ABS, 'vite.svg')
    if os.path.exists(svg_path):
        return FileResponse(svg_path)
    raise HTTPException(status_code=404)

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    file_path = os.path.join(FRONTEND_DIST_ABS, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    return await serve_frontend()


if __name__ == "__main__":
    import uvicorn
    host = os.getenv('SERVER_HOST', '127.0.0.1')
    port = int(os.getenv('SERVER_PORT', 8000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    print(f"\nStarting server at http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=debug)