"""Application configuration."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Database
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_USER: str = os.getenv('DB_USER', 'root')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'root')
    DB_NAME: str = os.getenv('DB_NAME', 'ITAssetData')
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = int(os.getenv('JWT_EXPIRY_HOURS', 24))
    
    # Server
    SERVER_HOST: str = os.getenv('SERVER_HOST', '127.0.0.1')
    SERVER_PORT: int = int(os.getenv('SERVER_PORT', 8000))
    DEBUG: bool = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Frontend
    FRONTEND_DIST_PATH: str = os.getenv('FRONTEND_DIST_PATH', '../dist')
    
    @property
    def db_config(self) -> dict:
        return {
            'host': self.DB_HOST,
            'user': self.DB_USER,
            'password': self.DB_PASSWORD,
            'database': self.DB_NAME
        }


settings = Settings()