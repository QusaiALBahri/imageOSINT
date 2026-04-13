"""
Example Usage of OSINT Module Components
Demonstrates how to use the library programmatically
"""

import logging
from pathlib import Path
from modules.metadata_extractor import MetadataExtractor
from modules.location_extractor import LocationExtractor
from modules.image_search import ReverseImageSearcher
from modules.maps_scraper import GoogleMapsScraper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_extract_metadata():
    """Example: Extract metadata from image"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Extract Image Metadata")
    print("="*60)
    
    image_path = "uploads/example_image.jpg"  # Replace with actual image
    
    if Path(image_path).exists():
        extractor = MetadataExtractor()
        
        # Get all metadata
        metadata = extractor.get_full_metadata(image_path)
        
        print("\nBasic Metadata:")
        for key, value in metadata.get("basic", {}).items():
            print(f"  {key}: {value}")
        
        # Extract GPS coordinates
        if metadata.get("gps"):
            gps = metadata["gps"]
            print(f"\nGPS Coordinates: {gps['latitude']}, {gps['longitude']}")
        else:
            print("\nNo GPS data found")
        
        # Extract camera info
        camera_info = extractor.extract_camera_info(image_path)
        if camera_info:
            print("\nCamera Information:")
            for key, value in camera_info.items():
                print(f"  {key}: {value}")
    else:
        print(f"Image not found: {image_path}")


def example_2_reverse_geocoding():
    """Example: Convert GPS coordinates to address"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Reverse Geocoding (GPS to Address)")
    print("="*60)
    
    # Example coordinates (Statue of Liberty, New York)
    latitude = 40.6892
    longitude = -74.0445
    
    locator = LocationExtractor()
    
    print(f"\nCoordinates: {latitude}, {longitude}")
    print("Performing reverse geocoding...")
    
    location = locator.reverse_geocode(latitude, longitude)
    
    if location:
        print("\nLocation Information:")
        print(f"  Full Address: {location.get('full_address', 'N/A')}")
        print(f"  City: {location.get('city', 'N/A')}")
        print(f"  Country: {location.get('country', 'N/A')}")
    else:
        print("Could not determine location")


def example_3_forward_geocoding():
    """Example: Convert location name to coordinates"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Forward Geocoding (Address to GPS)")
    print("="*60)
    
    location_name = "Times Square, New York"
    
    locator = LocationExtractor()
    
    print(f"\nSearching for: {location_name}")
    print("Performing forward geocoding...")
    
    coords = locator.forward_geocode(location_name)
    
    if coords:
        print("\nCoordinates Found:")
        print(f"  Latitude: {coords['latitude']}")
        print(f"  Longitude: {coords['longitude']}")
        print(f"  Address: {coords['address']}")
    else:
        print("Location not found")


def example_4_reverse_image_search():
    """Example: Perform reverse image search"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Reverse Image Search")
    print("="*60)
    
    image_path = "uploads/example_image.jpg"  # Replace with actual image
    
    if Path(image_path).exists():
        searcher = ReverseImageSearcher()
        
        print(f"\nSearching for image: {image_path}")
        print("Searching Google Images, Bing Images, and Yandex Images...")
        
        results = searcher.search_all(image_path)
        
        for engine, engine_results in results.items():
            print(f"\n{engine.upper()} Images: {len(engine_results)} results")
            for idx, result in enumerate(engine_results[:3], 1):  # Show top 3
                print(f"  {idx}. {result.get('title', 'No title')}")
    else:
        print(f"Image not found: {image_path}")


def example_5_google_maps_analysis():
    """Example: Analyze location using Google Maps"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Google Maps Location Analysis")
    print("="*60)
    
    # Example coordinates
    latitude = 40.7128
    longitude = -74.0060
    
    scraper = GoogleMapsScraper()
    
    print(f"\nAnalyzing location: {latitude}, {longitude}")
    print("Searching for nearby places...")
    
    # Get Street View info
    street_view = scraper.get_street_view_metadata(latitude, longitude)
    print(f"\nStreet View Available: {street_view['street_view_url']}")
    
    # Search nearby restaurants
    print("\nNearby Restaurants:")
    restaurants = scraper.search_nearby_businesses(latitude, longitude, "restaurant")
    for idx, restaurant in enumerate(restaurants[:5], 1):
        print(f"  {idx}. {restaurant['name']}")
    
    # Get comprehensive summary
    print("\nGetting comprehensive map data...")
    map_summary = scraper.get_map_data_summary(latitude, longitude)
    print(f"Attractions found: {len(map_summary.get('attractions', []))}")
    print(f"Hotels found: {len(map_summary.get('hotels', []))}")
    print(f"Restaurants found: {len(map_summary.get('restaurants', []))}")


def example_6_complete_osint_workflow():
    """Example: Complete OSINT analysis workflow"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Complete OSINT Workflow")
    print("="*60)
    
    image_path = "uploads/example_image.jpg"  # Replace with actual image
    
    if not Path(image_path).exists():
        print(f"Image not found: {image_path}")
        return
    
    print(f"\nAnalyzing image: {image_path}\n")
    
    # Step 1: Extract metadata
    print("STEP 1: Extracting Metadata...")
    extractor = MetadataExtractor()
    metadata = extractor.get_full_metadata(image_path)
    print(f"  ✓ Metadata extracted")
    
    # Step 2: Check for GPS data
    print("\nSTEP 2: Checking for Location Data...")
    if metadata.get("gps"):
        lat = metadata["gps"]["latitude"]
        lon = metadata["gps"]["longitude"]
        print(f"  ✓ GPS Found: {lat}, {lon}")
        
        # Step 3: Reverse geocode GPS
        print("\nSTEP 3: Converting GPS to Address...")
        locator = LocationExtractor()
        location = locator.reverse_geocode(lat, lon)
        
        if location:
            print(f"  ✓ Location: {location['full_address']}")
            
            # Step 4: Analyze nearby places
            print("\nSTEP 4: Analyzing Nearby Locations...")
            scraper = GoogleMapsScraper()
            places = scraper.search_nearby_businesses(lat, lon, "restaurant")
            print(f"  ✓ Found {len(places)} nearby restaurants")
    else:
        print("  ✗ No GPS data found in image")
    
    # Step 5: Perform reverse image search
    print("\nSTEP 5: Reverse Image Search...")
    searcher = ReverseImageSearcher()
    results = searcher.search_all(image_path)
    total = sum(len(v) for v in results.values())
    print(f"  ✓ Found {total} results across all engines")
    
    # Step 6: Generate summary
    print("\nSTEP 6: Generating Summary...")
    print("""
    ✓ Analysis Complete
    
    Summary:
    - Image metadata extracted
    - Location identified and verified
    - Nearby places analyzed
    - Image sources found via reverse search
    
    Next Steps:
    1. Verify location using Street View
    2. Cross-reference with other sources
    3. Document findings
    4. Respect privacy and legal considerations
    """)


