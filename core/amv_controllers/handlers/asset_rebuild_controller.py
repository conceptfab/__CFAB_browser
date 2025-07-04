"""
AssetRebuildController - Controller for managing background asset rebuilding.
"""

import logging

from PyQt6.QtCore import QObject

from core.workers.asset_rebuilder_worker import AssetRebuilderWorker

logger = logging.getLogger(__name__)


class AssetRebuildController(QObject):
    def __init__(self, model, view, controller):
        super().__init__()
        self.model = model
        self.view = view
        self.controller = controller
        self.asset_rebuilder = None

    def rebuild_assets_in_folder(self, folder_path: str):
        """Rebuilds assets in the specified folder"""
        logger.debug("Started rebuilding assets in folder: %s", folder_path)

        # Create a worker for rebuilding
        self.asset_rebuilder = AssetRebuilderWorker(folder_path)

        # Connect signals
        self.asset_rebuilder.progress_updated.connect(self.on_rebuild_progress)
        self.asset_rebuilder.finished.connect(self.on_rebuild_finished)
        self.asset_rebuilder.error_occurred.connect(self.on_rebuild_error)

        # Start the worker
        self.asset_rebuilder.start()

    def on_rebuild_progress(self, current: int, total: int, message: str):
        """Handles asset rebuild progress"""
        progress = int((current / total) * 100) if total > 0 else 0
        self.model.control_panel_model.set_progress(progress)
        logger.debug(f"Rebuild progress: {progress}% - {message}")
        # Update button states during rebuild
        self.controller.control_panel_controller.update_button_states()

    def on_rebuild_finished(self, message: str):
        """Handles asset rebuild completion"""
        logger.debug(f"Rebuild finished: {message}")
        self.model.control_panel_model.set_progress(100)

        # ODŚWIEŻ FOLDER po przebudowie assetów
        current_folder = self.model.asset_grid_model.get_current_folder()
        if current_folder:
            self.controller.folder_tree_controller.on_folder_refresh_requested(current_folder)
            logger.info(f"ODŚWIEŻONO FOLDER po przebudowie: {current_folder}")
        else:
            # Update button states if there is no working folder
            self.controller.control_panel_controller.update_button_states()

    def on_rebuild_error(self, error_message: str):
        """Handles errors during asset rebuild"""
        logger.error(f"Asset rebuild error: {error_message}")

        # Stop the progress spinner
        self.model.control_panel_model.set_progress(0)

        # Show error message to the user
        self.view.update_gallery_placeholder(
            f"Asset rebuild error: {error_message}"
        )

        # Clean up the worker
        if self.asset_rebuilder:
            self.asset_rebuilder.deleteLater()
            self.asset_rebuilder = None

        # Update button states after rebuild error
        self.controller.control_panel_controller.update_button_states()
