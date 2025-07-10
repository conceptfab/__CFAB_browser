import json
import logging
import os
import shutil

from PyQt6.QtCore import QObject, QThread, pyqtSignal, QMutex, QMutexLocker

logger = logging.getLogger(__name__)


class FileOperationsWorker(QThread):
    """Worker for performing file operations in a separate thread"""

    operation_progress = pyqtSignal(int, int, str)  # current, total, message
    operation_completed = pyqtSignal(list, list)  # success_messages, error_messages
    operation_error = pyqtSignal(str)

    def __init__(
        self, operation_type, assets_data, source_folder_path, target_folder_path
    ):
        super().__init__()
        self.operation_type = operation_type
        self.assets_data = assets_data
        self.source_folder_path = source_folder_path
        self.target_folder_path = target_folder_path
        self._should_stop = False

    def request_stop(self):
        """Safely requests the operation to stop"""
        self._should_stop = True
        self.requestInterruption()

    def run(self):
        try:
            if self.operation_type == "move":
                self._move_assets()
            elif self.operation_type == "delete":
                self._delete_assets()
        except Exception as e:
            if not self._should_stop:
                self.operation_error.emit(
                    f"Error during {self.operation_type} operation: {e}"
                )

    def _move_assets(self):
        """Moves selected assets to a new folder."""
        if not self.assets_data:
            self.operation_completed.emit([], [])
            return
        
        success_asset_names = []
        error_messages = []
        total_assets = len(self.assets_data)
        
        if not os.path.exists(self.target_folder_path):
            try:
                os.makedirs(self.target_folder_path)
                logger.debug(f"Target folder created: {self.target_folder_path}")
            except Exception as e:
                self.operation_error.emit(
                    f"Cannot create target folder "
                    f"{self.target_folder_path}: {e}"
                )
                return
        
        for i, asset_data in enumerate(self.assets_data):
            # Check if the operation should be stopped
            if self._should_stop or self.isInterruptionRequested():
                logger.debug("Operation was interrupted by the user")
                break
                
            asset_name = asset_data.get("name", "Unknown Asset")
            logger.debug(f"Processing asset {i}: name='{asset_name}'")
            self.operation_progress.emit(
                i + 1, total_assets, f"Moving: {asset_name}"
            )
            
            try:
                result = self._move_single_asset_with_conflict_resolution(
                    asset_data, asset_name
                )
                if result["success"]:
                    success_asset_names.append(asset_name)
                    logger.debug(f"Successfully moved asset: {asset_name}")
                else:
                    error_messages.append(result["message"])
                    logger.error(result["message"])
            except Exception as e:
                if not self._should_stop:
                    error_msg = f"Error moving asset {asset_name}: {e}"
                    error_messages.append(error_msg)
                    logger.error(error_msg)
        
        # Only if the operation was not interrupted
        if not self._should_stop:
            source_cache_dir = os.path.join(self.source_folder_path, ".cache")
            if os.path.exists(source_cache_dir) and not os.listdir(source_cache_dir):
                try:
                    os.rmdir(source_cache_dir)
                    logger.debug(
                        f"Removed empty .cache folder in source: {source_cache_dir}"
                    )
                except Exception as e:
                    logger.warning(
                        f"Cannot remove empty .cache folder in source {source_cache_dir}: {e}"
                    )
            
            self.operation_completed.emit(success_asset_names, error_messages)

    def _generate_unique_asset_name(self, original_name: str) -> str:
        """Generates a unique asset name by adding suffix _D_01, _D_02, etc."""
        base_name = original_name
        counter = 1

        while True:
            # Check if an asset with this name already exists (check .asset file)
            test_asset_file = os.path.join(
                self.target_folder_path, f"{base_name}.asset"
            )
            if not os.path.exists(test_asset_file):
                return base_name

            # If it exists, try with suffix _D_01, _D_02, etc.
            base_name = f"{original_name}_D_{counter:02d}"
            counter += 1

            # Protection against infinite loop
            if counter > 99:
                logger.warning(f"Maximum number of attempts reached for {original_name}")
                return f"{original_name}_D_{counter}"

    def _move_single_asset_with_conflict_resolution(
        self, asset_data: dict, original_name: str
    ) -> dict:
        """
        Moves a single asset with name conflict resolution.
        Returns a dict with keys: success (bool), message (str), final_name (str)
        """
        unique_name = self._generate_unique_asset_name(original_name)
        try:
            files_to_move, source_asset, target_asset = self._prepare_files_to_move(
                asset_data, original_name, unique_name
            )
            moved_files = self._move_files(files_to_move)
            self._handle_post_move(
                unique_name, original_name, source_asset, target_asset
            )
            message = self._compose_move_message(unique_name, original_name)
            return {"success": True, "message": message, "final_name": unique_name}
        except Exception as e:
            return {
                "success": False,
                "message": f"Error moving asset {original_name}: {e}",
                "final_name": original_name,
            }

    def _prepare_files_to_move(self, asset_data, original_name, unique_name):
        files_to_move = []
        source_asset = os.path.join(self.source_folder_path, f"{original_name}.asset")
        target_asset = os.path.join(self.target_folder_path, f"{unique_name}.asset")
        if os.path.exists(source_asset):
            files_to_move.append((source_asset, target_asset))
        archive_filename = asset_data.get("archive")
        if archive_filename:
            source_archive = os.path.join(self.source_folder_path, archive_filename)
            if os.path.exists(source_archive):
                archive_ext = os.path.splitext(archive_filename)[1]
                target_archive = os.path.join(
                    self.target_folder_path, f"{unique_name}{archive_ext}"
                )
                files_to_move.append((source_archive, target_archive))
        preview_filename = asset_data.get("preview")
        if preview_filename:
            source_preview = os.path.join(self.source_folder_path, preview_filename)
            if os.path.exists(source_preview):
                preview_ext = os.path.splitext(preview_filename)[1]
                target_preview = os.path.join(
                    self.target_folder_path, f"{unique_name}{preview_ext}"
                )
                files_to_move.append((source_preview, target_preview))
        source_thumb = os.path.join(
            self.source_folder_path, ".cache", f"{original_name}.thumb"
        )
        if os.path.exists(source_thumb):
            target_cache_dir = os.path.join(self.target_folder_path, ".cache")
            os.makedirs(target_cache_dir, exist_ok=True)
            target_thumb = os.path.join(target_cache_dir, f"{unique_name}.thumb")
            files_to_move.append((source_thumb, target_thumb))
        return files_to_move, source_asset, target_asset

    def _move_files(self, files_to_move):
        moved_files = []
        for source_path, target_path in files_to_move:
            shutil.move(source_path, target_path)
            moved_files.append(target_path)
            logger.debug(f"Moved: {source_path} -> {target_path}")
        return moved_files

    def _handle_post_move(self, unique_name, original_name, source_asset, target_asset):
        if unique_name != original_name:
            self._update_asset_file_after_rename(source_asset, target_asset)
            if os.path.exists(source_asset):
                self._mark_asset_as_duplicate(target_asset, source_asset)

    def _compose_move_message(self, unique_name, original_name):
        if unique_name != original_name:
            return (
                f"Moved asset: {original_name} -> {unique_name} (renamed due to conflict)"
            )
        else:
            return f"Successfully moved asset: {original_name}"

    def _update_asset_file_after_rename(self, original_asset_path, new_asset_path):
        try:
            # Ensure asset_file_path has .asset extension
            asset_file_path = new_asset_path
            if not asset_file_path.endswith('.asset'):
                asset_file_path = os.path.splitext(asset_file_path)[0] + '.asset'
            if self._file_exists(asset_file_path):
                with open(asset_file_path, "r", encoding="utf-8") as f:
                    asset_data = json.load(f)
                original_basename = os.path.splitext(
                    os.path.basename(original_asset_path)
                )[0]
                new_basename = os.path.splitext(os.path.basename(new_asset_path))[0]

                # Update name in asset data
                asset_data["name"] = new_basename

                # Update archive and preview filenames
                if "archive" in asset_data:
                    archive_ext = os.path.splitext(asset_data["archive"])[1]
                    asset_data["archive"] = f"{new_basename}{archive_ext}"

                if "preview" in asset_data:
                    preview_ext = os.path.splitext(asset_data["preview"])[1]
                    asset_data["preview"] = f"{new_basename}{preview_ext}"

                # Save updated data
                with open(asset_file_path, "w", encoding="utf-8") as f:
                    json.dump(asset_data, f, indent=2, ensure_ascii=False)

                logger.debug(
                    f"Updated .asset file after rename: "
                    f"{original_basename} -> {new_basename}"
                )

        except Exception as e:
            logger.error(f"Error updating .asset file: {e}")

    def _mark_asset_as_duplicate(self, asset_path, original_asset_path):
        try:
            if self._file_exists(asset_path):
                with open(asset_path, "r", encoding="utf-8") as f:
                    asset_data = json.load(f)

                # Add duplicate information
                if "meta" not in asset_data:
                    asset_data["meta"] = {}
                asset_data["meta"]["duplicate_of"] = os.path.basename(
                    original_asset_path
                )
                asset_data["meta"]["duplicate_date"] = str(
                    os.path.getctime(original_asset_path)
                )

                # Save updated data
                with open(asset_path, "w", encoding="utf-8") as f:
                    json.dump(asset_data, f, indent=2, ensure_ascii=False)

                logger.debug(f"Marked asset as duplicate: {asset_path}")

        except Exception as e:
            logger.error(f"Error marking asset as duplicate: {e}")

    def _delete_assets(self):
        """Deletes selected assets."""
        if not self.assets_data:
            self.operation_completed.emit([], [])
            return

        success_asset_names = []
        error_messages = []
        total_assets = len(self.assets_data)

        for i, asset_data in enumerate(self.assets_data):
            # Check if the operation should be stopped
            if self._should_stop or self.isInterruptionRequested():
                logger.debug("Delete operation was interrupted by the user")
                break
                
            asset_name = asset_data.get("name", "Unknown Asset")
            self.operation_progress.emit(
                i + 1, total_assets, f"Deleting: {asset_name}"
            )

            try:
                # Get paths to asset files
                asset_files = self._get_asset_files_paths(
                    asset_data, self.source_folder_path
                )

                # Delete all files
                for file_path in asset_files:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.debug(f"Deleted file: {file_path}")

                success_asset_names.append(asset_name)
                logger.debug(f"Successfully deleted asset: {asset_name}")

            except Exception as e:
                if not self._should_stop:
                    error_msg = f"Error deleting asset {asset_name}: {e}"
                    error_messages.append(error_msg)
                    logger.error(error_msg)

        # Only if the operation was not interrupted
        if not self._should_stop:
            # Remove empty .cache folder if it exists
            cache_dir = os.path.join(self.source_folder_path, ".cache")
            if os.path.exists(cache_dir) and not os.listdir(cache_dir):
                try:
                    os.rmdir(cache_dir)
                    logger.debug(f"Removed empty .cache folder: {cache_dir}")
                except Exception as e:
                    logger.warning(
                        f"Cannot remove empty .cache folder {cache_dir}: {e}"
                    )

            self.operation_completed.emit(success_asset_names, error_messages)

    def _get_asset_files_paths(self, asset_data: dict, folder_path: str) -> list:
        """Returns a list of paths to all files related to the asset."""
        asset_name = asset_data.get("name", "")
        files = []

        # 1. .asset file
        asset_file = os.path.join(folder_path, f"{asset_name}.asset")
        files.append(asset_file)

        # 2. Archive file
        archive_filename = asset_data.get("archive")
        if archive_filename:
            archive_file = os.path.join(folder_path, archive_filename)
            files.append(archive_file)

        # 3. Preview file
        preview_filename = asset_data.get("preview")
        if preview_filename:
            preview_file = os.path.join(folder_path, preview_filename)
            files.append(preview_file)

        # 4. Thumbnail file in .cache folder
        cache_dir = os.path.join(folder_path, ".cache")
        thumb_file = os.path.join(cache_dir, f"{asset_name}.thumb")
        files.append(thumb_file)

        return files

    def _file_exists(self, path):
        """Helper to check if a file exists."""
        return os.path.exists(path)