def example_7_batch_processing():
    """Example: Process multiple images"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Batch Processing Multiple Images")
    print("="*60)
    
    uploads_dir = Path("uploads")
    
    if not uploads_dir.exists():
        print("uploads/ directory not found")
        return
    
    # Get all image files
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]
    images = [f for f in uploads_dir.glob("*") if f.suffix.lower() in image_extensions]
    
    if not images:
        print("No images found in uploads/ directory")
        return
    
    print(f"\nFound {len(images)} images to process")
    
    extractor = MetadataExtractor()
    
    for image_path in images:
        print(f"\nProcessing: {image_path.name}")
        try:
            metadata = extractor.get_full_metadata(str(image_path))
            
            if metadata.get("basic"):
                print(f"  ✓ Size: {metadata['basic'].get('size', 'N/A')}")
            
            if metadata.get("gps"):
                print(f"  ✓ GPS: {metadata['gps'].get('coordinates', 'N/A')}")
            else:
                print(f"  • No GPS data")
        
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")


if __name__ == "__main__":
    """Run examples"""
    
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║       OSINT Module Examples & Usage Guide              ║
    ║                                                        ║
    ║  These examples demonstrate how to use the OSINT      ║
    ║  modules programmatically in your own scripts          ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    # Note: These examples require actual image files
    # Replace "uploads/example_image.jpg" with real paths
    
    # Run examples (uncomment to use)
    # example_1_extract_metadata()
    # example_2_reverse_geocoding()
    # example_3_forward_geocoding()
    # example_4_reverse_image_search()
    # example_5_google_maps_analysis()
    # example_6_complete_osint_workflow()
    # example_7_batch_processing()
    
    print("""
    EXAMPLES GUIDE
    ==============
    
    To run these examples:
    
    1. Place test images in the 'uploads/' directory
    2. Uncomment the example functions you want to run
    3. Run: python examples.py
    
    Available Examples:
    -------------------
    
    1. Extract Image Metadata
       - Gets EXIF data, GPS coordinates, camera info
       - Use: example_1_extract_metadata()
    
    2. Reverse Geocoding
       - Converts GPS coordinates to addresses
       - Use: example_2_reverse_geocoding()
    
    3. Forward Geocoding
       - Converts location names to GPS coordinates
       - Use: example_3_forward_geocoding()
    
    4. Reverse Image Search
       - Searches for image across multiple engines
       - Use: example_4_reverse_image_search()
    
    5. Google Maps Analysis
       - Finds nearby places, attractions, restaurants
       - Use: example_5_google_maps_analysis()
    
    6. Complete OSINT Workflow
       - Runs full analysis pipeline
       - Use: example_6_complete_osint_workflow()
    
    7. Batch Processing
       - Processes multiple images at once
       - Use: example_7_batch_processing()
    
    
    IMPORTS REFERENCE
    =================
    
    from modules.metadata_extractor import MetadataExtractor
    from modules.location_extractor import LocationExtractor
    from modules.image_search import ReverseImageSearcher
    from modules.maps_scraper import GoogleMapsScraper
    from modules.utils import safe_request, download_image
    
    
    BASIC USAGE
    ===========
    
    # Extract metadata
    extractor = MetadataExtractor()
    metadata = extractor.get_full_metadata("image.jpg")
    
    # Reverse geocode
    locator = LocationExtractor()
    address = locator.reverse_geocode(40.7128, -74.0060)
    
    # Reverse image search
    searcher = ReverseImageSearcher()
    results = searcher.search_all("image.jpg")
    
    # Google Maps scraping
    scraper = GoogleMapsScraper()
    places = scraper.search_nearby_businesses(40.7128, -74.0060)
    """)
