"""Complete file listing and quick reference for OSINT Image Tool"""

PROJECT_FILES = {
    "Application": [
        "app.py - Main Gradio application (1,000+ lines)",
        "config.py - Configuration and constants",
        "run.py - One-click startup script",
    ],
    
    "Core Modules": [
        "modules/metadata_extractor.py - EXIF & metadata extraction",
        "modules/location_extractor.py - Geolocation & geocoding",
        "modules/image_search.py - Reverse image search engines",
        "modules/maps_scraper.py - Google Maps scraping",
        "modules/utils.py - Utility functions & helpers",
        "modules/__init__.py - Module initialization",
    ],
    
    "Documentation": [
        "README.md - Complete user guide (700+ lines)",
        "QUICKSTART.md - 5-minute quick start guide",
        "ARCHITECTURE.md - System design & data flow",
        "SETUP_COMPLETE.md - Project completion summary",
        "examples.py - 7 complete code examples with documentation",
    ],
    
    "Configuration": [
        "config.py - All configuration settings",
        ".env.example - Environment variables template",
        "requirements.txt - Python dependencies (18 packages)",
        ".gitignore - Git ignore rules",
    ],
    
    "Directory Structure": [
        "uploads/ - Uploaded/downloaded images",
        "outputs/ - Generated reports and results",
        "logs/ - Application logs (created at runtime)",
        "modules/ - Core processing modules",
    ],
    
    "Helper Scripts": [
        "setup_dirs.py - Directory initialization",
        "examples.py - Standalone usage examples",
    ]
}

CORE_MODULES_API = {
    "MetadataExtractor": {
        "file": "modules/metadata_extractor.py",
        "methods": [
            "extract_basic_metadata(image_path) → dict",
            "extract_exif_data(image_path) → dict",
            "extract_gps_coordinates(image_path) → tuple(lat, lon)",
            "get_full_metadata(image_path) → dict",
            "extract_creation_date(image_path) → str",
            "extract_camera_info(image_path) → dict",
        ]
    },
    
    "LocationExtractor": {
        "file": "modules/location_extractor.py",
        "methods": [
            "reverse_geocode(latitude, longitude) → dict",
            "forward_geocode(location_name) → dict",
            "extract_locations_from_text(text) → list",
            "get_location_bounds(lat, lon, radius_km) → dict",
            "estimate_accuracy(metadata) → dict",
            "analyze_location_data() → dict",
        ]
    },
    
    "ReverseImageSearcher": {
        "file": "modules/image_search.py",
        "methods": [
            "search_google(image_path) → list",
            "search_bing(image_path) → list",
            "search_yandex(image_path) → list",
            "search_all(image_path) → dict",
            "search_by_url(image_url) → dict",
            "get_meta_description(result_url) → str",
        ]
    },
    
    "GoogleMapsScraper": {
        "file": "modules/maps_scraper.py",
        "methods": [
            "search_location(location_query) → dict",
            "extract_places_near_coordinates(lat, lon, radius) → list",
            "get_street_view_metadata(lat, lon) → dict",
            "search_nearby_businesses(lat, lon, type) → list",
            "extract_map_coordinates_from_url(url) → tuple",
            "get_map_data_summary(lat, lon) → dict",
        ]
    },
}

DEPENDENCIES = {
    "Web Framework": [
        "gradio==4.36.1 - Web interface",
    ],
    
    "Image Processing": [
        "pillow==10.1.0 - Image manipulation",
        "exifread==3.0.0 - EXIF data reading",
        "opencv-python==4.8.1.78 - Image analysis",
    ],
    
    "Web Scraping": [
        "requests==2.31.0 - HTTP client",
        "beautifulsoup4==4.12.2 - HTML parsing",
        "lxml==4.9.3 - XML/HTML processing",
    ],
    
    "Geolocation": [
        "geopy==2.4.0 - Geocoding services",
    ],
    
    "Browser Automation": [
        "selenium==4.15.2 - Browser control",
        "selenium-wire==5.1.0 - Request/response intercepting",
    ],
    
    "Utilities": [
        "fake-useragent==1.4.0 - User agent rotation",
        "urllib3==2.1.0 - URL utilities",
        "python-dotenv==1.0.0 - Environment variables",
    ],
    
    "Optional": [
        "bing-image-downloader==1.3.11 - Bing image downloading",
        "yandex-reverse-image-search==1.0.0 - Yandex integration",
        "google-search-results==2.4.2 - Google search API",
    ]
}

FEATURES = {
    "Reverse Image Search": [
        "✓ Google Images",
        "✓ Bing Images",
        "✓ Yandex Images",
    ],
    
    "Image Analysis": [
        "✓ EXIF data extraction",
        "✓ GPS coordinates extraction",
        "✓ Camera information",
        "✓ Creation date analysis",
        "✓ Format and size detection",
    ],
    
    "Location Tools": [
        "✓ GPS to address (reverse geocoding)",
        "✓ Address to GPS (forward geocoding)",
        "✓ Accuracy assessment",
        "✓ Location bounds calculation",
        "✓ Comprehensive location analysis",
    ],
    
    "Google Maps": [
        "✓ Nearby attractions search",
        "✓ Restaurant/hotel discovery",
        "✓ Street View metadata",
        "✓ Location search",
        "✓ Business type filtering",
    ],
    
    "User Interface": [
        "✓ Gradio web dashboard",
        "✓ Image upload/URL input",
        "✓ Multiple analysis tabs",
        "✓ JSON result display",
        "✓ Comprehensive reports",
    ],
    
    "Ethics & Safety": [
        "✓ Rate limiting",
        "✓ User agent rotation",
        "✓ Error handling",
        "✓ Logging",
        "✓ Respectful scraping",
    ]
}

if __name__ == "__main__":
    print("=" * 70)
    print("OSINT IMAGE SEARCH & GOOGLE MAPS SCRAPER - FILE REFERENCE")
    print("=" * 70)
    print()
    
    print("📂 PROJECT FILES")
    print("-" * 70)
    for category, files in PROJECT_FILES.items():
        print(f"\n{category}:")
        for file in files:
            print(f"  • {file}")
    
    print("\n\n📚 CORE MODULES API")
    print("-" * 70)
    for module_name, info in CORE_MODULES_API.items():
        print(f"\n{module_name} ({info['file']})")
        for method in info['methods']:
            print(f"  • {method}")
    
    print("\n\n📦 DEPENDENCIES")
    print("-" * 70)
    for category, packages in DEPENDENCIES.items():
        print(f"\n{category}:")
        for package in packages:
            print(f"  • {package}")
    
    print("\n\n✨ FEATURES")
    print("-" * 70)
    for category, features in FEATURES.items():
        print(f"\n{category}:")
        for feature in features:
            print(f"  {feature}")
    
    print("\n\n" + "=" * 70)
    print("QUICK START")
    print("=" * 70)
    print("\nWindows:")
    print("  python run.py")
    print("\nmacOS/Linux:")
    print("  python3 run.py")
    print("\nAccess: http://localhost:7860")
    print("\n" + "=" * 70)
