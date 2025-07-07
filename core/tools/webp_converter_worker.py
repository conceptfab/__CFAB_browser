"""
WebP Converter Worker module for CFAB Browser
Converts image files to WebP format
"""

import logging
import os
from typing import List, Tuple
from PyQt6.QtCore import QThread, pyqtSignal

from .base_worker import BaseWorker

logger = logging.getLogger(__name__)


class WebPConverterWorker(BaseWorker):
    """Worker for converting image files to WebP format"""

    # Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker
    finished = pyqtSignal(str)  # message

    def __init__(self, folder_path: str):
        super().__init__(folder_path)

    def _run_operation(self):
        """Main WebP conversion method"""
        try:
            logger.info(f"Starting WebP conversion in folder: {self.folder_path}")

            files_to_convert = self._find_files_to_convert()

            if not files_to_convert:
                self.finished.emit("No files to convert to WebP")
                return

            converted_count = 0
            skipped_count = 0
            error_count = 0

            for i, (original_path, webp_path) in enumerate(files_to_convert):
                try:
                    logger.info(
                        f"[WebP] START iteration {i+1}/{len(files_to_convert)}: {original_path}"
                    )
                    logger.debug(
                        f"[WebP] {i+1}/{len(files_to_convert)}: {original_path} -> {webp_path}"
                    )

                    logger.info(f"[WebP] Emitting progress_updated for {original_path}")
                    self.progress_updated.emit(
                        i,
                        len(files_to_convert),
                        f"Converting: {os.path.basename(original_path)}",
                    )

                    logger.info(f"[WebP] Checking if {webp_path} already exists")
                    if os.path.exists(webp_path):
                        skipped_count += 1
                        logger.info(f"[WebP] Skipping (already exists): {webp_path}")
                        QThread.msleep(1)
                        continue

                    logger.info(
                        f"[WebP] Starting conversion {original_path} -> {webp_path}"
                    )
                    if self._convert_to_webp(original_path, webp_path):
                        logger.info(
                            f"[WebP] Conversion successful, deleting original file: {original_path}"
                        )
                        try:
                            os.remove(original_path)
                            logger.info(
                                f"[WebP] File {original_path} deleted successfully"
                            )
                        except Exception as e_rm:
                            logger.error(
                                f"[WebP] Error deleting file {original_path}: {e_rm}"
                            )
                            error_count += 1
                            QThread.msleep(1)
                            continue
                        converted_count += 1
                        logger.info(
                            f"[WebP] Successfully converted: {original_path} -> {webp_path}"
                        )
                    else:
                        error_count += 1
                        logger.error(f"[WebP] Conversion error: {original_path}")

                    logger.info(
                        f"[WebP] END iteration {i+1}/{len(files_to_convert)}: {original_path}"
                    )
                    QThread.msleep(1)
                except Exception as e:
                    error_count += 1
                    logger.error(f"[WebP] Error during conversion {original_path}: {e}")
                    QThread.msleep(1)

            logger.info(f"[WebP] Preparing final message")
            message = f"Conversion completed: {converted_count} converted"
            if skipped_count > 0:
                message += f", {skipped_count} skipped (already exist)"
            if error_count > 0:
                message += f", {error_count} errors"

            logger.info(f"[WebP] Emitting final progress_updated")
            self.progress_updated.emit(
                len(files_to_convert), len(files_to_convert), "Conversion completed"
            )
            logger.info(f"[WebP] Emitting finished: {message}")
            self.finished.emit(message)

        except Exception as e:
            error_msg = f"Error during WebP conversion: {e}"
            logger.error(f"[WebP] {error_msg}")
            self.error_occurred.emit(error_msg)

    def _find_files_to_convert(self) -> List[Tuple[str, str]]:
        """Finds files to convert to WebP"""
        files_to_convert = []
        supported_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}

        try:
            for item in os.listdir(self.folder_path):
                item_path = os.path.join(self.folder_path, item)
                if os.path.isfile(item_path):
                    file_ext = os.path.splitext(item)[1].lower()
                    if file_ext in supported_extensions:
                        # Create WebP filename
                        name_without_ext = os.path.splitext(item)[0]
                        webp_filename = f"{name_without_ext}.webp"
                        webp_path = os.path.join(self.folder_path, webp_filename)
                        files_to_convert.append((item_path, webp_path))

            logger.info(f"Found {len(files_to_convert)} files to convert")
            return files_to_convert

        except Exception as e:
            logger.error(f"Error searching for files: {e}")
            return []

    def _convert_to_webp(self, input_path: str, output_path: str) -> bool:
        """Converts a single file to WebP"""
        try:
            logger.info(f"[WebP] _convert_to_webp START: {input_path} -> {output_path}")

            # PATH VALIDATION - using consolidated BaseWorker method
            if not self._validate_file_paths(input_path, output_path):
                logger.error(f"[WebP] Path validation failed: {input_path} -> {output_path}")
                return False

            # Import Pillow here to avoid global requirement
            logger.info(f"[WebP] Importing PIL.Image")
            from PIL import Image

            # Open image
            logger.info(f"[WebP] Opening image: {input_path}")
            with Image.open(input_path) as img:
                logger.info(
                    f"[WebP] Image opened, size: {img.size}, mode: {img.mode}"
                )

                # Convert to RGB if necessary (WebP does not support RGBA)
                if img.mode in ("RGBA", "LA", "P"):
                    logger.info(f"[WebP] Converting mode {img.mode} to RGB")
                    # Create white background
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(
                        img, mask=img.split()[-1] if img.mode == "RGBA" else None
                    )
                    img = background
                    logger.info(f"[WebP] Mode conversion completed")
                elif img.mode != "RGB":
                    logger.info(f"[WebP] Converting mode {img.mode} to RGB")
                    img = img.convert("RGB")
                    logger.info(f"[WebP] Mode conversion completed")

                # Save as WebP with optimal quality
                logger.info(f"[WebP] Saving as WebP: {output_path}")
                img.save(output_path, "WEBP", quality=85, method=6)
                logger.info(f"[WebP] Save completed successfully")
                return True

        except ImportError:
            return self._handle_pillow_import_error("WebP")
        except Exception as e:
            return self._handle_operation_error(input_path, "WebP", e)
        finally:
            logger.info(f"[WebP] _convert_to_webp END: {input_path}") 