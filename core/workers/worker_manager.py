"""
WorkerManager - Common class for managing workers
"""

import logging

logger = logging.getLogger(__name__)


class WorkerManager:
    """Common class for managing workers"""

    @staticmethod
    def handle_progress(button, current, total, message):
        """Common logic for progress handling"""
        progress = int((current / total) * 100) if total > 0 else 0
        button.setText(f"{button.text().split('...')[0]}... {progress}%")
        logger.debug(f"Worker progress: {progress}% - {message}")

    @staticmethod
    def handle_finished(button, message, original_text, parent_instance):
        """Common logic for handling completion"""
        logger.info(f"Operation completed: {message}")
        parent_instance.show_info_message.emit("Success", message)
        if parent_instance.current_working_directory:
            parent_instance.scan_working_directory(
                parent_instance.current_working_directory
            )
        WorkerManager.reset_button_state(button, original_text, parent_instance)
        parent_instance.working_directory_changed.emit(
            parent_instance.current_working_directory
        )

    @staticmethod
    def handle_error(button, error_message, original_text, parent_instance):
        """Common logic for error handling"""
        logger.error(f"Operation error: {error_message}")
        parent_instance.show_error_message.emit("Error", error_message)
        WorkerManager.reset_button_state(button, original_text, parent_instance)

    @staticmethod
    def reset_button_state(button, original_text, parent_instance):
        """Common logic for resetting button state"""
        if button:
            button.setText(original_text)
            parent_instance._update_button_states() 