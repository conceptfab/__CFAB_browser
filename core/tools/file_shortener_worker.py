"""
File Shortener Worker module for CFAB Browser
Shortens file names with duplicate handling while preserving file extensions and handling pairs
"""

import logging
import os
from typing import Dict, List
from PyQt6.QtCore import pyqtSignal

from .base_worker import BaseWorker

logger = logging.getLogger(__name__)


class FileShortenerWorker(BaseWorker):
    """Worker for shortening file names with duplicate handling"""

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
        """Main method for shortening file names"""
        try:
            logger.info(f"Starting name shortening in folder: {self.folder_path}")

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

            # Now start shortening names
            self._perform_shortening()

        except Exception as e:
            error_msg = f"Error during name shortening: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def _perform_shortening(self):
        """Performs the actual name shortening"""
        try:
            shortened_count = 0
            error_count = 0

            # First, pairs
            if self.files_info and self.files_info["pairs"]:
                self.progress_updated.emit(
                    0, len(self.files_info["pairs"]), "Shortening pair names..."
                )
                for i, (archive_file, preview_file) in enumerate(
                    self.files_info["pairs"]
                ):
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

                        self.progress_updated.emit(
                            i + 1,
                            len(self.files_info["pairs"]),
                            f"Shortened pair: {archive_name[:20]}...",
                        )

                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error shortening pair: {e}")

            # Then unpaired files
            if self.files_info and self.files_info["unpaired"]:
                self.progress_updated.emit(
                    0,
                    len(self.files_info["unpaired"]),
                    "Shortening unpaired file names...",
                )
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

                        self.progress_updated.emit(
                            i + 1,
                            len(self.files_info["unpaired"]),
                            f"Processing: {filename[:20]}...",
                        )

                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error shortening {filename}: {e}")

            # Prepare final message
            message = f"Name shortening completed: {shortened_count} files shortened"
            if error_count > 0:
                message += f", {error_count} errors"

            self.finished.emit(message)

        except Exception as e:
            error_msg = f"Error during name shortening: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

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

    def _rename_file(self, file_path: str, new_name: str) -> bool:
        """Zmienia nazwę pliku zachowując rozszerzenie"""
        try:
            # Pobierz rozszerzenie
            file_dir = os.path.dirname(file_path)
            file_ext = os.path.splitext(file_path)[1]

            # Utwórz nową nazwę z rozszerzeniem
            new_file_path = os.path.join(file_dir, new_name + file_ext)

            # Use consolidated validation from base_worker
            if not self._validate_file_paths(file_path, new_file_path):
                return False

            # Zmień nazwę
            os.rename(file_path, new_file_path)
            logger.debug(
                f"Zmieniono nazwę: {os.path.basename(file_path)} -> {new_name + file_ext}"
            )
            return True

        except Exception as e:
            logger.error(f"Błąd podczas zmiany nazwy {file_path}: {e}")
            return False 