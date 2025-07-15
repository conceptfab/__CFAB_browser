"""
WorkerManager - Common class for managing workers with thread safety
"""

import logging
from typing import Callable, Optional
from threading import Lock
from PyQt6.QtCore import QThread, QMetaObject, Qt

logger = logging.getLogger(__name__)


class ManagedWorker:
    """Abstract base class for workers"""
    def start(self):
        raise NotImplementedError
    def stop(self):
        raise NotImplementedError
    def isRunning(self):
        raise NotImplementedError


class WorkerManager:
    """Thread-safe worker management class"""
    
    _lock = Lock()  # Class-level lock for thread safety
    
    @classmethod
    def handle_progress(cls, button, current: int, total: int, message: str):
        """Thread-safe progress handling
        
        Args:
            button: QButton instance
            current: Current progress value
            total: Total progress value
            message: Progress message
        
        Raises:
            RuntimeError: If called from non-GUI thread without proper handling
        """
        with cls._lock:
            if QThread.currentThread() != button.thread():
                QMetaObject.invokeMethod(
                    button,
                    lambda: button.setText(f"{button.text().split('...')[0]}... {cls._get_progress_text(current, total)}"),
                    Qt.ConnectionType.QueuedConnection
                )
                return
            
            button.setText(f"{button.text().split('...')[0]}... {cls._get_progress_text(current, total)}")
            logger.debug(f"Worker progress: {cls._get_progress_text(current, total)} - {message}")

    @staticmethod
    def _get_progress_text(current: int, total: int) -> str:
        """Helper method to calculate progress percentage"""
        return f"{int((current / total) * 100) if total > 0 else 0}%"

    @staticmethod
    def handle_finished(button, message, original_text, parent_instance):
        """Common logic for handling completion
        UWAGA: Ta metoda MUSI być wywoływana w głównym wątku GUI Qt!
        Jeśli nie masz pewności, użyj QMetaObject.invokeMethod lub sygnałów Qt.
        """
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
        """Common logic for error handling
        UWAGA: Ta metoda MUSI być wywoływana w głównym wątku GUI Qt!
        Jeśli nie masz pewności, użyj QMetaObject.invokeMethod lub sygnałów Qt.
        """
        logger.error(f"Operation error: {error_message}")
        parent_instance.show_error_message.emit("Error", error_message)
        WorkerManager.reset_button_state(button, original_text, parent_instance)

    @staticmethod
    def reset_button_state(button, original_text, parent_instance=None):
        """Common logic for resetting button state
        UWAGA: Ta metoda MUSI być wywoływana w głównym wątku GUI Qt!
        Jeśli nie masz pewności, użyj QMetaObject.invokeMethod lub sygnałów Qt.
        """
        if button:
            button.setText(original_text)
            if parent_instance:
                parent_instance._update_button_states()
    
    @staticmethod
    def start_worker_lifecycle(worker, button, original_text, parent_instance):
        """Unified worker lifecycle management
        UWAGA: Ta metoda MUSI być wywoływana w głównym wątku GUI Qt!
        Jeśli nie masz pewności, użyj QMetaObject.invokeMethod lub sygnałów Qt.
        """
        try:
            # Disable button during operation
            button.setEnabled(False)
            button.setText(f"{original_text}...")

            # Connect signals
            worker.progress_updated.connect(
                lambda c, t, m: WorkerManager.handle_progress(button, c, t, m)
            )
            worker.finished.connect(
                lambda m: WorkerManager.handle_finished(button, m, original_text, parent_instance)
            )
            worker.error_occurred.connect(
                lambda e: WorkerManager.handle_error(button, e, original_text, parent_instance)
            )

            # Start worker
            worker.start()

            logger.info(f"Operation started in folder: {parent_instance.current_working_directory}")

        except Exception as e:
            logger.error(f"Error starting operation: {e}")
            parent_instance.show_error_message.emit("Error", f"Cannot start operation: {e}")
            WorkerManager.reset_button_state(button, original_text, parent_instance)
    
    @staticmethod
    def create_worker_with_confirmation(
        operation_name: str, 
        description: str, 
        worker_factory: Callable,
        parent_instance,
        button
    ):
        """Universal method for creating workers with confirmation
        UWAGA: Ta metoda MUSI być wywoływana w głównym wątku GUI Qt!
        Jeśli nie masz pewności, użyj QMetaObject.invokeMethod lub sygnałów Qt.
        """
        if not parent_instance._validate_working_directory():
            return None

        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            parent_instance,
            f"Confirm {operation_name.lower()}",
            f"Are you sure you want to {operation_name.lower()} in folder:\n{parent_instance.current_working_directory}?\n\n{description}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            return worker_factory()
        
        return None 