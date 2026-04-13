"""
FastAPI Backend Server for OSINT Image Tool
Provides REST API endpoints for image analysis and result management
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.models import AnalysisJob, UserAccount, CachedResult, SearchHistory
from database.session import get_db, engine, Base
from database.schemas import (
    AnalysisRequest, AnalysisResponse, JobStatus, 
    UserCreate, UserLogin, TokenResponse
)
from core.auth import create_access_token, verify_token, hash_password, verify_password
from core.config import settings
from tasks.celery_tasks import (
    process_image_analysis,
    reverse_image_search_task,
    extract_metadata_task,
    location_analysis_task,
    maps_scraping_task
)
from core.cache import cache_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="OSINT Image Tool API",
    description="Backend API for reverse image search, metadata extraction, and geolocation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account"""
    
    # Check if user exists
    existing_user = db.query(UserAccount).filter(
        UserAccount.email == user.email
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = hash_password(user.password)
    new_user = UserAccount(
        email=user.email,
        username=user.username,
        password_hash=hashed_password,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate token
    access_token = create_access_token(data={"sub": new_user.id})
    
    logger.info(f"New user registered: {user.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user.id,
        "email": new_user.email
    }


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login user account"""
    
    db_user = db.query(UserAccount).filter(
        UserAccount.email == user.email
    ).first()
    
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": db_user.id})
    
    logger.info(f"User logged in: {user.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "email": db_user.email
    }


# ============================================================================
# Analysis Endpoints
# ============================================================================

@app.post("/api/analyze", response_model=AnalysisResponse)
async def submit_analysis(
    file: UploadFile = File(...),
    analysis_types: str = Query("all"),  # all, metadata, search, location, maps
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_token)
):
    """
    Submit an image for analysis
    
    - **file**: Image file to analyze
    - **analysis_types**: Types of analysis to perform (all, metadata, search, location, maps)
    - **Returns**: Job ID and status
    """
    
    try:
        # Validate file
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = Path(settings.UPLOADS_DIR) / f"{file_id}_{file.filename}"
        
        # Save file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        logger.info(f"File uploaded: {file_id}")
        
        # Create analysis job
        job = AnalysisJob(
            job_id=file_id,
            user_id=user_id,
            file_path=str(file_path),
            filename=file.filename,
            analysis_types=analysis_types,
            status="pending",
            progress=0,
            created_at=datetime.utcnow()
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Submit background task
        background_tasks.add_task(
            process_image_analysis,
            job_id=file_id,
            file_path=str(file_path),
            analysis_types=analysis_types,
            user_id=user_id
        )
        
        logger.info(f"Analysis job created: {file_id}")
        
        return AnalysisResponse(
            job_id=file_id,
            status="pending",
            progress=0,
            message="Analysis job submitted successfully"
        )
    
    except Exception as e:
        logger.error(f"Analysis submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analyze/{job_id}")
async def get_analysis_status(
    job_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_token)
):
    """Get analysis job status and results"""
    
    job = db.query(AnalysisJob).filter(
        AnalysisJob.job_id == job_id,
        AnalysisJob.user_id == user_id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    response = {
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "filename": job.filename,
        "created_at": job.created_at.isoformat(),
    }
    
    if job.status == "completed":
        response["results"] = job.results
        response["completed_at"] = job.completed_at.isoformat() if job.completed_at else None
    
    elif job.status == "failed":
        response["error"] = job.error_message
    
    return response


@app.get("/api/analyze/{job_id}/results")
async def get_analysis_results(
    job_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_token)
):
    """Get full analysis results"""
    
    job = db.query(AnalysisJob).filter(
        AnalysisJob.job_id == job_id,
        AnalysisJob.user_id == user_id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job status is {job.status}, not completed"
        )
    
    return {
        "job_id": job.job_id,
        "results": job.results,
        "filename": job.filename,
        "analysis_types": job.analysis_types,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None
    }


# ============================================================================
# Metadata Endpoints
# ============================================================================

@app.post("/api/metadata/extract")
async def extract_metadata(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_token)
):
    """Extract metadata from image"""
    
    try:
        # Save file
        file_id = str(uuid.uuid4())
        file_path = Path(settings.UPLOADS_DIR) / f"{file_id}_{file.filename}"
        
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Submit task
        task = extract_metadata_task.delay(str(file_path))
        
        return {
            "task_id": task.id,
            "status": "processing",
            "message": "Metadata extraction started"
        }
    
    except Exception as e:
        logger.error(f"Metadata extraction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Reverse Image Search Endpoints
# ============================================================================

@app.post("/api/search/reverse")
async def reverse_search(
    file: UploadFile = File(...),
    engines: str = Query("google,bing,yandex"),
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_token)
):
    """Perform reverse image search"""
    
    try:
        file_id = str(uuid.uuid4())
        file_path = Path(settings.UPLOADS_DIR) / f"{file_id}_{file.filename}"
        
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Log search
        search = SearchHistory(
            user_id=user_id,
            image_filename=file.filename,
            search_engines=engines,
            created_at=datetime.utcnow()
        )
        db.add(search)
        db.commit()
        
        # Submit task
        task = reverse_image_search_task.delay(str(file_path), engines)
        
        return {
            "task_id": task.id,
            "status": "processing",
            "search_id": search.id,
            "message": f"Searching {engines}"
        }
    
    except Exception as e:
        logger.error(f"Reverse search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/history")
async def get_search_history(
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_token)
):
    """Get user search history"""
    
    searches = db.query(SearchHistory).filter(
        SearchHistory.user_id == user_id
    ).order_by(desc(SearchHistory.created_at)).limit(limit).all()
    
    return {
        "total": len(searches),
        "searches": [
            {
                "id": s.id,
                "image": s.image_filename,
                "engines": s.search_engines,
                "created_at": s.created_at.isoformat()
            }
            for s in searches
        ]
    }


# ============================================================================
# Location Endpoints
# ============================================================================

@app.post("/api/location/analyze")
async def analyze_location(
    latitude: float = Query(...),
    longitude: float = Query(...),
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_token)
):
    """Analyze location by GPS coordinates"""
    
    try:
        # Check cache first
        cache_key = f"location:{latitude}:{longitude}"
        cached = cache_manager.get(cache_key)
        
        if cached:
            logger.info(f"Cache hit for location: {latitude}, {longitude}")
            return {"cached": True, "results": cached}
        
        # Submit task
        task = location_analysis_task.delay(latitude, longitude)
        
        return {
            "task_id": task.id,
            "status": "processing",
            "location": {"latitude": latitude, "longitude": longitude}
        }
    
    except Exception as e:
        logger.error(f"Location analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/maps/nearby")
async def get_nearby_places(
    latitude: float = Query(...),
    longitude: float = Query(...),
    place_type: str = Query("restaurant"),
    radius: int = Query(1000),
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_token)
):
    """Get nearby places from Google Maps"""
    
    try:
        # Check cache
        cache_key = f"maps:{latitude}:{longitude}:{place_type}"
        cached = cache_manager.get(cache_key)
        
        if cached:
            return {"cached": True, "results": cached}
        
        # Submit task
        task = maps_scraping_task.delay(latitude, longitude, place_type, radius)
        
        return {
            "task_id": task.id,
            "status": "processing",
            "location": {"latitude": latitude, "longitude": longitude},
            "place_type": place_type
        }
    
    except Exception as e:
        logger.error(f"Maps scraping error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Task Status Endpoints
# ============================================================================

@app.get("/api/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    user_id: str = Depends(verify_token)
):
    """Get Celery task status"""
    
    try:
        from tasks.celery import celery_app
        
        task = celery_app.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": task.status,
            "progress": task.info.get("progress", 0) if isinstance(task.info, dict) else 0,
        }
    
    except Exception as e:
        logger.error(f"Task status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}/results")
async def get_task_results(
    task_id: str,
    user_id: str = Depends(verify_token)
):
    """Get Celery task results"""
    
    try:
        from tasks.celery import celery_app
        
        task = celery_app.AsyncResult(task_id)
        
        if task.status == "PENDING":
            return {"status": "pending"}
        elif task.status == "FAILURE":
            return {"status": "failed", "error": str(task.info)}
        elif task.status == "SUCCESS":
            return {"status": "completed", "results": task.result}
        else:
            return {
                "status": task.status,
                "progress": task.info.get("progress", 0) if isinstance(task.info, dict) else None
            }
    
    except Exception as e:
        logger.error(f"Task results error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Cache Management Endpoints
# ============================================================================

@app.get("/api/cache/stats")
async def get_cache_stats(
    user_id: str = Depends(verify_token)
):
    """Get cache statistics"""
    
    stats = cache_manager.get_stats()
    
    return {
        "hits": stats.get("hits", 0),
        "misses": stats.get("misses", 0),
        "size": stats.get("size", 0),
        "items": stats.get("items", 0)
    }


@app.delete("/api/cache")
async def clear_cache(
    user_id: str = Depends(verify_token)
):
    """Clear user cache"""
    
    cache_manager.clear()
    
    return {"message": "Cache cleared successfully"}


# ============================================================================
# Statistics Endpoints
# ============================================================================

@app.get("/api/stats")
async def get_user_stats(
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_token)
):
    """Get user statistics"""
    
    total_jobs = db.query(AnalysisJob).filter(
        AnalysisJob.user_id == user_id
    ).count()
    
    completed_jobs = db.query(AnalysisJob).filter(
        AnalysisJob.user_id == user_id,
        AnalysisJob.status == "completed"
    ).count()
    
    failed_jobs = db.query(AnalysisJob).filter(
        AnalysisJob.user_id == user_id,
        AnalysisJob.status == "failed"
    ).count()
    
    searches = db.query(SearchHistory).filter(
        SearchHistory.user_id == user_id
    ).count()
    
    return {
        "total_analyses": total_jobs,
        "completed_analyses": completed_jobs,
        "failed_analyses": failed_jobs,
        "total_searches": searches,
        "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info"
    )
