"""Configuration and constants for OSINT Image Tool"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Create directories if they don't exist
UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# Request settings - Ethical scraping parameters
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
RATE_LIMIT_DELAY = 1  # seconds between requests

# User agents - Rotate to avoid detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# Image search engines
SEARCH_ENGINES = {
    "google": {
        "url": "https://www.google.com/searchbyimage",
        "enabled": True
    },
    "bing": {
        "url": "https://www.bing.com/images/searchbyimage",
        "enabled": True
    },
    "yandex": {
        "url": "https://yandex.com/images/search",
        "enabled": True
    },
}

# Image constraints
MAX_IMAGE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_FORMATS = ["JPEG", "PNG", "GIF", "WEBP", "BMP"]

# MongoDB/Database (optional)
USE_DATABASE = False
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")

# API Keys (if using official APIs)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
REVERSE_IMAGE_API_KEY = os.getenv("REVERSE_IMAGE_API_KEY", "")

# Scraping settings
HEADLESS_BROWSER = True
MAX_RESULTS_PER_ENGINE = 10
SCRAPE_TIMEOUT = 30

# Geolocation
REVERSE_GEOCODER = "nominatim"  # or "geonames"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "app.log"
