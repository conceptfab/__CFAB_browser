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


def _is_command_available(command: str) -> bool:
    """
    Sprawdza czy komenda jest dostępna w systemie.

    Args:
        command (str): Nazwa komendy do sprawdzenia

    Returns:
        bool: True jeśli komenda jest dostępna, False w przeciwnym razie
    """
    try:
        subprocess.run(
            [command, "--version"], capture_output=True, timeout=5, check=False
        )
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


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
        # Walidacja inputu
        if not path or not isinstance(path, str):
            logger.error("Nieprawidłowa ścieżka: pusta lub nie string")
            return False

        # Normalizuj ścieżkę - napraw mieszane ukośniki
        normalized_path = os.path.normpath(path)
        logger.debug(
            f"open_path_in_explorer - znormalizowana ścieżka: " f"{normalized_path}"
        )

        # Sprawdź czy ścieżka istnieje
        if not os.path.exists(normalized_path):
            logger.error(f"Ścieżka nie istnieje: {normalized_path}")
            if parent_widget:
                QMessageBox.warning(
                    parent_widget, "Błąd", f"Ścieżka nie istnieje: {path}"
                )
            return False

        # Bezpieczne wywołania subprocess z walidacją
        if sys.platform == "win32":
            logger.debug(
                f"open_path_in_explorer - uruchamiam explorer z ścieżką: "
                f"{normalized_path}"
            )
            # Sprawdź czy explorer jest dostępny
            if not _is_command_available("explorer"):
                logger.error("Komenda 'explorer' nie jest dostępna")
                return False
            subprocess.run(["explorer", normalized_path], check=True, timeout=10)
        elif sys.platform == "darwin":  # macOS
            if not _is_command_available("open"):
                logger.error("Komenda 'open' nie jest dostępna")
                return False
            subprocess.run(["open", normalized_path], check=True, timeout=10)
        else:  # Linux
            if not _is_command_available("xdg-open"):
                logger.error("Komenda 'xdg-open' nie jest dostępna")
                return False
            subprocess.run(["xdg-open", normalized_path], check=True, timeout=10)
        logger.info(f"Otworzono ścieżkę w eksploratorze: {normalized_path}")
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout podczas otwierania ścieżki: {path}")
        if parent_widget:
            QMessageBox.warning(
                parent_widget, "Błąd", f"Timeout podczas otwierania ścieżki: {path}"
            )
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Błąd procesu podczas otwierania ścieżki {path}: {e}")
        if parent_widget:
            QMessageBox.warning(
                parent_widget, "Błąd", f"Błąd procesu podczas otwierania: {path}"
            )
        return False
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
        # Walidacja inputu
        if not path or not isinstance(path, str):
            logger.error("Nieprawidłowa ścieżka: pusta lub nie string")
            return False

        # Sprawdź czy plik istnieje
        if not os.path.exists(path):
            logger.error(f"Plik nie istnieje: {path}")
            if parent_widget:
                QMessageBox.warning(parent_widget, "Błąd", f"Plik nie istnieje: {path}")
            return False

        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":  # macOS
            if not _is_command_available("open"):
                logger.error("Komenda 'open' nie jest dostępna")
                return False
            subprocess.run(["open", path], check=True, timeout=10)
        else:  # Linux
            if not _is_command_available("xdg-open"):
                logger.error("Komenda 'xdg-open' nie jest dostępna")
                return False
            subprocess.run(["xdg-open", path], check=True, timeout=10)
        logger.info(f"Otworzono plik w domyślnej aplikacji: {path}")
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout podczas otwierania pliku: {path}")
        if parent_widget:
            QMessageBox.warning(
                parent_widget, "Błąd", f"Timeout podczas otwierania pliku: {path}"
            )
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Błąd procesu podczas otwierania pliku {path}: {e}")
        if parent_widget:
            QMessageBox.warning(
                parent_widget, "Błąd", f"Błąd procesu podczas otwierania pliku: {path}"
            )
        return False
    except Exception as e:
        logger.error(f"Błąd podczas otwierania pliku {path}: {e}")
        if parent_widget:
            QMessageBox.warning(
                parent_widget, "Błąd", f"Nie można otworzyć pliku: {path}"
            )
        return False