class FileOperationsModel(QObject):
    """
    Model for file operations (moving, deleting).

    Manages file operations in a separate thread to avoid blocking the UI.
    """

    operation_progress = pyqtSignal(int, int, str)  # current, total, message
    operation_completed = pyqtSignal(list, list)  # success_messages, error_messages
    operation_error = pyqtSignal(str)

    def __init__(self):
        """Initializes the file operations model."""
        super().__init__()
        self._worker = None
        self._worker_mutex = QMutex()
        self._last_target_folder = None  # Store the target folder

    def move_assets(
        self, assets_data: list, source_folder_path: str, target_folder_path: str
    ):
        """Moves the selected assets to a target folder."""
        with QMutexLocker(self._worker_mutex):
            if self._worker and self._worker.isRunning():
                logger.warning(
                    "Previous file operation is still running. Stopping it..."
                )
                self._stop_worker_safely()

            self._last_target_folder = target_folder_path  # Save the target folder
            self._worker = FileOperationsWorker(
                "move", assets_data, source_folder_path, target_folder_path
            )
            self._connect_worker_signals()
            self._worker.start()

    def get_last_target_folder(self) -> str:
        """Returns the target folder of the last move operation"""
        return self._last_target_folder

    def delete_assets(self, assets_data: list, current_folder_path: str):
        """Deletes selected assets."""
        with QMutexLocker(self._worker_mutex):
            if self._worker and self._worker.isRunning():
                logger.warning(
                    "Previous file operation is still running. Stopping it..."
                )
                self._stop_worker_safely()

            self._last_target_folder = None  # Clear the target folder on delete
            self._worker = FileOperationsWorker(
                "delete", assets_data, current_folder_path, None
            )
            self._connect_worker_signals()
            self._worker.start()

    def stop_operation(self):
        """Stops the current file operation."""
        self._stop_worker_safely()

    def _stop_worker_safely(self):
        """Safely stops the worker"""
        if self._worker and self._worker.isRunning():
            logger.info("Stopping current operation...")
            
            # First, request a stop
            self._worker.request_stop()
            
            # Try to gracefully quit
            if not self._worker.wait(3000):  # 3-second timeout
                logger.warning("Worker did not stop gracefully, forcing termination...")
                self._worker.terminate()
                self._worker.wait()
            
            logger.info("Operation has been stopped.")

    def _connect_worker_signals(self):
        """Connects worker signals to model signals."""
        if self._worker:
            self._worker.operation_progress.connect(self.operation_progress.emit)
            self._worker.operation_completed.connect(self.operation_completed.emit)
            self._worker.operation_error.connect(self.operation_error.emit)
            self._worker.finished.connect(self._on_worker_finished)

    def _on_worker_finished(self):
        """Handles worker finished event."""
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
            logger.debug("Worker has been safely deleted.")

    def __del__(self):
        """Destructor - ensures the worker is stopped"""
        if hasattr(self, '_worker') and self._worker and self._worker.isRunning():
            self._stop_worker_safely()
