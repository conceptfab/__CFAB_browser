"""
Moduł utility dla operacji na plikach i ścieżkach.
Zawiera funkcje używane przez różne komponenty aplikacji.
"""

import logging
import os
import subprocess
import sys

from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)


def open_path_in_explorer(path: str, parent_widget=None) -> bool:
    """
    Otwiera ścieżkę w eksploratorze plików systemu.

    Args:
        path (str): Ścieżka do otwarcia
        parent_widget: Widget nadrzędny dla wyświetlania komunikatów błędów

    Returns:
        bool: True jeśli operacja się powiodła, False w przeciwnym razie
    """
    logger.debug(f"open_path_in_explorer - otrzymana ścieżka: {path}")
    try:
        # Normalizuj ścieżkę - napraw mieszane ukośniki
        normalized_path = os.path.normpath(path)
        logger.debug(
            f"open_path_in_explorer - znormalizowana ścieżka: {normalized_path}"
        )

        if sys.platform == "win32":
            logger.debug(
                f"open_path_in_explorer - uruchamiam explorer z ścieżką: "
                f"{normalized_path}"
            )
            subprocess.run(["explorer", normalized_path])
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", normalized_path])
        else:  # Linux
            subprocess.run(["xdg-open", normalized_path])
        logger.info(f"Otworzono ścieżkę w eksploratorze: {normalized_path}")
        return True
    except Exception as e:
        logger.error(f"Błąd podczas otwierania ścieżki {path}: {e}")
        if parent_widget:
            QMessageBox.warning(
                parent_widget, "Błąd", f"Nie można otworzyć ścieżki: {path}"
            )
        return False


def open_file_in_default_app(path: str, parent_widget=None) -> bool:
    """
    Otwiera plik w domyślnej aplikacji systemu.

    Args:
        path (str): Ścieżka do pliku
        parent_widget: Widget nadrzędny dla wyświetlania komunikatów błędów

    Returns:
        bool: True jeśli operacja się powiodła, False w przeciwnym razie
    """
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])
        logger.info(f"Otworzono plik w domyślnej aplikacji: {path}")
        return True
    except Exception as e:
        logger.error(f"Błąd podczas otwierania pliku {path}: {e}")
        if parent_widget:
            QMessageBox.warning(
                parent_widget, "Błąd", f"Nie można otworzyć pliku: {path}"
            )
        return False
