"""
ThumbnailLoaderWorker - Asynchronous thumbnail loading.
"""

import logging
import os

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal
from PyQt6.QtGui import QImage

logger = logging.getLogger(__name__)


class ThumbnailLoaderSignals(QObject):
    """Signals for thumbnail loading worker.
    Emits QImage (thread-safe) - convert to QPixmap in GUI thread slot."""
    finished = pyqtSignal(str, QImage)  # path, image
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
        """Loads thumbnail from disk. Uses QImage (thread-safe) instead of QPixmap."""
        try:
            if not os.path.exists(self.path):
                raise FileNotFoundError(f"Thumbnail file does not exist: {self.path}")

            image = QImage(self.path)

            if image.isNull():
                raise IOError(f"Cannot load QImage from file: {self.path}")

            self.signals.finished.emit(self.path, image)
            logger.debug(f"Successfully loaded thumbnail: {self.path}")

        except Exception as e:
            error_msg = f"Error loading thumbnail {self.path}: {e}"
            logger.error(error_msg)
            self.signals.error.emit(self.path, error_msg)
