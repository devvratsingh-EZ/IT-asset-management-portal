"""Frontend serving routes."""
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse

from app.config import settings

router = APIRouter()

FRONTEND_DIST_ABS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..', settings.FRONTEND_DIST_PATH)
)


async def serve_frontend():
    """Serve the frontend index.html."""
    index_path = os.path.join(FRONTEND_DIST_ABS, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Frontend not built. Run: npm run build</h1>", status_code=200)


@router.get("/", response_class=HTMLResponse)
async def root():
    return await serve_frontend()


@router.get("/login", response_class=HTMLResponse)
async def login_page():
    return await serve_frontend()


@router.get("/asset_addition", response_class=HTMLResponse)
async def asset_addition_page():
    return await serve_frontend()


@router.get("/asset_assignment", response_class=HTMLResponse)
async def asset_assignment_page():
    return await serve_frontend()


@router.get("/summary", response_class=HTMLResponse)
async def summary_page():
    return await serve_frontend()


@router.get("/delete_asset", response_class=HTMLResponse)
async def delete_asset_page():
    return await serve_frontend()


@router.get("/vite.svg")
async def vite_svg():
    svg_path = os.path.join(FRONTEND_DIST_ABS, 'vite.svg')
    if os.path.exists(svg_path):
        return FileResponse(svg_path)
    raise HTTPException(status_code=404)


@router.get("/{full_path:path}")
async def catch_all(full_path: str):
    file_path = os.path.join(FRONTEND_DIST_ABS, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    return await serve_frontend()