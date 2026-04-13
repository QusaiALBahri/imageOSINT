"""Reverse image search across multiple search engines"""

import logging
import io
import base64
from typing import Dict, List, Optional
from pathlib import Path
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
from modules.utils import safe_request, get_random_user_agent, extract_domain

logger = logging.getLogger(__name__)


class ReverseImageSearcher:
    """Perform reverse image search across multiple engines"""
    
    def __init__(self):
        """Initialize the reverse image searcher"""
        self.results = {
            "google": [],
            "bing": [],
            "yandex": [],
        }
    
    def search_google(self, image_path: str) -> List[Dict]:
        """
        Search Google Images with reverse image
        
        Args:
            image_path: Path to local image file
            
        Returns:
            List of search results
        """
        try:
            results = []
            
            # Read image and convert to base64
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Google Images search
            url = "https://www.google.com/searchbyimage"
            files = {"encoded_image": (Path(image_path).name, image_data)}
            
            response = safe_request(url, method="POST", files=files, allow_redirects=True)
            
            if response:
                # Parse the response to extract similar images
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Extract image search results
                image_results = soup.find_all("img", limit=10)
                
                for idx, img in enumerate(image_results):
                    if img.get("alt") and img.get("src"):
                        results.append({
                            "title": img.get("alt", "")[:100],
                            "url": img.get("src", ""),
                            "source": "Google Images",
                            "rank": idx + 1,
                            "image_url": img.get("src", ""),
                        })
                
                logger.info(f"Google Images found {len(results)} results")
            
            return results
        except Exception as e:
            logger.error(f"Google Images search error: {str(e)}")
            return []
    
    def search_bing(self, image_path: str) -> List[Dict]:
        """
        Search Bing Images with reverse image
        
        Args:
            image_path: Path to local image file
            
        Returns:
            List of search results
        """
        try:
            results = []
            
            # Read image
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Bing Images search
            url = "https://www.bing.com/images/search"
            files = {"cbir": ("image", image_data)}
            
            response = safe_request(url, method="POST", files=files)
            
            if response:
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Extract image results from Bing's JSON data
                images = soup.find_all("img", {"class": "mimg"}, limit=10)
                
                for idx, img in enumerate(images):
                    if img.get("alt"):
                        results.append({
                            "title": img.get("alt", "")[:100],
                            "url": img.get("src", ""),
                            "source": "Bing Images",
                            "rank": idx + 1,
                            "image_url": img.get("src", ""),
                        })
                
                logger.info(f"Bing Images found {len(results)} results")
            
            return results
        except Exception as e:
            logger.error(f"Bing Images search error: {str(e)}")
            return []
    
    def search_yandex(self, image_path: str) -> List[Dict]:
        """
        Search Yandex Images with reverse image
        
        Args:
            image_path: Path to local image file
            
        Returns:
            List of search results
        """
        try:
            results = []
            
            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Prepare Yandex search
            url = "https://yandex.com/images"
            files = {"upfile": ("image", image_data)}
            params = {"rpt": "imageview"}
            
            response = safe_request(url, files=files, params=params)
            
            if response:
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Extract results
                images = soup.find_all("img", limit=10)
                
                for idx, img in enumerate(images):
                    if img.get("alt") or img.get("src"):
                        results.append({
                            "title": img.get("alt", "Similar Image")[:100],
                            "url": img.get("src", ""),
                            "source": "Yandex Images",
                            "rank": idx + 1,
                            "image_url": img.get("src", ""),
                        })
                
                logger.info(f"Yandex Images found {len(results)} results")
            
            return results
        except Exception as e:
            logger.error(f"Yandex Images search error: {str(e)}")
            return []
    
    def search_all(self, image_path: str) -> Dict[str, List[Dict]]:
        """
        Search all engines and compile results
        
        Args:
            image_path: Path to local image file
            
        Returns:
            Dictionary with results from each engine
        """
        results = {
            "google": self.search_google(image_path),
            "bing": self.search_bing(image_path),
            "yandex": self.search_yandex(image_path),
        }
        
        self.results = results
        
        # Compile summary
        total_results = sum(len(v) for v in results.values())
        logger.info(f"Total reverse image search results: {total_results}")
        
        return results
    
    def search_by_url(self, image_url: str) -> Dict[str, List[Dict]]:
        """
        Perform reverse image search using URL instead of local file
        
        Args:
            image_url: URL of the image to search
            
        Returns:
            Dictionary with results from each engine
        """
        results = {}
        
        try:
            # Google Images URL-based search
            google_url = f"https://www.google.com/searchbyimage?image_url={quote(image_url)}"
            response = safe_request(google_url)
            google_results = []
            
            if response:
                soup = BeautifulSoup(response.content, "html.parser")
                images = soup.find_all("img", limit=10)
                for idx, img in enumerate(images):
                    google_results.append({
                        "title": img.get("alt", "")[:100],
                        "url": img.get("src", ""),
                        "source": "Google Images",
                        "rank": idx + 1,
                    })
            
            results["google"] = google_results
            
            # Bing URL-based search
            bing_url = f"https://www.bing.com/images/search?view=detailv2&iss=sbi&q=imgurl:{image_url}"
            results["bing"] = []
            
            # Yandex URL-based search  
            yandex_url = f"https://yandex.com/images/search?rpt=imageview&url={quote(image_url)}"
            results["yandex"] = []
            
            logger.info(f"URL-based reverse search completed for {image_url}")
            
        except Exception as e:
            logger.error(f"URL-based reverse search error: {str(e)}")
        
        return results
    
    def get_meta_description(self, result_url: str) -> Optional[str]:
        """
        Extract meta description from result URL
        
        Args:
            result_url: URL to extract description from
            
        Returns:
            Meta description or None
        """
        try:
            response = safe_request(result_url)
            if response:
                soup = BeautifulSoup(response.content, "html.parser")
                meta = soup.find("meta", attrs={"name": "description"})
                if meta:
                    return meta.get("content", "")
        except Exception as e:
            logger.debug(f"Could not extract meta description: {str(e)}")
        
        return None
