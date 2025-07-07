"""
Utility module for file and path operations.
Contains functions used by various application components.
"""

import logging
import os
import subprocess
import sys

from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)


def _is_command_available(command: str) -> bool:
    """
    Checks if a command is available in the system.

    Args:
        command (str): Name of the command to check

    Returns:
        bool: True if the command is available, False otherwise
    """
    try:
        subprocess.run(
            [command, "--version"], capture_output=True, timeout=5, check=False
        )
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def _validate_path_input(path: str) -> tuple[bool, str]:
    """
    Validates and normalizes input path.
    
    Args:
        path (str): Input path to validate
        
    Returns:
        tuple[bool, str]: (is_valid, normalized_path_or_error_message)
    """
    if not path or not isinstance(path, str):
        return False, "Invalid path: empty or not a string"
    
    normalized_path = os.path.normpath(path)
    
    if not os.path.exists(normalized_path):
        return False, f"Path does not exist: {normalized_path}"
    
    return True, normalized_path


def _open_path_windows(normalized_path: str) -> bool:
    """
    Opens path in Windows Explorer.
    
    Args:
        normalized_path (str): Validated and normalized path
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.debug(f"_open_path_windows - launching os.startfile with path: {normalized_path}")
        os.startfile(normalized_path)
        return True
    except FileNotFoundError as e:
        logger.error(f"Windows Explorer or path not found: {normalized_path} - {e}")
        return False
    except OSError as e:
        logger.error(f"OS error opening path {normalized_path}: {e}")
        return False


def _open_path_macos(normalized_path: str) -> bool:
    """
    Opens path in macOS Finder.
    
    Args:
        normalized_path (str): Validated and normalized path
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not _is_command_available("open"):
        logger.error("Command 'open' is not available")
        return False
    
    try:
        subprocess.run(["open", normalized_path], check=True, timeout=10)
        return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        logger.error(f"Error opening path in macOS: {e}")
        return False


def _open_path_linux(normalized_path: str) -> bool:
    """
    Opens path in Linux file manager.
    
    Args:
        normalized_path (str): Validated and normalized path
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not _is_command_available("xdg-open"):
        logger.error("Command 'xdg-open' is not available")
        return False
    
    try:
        subprocess.run(["xdg-open", normalized_path], check=True, timeout=10)
        return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        logger.error(f"Error opening path in Linux: {e}")
        return False


def _open_file_windows(normalized_path: str) -> bool:
    """
    Opens file in Windows default application.
    
    Args:
        normalized_path (str): Validated and normalized path to file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.startfile(normalized_path)
        return True
    except FileNotFoundError as e:
        logger.error(f"Windows application or file not found: {normalized_path} - {e}")
        return False
    except OSError as e:
        logger.error(f"OS error opening file {normalized_path}: {e}")
        return False


def _open_file_macos(normalized_path: str) -> bool:
    """
    Opens file in macOS default application.
    
    Args:
        normalized_path (str): Validated and normalized path to file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not _is_command_available("open"):
        logger.error("Command 'open' is not available")
        return False
    
    try:
        subprocess.run(["open", normalized_path], check=True, timeout=10)
        return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        logger.error(f"Error opening file in macOS: {e}")
        return False


def _open_file_linux(normalized_path: str) -> bool:
    """
    Opens file in Linux default application.
    
    Args:
        normalized_path (str): Validated and normalized path to file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not _is_command_available("xdg-open"):
        logger.error("Command 'xdg-open' is not available")
        return False
    
    try:
        subprocess.run(["xdg-open", normalized_path], check=True, timeout=10)
        return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        logger.error(f"Error opening file in Linux: {e}")
        return False


def _show_error_message(parent_widget, error_message: str, context: str):
    """
    Shows error message to user if parent_widget is available.
    
    Args:
        parent_widget: Parent widget for message box
        error_message (str): Error message to display
        context (str): Context information (path, operation type)
    """
    if parent_widget:
        QMessageBox.warning(parent_widget, "Error", f"{error_message}: {context}")


