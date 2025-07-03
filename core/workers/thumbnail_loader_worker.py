"""
ThumbnailLoaderWorker - Asynchroniczne ładowanie miniatur.
"""

import logging
import os

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal
from PyQt6.QtGui import QPixmap

logger = logging.getLogger(__name__)


class ThumbnailLoaderSignals(QObject):
    """Sygnały dla workera ładowania miniatur."""
    finished = pyqtSignal(str, QPixmap)  # path, pixmap
    error = pyqtSignal(str, str)  # path, error_message


class ThumbnailLoaderWorker(QRunnable):
    """
    Worker (QRunnable) do asynchronicznego ładowania pojedynczej miniatury.
    Używa QThreadPool dla lepszego zarządzania wątkami.
    """

    def __init__(self, path: str):
        super().__init__()
        self.path = path
        self.signals = ThumbnailLoaderSignals()

    def run(self):
        """Ładuje miniaturę z dysku."""
        try:
            if not os.path.exists(self.path):
                raise FileNotFoundError(f"Plik miniatury nie istnieje: {self.path}")

            pixmap = QPixmap(self.path)

            if pixmap.isNull():
                raise IOError(f"Nie można załadować QPixmap z pliku: {self.path}")

            self.signals.finished.emit(self.path, pixmap)
            logger.debug(f"Pomyślnie załadowano miniaturę: {self.path}")

        except Exception as e:
            error_msg = f"Błąd ładowania miniatury {self.path}: {e}"
            logger.error(error_msg)
            self.signals.error.emit(self.path, error_msg)
