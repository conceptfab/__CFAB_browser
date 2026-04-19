"""
Worker for asynchronous image resolution loading.
Prevents UI blocking when displaying folder contents with many images.
"""

import logging
from typing import List, Tuple
from PIL import Image
from PyQt6.QtCore import QThread, pyqtSignal

logger = logging.getLogger(__name__)


class ResolutionLoaderWorker(QThread):
    """
    Worker thread that loads image resolutions in the background.
    Emits 'resolution_loaded' signal for each processed file.
    """

    # Signal emits (file_name, resolution_string)
    resolution_loaded = pyqtSignal(str, str)
    finished_loading = pyqtSignal()

    def __init__(self, file_paths: List[Tuple[str, str]]):
        """
        Initialize the worker.
        
        Args:
            file_paths: List of tuples (file_name, full_path) to process
        """
        super().__init__()
        self.file_paths = file_paths
        self._is_running = True

    def run(self):
        """Process files and emit resolution for each"""
        logger.debug(f"Starting resolution loader for {len(self.file_paths)} files")
        
        for file_name, full_path in self.file_paths:
            if not self._is_running:
                break
                
            try:
                resolution = self._get_image_resolution(full_path)
                self.resolution_loaded.emit(file_name, resolution)
            except Exception as e:
                logger.debug(f"Error loading resolution for {file_name}: {e}")
                self.resolution_loaded.emit(file_name, "error")
        
        logger.debug("Resolution loading finished")
        self.finished_loading.emit()

    # Max time to wait for the run loop to observe `_is_running = False`.
    # Pillow can hold us for one file at a time; 3 s is a generous ceiling.
    _STOP_TIMEOUT_MS = 3000

    def stop(self):
        """Request stop and wait up to `_STOP_TIMEOUT_MS` milliseconds.

        A bounded wait prevents shutdown from hanging forever if the worker
        is stuck inside Pillow (e.g. decoding a large or corrupt image).
        """
        self._is_running = False
        if not self.wait(self._STOP_TIMEOUT_MS):
            logger.warning(
                "ResolutionLoaderWorker did not stop within "
                f"{self._STOP_TIMEOUT_MS} ms; requesting interruption."
            )
            self.requestInterruption()
            self.wait(1000)

    def _get_image_resolution(self, file_path: str) -> str:
        """Reads image resolution using Pillow"""
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                return f"{width} x {height}"
        except Exception:
            return "?"
