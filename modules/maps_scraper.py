"""Google Maps scraping and location data extraction"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from modules.utils import safe_request, extract_domain
import json

logger = logging.getLogger(__name__)


class GoogleMapsScraper:
    """Scrape and extract location data from Google Maps"""
    
    @staticmethod
    def search_location(location_query: str) -> Optional[Dict]:
        """
        Search for location on Google Maps
        
        Args:
            location_query: Location name or address to search
            
        Returns:
            Dictionary with location information
        """
        try:
            # Use Google Maps search URL
            url = f"https://www.google.com/maps/search/{location_query}"
            response = safe_request(url)
            
            if response:
                # Parse the response - Note: Modern Google Maps uses heavy JavaScript
                # This approach works better for location data extraction
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Extract scripts containing JSON data
                scripts = soup.find_all("script")
                location_data = None
                
                for script in scripts:
                    if script.string and "window" in script.string:
                        try:
                            # Try to find location data in script contents
                            if "lat" in script.string or "lng" in script.string:
                                location_data = script.string
                                break
                        except:
                            continue
                
                return {
                    "query": location_query,
                    "url": url,
                    "found": location_data is not None,
                    "raw_data": location_data,
                }
        except Exception as e:
            logger.error(f"Google Maps location search error: {str(e)}")
        
        return None
    
    @staticmethod
    def extract_places_near_coordinates(latitude: float, 
                                       longitude: float,
                                       radius_meters: int = 1000) -> List[Dict]:
        """
        Extract places near given coordinates using Google Maps
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius_meters: Search radius in meters
            
        Returns:
            List of places found near the coordinates
        """
        places = []
        
        try:
            # Google Maps URL for nearby places
            url = f"https://www.google.com/maps/@{latitude},{longitude},15z"
            response = safe_request(url)
            
            if response:
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Extract place cards
                place_cards = soup.find_all("div", {"class": "VfPpkd-t08AT-Bz112c-M1sRZc"}, limit=20)
                
                for idx, card in enumerate(place_cards):
                    try:
                        title = card.get_text(strip=True)
                        if title:
                            places.append({
                                "name": title[:100],
                                "rank": idx + 1,
                                "latitude": latitude,
                                "longitude": longitude,
                                "radius_meters": radius_meters,
                            })
                    except:
                        continue
                
                logger.info(f"Found {len(places)} places near coordinates")
            
        except Exception as e:
            logger.error(f"Extract places error: {str(e)}")
        
        return places
    
    @staticmethod
    def get_street_view_metadata(latitude: float, 
                                longitude: float) -> Optional[Dict]:
        """
        Get Street View metadata for coordinates
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Street View metadata if available
        """
        try:
            # Street View metadata endpoint (unofficial)
            url = f"https://maps.googleapis.com/maps/api/streetview/metadata?location={latitude},{longitude}"
            
            # Note: This requires an API key. For open-source approach:
            # Use the web interface
            street_view_url = f"https://www.google.com/maps/@{latitude},{longitude},0a,75y,0h/data=!3m6!1e1!3m4!1s0x0:0x0!2e0!7i13312!8i8448"
            
            return {
                "latitude": latitude,
                "longitude": longitude,
                "street_view_url": street_view_url,
                "source": "Google Street View",
            }
        
        except Exception as e:
            logger.error(f"Street View metadata error: {str(e)}")
        
        return None
    
    @staticmethod
    def search_nearby_businesses(latitude: float, 
                                longitude: float,
                                business_type: str = "restaurant") -> List[Dict]:
        """
        Search for nearby businesses of a specific type
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            business_type: Type of business (restaurant, hotel, etc.)
            
        Returns:
            List of nearby businesses
        """
        businesses = []
        
        try:
            url = f"https://www.google.com/maps/search/{business_type}/@{latitude},{longitude},15z"
            response = safe_request(url)
            
            if response:
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Extract business listings
                listings = soup.find_all("div", {"role": "button"}, limit=15)
                
                for idx, listing in enumerate(listings):
                    try:
                        name = listing.get_text(strip=True)
                        if name and len(name) > 2:
                            businesses.append({
                                "name": name[:100],
                                "type": business_type,
                                "rank": idx + 1,
                                "latitude": latitude,
                                "longitude": longitude,
                            })
                    except:
                        continue
                
                logger.info(f"Found {len(businesses)} {business_type}s nearby")
            
        except Exception as e:
            logger.error(f"Nearby businesses search error: {str(e)}")
        
        return businesses
    
    @staticmethod
    def extract_map_coordinates_from_url(maps_url: str) -> Optional[Tuple[float, float]]:
        """
        Extract coordinates from Google Maps URL
        
        Args:
            maps_url: Google Maps URL
            
        Returns:
            Tuple of (latitude, longitude) or None
        """
        try:
            # Parse common Google Maps URL formats
            # Format: https://www.google.com/maps/@lat,lng,zoom
            # Format: https://maps.google.com/?q=lat,lng
            
            if "@" in maps_url:
                coords_part = maps_url.split("@")[1].split(",")
                if len(coords_part) >= 2:
                    lat = float(coords_part[0])
                    lng = float(coords_part[1])
                    return (lat, lng)
            
            elif "q=" in maps_url:
                coords_part = maps_url.split("q=")[1].split(",")
                if len(coords_part) >= 2:
                    try:
                        lat = float(coords_part[0])
                        lng = float(coords_part[1])
                        return (lat, lng)
                    except ValueError:
                        pass
            
        except Exception as e:
            logger.debug(f"Could not parse coordinates from URL: {str(e)}")
        
        return None
    
    @staticmethod
    def get_map_data_summary(latitude: float, 
                            longitude: float) -> Dict:
        """
        Get comprehensive map data summary for location
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with comprehensive map data
        """
        summary = {
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "street_view": GoogleMapsScraper.get_street_view_metadata(latitude, longitude),
            "restaurants": GoogleMapsScraper.search_nearby_businesses(latitude, longitude, "restaurant"),
            "hotels": GoogleMapsScraper.search_nearby_businesses(latitude, longitude, "hotel"),
            "attractions": GoogleMapsScraper.search_nearby_businesses(latitude, longitude, "tourist attraction"),
        }
        
        return summary
