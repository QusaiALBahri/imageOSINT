"""Core configuration settings"""

from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "OSINT Image Tool"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    
    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_PREFIX: str = "/api"
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:7860",
        "http://127.0.0.1:7860",
        "http://127.0.0.1:3000",
    ]
    
    # Database
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "sqlite")  # sqlite, postgresql, mysql
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "osint_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "osint_password")
    DB_NAME: str = os.getenv("DB_NAME", "osint_db")
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "database/osint.db")
    
    # Redis/Cache
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    
    # Celery
    CELERY_BROKER: str = os.getenv("CELERY_BROKER", "redis://localhost:6379/1")
    CELERY_BACKEND: str = os.getenv("CELERY_BACKEND", "redis://localhost:6379/2")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "jwt-secret-key")
    JWT_ALGORITHM: str = "HS256"
    
    # File Upload
    UPLOADS_DIR: str = os.getenv("UPLOADS_DIR", "uploads")
    OUTPUTS_DIR: str = os.getenv("OUTPUTS_DIR", "outputs")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "104857600"))  # 100MB
    ALLOWED_EXTENSIONS: list = ["jpg", "jpeg", "png", "gif", "webp", "bmp"]
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    LOG_DIR: str = "logs"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DELAY: float = float(os.getenv("RATE_LIMIT_DELAY", "1.0"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Search Engines
    GOOGLE_ENABLED: bool = True
    BING_ENABLED: bool = True
    YANDEX_ENABLED: bool = True
    MAX_RESULTS_PER_ENGINE: int = 10
    
    # Email
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    # API Keys (Optional)
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_SEARCH_ENGINE_ID: str = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
    
    # Monitoring
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    PROMETHEUS_ENABLED: bool = os.getenv("PROMETHEUS_ENABLED", "False") == "True"
    
    # Worker
    WORKER_PROCESSES: int = int(os.getenv("WORKER_PROCESSES", "4"))
    WORKER_THREADS: int = int(os.getenv("WORKER_THREADS", "2"))
    USER_AGENTS: list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
