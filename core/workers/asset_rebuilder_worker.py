"""
AssetRebuilderWorker - Worker for rebuilding assets in a folder.
Moved from AmvController for better separation of concerns.
"""

import logging
import os

from PyQt6.QtCore import QThread, pyqtSignal

from ..scanner import AssetRepository

logger = logging.getLogger(__name__)


class AssetRebuilderWorker(QThread):
    """Worker for rebuilding assets in a folder"""

    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(str)  # message
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self, folder_path: str):
        super().__init__()
        self.folder_path = folder_path
        self._should_stop = False

    def request_stop(self):
        """Safely requests the operation to stop"""
        self._should_stop = True
        self.requestInterruption()
    
    def _is_interruption_requested(self) -> bool:
        """Ujednolicone sprawdzanie przerwania operacji"""
        return self._should_stop or self.isInterruptionRequested()

    def run(self):
        """Main asset rebuild method"""
        try:
            if not self.folder_path or not os.path.exists(self.folder_path):
                error_msg = f"Invalid folder: {self.folder_path}"
                self.error_occurred.emit(error_msg)
                return

            logger.info(
                "Starting asset rebuild in folder: %s", self.folder_path
            )

            # Step 1: Removing .asset files
            if self._is_interruption_requested():
                logger.debug("Rebuild was interrupted by the user")
                return
            self.progress_updated.emit(0, 100, "Removing old .asset files...")
            self._remove_asset_files()

            # Step 2: Removing unpair_files.json
            if self._is_interruption_requested():
                logger.debug("Rebuild was interrupted by the user")
                return
            self.progress_updated.emit(15, 100, "Removing unpair_files.json...")
            self._remove_unpair_files()

            # Step 3: Removing .cache folder
            if self._is_interruption_requested():
                logger.debug("Rebuild was interrupted by the user")
                return
            self.progress_updated.emit(20, 100, "Removing .cache folder...")
            self._remove_cache_folder()

            # Step 4: Running scanner.py
            if self._is_interruption_requested():
                logger.debug("Rebuild was interrupted by the user")
                return
            self.progress_updated.emit(
                40, 100, "Scanning and creating new assets..."
            )
            self._run_scanner()

            # Finish only if not stopped
            if not self._is_interruption_requested():
                self.progress_updated.emit(100, 100, "Rebuild completed!")
                self.finished.emit(
                    f"Successfully rebuilt assets in folder: {self.folder_path}"
                )

        except Exception as e:
            if not self._is_interruption_requested():
                error_msg = f"Error during asset rebuild: {e}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)

    def _remove_asset_files(self):
        """Removes all .asset files from the folder"""
        try:
            asset_files = [
                f for f in os.listdir(self.folder_path) if f.endswith(".asset")
            ]
            for asset_file in asset_files:
                # Check if the operation should be stopped
                if self._is_interruption_requested():
                    logger.debug("Removing .asset files was interrupted")
                    return
                    
                file_path = os.path.join(self.folder_path, asset_file)
                os.remove(file_path)
                logger.debug("Removed asset file: %s", asset_file)
            logger.debug("Removed %d .asset files", len(asset_files))
        except Exception as e:
            logger.error(f"Error removing .asset files: {e}")
            raise

    def _remove_unpair_files(self):
        """Removes the unpair_files.json file if it exists."""
        try:
            unpair_file_path = os.path.join(self.folder_path, "unpair_files.json")
            if os.path.exists(unpair_file_path):
                os.remove(unpair_file_path)
                logger.debug("Removed unpair_files.json: %s", unpair_file_path)
            else:
                logger.debug("unpair_files.json did not exist")
        except Exception as e:
            logger.error(f"Error removing unpair_files.json: {e}")
            raise

    def _remove_cache_folder(self):
        """ABSOLUTELY removes the .cache folder - it's a cache folder, so its contents don't matter"""
        try:
            import shutil

            cache_folder = os.path.join(self.folder_path, ".cache")

            # ABSOLUTELY remove the .cache folder - its contents don't matter
            if os.path.exists(cache_folder):
                shutil.rmtree(cache_folder, ignore_errors=True)
                logger.debug("ABSOLUTELY removed .cache folder: %s", cache_folder)
            else:
                logger.debug(".cache folder did not exist - we removed it anyway")
        except Exception as e:
            logger.error(f"Error removing .cache folder: {e}")
            # Even if there's an error - continue, the cache folder must be deleted
            raise

    def _run_scanner(self):
        """Runs scanner.py in the folder"""
        try:

            def progress_callback(current, total, message):
                # Check if the operation should be stopped
                if self._is_interruption_requested():
                    return
                    
                if total > 0:
                    # Map scanning progress to the 40-100% range
                    scanner_progress = int(40 + (current / total) * 60)
                    self.progress_updated.emit(scanner_progress, 100, message)
                else:
                    self.progress_updated.emit(100, 100, message)

            asset_repository = AssetRepository()
            created_assets = asset_repository.find_and_create_assets(
                self.folder_path, progress_callback
            )
            logger.debug("Scanner created %d new assets", len(created_assets))

        except Exception as e:
            logger.error(f"Error running scanner: {e}")
            raise
