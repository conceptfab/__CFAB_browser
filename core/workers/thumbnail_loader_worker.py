"""
ThumbnailLoaderWorker - Asynchronous thumbnail loading.
"""

import logging
import os

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal
from PyQt6.QtGui import QPixmap

logger = logging.getLogger(__name__)


class ThumbnailLoaderSignals(QObject):
    """Signals for thumbnail loading worker."""
    finished = pyqtSignal(str, QPixmap)  # path, pixmap
    error = pyqtSignal(str, str)  # path, error_message


class ThumbnailLoaderWorker(QRunnable):
    """
    Worker (QRunnable) for asynchronous loading of a single thumbnail.
    Uses QThreadPool for better thread management.
    """

    def __init__(self, path: str):
        super().__init__()
        self.path = path
        self.signals = ThumbnailLoaderSignals()

    def run(self):
        """Loads thumbnail from disk."""
        try:
            if not os.path.exists(self.path):
                raise FileNotFoundError(f"Thumbnail file does not exist: {self.path}")

            pixmap = QPixmap(self.path)

            if pixmap.isNull():
                raise IOError(f"Cannot load QPixmap from file: {self.path}")

            self.signals.finished.emit(self.path, pixmap)
            logger.debug(f"Successfully loaded thumbnail: {self.path}")

        except Exception as e:
            error_msg = f"Error loading thumbnail {self.path}: {e}"
            logger.error(error_msg)
            self.signals.error.emit(self.path, error_msg)
