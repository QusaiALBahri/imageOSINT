"""Utility functions for the OSINT tool"""

import logging
import time
import random
import hashlib
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
import requests
from fake_useragent import UserAgent
from core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ua = UserAgent()


def get_random_user_agent() -> str:
    """Get a random user agent string"""
    try:
        return ua.random
    except Exception:
        return random.choice(settings.USER_AGENTS if hasattr(settings, 'USER_AGENTS') else ["Mozilla/5.0"])


def get_session_with_headers() -> requests.Session:
    """Create a requests session with realistic headers"""
    session = requests.Session()
    session.headers.update({
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    })
    return session


def safe_request(url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
    """Make a safe HTTP request with rate limiting and error handling"""
    time.sleep(RATE_LIMIT_DELAY)
    
    try:
        session = get_session_with_headers()
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        
        if method.upper() == "GET":
            response = session.get(url, **kwargs)
        elif method.upper() == "POST":
            response = session.post(url, **kwargs)
        else:
            return None
        
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.warning(f"Request failed for {url}: {str(e)}")
        return None


def download_image(url: str, output_path: Path) -> bool:
    """Download image from URL to local path"""
    try:
        response = safe_request(url)
        if response and response.content:
            with open(output_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Downloaded image to {output_path}")
            return True
    except Exception as e:
        logger.error(f"Failed to download image from {url}: {str(e)}")
    return False


def generate_file_hash(file_path: Path) -> str:
    """Generate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return "unknown"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file storage"""
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename[:255]  # Limit filename length


def format_results(results: dict) -> dict:
    """Format results for display"""
    return {
        "image_search": results.get("image_search", []),
        "metadata": results.get("metadata", {}),
        "location": results.get("location", {}),
        "maps_data": results.get("maps_data", []),
        "summary": results.get("summary", ""),
    }


def merge_results(*result_dicts) -> dict:
    """Merge multiple result dictionaries"""
    merged = {}
    for result_dict in result_dicts:
        if isinstance(result_dict, dict):
            for key, value in result_dict.items():
                if key not in merged:
                    merged[key] = value
                elif isinstance(merged[key], list) and isinstance(value, list):
                    merged[key].extend(value)
    return merged
