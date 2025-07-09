"""
ThumbnailCache - Manages in-memory thumbnail caching with thread safety.
"""

import logging
import threading
from collections import OrderedDict
from typing import Optional

from PyQt6.QtGui import QPixmap

logger = logging.getLogger(__name__)


class ThumbnailCache:
    """
    Thread-safe class for caching thumbnails (QPixmap) in memory with size limit (LRU).
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ThumbnailCache, cls).__new__(cls)
        return cls._instance

    def __init__(self, max_size_mb: int = 600):
        """
        Initializes the cache.

        Args:
            max_size_mb (int): Maximum cache size in megabytes.
        """
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self.max_size_bytes = max_size_mb * 1024 * 1024
                    self.max_single_item_size = 50 * 1024 * 1024  # 50MB max per item
                    self.current_size_bytes = 0
                    self.cache = OrderedDict()
                    self._cache_lock = threading.RLock()  # Reentrant lock for cache operations
                    self._initialized = True
                    logger.info(f"ThumbnailCache initialized with limit {max_size_mb} MB.")

    def get(self, path: str) -> Optional[QPixmap]:
        """
        Retrieves QPixmap from cache.

        Args:
            path (str): Key (thumbnail path).

        Returns:
            Optional[QPixmap]: Returns QPixmap if exists, otherwise None.
        """
        with self._cache_lock:
            if path in self.cache:
                # Move element to end to mark as recently used (LRU)
                self.cache.move_to_end(path)
                logger.debug(f"Cache HIT for: {path}")
                return self.cache[path]
            logger.debug(f"Cache MISS for: {path}")
            return None

    def put(self, path: str, pixmap: QPixmap):
        """
        Adds QPixmap to cache.

        Args:
            path (str): Key (thumbnail path).
            pixmap (QPixmap): Thumbnail to cache.
        """
        with self._cache_lock:
            if path in self.cache:
                return  # Already in cache

            pixmap_size = pixmap.toImage().sizeInBytes()
            
            # Check if single item is too large
            if pixmap_size > self.max_single_item_size:
                logger.warning(f"Pixmap too large for cache: {pixmap_size / (1024*1024):.1f} MB > {self.max_single_item_size / (1024*1024):.1f} MB")
                return

            # Ensure there is enough space
            self._ensure_cache_space(pixmap_size)

            # Add new item
            self.cache[path] = pixmap
            self.current_size_bytes += pixmap_size
            logger.debug(
                f"Added to cache: {path} ({pixmap_size / 1024:.1f} KB)."
                f" Current cache size: {self.current_size_bytes / (1024*1024):.1f} MB"
            )

    def _ensure_cache_space(self, required_size: int):
        """
        Ensures there is enough space in cache by evicting oldest items.
        
        Args:
            required_size (int): Size in bytes needed for new item.
        """
        while self.current_size_bytes + required_size > self.max_size_bytes and self.cache:
            self._evict_oldest()

    def _evict_oldest(self):
        """Removes the oldest item from the cache (LRU)."""
        if not self.cache:
            return

        oldest_path, oldest_pixmap = self.cache.popitem(last=False)
        pixmap_size = oldest_pixmap.toImage().sizeInBytes()
        self.current_size_bytes -= pixmap_size
        logger.debug(
            f"Removed from cache (LRU): {oldest_path}."
            f" Current cache size: {self.current_size_bytes / (1024*1024):.1f} MB"
        )

    def clear(self):
        """Clears the entire cache."""
        with self._cache_lock:
            self.cache.clear()
            self.current_size_bytes = 0
            logger.info("ThumbnailCache has been cleared.")

    def get_stats(self) -> dict:
        """
        Returns cache statistics.
        
        Returns:
            dict: Cache statistics including size, item count, etc.
        """
        with self._cache_lock:
            return {
                'current_size_mb': self.current_size_bytes / (1024 * 1024),
                'max_size_mb': self.max_size_bytes / (1024 * 1024),
                'item_count': len(self.cache),
                'utilization_percent': (self.current_size_bytes / self.max_size_bytes) * 100
            }


# Global cache instance
thumbnail_cache = ThumbnailCache()
