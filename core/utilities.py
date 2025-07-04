"""
Moduł utilities - wspólne funkcje narzędziowe
"""

import logging
import os

logger = logging.getLogger(__name__)


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
    """Aktualizuje pasek statusu w głównym oknie, jeśli widget nadrzędny go posiada."""
    try:
        while widget and widget.parent():
            widget = widget.parent()
            if hasattr(widget, "update_selection_status"):
                widget.update_selection_status()
                break
    except Exception:
        pass
