"""Entry point for the application."""
import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"\nStarting server at http://{settings.SERVER_HOST}:{settings.SERVER_PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG
    )