"""Main Gradio application for OSINT Image Search and Analysis Tool"""

import gradio as gr
import logging
import json
from pathlib import Path
from typing import Tuple, List, Dict, Optional
import traceback

from modules.metadata_extractor import MetadataExtractor
from modules.location_extractor import LocationExtractor
from modules.image_search import ReverseImageSearcher
from modules.maps_scraper import GoogleMapsScraper
from modules.utils import format_results, merge_results
from core.config import settings
from core.config import UPLOADS_DIR, OUTPUTS_DIR

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components
metadata_extractor = MetadataExtractor()
location_extractor = LocationExtractor()
image_searcher = ReverseImageSearcher()
maps_scraper = GoogleMapsScraper()


def process_image_input(image_input: Tuple) -> Tuple[str, str, str]:
    """
    Handle image input - either uploaded file or URL
    
    Args:
        image_input: Tuple of (file_path_or_url, input_type)
        
    Returns:
        Tuple of (status, file_path, message)
    """
    try:
        if image_input[1] == "upload" and image_input[0]:
            file_path = image_input[0].name
            return "success", file_path, f"✓ Image uploaded successfully: {Path(file_path).name}"
        elif image_input[1] == "url" and image_input[2]:
            # Download image from URL
            url = image_input[2]
            from modules.utils import download_image
            output_path = UPLOADS_DIR / "downloaded_image.jpg"
            
            if download_image(url, output_path):
                return "success", str(output_path), f"✓ Image downloaded from URL: {url}"
            else:
                return "error", "", "✗ Failed to download image from URL"
        else:
            return "error", "", "✗ Please provide either an image or a URL"
    
    except Exception as e:
        logger.error(f"Image input processing error: {str(e)}")
        return "error", "", f"✗ Error processing image: {str(e)}"


def extract_metadata_tab(image_path: str) -> Tuple[str, str, str, str]:
    """
    Extract and display image metadata
    
    Args:
        image_path: Path to image file
        
    Returns:
        Tuple of (basic_metadata, exif_data, gps_data, camera_info) as JSON strings
    """
    try:
        if not image_path:
            return "{}", "{}", "{}", "{}"
        
        logger.info(f"Extracting metadata from: {image_path}")
        
        # Extract all metadata
        metadata = metadata_extractor.get_full_metadata(image_path)
        
        # Format for display
        basic_json = json.dumps(metadata.get("basic", {}), indent=2)
        exif_json = json.dumps(metadata.get("exif", {}), indent=2)
        gps_json = json.dumps(metadata.get("gps", {}), indent=2)
        
        camera_info = metadata_extractor.extract_camera_info(image_path)
        camera_json = json.dumps(camera_info, indent=2)
        
        logger.info("Metadata extraction completed")
        
        return basic_json, exif_json, gps_json, camera_json
    
    except Exception as e:
        logger.error(f"Metadata extraction error: {str(e)}")
        error_msg = json.dumps({"error": str(e)}, indent=2)
        return error_msg, error_msg, error_msg, error_msg


def reverse_image_search_tab(image_path: str) -> Tuple[str, str, str, str]:
    """
    Perform reverse image search on multiple engines
    
    Args:
        image_path: Path to image file
        
    Returns:
        Tuple of (google_results, bing_results, yandex_results, summary) as JSON/text
    """
    try:
        if not image_path:
            return "No image provided", "No image provided", "No image provided", ""
        
        logger.info(f"Starting reverse image search for: {image_path}")
        
        # Perform searches
        results = image_searcher.search_all(image_path)
        
        # Format results
        google_json = json.dumps(results.get("google", []), indent=2)
        bing_json = json.dumps(results.get("bing", []), indent=2)
        yandex_json = json.dumps(results.get("yandex", []), indent=2)
        
        # Create summary
        summary = f"""
        Reverse Image Search Summary
        =============================
        Google Images Results: {len(results.get("google", []))}
        Bing Images Results: {len(results.get("bing", []))}
        Yandex Images Results: {len(results.get("yandex", []))}
        
        Total Results: {sum(len(v) for v in results.values())}
        
        Search Recommendations:
        - Review results from multiple engines for better accuracy
        - Cross-reference URLs to verify source websites
        - Check metadata of found images for additional clues
        """
        
        logger.info("Reverse image search completed")
        
        return google_json, bing_json, yandex_json, summary.strip()
    
    except Exception as e:
        logger.error(f"Reverse image search error: {str(e)}")
        error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        return error_msg, error_msg, error_msg, error_msg


