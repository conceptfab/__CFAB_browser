"""
File Shortener Worker module for CFAB Browser
Shortens file names with duplicate handling while preserving file extensions and handling pairs
"""

import logging
import os
from typing import Dict, List
from PyQt6.QtCore import pyqtSignal

from .base_worker import BaseNameWorker

logger = logging.getLogger(__name__)


class FileShortenerWorker(BaseNameWorker):
    """Worker for shortening file names with duplicate handling"""

    def _generate_unique_name(self, base_name: str) -> str:
        """Generates a unique name by adding suffix _D_01, _D_02 if needed"""
        original_name = base_name
        counter = 1

        while True:
            # Check if a file with this name already exists in the folder
            test_files = []
            for ext in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.sbsar', '.spsm',
                       '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
                test_file = os.path.join(self.folder_path, f"{base_name}{ext}")
                if os.path.exists(test_file):
                    test_files.append(test_file)
            
            if not test_files:
                return base_name

            # If it exists, try with suffix _D_01, _D_02, etc.
            base_name = f"{original_name}_D_{counter:02d}"
            counter += 1

            # Protection against infinite loop
            if counter > 99:
                logger.warning(f"Maximum number of attempts reached for {original_name}")
                return f"{original_name}_D_{counter}"

    def _run_operation(self):
        """Main method for shortening file names"""
        try:
            self._log_operation_start()

            # Find pairs and files to shorten
            self.files_info = self._analyze_files()

            if not self.files_info["all_files"]:
                self._log_operation_end("No files to process")
                return

            # Send list of pairs for display and wait for confirmation
            self.user_confirmation_needed.emit(self.files_info["pairs"])

            # Wait for user confirmation
            while not self.user_confirmed:
                self.msleep(100)  # Wait 100ms
                if self.isInterruptionRequested():
                    return

            # Now start shortening names
            self._perform_shortening()

        except Exception as e:
            self._log_error(f"Error during name shortening: {e}")

    def _perform_shortening(self):
        """Performs the actual name shortening"""
        try:
            shortened_count = 0
            error_count = 0

            # First, pairs
            if self.files_info and self.files_info["pairs"]:
                self._log_progress(0, len(self.files_info["pairs"]), "Skracanie nazw par...")
                for i, (archive_file, preview_file) in enumerate(self.files_info["pairs"]):
                    try:
                        # Check if name needs shortening
                        archive_name = os.path.splitext(os.path.basename(archive_file))[0]
                        if len(archive_name) > self.max_name_length:
                            # Generate shortened name
                            shortened_name = archive_name[:self.max_name_length]
                            # Check for conflicts and add suffix if needed
                            unique_name = self._generate_unique_name(shortened_name)

                            # Rename archive file
                            if self._rename_file(archive_file, unique_name):
                                shortened_count += 1

                            # Rename preview file
                            if self._rename_file(preview_file, unique_name):
                                shortened_count += 1

                            logger.info(f"Shortened pair: {archive_name} -> {unique_name}")
                        else:
                            logger.debug(f"Skipped pair (name within limits): {archive_name}")

                        self._log_progress(i + 1, len(self.files_info["pairs"]), f"Shortened pair: {archive_name[:20]}...")

                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error shortening pair: {e}")

            # Then unpaired files
            if self.files_info and self.files_info["unpaired"]:
                self._log_progress(0, len(self.files_info["unpaired"]), "Shortening names of unpaired files...")
                for i, file_path in enumerate(self.files_info["unpaired"]):
                    try:
                        filename = os.path.basename(file_path)
                        name_without_ext = os.path.splitext(filename)[0]

                        if len(name_without_ext) > self.max_name_length:
                            # Generate shortened name
                            shortened_name = name_without_ext[:self.max_name_length]
                            # Check for conflicts and add suffix if needed
                            unique_name = self._generate_unique_name(shortened_name)

                            if self._rename_file(file_path, unique_name):
                                shortened_count += 1
                                logger.info(f"Shortened name: {filename} -> {unique_name}")
                        else:
                            logger.debug(f"Skipped (name within limits): {filename}")

                        self._log_progress(i + 1, len(self.files_info["unpaired"]), f"Przetwarzanie: {filename[:20]}...")

                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error shortening {filename}: {e}")

            # Prepare final message
            message = f"Name shortening completed: {shortened_count} files shortened"
            if error_count > 0:
                message += f", {error_count} errors"

            self._log_operation_end(message)

        except Exception as e:
            self._log_error(f"Error during name shortening: {e}") 