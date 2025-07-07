"""
AmvController - Controller for the AMV tab
Connects the Model with the View, handles user interactions, and updates the application state.
"""

import logging
import os

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from core.file_utils import open_file_in_default_app, open_path_in_explorer, handle_file_action
from core.performance_monitor import measure_operation



logger = logging.getLogger(__name__)


class AmvController(QObject):
    """Controller for the AMV tab - Model-View connector"""

    # Sygnał emitowany przy zmianie folderu roboczego
    working_directory_changed = pyqtSignal(str)

    def __init__(self, model, view, main_window=None):
        """
        Simplified constructor - uses only main components.
        All sub-models are accessible via the model.
        """
        from ..amv_models.amv_model import AmvModel

        super().__init__()
        self.model: AmvModel = model
        self.view = view
        self.main_window = main_window



        from .handlers.asset_grid_controller import AssetGridController
        from .handlers.asset_rebuild_controller import AssetRebuildController
        from .handlers.control_panel_controller import ControlPanelController
        from .handlers.file_operation_controller import FileOperationController
        from .handlers.folder_tree_controller import FolderTreeController

        # Najpierw utwórz wszystkie kontrolery
        self.folder_tree_controller = FolderTreeController(self.model, self.view, self)
        self.asset_grid_controller = AssetGridController(self.model, self.view, self)
        self.control_panel_controller = ControlPanelController(
            self.model, self.view, self
        )
        self.file_operation_controller = FileOperationController(
            self.model, self.view, self
        )
        self.asset_rebuild_controller = AssetRebuildController(
            self.model, self.view, self
        )

        # Następnie wywołaj setup() na każdym z nich
        self.folder_tree_controller.setup()
        self.asset_grid_controller.setup()
        self.control_panel_controller.setup()
        self.file_operation_controller.setup()

        self._connect_signals()
        logger.debug("AmvController initialized with dependency injection - STAGE 15")

    def _connect_signals(self):
        from .handlers.signal_connector import SignalConnector

        self.signal_connector = SignalConnector(self.model, self.view, self, self.main_window)
        self.signal_connector.connect_all()

    def _on_splitter_state_changed(self, is_open: bool):
        sizes = self.model.get_splitter_sizes()
        self.view.update_splitter_sizes(sizes)
        self.view.update_toggle_button_text(is_open)
        state = "open" if is_open else "collapsed"
        logger.debug(f"Panel state changed: {state}")

    def _on_config_loaded(self, config: dict):
        self.model.set_config(config)
        logger.debug("Configuration loaded successfully")

    def _on_state_initialized(self):
        self.model.workspace_folders_model.load_folders()
        logger.debug("Application state initialized")

    def _on_scan_started(self, folder_path: str):
        logger.info(f"Controller: Scan started for: {folder_path}")
        self.view.update_gallery_placeholder("Scanning folder...")
        self.model.control_panel_model.set_progress(0)
        # Update button states at the start of the scan
        self.control_panel_controller.update_button_states()

    def _on_scan_progress(self, current: int, total: int, message: str):
        """Handles scan progress."""
        progress = int((current / total) * 100) if total > 0 else 0
        self.model.control_panel_model.set_progress(progress)
        logger.debug(f"Scan progress: {progress}% - {message}")
        # Update button states during the scan
        self.control_panel_controller.update_button_states()

    def _on_scan_completed(self, assets: list, duration: float, operation_type: str):
        with measure_operation(
            "amv_controller.scan_completed",
            {
                "assets_count": len(assets),
                "duration": duration,
                "operation_type": operation_type,
            },
        ):
            logger.info(
                "Controller: Scan completed - %d assets in %.2fs (%s)",
                len(assets),
                duration,
                operation_type,
            )
            self.model.control_panel_model.set_progress(100)
            self.view.update_gallery_placeholder("")

            # Zamiast resetować filtry, zastosuj aktualny filtr do nowych danych
            self.model.asset_grid_model.set_assets(assets)

    def _on_scan_error(self, error_msg: str):
        logger.error(f"Controller: Scan error: {error_msg}")
        self.model.control_panel_model.set_progress(0)
        self.view.update_gallery_placeholder(f"Scan error: {error_msg}")
        # Aktualizuj stan przycisków po błędzie skanowania
        self.control_panel_controller.update_button_states()

    def _handle_file_action(self, path: str, action_type: str):
        """
        Delegates file action handling to consolidated utility function
        """
        logger.debug(f"Controller: File action '{action_type}' for: {path}")
        return handle_file_action(path, action_type, self.view)
