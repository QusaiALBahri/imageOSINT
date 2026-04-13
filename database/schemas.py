"""Pydantic schemas for API request/response validation"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


# ============================================================================
# User Schemas
# ============================================================================

class UserCreate(BaseModel):
    """Create user request"""
    email: EmailStr
    username: str
    password: str
    
    @validator("username")
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not v.isalnum() and "_" not in v:
            raise ValueError("Username must be alphanumeric")
        return v
    
    @validator("password")
    def password_valid(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str
    user_id: str
    email: str


# ============================================================================
# Analysis Schemas
# ============================================================================

class AnalysisRequest(BaseModel):
    """Analysis request"""
    analysis_types: str = "all"
    priority: Optional[str] = "normal"


class AnalysisResponse(BaseModel):
    """Analysis response"""
    job_id: str
    status: str
    progress: int
    message: str


class JobStatus(BaseModel):
    """Job status response"""
    job_id: str
    status: str
    progress: int
    filename: str
    created_at: datetime


# ============================================================================
# Metadata Schemas
# ============================================================================

class BasicMetadata(BaseModel):
    """Basic image metadata"""
    format: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    size: Optional[int] = None
    dpi: Optional[str] = None


class ExifData(BaseModel):
    """EXIF data"""
    creation_date: Optional[str] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    focal_length: Optional[str] = None
    flash: Optional[str] = None
    iso: Optional[int] = None
    aperture: Optional[str] = None
    shutter_speed: Optional[str] = None


class GPSData(BaseModel):
    """GPS coordinate data"""
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: Optional[str] = None


class MetadataResponse(BaseModel):
    """Metadata response"""
    basic: BasicMetadata
    exif: Optional[Dict[str, Any]] = None
    gps: Optional[GPSData] = None
    camera: Optional[Dict[str, Any]] = None


# ============================================================================
# Location Schemas
# ============================================================================

class LocationInfo(BaseModel):
    """Location information"""
    address: str
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: float
    longitude: float
    confidence: float = 0.0


class LocationResponse(BaseModel):
    """Location analysis response"""
    primary_location: Optional[LocationInfo] = None
    secondary_locations: List[LocationInfo] = []
    accuracy_level: str
    confidence: float


# ============================================================================
# Search Schemas
# ============================================================================

class SearchResult(BaseModel):
    """Single search result"""
    title: str
    url: str
    source: str
    rank: int
    image_url: Optional[str] = None
    similarity: Optional[float] = None


class SearchResponse(BaseModel):
    """Search response"""
    engine: str
    total_results: int
    results: List[SearchResult]


# ============================================================================
# Maps Schemas
# ============================================================================

class PlaceInfo(BaseModel):
    """Place information"""
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class MapsResponse(BaseModel):
    """Maps response"""
    location: LocationInfo
    places: List[PlaceInfo]
    place_type: str
    total_found: int


# ============================================================================
# Cache Schemas
# ============================================================================

class CacheStats(BaseModel):
    """Cache statistics"""
    hits: int
    misses: int
    hit_rate: float
    size_mb: float
    items: int


# ============================================================================
# Stats Schemas
# ============================================================================

class UserStats(BaseModel):
    """User statistics"""
    total_analyses: int
    completed_analyses: int
    failed_analyses: int
    total_searches: int
    success_rate: float
    last_activity: Optional[datetime] = None


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    timestamp: datetime
    status_code: int
    details: Optional[Dict[str, Any]] = None
