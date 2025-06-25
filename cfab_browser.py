#!/usr/bin/env python3
"""
CFAB Browser - Główny plik uruchamiający aplikację
"""

import json
import logging
import os
import sys

from PyQt6.QtWidgets import QApplication

# Import głównego okna
from core.main_window import MainWindow


def setup_logger():
    """Setup logger based on config.json"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
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
    """Ładuje style z pliku QSS"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

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
    """Główna funkcja uruchamiająca aplikację"""
    logger = setup_logger()
    logger.info("Starting CFAB Browser application")

    try:
        app = QApplication(sys.argv)
        app.setApplicationName("CFAB Browser")
        app.setApplicationVersion("1.0.0")

        # Ładowanie stylów
        load_styles(app, logger)

        window = MainWindow()
        window.show()

        logger.info("CFAB Browser window displayed successfully")

        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
