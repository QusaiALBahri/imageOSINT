"""
Start FastAPI backend with Celery workers
Run this to start the complete backend stack
"""

import subprocess
import sys
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import fastapi
        import celery
        import sqlalchemy
        import redis
        import postgresql
        logger.info("✓ All dependencies installed")
        return True
    except ImportError as e:
        logger.error(f"✗ Missing dependency: {e}")
        logger.info("Install with: pip install -r requirements-backend.txt")
        return False


def check_services():
    """Check if Redis and PostgreSQL are running"""
    import socket
    
    # Check Redis
    try:
        socket.create_connection(("localhost", 6379), timeout=1)
        logger.info("✓ Redis running on localhost:6379")
    except:
        logger.warning("✗ Redis not found on localhost:6379")
        logger.info("  Start Redis: docker run -d -p 6379:6379 redis:7-alpine")
    
    # Check PostgreSQL
    try:
        socket.create_connection(("localhost", 5432), timeout=1)
        logger.info("✓ PostgreSQL running on localhost:5432")
    except:
        logger.warning("✗ PostgreSQL not found on localhost:5432")
        logger.info("  Start PostgreSQL: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=osint_password postgres:15")


def main():
    """Start backend stack"""
    
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║   OSINT Image Tool - Backend Stack Startup             ║
    ║   FastAPI + Celery + PostgreSQL + Redis               ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check services
    check_services()
    
    print("\n📋 Starting services...\n")
    
    # Initialize database
    try:
        from database.init_db import init_db
        logger.info("Initializing database...")
        init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization: {e}")
    
    # Start FastAPI
    logger.info("\n🚀 Starting FastAPI API server...")
    logger.info("   Access: http://localhost:8000")
    logger.info("   Docs: http://localhost:8000/api/docs")
    
    api_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "backend.server:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])
    
    print("\n" + "="*60)
    print("✓ Backend stack started successfully!")
    print("="*60)
    print("""
Available services:
- API Server: http://localhost:8000
- API Docs: http://localhost:8000/api/docs  
- Gradio Frontend: http://localhost:7860 (app_backend.py)

Start Celery Workers separately:
  Terminal 1: celery -A tasks.celery worker
  Terminal 2: celery -A tasks.celery beat
  Terminal 3: python app_backend.py (Gradio)

Or use Docker Compose:
  docker-compose up

Press Ctrl+C to stop
    """)
    
    try:
        api_process.wait()
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        api_process.terminate()
        sys.exit(0)


if __name__ == "__main__":
    main()
