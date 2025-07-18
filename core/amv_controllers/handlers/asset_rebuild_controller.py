"""
AssetRebuildController - Controller for managing background asset rebuilding.
"""

import logging

from PyQt6.QtCore import QObject, QMutex

from core.workers.asset_rebuilder_worker import AssetRebuilderWorker
# thumbnail_cache imported w utilities.clear_thumbnail_cache_after_rebuild()

logger = logging.getLogger(__name__)


class AssetRebuildController(QObject):
    def __init__(self, model, view, controller):
        super().__init__()
        self.model = model
        self.view = view
        self.controller = controller
        self.asset_rebuilder = None
        self._rebuild_mutex = QMutex()

    def rebuild_assets_in_folder(self, folder_path: str):
        """Rebuilds assets in the specified folder"""
        if not self._rebuild_mutex.tryLock():
            logger.warning("Rebuild already in progress. Ignoring new request.")
            return
            
        try:
            # Stop the existing worker if it's running
            if self.asset_rebuilder and self.asset_rebuilder.isRunning():
                logger.warning("Stopping previous rebuild operation.")
                self._stop_rebuild_safely()

            logger.debug("Started rebuilding assets in folder: %s", folder_path)

            # Create a worker for rebuilding
            self.asset_rebuilder = AssetRebuilderWorker(folder_path)

            # Connect signals
            self.asset_rebuilder.progress_updated.connect(self.on_rebuild_progress)
            self.asset_rebuilder.finished.connect(self.on_rebuild_finished)
            self.asset_rebuilder.error_occurred.connect(self.on_rebuild_error)

            # Start the worker
            self.asset_rebuilder.start()
        finally:
            self._rebuild_mutex.unlock()

    def stop_rebuild(self):
        """Stops the current rebuild operation"""
        self._stop_rebuild_safely()

    def _stop_rebuild_safely(self):
        """Safely stops the rebuild worker"""
        if self.asset_rebuilder and self.asset_rebuilder.isRunning():
            logger.info("Stopping asset rebuild...")
            
            # First, request a stop
            self.asset_rebuilder.request_stop()
            
            # Try to gracefully quit
            if not self.asset_rebuilder.wait(3000):  # 3-second timeout
                logger.warning("Rebuild worker did not stop gracefully, forcing termination...")
                self.asset_rebuilder.terminate()
                self.asset_rebuilder.wait()
            
            logger.info("Rebuild has been stopped.")

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

        # ABSOLUTE CLEARING OF RAM CACHE AFTER REBUILDING ASSETS!!!
        from core.utilities import clear_thumbnail_cache_after_rebuild
        clear_thumbnail_cache_after_rebuild(is_error=False)

        # PERFORMANCE: Refresh only the assets, not the entire folder structure
        current_folder = self.model.asset_grid_model.get_current_folder()
        if current_folder:
            # Instead of a full folder refresh, just refresh the assets
            self.model.asset_grid_model.scan_folder(current_folder)
            logger.info(f"ASSETS REFRESHED after rebuild: {current_folder}")
        else:
            # Update button states if there is no working folder
            self.controller.control_panel_controller.update_button_states()

        # Odśwież zakładki po przebudowie
        self._refresh_tabs_after_rebuild(current_folder)

        # Clean up the worker
        self._cleanup_worker()

    def on_rebuild_error(self, error_message: str):
        """Handles errors during asset rebuild"""
        logger.error(f"Asset rebuild error: {error_message}")

        # ABSOLUTE CLEARING OF RAM CACHE EVEN AFTER A REBUILD ERROR!!!
        from core.utilities import clear_thumbnail_cache_after_rebuild
        clear_thumbnail_cache_after_rebuild(is_error=True)

        # Stop the progress spinner
        self.model.control_panel_model.set_progress(0)

        # Show error message to the user
        self.view.update_gallery_placeholder(
            f"Asset rebuild error: {error_message}"
        )

        # Odśwież zakładki po błędzie przebudowy
        current_folder = self.model.asset_grid_model.get_current_folder()
        self._refresh_tabs_after_rebuild(current_folder)

        # Clean up the worker
        self._cleanup_worker()

        # Update button states after rebuild error
        self.controller.control_panel_controller.update_button_states()

    def _refresh_tabs_after_rebuild(self, folder_path):
        """Odświeża zakładki Asset Browser, PairingTab i ToolsTab po przebudowie asetów"""
        main_window = getattr(self.controller, 'main_window', None)
        if main_window:
            # Asset Browser (AMV Tab)
            amv_tab = getattr(main_window, 'amv_tab', None)
            if amv_tab and hasattr(amv_tab, 'get_controller'):
                try:
                    amv_controller = amv_tab.get_controller()
                    if amv_controller and hasattr(amv_controller.model, 'asset_grid_model'):
                        if folder_path:
                            amv_controller.model.asset_grid_model.scan_folder(folder_path)
                            logger.info("Asset Browser refreshed after asset rebuild.")
                except Exception as e:
                    logger.error(f"Error refreshing Asset Browser: {e}")
            # PairingTab
            pairing_tab = getattr(main_window, 'pairing_tab', None)
            if pairing_tab and hasattr(pairing_tab, 'load_data'):
                try:
                    pairing_tab.load_data()
                    logger.info("PairingTab refreshed after asset rebuild.")
                except Exception as e:
                    logger.error(f"Error refreshing PairingTab: {e}")
            # ToolsTab
            tools_tab = getattr(main_window, 'tools_tab', None)
            if tools_tab and hasattr(tools_tab, 'set_working_directory'):
                try:
                    if folder_path:
                        tools_tab.set_working_directory(folder_path)
                        logger.info("ToolsTab refreshed after asset rebuild.")
                except Exception as e:
                    logger.error(f"Error refreshing ToolsTab: {e}")

    def _cleanup_worker(self):
        """Safely deletes the worker"""
        if self.asset_rebuilder:
            self.asset_rebuilder.deleteLater()
            self.asset_rebuilder = None
            logger.debug("Rebuild worker has been safely deleted.")

    def __del__(self):
        """Destructor - ensures the worker is stopped"""
        if hasattr(self, 'asset_rebuilder') and self.asset_rebuilder and self.asset_rebuilder.isRunning():
            self._stop_rebuild_safely()