def location_analysis_tab(image_path: str) -> Tuple[str, str, str]:
    """
    Analyze location information from image and metadata
    
    Args:
        image_path: Path to image file
        
    Returns:
        Tuple of (location_analysis, gps_analysis, accuracy_assessment) as JSON/text
    """
    try:
        if not image_path:
            return "{}", "{}", ""
        
        logger.info(f"Analyzing location for: {image_path}")
        
        # Extract metadata and GPS
        metadata = metadata_extractor.get_full_metadata(image_path)
        gps_coords = metadata.get("gps")
        
        location_analysis = {}
        accuracy_info = ""
        
        if gps_coords:
            # Reverse geocode GPS coordinates
            lat, lon = gps_coords["latitude"], gps_coords["longitude"]
            geocoded = location_extractor.reverse_geocode(lat, lon)
            
            if geocoded:
                location_analysis = geocoded
                logger.info(f"Location identified: {geocoded.get('full_address', 'Unknown')}")
        
        # Accuracy assessment
        accuracy = location_extractor.estimate_accuracy(metadata)
        accuracy_json = json.dumps(accuracy, indent=2)
        
        if not location_analysis:
            location_analysis = {
                "status": "No GPS data found in image",
                "recommendation": "Image does not contain GPS coordinates. Try using reverse image search or other location clues."
            }
        
        location_json = json.dumps(location_analysis, indent=2)
        
        # Comprehensive analysis
        analysis_data = location_extractor.analyze_location_data(
            gps_coords=gps_coords,
            search_results=[]
        )
        
        logger.info("Location analysis completed")
        
        return location_json, accuracy_json, json.dumps(analysis_data, indent=2)
    
    except Exception as e:
        logger.error(f"Location analysis error: {str(e)}")
        error_msg = json.dumps({"error": str(e)}, indent=2)
        return error_msg, error_msg, error_msg


def maps_scraping_tab(latitude_input: str, longitude_input: str) -> Tuple[str, str, str, str]:
    """
    Scrape and display Google Maps data for coordinates
    
    Args:
        latitude_input: Latitude as string
        longitude_input: Longitude as string
        
    Returns:
        Tuple of (places_data, street_view, restaurants, summary)
    """
    try:
        if not latitude_input or not longitude_input:
            return "{}", json.dumps({"error": "Please provide coordinates"}), "{}", ""
        
        try:
            latitude = float(latitude_input)
            longitude = float(longitude_input)
        except ValueError:
            return "{}", json.dumps({"error": "Invalid coordinates"}), "{}", ""
        
        logger.info(f"Scraping Google Maps for: {latitude}, {longitude}")
        
        # Get comprehensive map data
        map_summary = maps_scraper.get_map_data_summary(latitude, longitude)
        
        # Extract components
        street_view = map_summary.get("street_view", {})
        places = map_summary.get("attractions", [])
        restaurants = map_summary.get("restaurants", [])
        
        places_json = json.dumps(places, indent=2)
        street_view_json = json.dumps(street_view, indent=2)
        restaurants_json = json.dumps(restaurants, indent=2)
        
        # Create summary
        summary = f"""
        Google Maps Analysis Summary
        ============================
        Coordinates: {latitude}, {longitude}
        
        Nearby Attractions: {len(places)}
        Nearby Restaurants: {len(restaurants)}
        
        Map URL: https://www.google.com/maps/@{latitude},{longitude},15z
        Street View: {street_view.get('street_view_url', 'Not available')}
        
        Tips:
        - Use the Map URL to verify the location visually
        - Check nearby business listings for area verification
        - Cross-reference with other location data sources
        """
        
        logger.info("Maps scraping completed")
        
        return places_json, street_view_json, restaurants_json, summary.strip()
    
    except Exception as e:
        logger.error(f"Maps scraping error: {str(e)}")
        error_msg = f"Error: {str(e)}"
        return error_msg, error_msg, error_msg, error_msg


