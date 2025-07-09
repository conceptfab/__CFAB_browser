"""
Prefix Suffix Remover Worker module for CFAB Browser
Removes prefixes or suffixes from file names
"""

import logging
import os

from .base_worker import BaseToolWorker

logger = logging.getLogger(__name__)


class PrefixSuffixRemoverWorker(BaseToolWorker):
    """Worker for removing prefix/suffix from file names"""

    def __init__(self, folder_path: str, text_to_remove: str, mode: str):
        super().__init__(folder_path)
        self.text_to_remove = text_to_remove
        self.mode = mode  # "prefix" lub "suffix"

    def _run_operation(self):
        """Main method for removing prefix/suffix"""
        try:
            self._log_operation_start(f"Starting removal of {self.mode}")

            # Find all files in the folder
            files_to_process = []
            for item in os.listdir(self.folder_path):
                item_path = os.path.join(self.folder_path, item)
                if os.path.isfile(item_path):
                    files_to_process.append(item_path)

            if not files_to_process:
                self._log_operation_end("No files to process")
                return

            # Process files
            renamed_count = 0
            error_count = 0

            for i, file_path in enumerate(files_to_process):
                try:
                    filename_with_ext = os.path.basename(file_path)
                    filename_base, file_extension = os.path.splitext(filename_with_ext)
                    new_filename_base = None

                    # Check if file matches criteria
                    if self.mode == "prefix" and filename_base.startswith(self.text_to_remove):
                        new_filename_base = filename_base.removeprefix(self.text_to_remove).rstrip()
                    elif self.mode == "suffix" and filename_base.endswith(self.text_to_remove):
                        new_filename_base = filename_base.removesuffix(self.text_to_remove).rstrip()

                    if new_filename_base is not None and new_filename_base:
                        new_full_filename = new_filename_base + file_extension
                        new_file_path = os.path.join(self.folder_path, new_full_filename)

                        # Use consolidated validation from base_worker
                        if not self._validate_file_paths(file_path, new_file_path):
                            continue

                        # Rename using safe operation
                        if self._safe_file_operation(os.rename, file_path, new_file_path):
                            renamed_count += 1
                            logger.info(f"Renamed: '{filename_with_ext}' -> '{new_full_filename}'")

                    self._log_progress(i + 1, len(files_to_process), f"Przetwarzanie: {filename_with_ext}")

                except Exception as e:
                    error_count += 1
                    logger.error(f"Error processing {os.path.basename(file_path)}: {e}")

            # Prepare final message
            message = f"Removal of {self.mode} completed: {renamed_count} files changed"
            if error_count > 0:
                message += f", {error_count} errors"

            self._log_operation_end(message)

        except Exception as e:
            self._log_error(f"Error during removal of {self.mode}: {e}") 