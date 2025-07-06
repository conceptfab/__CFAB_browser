"""
FileOperationController - Controller for managing file operations.
Responsible for moving, deleting, and handling drag & drop of assets.
"""

import logging
import os

from PyQt6.QtCore import QObject, QTimer
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
        """Enhanced selection validation for operations with better error handling"""
        selected_asset_ids = self.model.selection_model.get_selected_asset_ids()
        
        # Check if any assets are selected
        if not selected_asset_ids:
            QMessageBox.information(
                self.view,
                operation_name,
                f"No assets selected for {operation_name.lower()}.",
            )
            return []

        # Get full asset data for selected IDs
        assets_to_process = self._get_assets_by_ids(selected_asset_ids)
        
        # Validate that we found full data for all selected assets
        if not assets_to_process:
            QMessageBox.warning(
                self.view,
                operation_name,
                "Could not find full data for the selected assets.",
            )
            return []
        
        # Check for partial data loss (some selected assets not found)
        found_asset_ids = [asset.get("name") for asset in assets_to_process]
        missing_count = len(selected_asset_ids) - len(found_asset_ids)
        
        if missing_count > 0:
            logger.warning(f"Missing data for {missing_count} selected assets")
            QMessageBox.warning(
                self.view,
                operation_name,
                f"Found {len(assets_to_process)} assets, but {missing_count} selected assets are missing data.",
            )

        return assets_to_process

    def on_move_selected_clicked(self):
        """Simplified method using central validation"""
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
        """Simplified method using central validation"""
        assets_to_delete = self._validate_selection("Deleting Assets")
        if not assets_to_delete:
            return
        reply = QMessageBox.question(
            self.view,
            "Confirm Deletion",
            (
                f"Are you sure you want to delete {len(assets_to_delete)} selected assets?\nThis operation is irreversible!"
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

                # TYMCZASOWO: CAŁKOWITE WYŁĄCZENIE ODŚWIEŻANIA - TEST
                logger.warning("TYMCZASOWO: CAŁKOWITE WYŁĄCZENIE ODŚWIEŻANIA GALERII - TYLKO CLEAR SELECTION")
                # self._fallback_refresh_gallery()

            # Clear selection after the operation
            self.model.selection_model.clear_selection()

            # Update button states after the operation is complete
            self.controller.control_panel_controller.update_button_states()

            # TYMCZASOWO WYŁĄCZONE: Odłożone odświeżanie struktury folderów
            # if success_messages:
            #     # Użyj QTimer żeby odłożyć odświeżanie struktury folderów
            #     # To pozwoli najpierw zakończyć usuwanie kafelków z galerii
            #     QTimer.singleShot(100, lambda: self._refresh_folder_structure_delayed())

            logger.info(
                "File operation completed - Success: %d, Errors: %d",
                len(success_messages),
                len(error_messages),
            )

    def _remove_moved_assets_optimized(self, success_messages: list):
        """OPTYMALIZACJA: Szybkie usuwanie tylko przeniesionych assetów bez przebudowy galerii"""
        try:
            if not self._validate_optimization_inputs(success_messages):
                return
            
            # Najpierw usuń kafelki z widoku
            self._remove_tiles_from_view_fast(success_messages)
            
            # Zaktualizuj model assetów BEZ EMITOWANIA SYGNAŁU (bez przebudowy galerii)
            current_assets = self.model.asset_grid_model.get_assets()
            updated_assets = [
                asset for asset in current_assets 
                if asset.get("name") not in success_messages
            ]
            
            # CICHA aktualizacja bez emitowania sygnału assets_changed
            self.model.asset_grid_model.update_assets_silently(updated_assets)
            
            # Odłożone odświeżanie struktury folderów
            QTimer.singleShot(100, self._refresh_folder_structure_delayed)
            
            logger.debug(f"OPTYMALIZACJA: Usunięto {len(success_messages)} assetów bez przebudowy galerii")

        except Exception as e:
            logger.error(f"Błąd podczas optymalizowanego usuwania assetów: {e}")
            self._fallback_refresh_gallery()
    
    def _validate_optimization_inputs(self, success_messages: list) -> bool:
        """Waliduje dane wejściowe dla optymalizacji"""
        if not success_messages:
            logger.debug("OPTYMALIZACJA: Brak wiadomości sukcesu - pomijam optymalizowane usuwanie")
            return False
        
        current_assets = self.model.asset_grid_model.get_assets()
        if not current_assets:
            logger.debug("OPTYMALIZACJA: Brak aktualnych assetów - pomijam optymalizowane usuwanie")
            return False
            
        return True
    


    def _remove_tiles_from_view_fast(self, asset_ids_to_remove: list):
        """OPTYMALIZACJA: Szybkie usuwanie kafelków bez reorganizacji layoutu"""
        try:
            # Walidacja danych wejściowych
            if not asset_ids_to_remove:
                logger.debug("OPTYMALIZACJA: Brak ID assetów do usunięcia")
                return
            
            # Znajdź kafelki do usunięcia (bez modyfikacji podczas iteracji)
            asset_tiles = self.controller.asset_grid_controller.get_asset_tiles()
            tiles_to_remove = []
            
            for tile in asset_tiles:
                if hasattr(tile, 'asset_id') and tile.asset_id in asset_ids_to_remove:
                    tiles_to_remove.append(tile)
            
            # Usuń znalezione kafelki
            for tile in tiles_to_remove:
                # Usuń z layoutu
                if hasattr(self.view, 'gallery_layout'):
                    self.view.gallery_layout.removeWidget(tile)
                
                # Usuń z listy asset_tiles BEZPIECZNIE
                if tile in asset_tiles:
                    asset_tiles.remove(tile)
                
                # Zwróć do puli
                if hasattr(self.controller.asset_grid_controller, 'tile_pool'):
                    self.controller.asset_grid_controller.tile_pool.release(tile)
                
                logger.debug(f"FAST REMOVE: {tile.asset_id}")

            logger.debug(f"OPTYMALIZACJA: Szybko usunięto {len(tiles_to_remove)} kafelków z widoku")

        except Exception as e:
            logger.error(f"Błąd podczas szybkiego usuwania kafelków: {e}")

    def _refresh_folder_structure_delayed(self):
        """OPTYMALIZACJA: Odłożone odświeżanie struktury folderów"""
        try:
            current_folder_path = self.model.asset_grid_model.get_current_folder()
            if current_folder_path:
                # Odśwież tylko strukturę drzewa folderów (dla liczników assetów)
                self.model.folder_system_model.refresh_folder(current_folder_path)
                logger.debug(f"OPTYMALIZACJA: Odświeżono strukturę folderów: {current_folder_path}")
            
            # Odśwież także folder docelowy przy operacjach move
            target_folder_path = self.model.file_operations_model.get_last_target_folder()
            if target_folder_path and target_folder_path != current_folder_path:
                self.model.folder_system_model.refresh_folder(target_folder_path)
                logger.debug(f"OPTYMALIZACJA: Odświeżono folder docelowy: {target_folder_path}")
            
        except Exception as e:
            logger.error(f"Błąd odświeżania struktury folderów: {e}")

    def _fallback_refresh_gallery(self):
        """Fallback: Pełne odświeżanie galerii w przypadku błędu optymalizacji"""
        try:
            logger.warning("FALLBACK: Pełne odświeżanie galerii po błędzie optymalizacji")
            current_folder = self.model.asset_grid_model.get_current_folder()
            if current_folder:
                self.model.asset_grid_model.scan_folder(current_folder)
        except Exception as e:
            logger.error(f"Błąd podczas fallback refresh galerii: {e}")

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
