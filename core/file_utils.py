"""
Utility module for file and path operations.
Contains functions used by various application components.
"""

import logging
import os
import subprocess
import sys

from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)


def _is_command_available(command: str) -> bool:
    """
    Checks if a command is available in the system.

    Args:
        command (str): Name of the command to check

    Returns:
        bool: True if the command is available, False otherwise
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
    Opens a path in the system file explorer.

    Args:
        path (str): Path to open
        parent_widget: Parent widget for displaying error messages

    Returns:
        bool: True if the operation succeeded, False otherwise
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
            logger.error(f"Path does not exist: {normalized_path}")
            if parent_widget:
                QMessageBox.warning(
                    parent_widget, "Error", f"Path does not exist: {path}"
                )
            return False

        # Bezpieczne wywołania subprocess z walidacją
        if sys.platform == "win32":
            logger.debug(
                f"open_path_in_explorer - uruchamiam os.startfile z ścieżką: "
                f"{normalized_path}"
            )
            try:
                os.startfile(normalized_path)
            except FileNotFoundError:
                logger.error(f"Windows Explorer or path not found: {normalized_path}")
                if parent_widget:
                    QMessageBox.warning(
                        parent_widget, "Error", f"Windows Explorer or path not found: {normalized_path}"
                    )
                return False
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
        logger.error(f"Timeout while opening path: {path}")
        if parent_widget:
            QMessageBox.warning(
                parent_widget, "Error", f"Timeout while opening path: {path}"
            )
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Process error while opening path {path}: {e}")
        if parent_widget:
            QMessageBox.warning(
                parent_widget, "Error", f"Process error while opening: {path}"
            )
        return False
    except Exception as e:
        logger.error(f"Error while opening path {path}: {e}")
        if parent_widget:
            QMessageBox.warning(
                parent_widget, "Error", f"Cannot open path: {path}"
            )
        return False


def open_file_in_default_app(path: str, parent_widget=None) -> bool:
    """
    Opens a file in the system's default application.

    Args:
        path (str): Path to the file
        parent_widget: Parent widget for displaying error messages

    Returns:
        bool: True if the operation succeeded, False otherwise
    """
    try:
        # Walidacja inputu
        if not path or not isinstance(path, str):
            logger.error("Nieprawidłowa ścieżka: pusta lub nie string")
            return False

        # Sprawdź czy plik istnieje
        if not os.path.exists(path):
            logger.error(f"File does not exist: {path}")
            if parent_widget:
                QMessageBox.warning(parent_widget, "Error", f"File does not exist: {path}")
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
        logger.error(f"Timeout while opening file: {path}")
        if parent_widget:
            QMessageBox.warning(
                parent_widget, "Error", f"Timeout while opening file: {path}"
            )
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Process error while opening file {path}: {e}")
        if parent_widget:
            QMessageBox.warning(
                parent_widget, "Error", f"Process error while opening file: {path}"
            )
        return False
    except Exception as e:
        logger.error(f"Error while opening file {path}: {e}")
        if parent_widget:
            QMessageBox.warning(
                parent_widget, "Error", f"Cannot open file: {path}"
            )
        return False
