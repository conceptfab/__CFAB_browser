"""
ThumbnailCache - Manages in-memory thumbnail caching.
"""

import logging
import threading
from collections import OrderedDict
from typing import Optional

from PyQt6.QtGui import QPixmap

logger = logging.getLogger(__name__)


class ThumbnailCache:
    """
    Class for caching thumbnails (QPixmap) in memory with size limit (LRU).
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ThumbnailCache, cls).__new__(cls)
        return cls._instance

    def __init__(self, max_size_mb: int = 600):
        """
        Initializes the cache.

        Args:
            max_size_mb (int): Maximum cache size in megabytes.
        """
        if not hasattr(self, "_initialized"):  # Prevents re-initialization
            self.max_size_bytes = max_size_mb * 1024 * 1024
            self.max_single_item_size = 50 * 1024 * 1024  # 50MB max per item
            self.current_size_bytes = 0
            self.cache = OrderedDict()
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
        if path in self.cache:
            return  # Already in cache

        pixmap_size = pixmap.toImage().sizeInBytes()
        
        # Check if single item is too large
        if pixmap_size > self.max_single_item_size:
            logger.warning(f"Pixmap too large for cache: {pixmap_size / (1024*1024):.1f} MB > {self.max_single_item_size / (1024*1024):.1f} MB")
            return

        # Check if there is enough space
        while self.current_size_bytes + pixmap_size > self.max_size_bytes:
            self._evict_oldest()

        # Add new item
        self.cache[path] = pixmap
        self.current_size_bytes += pixmap_size
        logger.debug(
            f"Added to cache: {path} ({pixmap_size / 1024:.1f} KB)."
            f" Current cache size: {self.current_size_bytes / (1024*1024):.1f} MB"
        )

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
        self.cache.clear()
        self.current_size_bytes = 0
        logger.info("ThumbnailCache has been cleared.")


# Global cache instance
thumbnail_cache = ThumbnailCache()
