"""
File Shortener Worker module for CFAB Browser
Shortens file names with duplicate handling while preserving file extensions and handling pairs
"""

import logging
import os
from typing import Dict, List
from PyQt6.QtCore import pyqtSignal

from .base_worker import BaseToolWorker

logger = logging.getLogger(__name__)


class FileShortenerWorker(BaseToolWorker):
    """Worker for shortening file names with duplicate handling"""

    pairs_found = pyqtSignal(list)  # list of pairs to display
    user_confirmation_needed = pyqtSignal(list)  # waits for user confirmation

    def __init__(self, folder_path: str, max_name_length: int):
        super().__init__(folder_path)
        self.max_name_length = max_name_length
        self.user_confirmed = False
        self.files_info = None

    def confirm_operation(self):
        """Method called after user confirmation"""
        self.user_confirmed = True

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

    def _generate_unique_name(self, base_name: str) -> str:
        """Generates a unique name by adding suffix _D_01, _D_02 if needed"""
        original_name = base_name
        counter = 1

        while True:
            # Check if a file with this name already exists in the folder
            test_files = []
            for ext in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.sbsar', 
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

    def _analyze_files(self) -> Dict[str, List]:
        """Analyzes files in a folder and finds pairs"""
        files_info = {"all_files": [], "pairs": [], "unpaired": []}

        try:
            # File extensions
            archive_extensions = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".sbsar"}
            preview_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}

            # Collect all files
            archive_files = []
            preview_files = []

            for item in os.listdir(self.folder_path):
                item_path = os.path.join(self.folder_path, item)
                if os.path.isfile(item_path):
                    file_ext = os.path.splitext(item)[1].lower()
                    name_without_ext = os.path.splitext(item)[0]

                    if file_ext in archive_extensions:
                        archive_files.append((name_without_ext, item_path))
                    elif file_ext in preview_extensions:
                        preview_files.append((name_without_ext, item_path))

            # Find pairs (files with the same name without extension)
            archive_names = {name: path for name, path in archive_files}
            preview_names = {name: path for name, path in preview_files}

            # Find common names (pairs)
            common_names = set(archive_names.keys()) & set(preview_names.keys())
            for name in common_names:
                files_info["pairs"].append((archive_names[name], preview_names[name]))

            # Find unpaired files
            unpaired_archive = set(archive_names.keys()) - common_names
            unpaired_preview = set(preview_names.keys()) - common_names

            for name in unpaired_archive:
                files_info["unpaired"].append(archive_names[name])
            for name in unpaired_preview:
                files_info["unpaired"].append(preview_names[name])

            # All files
            files_info["all_files"] = files_info["pairs"] + files_info["unpaired"]

            logger.info(f"Found {len(files_info['pairs'])} pairs and {len(files_info['unpaired'])} unpaired files")
            return files_info

        except Exception as e:
            logger.error(f"Error analyzing files: {e}")
            return files_info

    def _rename_file(self, file_path: str, new_name: str) -> bool:
        """Renames a file with error handling"""
        try:
            if not self._validate_single_file_path(file_path):
                return False

            directory = os.path.dirname(file_path)
            file_ext = os.path.splitext(os.path.basename(file_path))[1]
            new_path = os.path.join(directory, new_name + file_ext)

            # Check if target file already exists
            if os.path.exists(new_path):
                logger.error(f"Target file already exists: {new_path}")
                return False

            return self._safe_file_operation(os.rename, file_path, new_path)

        except Exception as e:
            logger.error(f"Error renaming file {file_path}: {e}")
            return False 