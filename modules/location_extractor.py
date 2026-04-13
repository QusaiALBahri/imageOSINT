"""Extract and analyze location information from images and search results"""

import logging
from typing import Dict, List, Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

logger = logging.getLogger(__name__)


class LocationExtractor:
    """Extract location information from various sources"""
    
    def __init__(self):
        """Initialize geocoder"""
        self.geocoder = Nominatim(user_agent="osint-image-tool-v1")
    
    def reverse_geocode(self, 
                       latitude: float, 
                       longitude: float) -> Optional[Dict]:
        """
        Convert GPS coordinates to address using reverse geocoding
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with address information or None
        """
        try:
            location = self.geocoder.reverse(f"{latitude}, {longitude}", language="en")
            
            if location:
                address_parts = location.address.split(",")
                return {
                    "full_address": location.address,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "city": address_parts[-3].strip() if len(address_parts) >= 3 else "",
                    "country": address_parts[-1].strip() if address_parts else "",
                    "raw_address": location.raw.get("address", {}),
                }
        except GeocoderTimedOut:
            logger.warning(f"Geocoder timeout for {latitude}, {longitude}")
        except GeocoderServiceError as e:
            logger.error(f"Geocoder service error: {str(e)}")
        except Exception as e:
            logger.error(f"Reverse geocoding error: {str(e)}")
        
        return None
    
    def forward_geocode(self, location_name: str) -> Optional[Dict]:
        """
        Convert location name to GPS coordinates
        
        Args:
            location_name: Name of location
            
        Returns:
            Dictionary with coordinate information or None
        """
        try:
            location = self.geocoder.geocode(location_name)
            
            if location:
                return {
                    "address": location.address,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "location_name": location_name,
                }
        except GeocoderTimedOut:
            logger.warning(f"Geocoder timeout for {location_name}")
        except Exception as e:
            logger.error(f"Forward geocoding error: {str(e)}")
        
        return None
    
    def extract_locations_from_text(self, text: str) -> List[str]:
        """
        Extract potential location names from text
        
        Args:
            text: Text to search for locations
            
        Returns:
            List of potential location names
        """
        locations = []
        
        # Simple keyword-based location extraction
        location_keywords = [
            "street", "road", "avenue", "boulevard", "city", "town",
            "village", "district", "area", "region", "province",
            "state", "country", "area code", "zip", "coordinates"
        ]
        
        text_lower = text.lower()
        for keyword in location_keywords:
            if keyword in text_lower:
                # This is a simplified approach
                idx = text_lower.find(keyword)
                start = max(0, idx - 50)
                end = min(len(text), idx + 100)
                snippet = text[start:end].strip()
                if snippet not in locations:
                    locations.append(snippet)
        
        return locations
    
    def get_location_bounds(self, 
                          latitude: float, 
                          longitude: float, 
                          radius_km: float = 1.0) -> Dict:
        """
        Get bounding box for a location with radius
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Radius in kilometers
            
        Returns:
            Bounding box with north, south, east, west coordinates
        """
        # Approximate conversion: 1 degree ≈ 111 km
        deg_radius = radius_km / 111.0
        
        return {
            "center": {"lat": latitude, "lon": longitude},
            "radius_km": radius_km,
            "north": latitude + deg_radius,
            "south": latitude - deg_radius,
            "east": longitude + deg_radius,
            "west": longitude - deg_radius,
        }
    
    def estimate_accuracy(self, 
                         metadata: Dict) -> Dict:
        """
        Estimate location accuracy based on available data
        
        Args:
            metadata: Image metadata dictionary
            
        Returns:
            Dictionary with accuracy analysis
        """
        accuracy = {
            "has_gps": False,
            "has_exif": False,
            "accuracy_level": "Low",
            "confidence": 0,
        }
        
        if metadata.get("gps"):
            accuracy["has_gps"] = True
            accuracy["accuracy_level"] = "High"
            accuracy["confidence"] = 0.9
        
        if metadata.get("exif"):
            accuracy["has_exif"] = True
            if not accuracy["has_gps"]:
                accuracy["accuracy_level"] = "Medium"
                accuracy["confidence"] = 0.5
        
        return accuracy
    
    def analyze_location_data(self, 
                            gps_coords: Optional[Tuple[float, float]] = None,
                            search_results: List[Dict] = None) -> Dict:
        """
        Comprehensive location analysis from multiple sources
        
        Args:
            gps_coords: GPS coordinates tuple (lat, lon)
            search_results: List of search results with location info
            
        Returns:
            Comprehensive location analysis
        """
        analysis = {
            "primary_location": None,
            "secondary_locations": [],
            "coordinates": gps_coords,
            "confidence": 0,
        }
        
        # Process GPS coordinates first
        if gps_coords:
            geocoded = self.reverse_geocode(gps_coords[0], gps_coords[1])
            if geocoded:
                analysis["primary_location"] = geocoded
                analysis["confidence"] = 0.9
        
        # Process search results for location hints
        if search_results:
            for result in search_results:
                if "location" in result and result["location"]:
                    secondary = self.forward_geocode(result["location"])
                    if secondary:
                        analysis["secondary_locations"].append(secondary)
        
        return analysis
