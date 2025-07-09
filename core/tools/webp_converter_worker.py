"""
WebP Converter Worker module for CFAB Browser
Converts image files to WebP format
"""

import logging
import os
from typing import List
from PyQt6.QtCore import QThread

from .base_worker import BaseToolWorker

# Import Rust module without pyright ignore
try:
    from core.__rust import image_tools
    
    # Informational log about loading Rust module
    try:
        image_tools_location = image_tools.__file__
        build_info = image_tools.get_build_info()
        build_timestamp = build_info.get('build_timestamp', 'unknown')
        module_number = build_info.get('module_number', '3')
        
        print(f"🦀 RUST IMAGE_TOOLS (WebP): Using LOCAL version from: {image_tools_location} [build: {build_timestamp}, module: {module_number}]")
    except AttributeError:
        print(f"🦀 RUST IMAGE_TOOLS (WebP): Module loaded (no location information)")
except ImportError as e:
    print(f"⚠️ Warning: Could not import image_tools module: {e}")
    image_tools = None

logger = logging.getLogger(__name__)


class WebPConverterWorker(BaseToolWorker):
    """Worker for converting image files to WebP format"""

    def __init__(self, folder_path: str):
        super().__init__(folder_path)

    def _run_operation(self):
        """Main method for WebP conversion"""
        try:
            self._log_operation_start()

            files_to_convert = self._find_files_to_convert()

            if not files_to_convert:
                self._log_operation_end("No files to convert to WebP")
                return

            converted_count = 0
            skipped_count = 0
            error_count = 0

            for i, (original_path, webp_path) in enumerate(files_to_convert):
                try:
                    logger.debug(f"Processing {i+1}/{len(files_to_convert)}: {original_path}")

                    self._log_progress(
                        i,
                        len(files_to_convert),
                        f"Converting: {os.path.basename(original_path)}",
                    )

                    if os.path.exists(webp_path):
                        skipped_count += 1
                        logger.info(f"Skipping (already exists): {webp_path}")
                        QThread.msleep(1)
                        continue

                    if self._convert_to_webp(original_path, webp_path):
                        # Delete original file after successful conversion
                        if self._safe_file_operation(os.remove, original_path):
                            converted_count += 1
                            logger.info(f"Successfully converted: {original_path} -> {webp_path}")
                        else:
                            error_count += 1
                    else:
                        error_count += 1
                        logger.error(f"Conversion error: {original_path}")

                    QThread.msleep(1)
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error during conversion {original_path}: {e}")
                    QThread.msleep(1)

            # Prepare final message
            message = f"Conversion completed: {converted_count} converted"
            if skipped_count > 0:
                message += f", {skipped_count} skipped (already exist)"
            if error_count > 0:
                message += f", {error_count} errors"

            self._log_progress(len(files_to_convert), len(files_to_convert), "Conversion completed")
            self._log_operation_end(message)

        except Exception as e:
            self._log_error(f"Error during WebP conversion: {e}")

    def _find_files_to_convert(self) -> List[tuple]:
        """Finds files to convert to WebP"""
        supported_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
        files_to_convert = []

        try:
            image_files = self._find_files_by_extensions(supported_extensions)
            
            for item_path in image_files:
                # Create WebP filename
                name_without_ext = os.path.splitext(os.path.basename(item_path))[0]
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
        if image_tools is None:
            logger.error("Rust image_tools module not available")
            return False
            
        logger.info(f"🦀 Calling Rust convert for: {input_path}")
        converted = image_tools.convert_to_webp(input_path, output_path)
        logger.info(f"🦀 Rust module returned: {converted}")
        return converted 