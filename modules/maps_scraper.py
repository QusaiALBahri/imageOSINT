"""Google Maps scraping and location data extraction"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from modules.utils import safe_request, extract_domain
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class GoogleMapsScraper:
    """Scrape and extract location data from Google Maps"""

    @staticmethod
    def _get_driver():
        """Initialize a headless selenium driver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-resource")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    @staticmethod
    def search_location(location_query: str) -> Optional[Dict]:
        """
        Search for location on Google Maps using Selenium for JS rendering
        """
        driver = None
        try:
            driver = GoogleMapsScraper._get_driver()
            url = f"https://www.google.com/maps/search/{location_query}"
            driver.get(url)

            # Wait for content to load
            time.sleep(5)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            # Extract scripts containing JSON data
            scripts = soup.find_all("script")
            location_data = None

            for script in scripts:
                if script.string and "window" in script.string:
                    if "lat" in script.string or "lng" in script.string:
                        location_data = script.string
                        break

            return {
                "query": location_query,
                "url": url,
                "found": location_data is not None,
                "raw_data": location_data,
            }
        except Exception as e:
            logger.error(f"Google Maps location search error: {str(e)}")
            return None
        finally:
            if driver:
                driver.quit()

    @staticmethod
    def extract_places_near_coordinates(latitude: float, 
                                       longitude: float,
                                       radius_meters: int = 1000) -> List[Dict]:
        """
        Extract places near given coordinates using Selenium
        """
        places = []
        driver = None
        try:
            driver = GoogleMapsScraper._get_driver()
            url = f"https://www.google.com/maps/@{latitude},{longitude},15z"
            driver.get(url)

            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, "html.parser")
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
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"Google Maps nearby places error: {str(e)}")
        finally:
            if driver:
                driver.quit()

        return places
