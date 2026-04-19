"""
File Renamer Worker module for CFAB Browser
Randomizes file names while preserving file extensions and handling pairs
"""

import logging
import os
import secrets
import string

from .base_worker import BaseNameWorker

logger = logging.getLogger(__name__)


class FileRenamerWorker(BaseNameWorker):
    """Worker for randomizing file names. _analyze_files / _rename_file
    come from BaseNameWorker unchanged."""

    def _generate_random_name(self) -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(self.max_name_length))

    def _run_operation(self):
        """Main method for randomizing file names"""
        try:
            self._log_operation_start()
            self.files_info = self._analyze_files()
            if not self.files_info["all_files"]:
                self._log_operation_end("No files to process")
                return
            self.user_confirmation_needed.emit(self.files_info["pairs"])
            while not self.user_confirmed:
                self.msleep(100)
                if self.isInterruptionRequested():
                    return
            self._perform_renaming()
        except Exception as e:
            self._log_error(f"Error during name randomization: {e}")

    def _perform_renaming(self):
        try:
            renamed_count = 0
            error_count = 0
            # Pary
            if self.files_info and self.files_info["pairs"]:
                self._log_progress(0, len(self.files_info["pairs"]), "Randomizowanie nazw par...")
                for i, (archive_file, preview_file) in enumerate(self.files_info["pairs"]):
                    try:
                        archive_name = os.path.splitext(os.path.basename(archive_file))[0]
                        if len(archive_name) > self.max_name_length:
                            new_name = self._generate_random_name()
                            if self._rename_file(archive_file, new_name):
                                renamed_count += 1
                            if self._rename_file(preview_file, new_name):
                                renamed_count += 1
                            self._log_progress(i + 1, len(self.files_info["pairs"]), f"Zrandomizowana para: {new_name}")
                        else:
                            self._log_progress(i + 1, len(self.files_info["pairs"]), f"Pominięto parę: {archive_name}")
                    except Exception as e:
                        error_count += 1
                        self._log_error(f"Error randomizing pair: {e}")
            # Nieparzyste
            if self.files_info and self.files_info["unpaired"]:
                self._log_progress(0, len(self.files_info["unpaired"]), "Randomizing names of unpaired files...")
                for i, file_path in enumerate(self.files_info["unpaired"]):
                    try:
                        filename = os.path.basename(file_path)
                        name_without_ext = os.path.splitext(filename)[0]
                        if len(name_without_ext) > self.max_name_length:
                            new_name = self._generate_random_name()
                            if self._rename_file(file_path, new_name):
                                renamed_count += 1
                            self._log_progress(i + 1, len(self.files_info["unpaired"]), f"Zrandomizowano: {filename} -> {new_name}")
                        else:
                            self._log_progress(i + 1, len(self.files_info["unpaired"]), f"Pominięto: {filename}")
                    except Exception as e:
                        error_count += 1
                        self._log_error(f"Error randomizing {filename}: {e}")
            message = f"Name randomization completed: {renamed_count} files randomized"
            if error_count > 0:
                message += f", {error_count} errors"
            self._log_operation_end(message)
        except Exception as e:
            self._log_error(f"Error during name randomization: {e}")