def comprehensive_analysis(image_input) -> str:
    """
    Run comprehensive OSINT analysis on image
    
    Args:
        image_input: Image input from Gradio
        
    Returns:
        HTML-formatted comprehensive report
    """
    try:
        # Get image path
        if hasattr(image_input, 'name'):
            image_path = image_input.name
        else:
            image_path = image_input
        
        if not image_path:
            return "<h4>❌ No image provided</h4>"
        
        logger.info(f"Starting comprehensive analysis for: {image_path}")
        
        # Run all analyses
        results = {
            "metadata": metadata_extractor.get_full_metadata(image_path),
            "image_search": image_searcher.search_all(image_path),
        }
        
        # Generate HTML report
        html_report = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .section {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }}
                h2 {{ color: #333; }}
                .metadata {{ background: #e8f4f8; }}
                .search {{ background: #f0e8f8; }}
                .location {{ background: #f0f8e8; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #007bff; color: white; }}
            </style>
        </head>
        <body>
            <h1>🔍 OSINT Image Analysis Report</h1>
            
            <div class="section metadata">
                <h2>📷 Image Metadata</h2>
                <table>
                    <tr>
                        <th>Property</th>
                        <th>Value</th>
                    </tr>
        """
        
        # Add metadata to report
        basic_meta = results["metadata"].get("basic", {})
        for key, value in basic_meta.items():
            html_report += f"<tr><td>{key}</td><td>{value}</td></tr>"
        
        html_report += """
                </table>
            </div>
            
            <div class="section search">
                <h2>🔎 Reverse Image Search Results</h2>
        """
        
        # Add search results
        for engine, engine_results in results["image_search"].items():
            html_report += f"<h3>{engine.title()}: {len(engine_results)} results</h3>"
            if engine_results:
                html_report += "<ul>"
                for result in engine_results[:5]:  # Show top 5
                    html_report += f"<li>{result.get('title', 'No title')}</li>"
                html_report += "</ul>"
        
        html_report += """
            </div>
            
            <div class="section location">
                <h2>📍 Location Information</h2>
        """
        
        # Add location info
        gps = results["metadata"].get("gps")
        if gps:
            html_report += f"""
                <p><strong>GPS Coordinates:</strong> {gps.get('latitude')}, {gps.get('longitude')}</p>
                <p><strong>Maps Link:</strong> https://www.google.com/maps/@{gps.get('latitude')},{gps.get('longitude')},15z</p>
            """
        else:
            html_report += "<p>No GPS data found in image metadata</p>"
        
        html_report += """
            </div>
            
            <div class="section">
                <h3>⚠️ Disclaimer</h3>
                <p>This tool is for lawful OSINT and research purposes only. 
                Always respect privacy laws and ethical considerations. 
                Unauthorized access to private information is illegal.</p>
            </div>
        </body>
        </html>
        """
        
        logger.info("Comprehensive analysis completed")
        return html_report
    
    except Exception as e:
        logger.error(f"Comprehensive analysis error: {str(e)}")
        return f"<h4>❌ Error during analysis: {str(e)}</h4>"


# Define the Gradio interface
with gr.Blocks(title="ImageOSINT Analysis Platform", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📷 ImageOSINT Analysis Platform")
    gr.Markdown("Advanced OSINT image analysis with metadata extraction, reverse search, and geolocation.")
    
    with gr.Tab("Metadata Extraction"):
        # ... (Add the metadata tab UI here)
        pass
    
    with gr.Tab("Reverse Image Search"):
        # ... (Add the search tab UI here)
        pass

# Export demo for run.py
if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
