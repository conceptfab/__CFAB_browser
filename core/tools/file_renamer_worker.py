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

from .base_worker import BaseWorker

logger = logging.getLogger(__name__)


class FileRenamerWorker(BaseWorker):
    """Worker for randomizing file names"""

    # Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker
    finished = pyqtSignal(str)  # message
    pairs_found = pyqtSignal(list)  # lista par do wyświetlenia
    user_confirmation_needed = pyqtSignal(list)  # czeka na potwierdzenie użytkownika

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
            logger.info(f"Starting name randomization in folder: {self.folder_path}")

            # Find pairs and files to shorten
            self.files_info = self._analyze_files()

            if not self.files_info["all_files"]:
                self.finished.emit("No files to process")
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
            error_msg = f"Error during name randomization: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def _perform_renaming(self):
        """Performs the actual name randomization"""
        try:
            renamed_count = 0
            error_count = 0

            # First, pairs
            if self.files_info and self.files_info["pairs"]:
                self.progress_updated.emit(
                    0, len(self.files_info["pairs"]), "Randomizing pair names..."
                )
                for i, (archive_file, preview_file) in enumerate(
                    self.files_info["pairs"]
                ):
                    try:
                        # Check if name needs shortening
                        archive_name = os.path.splitext(os.path.basename(archive_file))[
                            0
                        ]
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
                            logger.debug(
                                f"Skipped pair (name within limits): {archive_name}"
                            )

                        self.progress_updated.emit(
                            i + 1,
                            len(self.files_info["pairs"]),
                            f"Randomized pair: {new_name if len(archive_name) > self.max_name_length else archive_name}",
                        )

                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error randomizing pair: {e}")

            # Then unpaired files
            if self.files_info and self.files_info["unpaired"]:
                self.progress_updated.emit(
                    0,
                    len(self.files_info["unpaired"]),
                    "Randomizing unpaired file names...",
                )
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

                        self.progress_updated.emit(
                            i + 1,
                            len(self.files_info["unpaired"]),
                            f"Processing: {filename}",
                        )

                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error randomizing {filename}: {e}")

            # Prepare final message
            message = f"Name randomization completed: {renamed_count} files randomized"
            if error_count > 0:
                message += f", {error_count} errors"

            self.finished.emit(message)

        except Exception as e:
            error_msg = f"Error during name shortening: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def _analyze_files(self) -> Dict[str, List]:
        """Analyzes files in a folder and finds pairs"""
        files_info = {"all_files": [], "pairs": [], "unpaired": []}

        try:
            # File extensions
            archive_extensions = {
                ".zip",
                ".rar",
                ".7z",
                ".tar",
                ".gz",
                ".bz2",
                ".sbsar",
            }
            preview_extensions = {
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".bmp",
                ".tiff",
                ".webp",
            }

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
            all_archive_paths = set(archive_names.values())
            all_preview_paths = set(preview_names.values())
            paired_archive_paths = {archive_names[name] for name in common_names}
            paired_preview_paths = {preview_names[name] for name in common_names}

            unpaired_archives = all_archive_paths - paired_archive_paths
            unpaired_images = all_preview_paths - paired_preview_paths

            files_info["unpaired"] = list(unpaired_archives | unpaired_images)
            files_info["all_files"] = list(all_archive_paths | all_preview_paths)

            logger.info(
                f"Found {len(files_info['pairs'])} pairs and {len(files_info['unpaired'])} unpaired files"
            )
            return files_info

        except Exception as e:
            logger.error(f"Error during file analysis: {e}")
            return files_info

    def _generate_random_name(self) -> str:
        """Generates a random name from a set of 8 digits + 8 letters"""
        # Generate 8 digits and 8 letters
        digits = "".join(secrets.choice(string.digits) for _ in range(8))
        letters = "".join(secrets.choice(string.ascii_uppercase) for _ in range(8))
        # Combine and shuffle
        combined = digits + letters
        shuffled = "".join(secrets.choice(combined) for _ in range(len(combined)))
        return shuffled

    def _rename_file(self, file_path: str, new_name: str) -> bool:
        """Renames a file while preserving its extension"""
        try:
            # Get extension
            file_dir = os.path.dirname(file_path)
            file_ext = os.path.splitext(file_path)[1]

            # Create new name with extension
            new_file_path = os.path.join(file_dir, new_name + file_ext)

            # Check if new name already exists
            if os.path.exists(new_file_path):
                logger.warning(f"File named {new_name + file_ext} already exists")
                return False

            # Rename
            os.rename(file_path, new_file_path)
            logger.debug(
                f"Renamed: {os.path.basename(file_path)} -> {new_name + file_ext}"
            )
            return True

        except Exception as e:
            logger.error(f"Error renaming {file_path}: {e}")
            return False 