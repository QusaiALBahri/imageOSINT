"""Database initialization utilities"""

from pathlib import Path
from database.session import Base, engine
from database.models import (
    UserAccount, APIKey, AnalysisJob, SearchHistory,
    CachedResult, LocationAnalysis, ImageMetadata
)
import logging

logger = logging.getLogger(__name__)


def init_db():
    """Initialize database"""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def drop_db():
    """Drop all database tables (DEVELOPMENT ONLY)"""
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All tables dropped")


def reset_db():
    """Reset database (drop and recreate)"""
    drop_db()
    init_db()
    logger.info("Database reset complete")


if __name__ == "__main__":
    init_db()
