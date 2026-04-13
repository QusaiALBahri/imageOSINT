"""Celery async tasks for image analysis"""

import logging
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tasks.celery import celery_app
from database.models import AnalysisJob, CachedResult
from database.session import SessionLocal
from core.cache import cache_manager
from core.config import settings
from modules.metadata_extractor import MetadataExtractor
from modules.image_search import ReverseImageSearcher
from modules.location_extractor import LocationExtractor
from modules.maps_scraper import GoogleMapsScraper

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.process_image_analysis")
def process_image_analysis(
    self,
    job_id: str,
    file_path: str,
    analysis_types: str,
    user_id: str
):
    """
    Process complete image analysis
    
    Args:
        job_id: Unique job identifier
        file_path: Path to image file
        analysis_types: comma-separated analysis types
        user_id: User ID
    """
    db = SessionLocal()
    
    try:
        # Update job status
        job = db.query(AnalysisJob).filter(
            AnalysisJob.job_id == job_id
        ).first()
        
        if not job:
            logger.error(f"Job not found: {job_id}")
            return
        
        job.status = "processing"
        job.started_at = datetime.utcnow()
        job.progress = 5
        db.commit()
        
        logger.info(f"Starting analysis: {job_id}")
        
        results = {}
        types = [t.strip() for t in analysis_types.split(",")]
        
        # Process metadata
        if "metadata" in types or "all" in analysis_types:
            self.update_state(state="PROGRESS", meta={"progress": 20})
            job.progress = 20
            db.commit()
            
            metadata = extract_metadata_task.apply_async(
                args=[file_path]
            ).get(timeout=30)
            
            results["metadata"] = metadata
        
        # Process reverse image search
        if "search" in types or "all" in analysis_types:
            self.update_state(state="PROGRESS", meta={"progress": 40})
            job.progress = 40
            db.commit()
            
            search_results = reverse_image_search_task.apply_async(
                args=[file_path, "google,bing,yandex"]
            ).get(timeout=60)
            
            results["image_search"] = search_results
        
        # Process location analysis
        if "location" in types or "all" in analysis_types:
            self.update_state(state="PROGRESS", meta={"progress": 60})
            job.progress = 60
            db.commit()
            
            if results.get("metadata", {}).get("gps"):
                gps = results["metadata"]["gps"]
                location = location_analysis_task.apply_async(
                    args=[gps["latitude"], gps["longitude"]]
                ).get(timeout=30)
                
                results["location"] = location
        
        # Process Google Maps
        if "maps" in types or "all" in analysis_types:
            self.update_state(state="PROGRESS", meta={"progress": 80})
            job.progress = 80
            db.commit()
            
            if results.get("location", {}).get("primary_location"):
                loc = results["location"]["primary_location"]
                maps_data = maps_scraping_task.apply_async(
                    args=[loc["latitude"], loc["longitude"], "restaurant", 1000]
                ).get(timeout=60)
                
                results["maps"] = maps_data
        
        # Update job with results
        job.status = "completed"
        job.progress = 100
        job.results = results
        job.completed_at = datetime.utcnow()
        job.processing_time = int(
            (job.completed_at - job.started_at).total_seconds()
        )
        db.commit()
        
        logger.info(f"Analysis completed: {job_id}")
        self.update_state(state="SUCCESS", meta={"progress": 100})
        
        return {"job_id": job_id, "status": "completed", "results": results}
    
    except Exception as e:
        logger.error(f"Analysis error {job_id}: {str(e)}")
        
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()
        
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise
    
    finally:
        db.close()


@celery_app.task(name="tasks.extract_metadata")
def extract_metadata_task(file_path: str):
    """Extract image metadata"""
    try:
        logger.info(f"Extracting metadata: {file_path}")
        
        extractor = MetadataExtractor()
        metadata = extractor.get_full_metadata(file_path)
        
        return metadata
    
    except Exception as e:
        logger.error(f"Metadata extraction error: {str(e)}")
        raise


@celery_app.task(name="tasks.reverse_image_search")
def reverse_image_search_task(file_path: str, engines: str = "google,bing,yandex"):
    """Perform reverse image search"""
    try:
        logger.info(f"Reverse image search: {file_path}")
        
        searcher = ReverseImageSearcher()
        results = searcher.search_all(file_path)
        
        # Cache results
        cache_key = f"search:{Path(file_path).name}"
        cache_manager.set(cache_key, results, ttl=86400)  # 24 hours
        
        return results
    
    except Exception as e:
        logger.error(f"Reverse search error: {str(e)}")
        raise


@celery_app.task(name="tasks.location_analysis")
def location_analysis_task(latitude: float, longitude: float):
    """Analyze location from GPS coordinates"""
    try:
        logger.info(f"Location analysis: {latitude}, {longitude}")
        
        locator = LocationExtractor()
        
        # Reverse geocode
        location = locator.reverse_geocode(latitude, longitude)
        
        # Get accuracy
        accuracy = locator.estimate_accuracy({
            "gps": {"latitude": latitude, "longitude": longitude}
        })
        
        result = {
            "location": location,
            "accuracy": accuracy,
            "primary_location": location
        }
        
        # Cache results
        cache_key = f"location:{latitude}:{longitude}"
        cache_manager.set(cache_key, result, ttl=604800)  # 7 days
        
        return result
    
    except Exception as e:
        logger.error(f"Location analysis error: {str(e)}")
        raise


@celery_app.task(name="tasks.maps_scraping")
def maps_scraping_task(
    latitude: float,
    longitude: float,
    place_type: str = "restaurant",
    radius: int = 1000
):
    """Scrape nearby places from Google Maps"""
    try:
        logger.info(f"Maps scraping: {latitude}, {longitude} - {place_type}")
        
        scraper = GoogleMapsScraper()
        
        places = scraper.search_nearby_businesses(
            latitude, longitude, place_type
        )
        
        result = {
            "location": {"latitude": latitude, "longitude": longitude},
            "place_type": place_type,
            "radius": radius,
            "places": places,
            "count": len(places)
        }
        
        # Cache results
        cache_key = f"maps:{latitude}:{longitude}:{place_type}"
        cache_manager.set(cache_key, result, ttl=604800)  # 7 days
        
        return result
    
    except Exception as e:
        logger.error(f"Maps scraping error: {str(e)}")
        raise


@celery_app.task(name="tasks.cleanup_old_files")
def cleanup_old_files():
    """Cleanup old uploaded files"""
    try:
        uploads_dir = Path(settings.UPLOADS_DIR)
        cutoff_time = (datetime.utcnow() - timedelta(days=7)).timestamp()
        
        deleted_count = 0
        for file in uploads_dir.glob("*"):
            if file.stat().st_mtime < cutoff_time:
                file.unlink()
                deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old files")
        
        return {"deleted": deleted_count}
    
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")


@celery_app.task(name="tasks.cleanup_expired_cache")
def cleanup_expired_cache():
    """Cleanup expired cache entries"""
    try:
        # Redis handles expiry automatically
        # This task is for periodic maintenance
        logger.info("Cache maintenance completed")
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Cache cleanup error: {str(e)}")


# Schedule periodic tasks
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "cleanup-old-files-daily": {
        "task": "tasks.cleanup_old_files",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
    },
    "cleanup-cache-daily": {
        "task": "tasks.cleanup_expired_cache",
        "schedule": crontab(hour=3, minute=0),  # 3 AM daily
    },
}
