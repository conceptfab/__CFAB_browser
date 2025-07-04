"""
ThumbnailCache - Zarządzanie buforowaniem miniatur w pamięci.
"""

import logging
import threading
from collections import OrderedDict
from typing import Optional

from PyQt6.QtGui import QPixmap

logger = logging.getLogger(__name__)


class ThumbnailCache:
    """
    Klasa do buforowania miniatur (QPixmap) w pamięci z ograniczeniem rozmiaru (LRU).
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ThumbnailCache, cls).__new__(cls)
        return cls._instance

    def __init__(self, max_size_mb: int = 200):
        """
        Inicjalizuje cache.

        Args:
            max_size_mb (int): Maksymalny rozmiar cache w megabajtach.
        """
        if not hasattr(self, "_initialized"):  # Zapobiega ponownej inicjalizacji
            self.max_size_bytes = max_size_mb * 1024 * 1024
            self.current_size_bytes = 0
            self.cache = OrderedDict()
            self._initialized = True
            logger.info(f"ThumbnailCache zainicjalizowany z limitem {max_size_mb} MB.")

    def get(self, path: str) -> Optional[QPixmap]:
        """
        Pobiera QPixmap z cache.

        Args:
            path (str): Klucz (ścieżka do miniatury).

        Returns:
            Optional[QPixmap]: Zwraca QPixmap jeśli istnieje, w przeciwnym razie None.
        """
        if path in self.cache:
            # Przesuń element na koniec, aby oznaczyć go jako ostatnio używany (LRU)
            self.cache.move_to_end(path)
            logger.debug(f"Cache HIT dla: {path}")
            return self.cache[path]
        logger.debug(f"Cache MISS dla: {path}")
        return None

    def put(self, path: str, pixmap: QPixmap):
        """
        Dodaje QPixmap do cache.

        Args:
            path (str): Klucz (ścieżka do miniatury).
            pixmap (QPixmap): Miniatura do zbuforowania.
        """
        if path in self.cache:
            return  # Już w cache

        pixmap_size = pixmap.toImage().sizeInBytes()

        # Sprawdź, czy jest wystarczająco miejsca
        while self.current_size_bytes + pixmap_size > self.max_size_bytes:
            self._evict_oldest()

        # Dodaj nowy element
        self.cache[path] = pixmap
        self.current_size_bytes += pixmap_size
        logger.debug(
            f"Dodano do cache: {path} ({pixmap_size / 1024:.1f} KB)."
            f" Aktualny rozmiar cache: {self.current_size_bytes / (1024*1024):.1f} MB"
        )

    def _evict_oldest(self):
        """Usuwa najstarszy element z cache (LRU)."""
        if not self.cache:
            return

        oldest_path, oldest_pixmap = self.cache.popitem(last=False)
        pixmap_size = oldest_pixmap.toImage().sizeInBytes()
        self.current_size_bytes -= pixmap_size
        logger.debug(
            f"Usunięto z cache (LRU): {oldest_path}."
            f" Aktualny rozmiar cache: {self.current_size_bytes / (1024*1024):.1f} MB"
        )

    def clear(self):
        """Czyści cały cache."""
        self.cache.clear()
        self.current_size_bytes = 0
        logger.info("ThumbnailCache został wyczyszczony.")

    def get_current_size_mb(self) -> float:
        """Zwraca aktualny rozmiar cache w MB."""
        return self.current_size_bytes / (1024 * 1024)


# Globalna instancja cache
thumbnail_cache = ThumbnailCache()
