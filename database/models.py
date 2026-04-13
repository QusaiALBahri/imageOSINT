"""Database models for OSINT Image Tool"""

from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class UserAccount(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analysis_jobs = relationship("AnalysisJob", back_populates="user")
    search_history = relationship("SearchHistory", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")
    
    def __repr__(self):
        return f"<UserAccount {self.email}>"


class APIKey(Base):
    """API key for user authentication"""
    __tablename__ = "api_keys"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    key_hash = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("UserAccount", back_populates="api_keys")
    
    def __repr__(self):
        return f"<APIKey {self.name or self.id}>"


class AnalysisJob(Base):
    """Image analysis job record"""
    __tablename__ = "analysis_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(36), unique=True, index=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True)
    
    analysis_types = Column(String(255), nullable=False)  # comma-separated: metadata,search,location,maps
    
    status = Column(String(50), default="pending", index=True)  # pending, processing, completed, failed
    progress = Column(Integer, default=0)
    
    results = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    processing_time = Column(Integer, nullable=True)  # seconds
    
    # Relationships
    user = relationship("UserAccount", back_populates="analysis_jobs")
    
    def __repr__(self):
        return f"<AnalysisJob {self.job_id}>"


class SearchHistory(Base):
    """Search history record"""
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    image_filename = Column(String(255), nullable=False)
    search_engines = Column(String(255), nullable=False)  # comma-separated
    result_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("UserAccount", back_populates="search_history")
    
    def __repr__(self):
        return f"<SearchHistory {self.id}>"


class CachedResult(Base):
    """Cached analysis results"""
    __tablename__ = "cached_results"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), unique=True, index=True, nullable=False)
    result_type = Column(String(50), nullable=False)  # metadata, search, location, maps
    result_data = Column(JSON, nullable=False)
    
    hit_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    
    def __repr__(self):
        return f"<CachedResult {self.cache_key}>"


class LocationAnalysis(Base):
    """Stored location analysis results"""
    __tablename__ = "location_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(36), ForeignKey("analysis_jobs.job_id"), nullable=True)
    
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    
    address = Column(String(500), nullable=True)
    city = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    confidence = Column(Float, nullable=True)
    
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<LocationAnalysis {self.latitude},{self.longitude}>"


class ImageMetadata(Base):
    """Stored image metadata"""
    __tablename__ = "image_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(36), nullable=False, index=True)
    file_hash = Column(String(64), unique=True, index=True)
    
    format = Column(String(50), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=True)
    
    exif_data = Column(JSON, nullable=True)
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    
    camera_make = Column(String(255), nullable=True)
    camera_model = Column(String(255), nullable=True)
    lens_model = Column(String(255), nullable=True)
    
    creation_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ImageMetadata {self.file_hash}>"
