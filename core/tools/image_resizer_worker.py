"""
Image Resizer Worker module for CFAB Browser
Resizes image files according to specific scaling rules
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
        
        print(f"🦀 RUST IMAGE_TOOLS: Using LOCAL version from: {image_tools_location} [build: {build_timestamp}, module: {module_number}]")
    except AttributeError:
        print(f"🦀 RUST IMAGE_TOOLS: Module loaded (no location information)")
except ImportError as e:
    print(f"⚠️ Warning: Could not import image_tools module: {e}")
    image_tools = None

logger = logging.getLogger(__name__)


class ImageResizerWorker(BaseToolWorker):
    """Worker for resizing image files"""

    def __init__(self, folder_path: str):
        super().__init__(folder_path)

    def _run_operation(self):
        """Main image resizing method"""
        try:
            self._log_operation_start()

            files_to_resize = self._find_files_to_resize()

            if not files_to_resize:
                self._log_operation_end("No files to resize")
                return

            resized_count = 0
            skipped_count = 0
            error_count = 0

            for i, file_path in enumerate(files_to_resize):
                try:
                    filename = os.path.basename(file_path)
                    logger.debug(f"Processing {i+1}/{len(files_to_resize)}: {filename}")

                    self._log_progress(i, len(files_to_resize), f"Resizing: {filename}")

                    if self._resize_image(file_path):
                        resized_count += 1
                        logger.info(f"Successfully resized: {filename}")
                    else:
                        skipped_count += 1
                        logger.info(f"Skipped (no resizing needed): {filename}")

                    QThread.msleep(1)
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error during resizing {filename}: {e}")
                    QThread.msleep(1)

            # Prepare final message
            message = f"Resizing completed: {resized_count} resized"
            if skipped_count > 0:
                message += f", {skipped_count} skipped (no resizing needed)"
            if error_count > 0:
                message += f", {error_count} errors"

            self._log_progress(len(files_to_resize), len(files_to_resize), "Resizing completed")
            self._log_operation_end(message)

        except Exception as e:
            self._log_error(f"Error during image resizing: {e}")

    def _find_files_to_resize(self) -> List[str]:
        """Finds files to resize"""
        supported_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
        return self._find_files_by_extensions(supported_extensions)

    def _resize_image(self, file_path: str) -> bool:
        """Resizes a single image using Rust module"""
        if image_tools is None:
            logger.error("Rust image_tools module not available")
            return False
            
        logger.info(f"🦀 Calling Rust resize for: {file_path}")
        resized = image_tools.resize_image(file_path)
        logger.info(f"🦀 Rust module returned: {resized}")
        return resized 