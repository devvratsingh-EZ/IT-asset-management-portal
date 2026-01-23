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
    
   # REPLACE JWT section (lines 17-20) with:
    # JWT
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_EXPIRY_HOURS: int = int(os.getenv('JWT_EXPIRY_HOURS', 24))
    REFRESH_TOKEN_EXPIRE_HOURS: int = 24
    
    
    # Server
    SERVER_HOST: str = os.getenv('SERVER_HOST', '127.0.0.1')
    SERVER_PORT: int = int(os.getenv('SERVER_PORT', 8000))
    DEBUG: bool = os.getenv('DEBUG', 'True').lower() == 'true'
    # Note: Set DEBUG=False in production .env to enable HTTPS-only cookies
    
    # Frontend
    FRONTEND_DIST_PATH: str = os.getenv('FRONTEND_DIST_PATH', '../dist')
    
    @property
    def db_config(self) -> dict:
        """Legacy config for backwards compatibility."""
        return {
            'host': self.DB_HOST,
            'user': self.DB_USER,
            'password': self.DB_PASSWORD,
            'database': self.DB_NAME
        }
    
    @property
    def database_url(self) -> str:
        """SQLAlchemy database URL."""
        return (
            f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}/{self.DB_NAME}"
        )


settings = Settings()