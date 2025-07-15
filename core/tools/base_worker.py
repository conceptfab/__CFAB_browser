"""
Base Worker module for CFAB Browser
Contains the base worker class for all file operations
"""

import logging
import os
from PyQt6.QtCore import QThread, pyqtSignal

logger = logging.getLogger(__name__)


class BaseWorker(QThread):
    """Base class for file operation workers."""

    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(str)  # message
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self, folder_path: str):
        super().__init__()
        self.folder_path = folder_path
        self._should_stop = False

    def run(self):
        try:
            if not self.folder_path or not os.path.exists(self.folder_path):
                error_msg = f"Invalid folder: {self.folder_path}"
                self.error_occurred.emit(error_msg)
                return

            self._run_operation()

        except Exception as e:
            error_msg = f"Error during operation: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def _run_operation(self):
        """Method to be overridden in derived classes."""
        raise NotImplementedError(
            "The _run_operation method must be implemented in the derived class."
        )

    def stop(self):
        """Safely stops the thread"""
        self._should_stop = True
        self.quit()
        if not self.wait(3000):
            self.terminate()
    
    # ========================================
    # CONSOLIDATED PATH VALIDATION METHODS
    # ========================================
    
    def _validate_file_paths(self, input_path: str, output_path: str) -> bool:
        """
        Consolidated path validation for input/output file operations.
        Used by converters and similar workers that create new files.
        """
        try:
            # Validate input file
            if not self._validate_input_file(input_path):
                return False
            
            # Validate output path
            if not self._validate_output_path(output_path):
                return False
            
            # Additional cross-validation
            if os.path.abspath(input_path) == os.path.abspath(output_path):
                logger.error(f"Input and output paths are identical: {input_path}")
                return False
            
            logger.debug(f"Path validation successful: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error during path validation: {e}")
            return False
    
    def _validate_single_file_path(self, file_path: str) -> bool:
        """
        Consolidated path validation for single file operations.
        Used by processors that modify existing files in-place.
        """
        try:
            # Validate input file
            if not self._validate_input_file(file_path):
                return False
            
            # Check write permissions (for in-place modification)
            if not os.access(file_path, os.W_OK):
                logger.error(f"No write permissions: {file_path}")
                return False
            
            # Check parent directory write permissions
            parent_dir = os.path.dirname(file_path)
            if not os.access(parent_dir, os.W_OK):
                logger.error(f"No write permissions in directory: {parent_dir}")
                return False
            
            logger.debug(f"Single file path validation successful: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error during single file path validation: {e}")
            return False
    
    def _validate_input_file(self, file_path: str) -> bool:
        """Validates input file existence and basic properties"""
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return False
        
        # Check if it's actually a file (not a directory)
        if not os.path.isfile(file_path):
            logger.error(f"Path is not a file: {file_path}")
            return False
        
        # Check read permissions
        if not os.access(file_path, os.R_OK):
            logger.error(f"No read permissions: {file_path}")
            return False
        
        return True
    
    def _validate_output_path(self, output_path: str) -> bool:
        """Validates output path for new file creation"""
        # Check if target directory exists
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            logger.error(f"Target directory does not exist: {output_dir}")
            return False
        
        # Check write permissions in target directory
        if not os.access(output_dir, os.W_OK):
            logger.error(f"No write permissions in directory: {output_dir}")
            return False
        
        # If output file already exists, check overwrite permissions
        if os.path.exists(output_path):
            if not os.access(output_path, os.W_OK):
                logger.error(f"No overwrite permissions: {output_path}")
                return False
        
        return True


class BaseToolWorker(BaseWorker):
    """Enhanced base class for tool workers with common patterns"""
    
    def __init__(self, folder_path: str):
        super().__init__(folder_path)
        self._operation_name = self.__class__.__name__.replace('Worker', '')
    
    def _log_operation_start(self, message: str = None):
        """Logs operation start with consistent format"""
        if message is None:
            message = f"Starting {self._operation_name} in folder: {self.folder_path}"
        logger.info(f"[{self._operation_name}] {message}")
    
    def _log_operation_end(self, message: str):
        """Logs operation end with consistent format"""
        logger.info(f"[{self._operation_name}] {message}")
        self.finished.emit(message)
    
    def _log_error(self, error_msg: str):
        """Logs error with consistent format"""
        logger.error(f"[{self._operation_name}] {error_msg}")
        self.error_occurred.emit(error_msg)
    
    def _log_progress(self, current: int, total: int, message: str):
        """Logs progress with consistent format"""
        logger.info(f"[{self._operation_name}] {message}")
        self.progress_updated.emit(current, total, message)
    
    def _find_files_by_extensions(self, extensions: set) -> list:
        """Finds files with specified extensions in the folder"""
        files = []
        try:
            for item in os.listdir(self.folder_path):
                item_path = os.path.join(self.folder_path, item)
                if os.path.isfile(item_path):
                    file_ext = os.path.splitext(item)[1].lower()
                    if file_ext in extensions:
                        files.append(item_path)
            return files
        except Exception as e:
            logger.error(f"Error searching for files: {e}")
            return []
    
    def _safe_file_operation(self, operation_func, *args, **kwargs):
        """Safely executes file operation with error handling"""
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error during file operation: {e}")
            return False 


class BaseNameWorker(BaseToolWorker):
    """Bazowa klasa dla workerów zmieniających nazwy plików (randomizacja, skracanie)"""

    pairs_found = pyqtSignal(list)  # list of pairs to display
    user_confirmation_needed = pyqtSignal(list)  # waits for user confirmation

    def __init__(self, folder_path: str, max_name_length: int):
        super().__init__(folder_path)
        self.max_name_length = max_name_length
        self.user_confirmed = False
        self.files_info = None

    def confirm_operation(self):
        """Metoda wywoływana po potwierdzeniu przez użytkownika"""
        self.user_confirmed = True

    def _analyze_files(self) -> dict:
        """Analizuje pliki w folderze i znajduje pary"""
        files_info = {"all_files": [], "pairs": [], "unpaired": []}
        try:
            archive_extensions = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".sbsar", ".spsm"}
            preview_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
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
            archive_names = {name: path for name, path in archive_files}
            preview_names = {name: path for name, path in preview_files}
            common_names = set(archive_names.keys()) & set(preview_names.keys())
            for name in common_names:
                files_info["pairs"].append((archive_names[name], preview_names[name]))
            unpaired_archive = set(archive_names.keys()) - common_names
            unpaired_preview = set(preview_names.keys()) - common_names
            for name in unpaired_archive:
                files_info["unpaired"].append(archive_names[name])
            for name in unpaired_preview:
                files_info["unpaired"].append(preview_names[name])
            files_info["all_files"] = files_info["pairs"] + files_info["unpaired"]
            logger.info(f"Found {len(files_info['pairs'])} pairs and {len(files_info['unpaired'])} unpaired files")
            return files_info
        except Exception as e:
            logger.error(f"Error analyzing files: {e}")
            return files_info

    def _rename_file(self, file_path: str, new_name: str) -> bool:
        """Zmienia nazwę pliku z obsługą błędów"""
        try:
            if not self._validate_single_file_path(file_path):
                return False
            directory = os.path.dirname(file_path)
            file_ext = os.path.splitext(os.path.basename(file_path))[1]
            new_path = os.path.join(directory, new_name + file_ext)
            if os.path.exists(new_path):
                logger.error(f"Target file already exists: {new_path}")
                return False
            return self._safe_file_operation(os.rename, file_path, new_path)
        except Exception as e:
            logger.error(f"Error renaming file {file_path}: {e}")
            return False 