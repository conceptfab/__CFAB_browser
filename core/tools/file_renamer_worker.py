"""
File Renamer Worker module for CFAB Browser
Randomizes file names while preserving file extensions and handling pairs
"""

import logging
import os
import secrets
import string
from typing import Dict, List
from PyQt6.QtCore import pyqtSignal

from .base_worker import BaseToolWorker

logger = logging.getLogger(__name__)


class FileRenamerWorker(BaseToolWorker):
    """Worker for randomizing file names"""

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
        """Main method for randomizing file names"""
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

            # Now start randomizing names
            self._perform_renaming()

        except Exception as e:
            self._log_error(f"Error during name randomization: {e}")

    def _perform_renaming(self):
        """Performs the actual name randomization"""
        try:
            renamed_count = 0
            error_count = 0

            # First, pairs
            if self.files_info and self.files_info["pairs"]:
                self._log_progress(0, len(self.files_info["pairs"]), "Randomizowanie nazw par...")
                for i, (archive_file, preview_file) in enumerate(self.files_info["pairs"]):
                    try:
                        # Check if name needs shortening
                        archive_name = os.path.splitext(os.path.basename(archive_file))[0]
                        if len(archive_name) > self.max_name_length:
                            # Generate new name
                            new_name = self._generate_random_name()

                            # Rename archive file
                            if self._rename_file(archive_file, new_name):
                                renamed_count += 1

                            # Rename preview file
                            if self._rename_file(preview_file, new_name):
                                renamed_count += 1

                            logger.info(f"Randomized pair: {new_name}")
                        else:
                            logger.debug(f"Skipped pair (name within limits): {archive_name}")

                        self._log_progress(
                            i + 1,
                            len(self.files_info["pairs"]),
                            f"Zrandomizowana para: {new_name if len(archive_name) > self.max_name_length else archive_name}",
                        )

                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error randomizing pair: {e}")

            # Then unpaired files
            if self.files_info and self.files_info["unpaired"]:
                self._log_progress(0, len(self.files_info["unpaired"]), "Randomizing names of unpaired files...")
                for i, file_path in enumerate(self.files_info["unpaired"]):
                    try:
                        filename = os.path.basename(file_path)
                        name_without_ext = os.path.splitext(filename)[0]

                        if len(name_without_ext) > self.max_name_length:
                            # Generate new name
                            new_name = self._generate_random_name()

                            if self._rename_file(file_path, new_name):
                                renamed_count += 1
                                logger.info(f"Randomized name: {filename} -> {new_name}")
                        else:
                            logger.debug(f"Skipped (name within limits): {filename}")

                        self._log_progress(i + 1, len(self.files_info["unpaired"]), f"Przetwarzanie: {filename}")

                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error randomizing {filename}: {e}")

            # Prepare final message
            message = f"Name randomization completed: {renamed_count} files randomized"
            if error_count > 0:
                message += f", {error_count} errors"

            self._log_operation_end(message)

        except Exception as e:
            self._log_error(f"Error during name shortening: {e}")

    def _analyze_files(self) -> Dict[str, List]:
        """Analyzes files in a folder and finds pairs"""
        files_info = {"all_files": [], "pairs": [], "unpaired": []}

        try:
            # File extensions
            archive_extensions = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".sbsar", ".spsm"}
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

    def _generate_random_name(self) -> str:
        """Generates a random name with specified length"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(self.max_name_length))

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