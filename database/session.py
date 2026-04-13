"""Database configuration and session management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
if settings.DATABASE_TYPE == "postgresql":
    DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
elif settings.DATABASE_TYPE == "mysql":
    DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
else:  # sqlite (default)
    DATABASE_URL = f"sqlite:///{settings.SQLITE_PATH}"

logger.info(f"Using database: {settings.DATABASE_TYPE}")

# Engine configuration
engine = create_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,  # Verify connections before using
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Session:
    """Get database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    from database.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")


def drop_db():
    """Drop all database tables (development only)"""
    from database.models import Base
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")
