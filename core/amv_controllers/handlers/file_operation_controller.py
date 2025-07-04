"""
FileOperationController - Controller for managing file operations.
Responsible for moving, deleting, and handling drag & drop of assets.
"""

import logging

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from core.performance_monitor import measure_operation

logger = logging.getLogger(__name__)


class FileOperationController(QObject):
    """Controller for managing file operations"""

    def __init__(self, model, view, controller):
        super().__init__()
        self.model = model
        self.view = view
        self.controller = controller

    def setup(self):
        """Initializes the file operations controller"""
        logger.debug("File operation controller initialized")

    def _get_assets_by_ids(self, asset_ids: list) -> list:
        """Gets full asset data based on a list of IDs."""
        all_assets = self.model.asset_grid_model.get_assets()
        return [asset for asset in all_assets if asset.get("name") in asset_ids]

    def _validate_selection(self, operation_name: str) -> list:
        """Wspólna walidacja zaznaczenia dla operacji"""
        selected_asset_ids = self.model.selection_model.get_selected_asset_ids()
        if not selected_asset_ids:
            QMessageBox.information(
                self.view,
                operation_name,
                f"No assets selected for {operation_name.lower()}.",
            )
            return []

        assets_to_process = self._get_assets_by_ids(selected_asset_ids)
        if not assets_to_process:
            QMessageBox.warning(
                self.view,
                operation_name,
                "Could not find full data for the selected assets.",
            )
            return []

        return assets_to_process

    def on_move_selected_clicked(self):
        """Uproszczona metoda z wykorzystaniem centralnej walidacji"""
        assets_to_move = self._validate_selection("Moving Assets")
        if not assets_to_move:
            return
        target_folder = QFileDialog.getExistingDirectory(
            self.view,
            "Select target folder",
            self.model.asset_grid_model.get_current_folder(),
        )
        if target_folder:
            self.model.file_operations_model.move_assets(
                assets_to_move,
                self.model.asset_grid_model.get_current_folder(),
                target_folder,
            )
            self.model.control_panel_model.set_progress(0)  # Reset progress bar
            self.view.update_gallery_placeholder("Moving assets...")

    def on_delete_selected_clicked(self):
        """Uproszczona metoda z wykorzystaniem centralnej walidacji"""
        assets_to_delete = self._validate_selection("Deleting Assets")
        if not assets_to_delete:
            return
        reply = QMessageBox.question(
            self.view,
            "Confirm Deletion",
            (
                f"Are you sure you want to delete {len(assets_to_delete)} "
                "selected assets?\nThis operation is irreversible!"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.model.file_operations_model.delete_assets(
                assets_to_delete,
                self.model.asset_grid_model.get_current_folder(),
            )
            self.model.control_panel_model.set_progress(0)  # Reset progress bar
            self.view.update_gallery_placeholder("Deleting assets...")

    def on_file_operation_progress(self, current: int, total: int, message: str):
        """Handles file operation progress"""
        progress = int((current / total) * 100) if total > 0 else 0
        self.model.control_panel_model.set_progress(progress)
        self.view.update_gallery_placeholder(message)
        # Update button states during file operations
        self.controller.control_panel_controller.update_button_states()

    def on_file_operation_completed(self, success_messages: list, error_messages: list):
        """Handles file operation completion"""
        with measure_operation(
            "file_operation_controller.file_operation_completed",
            {
                "success_count": len(success_messages),
                "error_count": len(error_messages),
            },
        ):
            # Disable progress bar
            self.model.control_panel_model.set_progress(0)

            # Log operation results (without pop-up windows)
            if success_messages and error_messages:
                logger.info(
                    f"Operation completed partially - Success: "
                    f"{len(success_messages)}, Errors: {len(error_messages)}"
                )
            elif success_messages:
                logger.info(
                    f"Operation completed successfully - Moved: "
                    f"{len(success_messages)} files"
                )
            elif error_messages:
                logger.error(f"Operation completed with errors: {error_messages}")

            # Remove moved/deleted assets from the list without rescanning
            if success_messages:
                logger.debug(f"Success messages: {success_messages}")

                # Remove assets from the data model
                current_assets = self.model.asset_grid_model.get_assets()
                logger.debug(f"Current assets count: {len(current_assets)}")

                for i, asset in enumerate(current_assets):
                    asset_name = asset.get("name")
                    logger.debug(
                        f"Asset {i}: name='{asset_name}', in success_messages: "
                        f"{asset_name in success_messages}"
                    )

                updated_assets = [
                    asset
                    for asset in current_assets
                    if asset.get("name") not in success_messages
                ]
                logger.debug(f"Updated assets count: {len(updated_assets)}")
                self.model.asset_grid_model._assets = updated_assets

                # Remove tiles from the view directly, without rebuilding the entire gallery
                asset_tiles = self.controller.asset_grid_controller.get_asset_tiles()
                logger.debug(f"Active tiles count before removal: {len(asset_tiles)}")
                for tile in asset_tiles:
                    logger.debug(
                        f"Tile asset_id: '{tile.asset_id}', in success_messages: "
                        f"{tile.asset_id in success_messages}"
                    )
                self.view.remove_asset_tiles(success_messages)

                # Also remove from the controller's asset_tiles list
                updated_tiles = [
                    tile
                    for tile in asset_tiles
                    if tile.asset_id not in success_messages
                ]
                self.controller.asset_grid_controller.asset_tiles = updated_tiles
                logger.debug(f"Active tiles count after removal: {len(updated_tiles)}")

                # Check if the gallery is empty after removing assets
                if not updated_assets:
                    self.view.update_gallery_placeholder(
                        "No assets found in this folder."
                    )
                else:
                    # Hide placeholder if there were assets
                    self.view.update_gallery_placeholder("")

                logger.debug(
                    "Removed %d assets from list and view without rescanning",
                    len(success_messages),
                )

            # Clear selection after the operation
            self.model.selection_model.clear_selection()

            # Update button states after the operation is complete
            self.controller.control_panel_controller.update_button_states()

            logger.info(
                "File operation completed - Success: %d, Errors: %d",
                len(success_messages),
                len(error_messages),
            )

    def on_file_operation_error(self, error_msg: str):
        """Handles file operation errors"""
        self.model.control_panel_model.set_progress(0)
        self.view.update_gallery_placeholder(f"File operation error: {error_msg}")
        # Update button states after a file operation error
        self.controller.control_panel_controller.update_button_states()

    def on_drag_drop_started(self, asset_ids: list):
        """Handles the start of a drag & drop operation"""
        logger.debug(
            "FileOperationController: Drag operation started for assets: %s", asset_ids
        )
        # Visual feedback can be added here, e.g., changing the cursor
        # Update button states after starting a drag & drop operation
        self.controller.control_panel_controller.update_button_states()

    def on_drag_drop_possible(self, possible: bool):
        """Handles checking if a drop is possible"""
        logger.debug(f"FileOperationController: Drop possible: {possible}")
        # Visual feedback can be added here, e.g., highlighting the target
        # Update button states after checking if a drop is possible
        self.controller.control_panel_controller.update_button_states()

    def on_drag_drop_completed(self, target_path: str, asset_ids: list):
        """Handles the completion of a drag & drop operation"""
        logger.debug(
            "FileOperationController: Drop completed to %s for assets: %s",
            target_path,
            asset_ids,
        )
        assets_to_move = self._get_assets_by_ids(asset_ids)

        if assets_to_move:
            current_folder = self.model.asset_grid_model.get_current_folder()
            self.model.file_operations_model.move_assets(
                assets_to_move,
                current_folder,
                target_path,
            )
            # Removed placeholder to eliminate gallery flickering during drag & drop
        else:
            logger.warning(
                "FileOperationController: No assets found for drag & drop operation."
            )
