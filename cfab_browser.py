#!/usr/bin/env python3
"""
CFAB Browser - Main application startup file
"""

import logging
import os
import sys
import time
import traceback


# ---------------------------------------------------------------------------
# Hide the system console window on Windows, no matter how we were launched.
#
# When started via ``python.exe`` (terminal, VS Code, double-click on .py),
# Windows attaches a console window. The user wants ALL output inside the
# in-app Console tab — never in a separate terminal. Hide the console window
# immediately; the in-app ConsoleTab still captures stdout/stderr through the
# early stdio buffer installed below.
# ---------------------------------------------------------------------------

if sys.platform == "win32" and os.environ.get("CFAB_KEEP_CONSOLE") != "1":
    try:
        import ctypes

        _hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if _hwnd:
            ctypes.windll.user32.ShowWindow(_hwnd, 0)  # SW_HIDE
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Bootstrap: keep the app launchable without a system console.
#
# When started through ``pythonw.exe`` on Windows or via a macOS ``.app``
# bundle, ``sys.stdout`` / ``sys.stderr`` may be ``None``. Any ``print()``
# would then crash before the UI is up. Provide a no-op fallback so the
# application starts cleanly; the in-app ConsoleTab takes over once created.
# ---------------------------------------------------------------------------


class _NullStream:
    def write(self, *args, **kwargs):
        return 0

    def flush(self):
        pass

    def isatty(self):
        return False


if sys.stdout is None:
    sys.stdout = _NullStream()
if sys.stderr is None:
    sys.stderr = _NullStream()


# Capture early log records and stdout/stderr writes so they can be replayed
# inside the ConsoleTab. Must happen BEFORE importing any module that may
# print at import time (scanner, image tools, hash utils, ...).
from core.console_tab import install_early_log_buffer, install_early_stdio_buffer

install_early_log_buffer()
install_early_stdio_buffer()

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QSplashScreen

# Import main window
from core.json_utils import load_from_file
from core.main_window import MainWindow
from core.thumbnail_cache import ThumbnailCache


def setup_logger():
    """Setup logger based on config.json"""
    try:
        config = load_from_file("config.json")
        logger_level = config.get("logger_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, logger_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger = logging.getLogger(__name__)
        logger.info(f"Logger initialized with level: {logger_level}")
        return logger
    except Exception as e:
        # Fallback logger setup
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to load config.json: {e}")
        return logger


def load_styles(app, logger):
    """Loads styles from QSS file"""
    try:
        config = load_from_file("config.json")

        use_styles = config.get("use_styles", True)

        if not use_styles:
            logger.info("Styles disabled in config")
            return

        styles_path = os.path.join("core", "resources", "styles.qss")

        if not os.path.exists(styles_path):
            logger.warning(f"Styles file not found: {styles_path}")
            return

        with open(styles_path, "r", encoding="utf-8") as f:
            styles = f.read()

        app.setStyleSheet(styles)
        logger.info("Styles loaded successfully")

    except Exception as e:
        logger.error(f"Failed to load styles: {e}")


def main():
    """Main function that starts the application"""
    logger = setup_logger()
    logger.info("Starting CFAB Browser application")

    try:
        app = QApplication(sys.argv)
        app.setApplicationName("CFAB Browser")
        app.setApplicationVersion("1.0.0")

        # Ekran powitalny (splash screen)
        pixmap = QPixmap("core/resources/img/icon.png")
        splash = QSplashScreen(pixmap)
        splash.show()

        # Daj czas na wyświetlenie ekranu powitalnego
        app.processEvents()

        # Ładowanie stylów
        load_styles(app, logger)

        # Inicjalizacja cache miniatur po utworzeniu QApplication
        global thumbnail_cache
        thumbnail_cache = ThumbnailCache()

        logger.info("Creating MainWindow...")
        window = MainWindow()

        logger.info("Showing MainWindow...")
        window.show()
        splash.finish(window)

        # Aktualizuj status po uruchomieniu
        window.update_status("Application ready")

        logger.info("CFAB Browser window displayed successfully")

        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