def open_path_in_explorer(path: str, parent_widget=None) -> bool:
    """
    Opens a path in the system file explorer.

    Args:
        path (str): Path to open
        parent_widget: Parent widget for displaying error messages

    Returns:
        bool: True if the operation succeeded, False otherwise
    """
    logger.debug(f"open_path_in_explorer - received path: {path}")
    
    try:
        # Step 1: Validate input
        is_valid, result = _validate_path_input(path)
        if not is_valid:
            logger.error(result)
            _show_error_message(parent_widget, result, path)
            return False
        
        normalized_path = result
        logger.debug(f"open_path_in_explorer - normalized path: {normalized_path}")
        
        # Step 2: Choose platform-specific handler
        platform_handlers = {
            "win32": _open_path_windows,
            "darwin": _open_path_macos,
        }
        
        handler = platform_handlers.get(sys.platform, _open_path_linux)
        success = handler(normalized_path)
        
        if success:
            logger.info(f"Opened path in explorer: {normalized_path}")
            return True
        else:
            _show_error_message(parent_widget, "Failed to open path", normalized_path)
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error while opening path {path}: {e}")
        _show_error_message(parent_widget, "Unexpected error opening path", path)
        return False


def open_file_in_default_app(path: str, parent_widget=None) -> bool:
    """
    Opens a file in the system's default application.

    Args:
        path (str): Path to the file
        parent_widget: Parent widget for displaying error messages

    Returns:
        bool: True if the operation succeeded, False otherwise
    """
    logger.debug(f"open_file_in_default_app - received path: {path}")
    
    try:
        # Step 1: Validate input  
        is_valid, result = _validate_path_input(path)
        if not is_valid:
            logger.error(result)
            _show_error_message(parent_widget, result, path)
            return False
        
        normalized_path = result
        logger.debug(f"open_file_in_default_app - normalized path: {normalized_path}")
        
        # Step 2: Choose platform-specific handler
        platform_handlers = {
            "win32": _open_file_windows,
            "darwin": _open_file_macos,
        }
        
        handler = platform_handlers.get(sys.platform, _open_file_linux)
        success = handler(normalized_path)
        
        if success:
            logger.info(f"Opened file in default application: {normalized_path}")
            return True
        else:
            _show_error_message(parent_widget, "Failed to open file", normalized_path)
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error while opening file {path}: {e}")
        _show_error_message(parent_widget, "Unexpected error opening file", path)
        return False


def handle_file_action(path: str, action_type: str, parent_widget=None):
    """
    Consolidated file action handler for common file operations.
    
    Args:
        path (str): Path to file or folder
        action_type (str): Type of action ("thumbnail", "filename", "folder")
        parent_widget: Parent widget for displaying error messages and preview windows
        
    Returns:
        bool: True if operation succeeded, False otherwise
    """
    logger.debug(f"handle_file_action: '{action_type}' for: {path}")
    
    if not path:
        logger.warning("handle_file_action: Empty path provided")
        return False

    if not os.path.exists(path):
        logger.warning(f"handle_file_action: Path does not exist: {path}")
        if parent_widget:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(parent_widget, "Error", f"Path does not exist: {path}")
        return False

    try:
        if os.path.isdir(path):
            # Open folder in explorer
            success = open_path_in_explorer(path, parent_widget)
            if success:
                logger.info(f"Opened folder in explorer: {path}")
            return success
        else:
            # Handle file actions
            if action_type == "thumbnail":
                # Open preview window
                try:
                    from core.preview_window import PreviewWindow
                    
                    # Close existing preview window if any
                    if hasattr(parent_widget, 'current_preview_window') and parent_widget.current_preview_window:
                        parent_widget.current_preview_window.close()
                        parent_widget.current_preview_window.deleteLater()
                        parent_widget.current_preview_window = None
                    
                    # Create new preview window
                    preview_window = PreviewWindow(path, parent_widget)
                    if hasattr(parent_widget, '__dict__'):
                        parent_widget.current_preview_window = preview_window
                    preview_window.show_window()
                    logger.info(f"Opened preview in dedicated window: {path}")
                    return True
                except Exception as e:
                    logger.error(f"Error opening preview window for {path}: {e}")
                    return False
                    
            elif action_type == "filename":
                # Open file in default application
                success = open_file_in_default_app(path, parent_widget)
                if success:
                    logger.info(f"Opened file in external application: {path}")
                return success
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return False
                
    except Exception as e:
        logger.error(f"Error in handle_file_action for {path}: {e}")
        if parent_widget:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(parent_widget, "Error", f"Cannot open: {path}")
        return False
