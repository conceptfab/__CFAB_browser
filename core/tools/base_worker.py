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
            self.wait(2000)
    
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
    
    # ========================================
    # CONSOLIDATED ERROR HANDLING METHODS
    # ========================================
    
    def _handle_pillow_import_error(self, operation_name: str) -> bool:
        """Standardized handling of Pillow import errors"""
        logger.error(f"[{operation_name}] Pillow library is not installed")
        return False
    
    def _handle_operation_error(self, file_path: str, operation_name: str, error: Exception) -> bool:
        """Standardized handling of operation errors"""
        logger.error(f"[{operation_name}] Error processing {file_path}: {error}")
        return False 