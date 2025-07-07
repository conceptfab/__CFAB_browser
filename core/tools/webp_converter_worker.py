"""
WebP Converter Worker module for CFAB Browser
Converts image files to WebP format
"""

import logging
import os
from typing import List
from PyQt6.QtCore import QThread, pyqtSignal

from .base_worker import BaseWorker
from core.__rust import image_tools  # pyright: ignore

# Informational log about loading Rust module
try:
    image_tools_location = image_tools.__file__
    
    # Pobierz informacje o kompilacji
    build_info = image_tools.get_build_info()
    build_timestamp = build_info.get('build_timestamp', 'unknown')
    module_number = build_info.get('module_number', '3')
    
    print(f"🦀 RUST IMAGE_TOOLS (WebP): Using LOCAL version from: {image_tools_location} [build: {build_timestamp}, module: {module_number}]")
except AttributeError:
    print(f"🦀 RUST IMAGE_TOOLS (WebP): Module loaded (no location information)")

logger = logging.getLogger(__name__)


class WebPConverterWorker(BaseWorker):
    """Worker for converting image files to WebP format"""

    # Changed signal name to 'finished' according to BaseWorker
    finished = pyqtSignal(str)  # message

    def __init__(self, folder_path: str):
        super().__init__(folder_path)

    def _run_operation(self):
        """Main method for WebP conversion"""
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

    def _find_files_to_convert(self) -> List[tuple]:
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
        """Converts a single file to WebP using Rust module"""
        logger.info(f"🦀 [WebP] Calling Rust convert for: {input_path}")
        converted = image_tools.convert_to_webp(input_path, output_path)
        logger.info(f"🦀 [WebP] Rust module returned: {converted}")
        return converted 