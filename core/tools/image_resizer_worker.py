"""
Image Resizer Worker module for CFAB Browser
Resizes image files according to specific scaling rules
"""

import logging
import os
from typing import List, Tuple
from PyQt6.QtCore import QThread, pyqtSignal

from .base_worker import BaseWorker

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
        """Resizes a single image"""
        try:
            logger.info(f"[Resize] _resize_image START: {file_path}")

            # PATH VALIDATION - using consolidated BaseWorker method
            if not self._validate_single_file_path(file_path):
                logger.error(f"[Resize] Path validation failed: {file_path}")
                return False

            # Import Pillow here to avoid global requirement
            logger.info(f"[Resize] Importing PIL.Image")
            from PIL import Image

            # Open image
            logger.info(f"[Resize] Opening image: {file_path}")
            with Image.open(file_path) as img:
                logger.info(f"[Resize] Image opened, size: {img.size}")

                original_width, original_height = img.size
                new_width, new_height = self._calculate_new_size(
                    original_width, original_height
                )

                logger.info(f"[Resize] New size: {new_width}x{new_height}")

                # Check if resizing is needed
                if new_width >= original_width and new_height >= original_height:
                    logger.info(f"[Resize] Resizing not needed")
                    return False

                # Resize image
                logger.info(f"[Resize] Resizing image")
                resized_img = img.resize(
                    (new_width, new_height), Image.Resampling.LANCZOS
                )

                # Save back to the same file
                logger.info(f"[Resize] Saving resized image: {file_path}")
                resized_img.save(file_path, quality=85, optimize=True)
                logger.info(f"[Resize] Save completed successfully")
                return True

        except ImportError:
            return self._handle_pillow_import_error("Resize")
        except Exception as e:
            return self._handle_operation_error(file_path, "Resize", e)
        finally:
            logger.info(f"[Resize] _resize_image END: {file_path}")

    def _calculate_new_size(self, width: int, height: int) -> Tuple[int, int]:
        """Calculates new dimensions according to scaling rules"""
        # Calculate percentage difference between sides
        max_side = max(width, height)
        min_side = min(width, height)
        difference_percent = ((max_side - min_side) / max_side) * 100

        # If difference <= 30% (square or nearly square)
        if difference_percent <= 30:
            # Scale so that the smaller side is 1024px
            if width <= height:
                # Image is wider than tall or square
                new_width = 1024
                new_height = int((height / width) * 1024)
            else:
                # Image is taller than wide
                new_height = 1024
                new_width = int((width / height) * 1024)
        else:
            # Difference > 30% - scale so that the larger side is 1600px
            if width >= height:
                # Image is wider than tall
                new_width = 1600
                new_height = int((height / width) * 1600)
            else:
                # Image is taller than wide
                new_height = 1600
                new_width = int((width / height) * 1600)

        # Check if new dimensions are not larger than original
        if new_width > width or new_height > height:
            return width, height  # Do not enlarge

        return new_width, new_height 