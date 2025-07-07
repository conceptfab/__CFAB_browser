"""
Image Resizer Worker module for CFAB Browser
Resizes image files according to specific scaling rules
"""

import logging
import os
from typing import List
from PyQt6.QtCore import QThread, pyqtSignal

from .base_worker import BaseWorker
from core.__rust import image_tools

# Log informacyjny o załadowaniu modułu Rust
try:
    image_tools_location = image_tools.__file__
    print(f"🦀 RUST IMAGE_TOOLS: Używam LOKALNEJ wersji z: {image_tools_location}")
except AttributeError:
    print(f"🦀 RUST IMAGE_TOOLS: Moduł załadowany (brak informacji o lokalizacji)")

logger = logging.getLogger(__name__)


class ImageResizerWorker(BaseWorker):
    """Worker for resizing image files"""

    # Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker
    finished = pyqtSignal(str)  # message

    def __init__(self, folder_path: str):
        super().__init__(folder_path)

    def _run_operation(self):
        """Main image resizing method"""
        try:
            logger.info(
                f"Starting image resizing in folder: {self.folder_path}"
            )

            files_to_resize = self._find_files_to_resize()

            if not files_to_resize:
                self.finished.emit("No files to resize")
                return

            resized_count = 0
            skipped_count = 0
            error_count = 0

            for i, file_path in enumerate(files_to_resize):
                try:
                    filename = os.path.basename(file_path)
                    logger.info(
                        f"[Resize] START iteration {i+1}/{len(files_to_resize)}: {filename}"
                    )
                    logger.debug(f"[Resize] {i+1}/{len(files_to_resize)}: {filename}")

                    logger.info(f"[Resize] Emitting progress_updated for {filename}")
                    self.progress_updated.emit(
                        i, len(files_to_resize), f"Resizing: {filename}"
                    )

                    logger.info(f"[Resize] Starting resize: {filename}")
                    if self._resize_image(file_path):
                        resized_count += 1
                        logger.info(f"[Resize] Successfully resized: {filename}")
                    else:
                        skipped_count += 1
                        logger.info(
                            f"[Resize] Skipped (no resizing needed): {filename}"
                        )

                    logger.info(
                        f"[Resize] END iteration {i+1}/{len(files_to_resize)}: {filename}"
                    )
                    QThread.msleep(1)
                except Exception as e:
                    error_count += 1
                    logger.error(f"[Resize] Error during resizing {filename}: {e}")
                    QThread.msleep(1)

            logger.info(f"[Resize] Preparing final message")
            message = f"Resizing completed: {resized_count} resized"
            if skipped_count > 0:
                message += f", {skipped_count} skipped (no resizing needed)"
            if error_count > 0:
                message += f", {error_count} errors"

            logger.info(f"[Resize] Emitting final progress_updated")
            self.progress_updated.emit(
                len(files_to_resize), len(files_to_resize), "Resizing completed"
            )
            logger.info(f"[Resize] Emitting finished: {message}")
            self.finished.emit(message)

        except Exception as e:
            error_msg = f"Error during image resizing: {e}"
            logger.error(f"[Resize] {error_msg}")
            self.error_occurred.emit(error_msg)

    def _find_files_to_resize(self) -> List[str]:
        """Finds files to resize"""
        files_to_resize = []
        supported_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".tiff",
            ".webp",
        }

        try:
            for item in os.listdir(self.folder_path):
                item_path = os.path.join(self.folder_path, item)
                if os.path.isfile(item_path):
                    file_ext = os.path.splitext(item)[1].lower()
                    if file_ext in supported_extensions:
                        files_to_resize.append(item_path)

            logger.info(f"Found {len(files_to_resize)} files to resize")
            return files_to_resize

        except Exception as e:
            logger.error(f"Error searching for files: {e}")
            return []

    def _resize_image(self, file_path: str) -> bool:
        """Resizes a single image using Rust module"""
        logger.info(f"🦀 [Resize] Calling Rust resize for: {file_path}")
        resized = image_tools.resize_image(file_path)
        logger.info(f"🦀 [Resize] Rust module returned: {resized}")
        return resized 