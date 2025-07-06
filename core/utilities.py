"""
Moduł utilities - wspólne funkcje narzędziowe
"""

import logging
import os

logger = logging.getLogger(__name__)


def clear_thumbnail_cache_after_rebuild(is_error: bool = False):
    """
    Czyści cache pamięci RAM po przebudowie assetów.
    Simplified version - removed duplicate logic and excessive logging.
    
    Args:
        is_error (bool): True jeśli czyszczenie po błędzie, False po sukcesie
    """
    try:
        from core.thumbnail_cache import thumbnail_cache
        
        thumbnail_cache.clear()
        
        status = "po błędzie" if is_error else "po przebudowie"
        logger.info(f"Cache pamięci RAM wyczyszczony {status}")
            
    except Exception as e:
        logger.error(f"Błąd podczas czyszczenia thumbnail cache: {e}")


def get_file_size_mb(file_path: str) -> float:
    """
    Pobiera rozmiar pliku w megabajtach

    Args:
        file_path (str): Ścieżka do pliku

    Returns:
        float: Rozmiar pliku w MB
    """
    try:
        if os.path.exists(file_path):
            size_bytes = os.path.getsize(file_path)
            size_mb = size_bytes / (1024 * 1024)  # Konwersja na MB
            return round(size_mb, 2)
        else:
            logger.warning(f"Plik nie istnieje: {file_path}")
            return 0.0
    except Exception as e:
        logger.error(f"Błąd podczas pobierania rozmiaru pliku {file_path}: {e}")
        return 0.0


def update_main_window_status(widget):
    """
    Aktualizuje pasek statusu w głównym oknie.
    Simplified version with optimized parent traversal.
    """
    try:
        # Optimized parent traversal - limit depth to prevent infinite loops
        current_widget = widget
        max_depth = 10  # Safety limit
        depth = 0
        
        while current_widget and depth < max_depth:
            if hasattr(current_widget, "update_selection_status"):
                current_widget.update_selection_status()
                logger.debug("Updated main window status")
                return  # Exit early on success
            
            current_widget = current_widget.parent()
            depth += 1
        
        # If we reach here, no status updater was found
        logger.debug("No status updater found in widget hierarchy")
        
    except Exception as e:
        logger.debug(f"Exception updating main window status: {e}")
