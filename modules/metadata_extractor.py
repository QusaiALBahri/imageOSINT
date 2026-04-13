"""Extract metadata from images including EXIF data and GPS coordinates"""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from PIL import Image
from PIL.ExifTags import TAGS
import exifread

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extract and parse image metadata"""
    
    @staticmethod
    def extract_basic_metadata(image_path: str) -> Dict:
        """Extract basic image metadata using PIL"""
        try:
            image = Image.open(image_path)
            metadata = {
                "format": image.format,
                "size": image.size,
                "width": image.width,
                "height": image.height,
                "mode": image.mode,
                "dpi": image.info.get("dpi", "Not available"),
            }
            return metadata
        except Exception as e:
            logger.error(f"Failed to extract basic metadata: {str(e)}")
            return {}
    
    @staticmethod
    def extract_exif_data(image_path: str) -> Dict:
        """Extract EXIF data from image"""
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            
            if not exif_data:
                logger.info("No EXIF data found in image")
                return {}
            
            exif_dict = {}
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                exif_dict[tag_name] = str(value)[:100]  # Limit value length
            
            return exif_dict
        except Exception as e:
            logger.debug(f"Could not extract EXIF via PIL: {str(e)}")
            return {}
    
    @staticmethod
    def extract_gps_coordinates(image_path: str) -> Optional[Tuple[float, float]]:
        """Extract GPS coordinates from image EXIF data"""
        try:
            with open(image_path, "rb") as f:
                tags = exifread.process_file(f, details=False)
            
            # Get GPS data
            gps_latitude = tags.get("GPS GPSLatitude")
            gps_longitude = tags.get("GPS GPSLongitude")
            
            if not gps_latitude or not gps_longitude:
                logger.info("No GPS data in image")
                return None
            
            # Parse GPS coordinates
            lat = MetadataExtractor._convert_to_degrees(gps_latitude.values)
            lon = MetadataExtractor._convert_to_degrees(gps_longitude.values)
            
            # Check for South/West indicators
            gps_lat_ref = str(tags.get("GPS GPSLatitudeRef", "N"))
            gps_lon_ref = str(tags.get("GPS GPSLongitudeRef", "E"))
            
            if "S" in gps_lat_ref:
                lat = -lat
            if "W" in gps_lon_ref:
                lon = -lon
            
            logger.info(f"Extracted GPS coordinates: {lat}, {lon}")
            return (lat, lon)
        except Exception as e:
            logger.debug(f"Failed to extract GPS coordinates: {str(e)}")
            return None
    
    @staticmethod
    def _convert_to_degrees(gps_data) -> float:
        """Convert GPS coordinates from fraction format to degrees"""
        try:
            d, m, s = gps_data
            degrees = d.num / d.den + (m.num / m.den) / 60 + (s.num / s.den) / 3600
            return float(degrees)
        except Exception as e:
            logger.error(f"GPS conversion error: {str(e)}")
            return 0.0
    
    @staticmethod
    def get_full_metadata(image_path: str) -> Dict:
        """Get all available metadata from image"""
        metadata = {
            "basic": MetadataExtractor.extract_basic_metadata(image_path),
            "exif": MetadataExtractor.extract_exif_data(image_path),
            "gps": None,
        }
        
        gps_coords = MetadataExtractor.extract_gps_coordinates(image_path)
        if gps_coords:
            metadata["gps"] = {
                "latitude": gps_coords[0],
                "longitude": gps_coords[1],
                "coordinates": f"{gps_coords[0]}, {gps_coords[1]}"
            }
        
        return metadata
    
    @staticmethod
    def extract_creation_date(image_path: str) -> Optional[str]:
        """Extract image creation/modification date"""
        try:
            with open(image_path, "rb") as f:
                tags = exifread.process_file(f, details=False)
            
            datetime_original = tags.get("EXIF DateTimeOriginal")
            datetime_digitized = tags.get("EXIF DateTimeDigitized")
            datetime_tag = tags.get("Image DateTime")
            
            if datetime_original:
                return str(datetime_original)
            elif datetime_digitized:
                return str(datetime_digitized)
            elif datetime_tag:
                return str(datetime_tag)
            
            return None
        except Exception as e:
            logger.debug(f"Could not extract creation date: {str(e)}")
            return None
    
    @staticmethod
    def extract_camera_info(image_path: str) -> Dict:
        """Extract camera and lens information from EXIF"""
        try:
            with open(image_path, "rb") as f:
                tags = exifread.process_file(f, details=False)
            
            camera_info = {}
            
            if "Image Model" in tags:
                camera_info["camera_model"] = str(tags["Image Model"])
            if "Image Make" in tags:
                camera_info["manufacturer"] = str(tags["Image Make"])
            if "EXIF LensModel" in tags:
                camera_info["lens_model"] = str(tags["EXIF LensModel"])
            if "EXIF FocalLength" in tags:
                camera_info["focal_length"] = str(tags["EXIF FocalLength"])
            if "EXIF Flash" in tags:
                camera_info["flash"] = str(tags["EXIF Flash"])
            
            return camera_info
        except Exception as e:
            logger.debug(f"Could not extract camera info: {str(e)}")
            return {}
