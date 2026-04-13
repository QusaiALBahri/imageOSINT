"""Caching layer for storing analysis results"""

import redis
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Manage caching of analysis results"""
    
    def __init__(self, redis_url: str = settings.REDIS_URL):
        """Initialize cache manager"""
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Cache initialized with Redis")
            self.available = True
        except Exception as e:
            logger.warning(f"Redis not available: {str(e)}")
            self.redis_client = None
            self.available = False
            self.memory_cache = {}
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached result"""
        if not self.available:
            return self.memory_cache.get(key)
        
        try:
            cached = self.redis_client.get(key)
            if cached:
                self.redis_client.incr(f"{key}:hits")
                return json.loads(cached)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    def set(self, key: str, value: Dict[str, Any], ttl: int = None) -> bool:
        """Set cached result"""
        if ttl is None:
            ttl = settings.CACHE_TTL
        
        if not self.available:
            self.memory_cache[key] = value
            return True
        
        try:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
            self.redis_client.set(f"{key}:created", datetime.utcnow().isoformat())
            self.redis_client.incr(f"{key}:writes")
            logger.debug(f"Cached result: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cached result"""
        if not self.available:
            self.memory_cache.pop(key, None)
            return True
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        if not self.available:
            self.memory_cache.clear()
            return True
        
        try:
            self.redis_client.flushdb()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.available:
            return key in self.memory_cache
        
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.available:
            return {
                "enabled": False,
                "items": len(self.memory_cache),
                "type": "memory"
            }
        
        try:
            info = self.redis_client.info()
            return {
                "enabled": True,
                "memory_used": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "hit_rate": self._calculate_hit_rate(),
                "type": "redis"
            }
        except Exception as e:
            logger.error(f"Cache stats error: {str(e)}")
            return {"enabled": False, "error": str(e)}
    
    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        if not self.available:
            return 0.0
        
        try:
            hits = int(self.redis_client.get("cache:hits") or 0)
            misses = int(self.redis_client.get("cache:misses") or 0)
            total = hits + misses
            
            if total == 0:
                return 0.0
            
            return (hits / total) * 100
        except Exception:
            return 0.0
    
    def record_hit(self):
        """Record cache hit"""
        if self.available:
            self.redis_client.incr("cache:hits")
    
    def record_miss(self):
        """Record cache miss"""
        if self.available:
            self.redis_client.incr("cache:misses")


# Global cache instance
cache_manager = CacheManager()
