"""
FileOperationController - Kontroler zarządzający operacjami na plikach
Odpowiedzialny za przenoszenie, usuwanie i obsługę drag & drop assetów.
"""

import logging

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from core.performance_monitor import measure_operation

logger = logging.getLogger(__name__)


class FileOperationController(QObject):
    """Controller zarządzający operacjami na plikach"""

    def __init__(self, model, view, controller):
        super().__init__()
        self.model = model
        self.view = view
        self.controller = controller

    def setup(self):
        """Inicjalizuje kontroler operacji na plikach"""
        logger.debug("File operation controller initialized")

    def get_assets_by_ids(self, asset_ids: list) -> list:
        """Pobiera pełne dane assetów na podstawie listy ID."""
        all_assets = self.model.asset_grid_model.get_assets()
        return [asset for asset in all_assets if asset.get("name") in asset_ids]

    def on_move_selected_clicked(self):
        """Obsługuje kliknięcie przycisku 'Przenieś zaznaczone'."""
        selected_asset_ids = self.model.selection_model.get_selected_asset_ids()
        if not selected_asset_ids:
            QMessageBox.information(
                self.view,
                "Przenoszenie assetów",
                "Brak zaznaczonych assetów do przeniesienia.",
            )
            return

        assets_to_move = self.get_assets_by_ids(selected_asset_ids)
        logger.debug(f"assets_to_move: {[a.get('name') for a in assets_to_move]}")

        if not assets_to_move:
            QMessageBox.warning(
                self.view,
                "Przenoszenie assetów",
                "Nie znaleziono pełnych danych dla zaznaczonych assetów.",
            )
            return

        target_folder = QFileDialog.getExistingDirectory(
            self.view,
            "Wybierz folder docelowy",
            self.model.asset_grid_model.get_current_folder(),
        )
        if target_folder:
            self.model.file_operations_model.move_assets(
                assets_to_move,
                self.model.asset_grid_model.get_current_folder(),
                target_folder,
            )
            self.model.control_panel_model.set_progress(0)  # Reset progress bar
            self.view.update_gallery_placeholder("Przenoszenie assetów...")

    def on_delete_selected_clicked(self):
        """Obsługuje kliknięcie przycisku 'Usuń zaznaczone'."""
        selected_asset_ids = self.model.selection_model.get_selected_asset_ids()
        if not selected_asset_ids:
            QMessageBox.information(
                self.view,
                "Usuwanie assetów",
                "Brak zaznaczonych assetów do usunięcia.",
            )
            return

        reply = QMessageBox.question(
            self.view,
            "Potwierdzenie usunięcia",
            (
                f"Czy na pewno chcesz usunąć {len(selected_asset_ids)} "
                "zaznaczonych assetów?\nTa operacja jest nieodwracalna!"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            assets_to_delete = self.get_assets_by_ids(selected_asset_ids)

            if not assets_to_delete:
                QMessageBox.warning(
                    self.view,
                    "Usuwanie assetów",
                    "Nie znaleziono pełnych danych dla zaznaczonych assetów.",
                )
                return

            self.model.file_operations_model.delete_assets(
                assets_to_delete,
                self.model.asset_grid_model.get_current_folder(),
            )
            self.model.control_panel_model.set_progress(0)  # Reset progress bar
            self.view.update_gallery_placeholder("Usuwanie assetów...")

    def on_file_operation_progress(self, current: int, total: int, message: str):
        """Obsługuje postęp operacji na plikach"""
        progress = int((current / total) * 100) if total > 0 else 0
        self.model.control_panel_model.set_progress(progress)
        self.view.update_gallery_placeholder(message)
        # Aktualizuj stan przycisków podczas operacji na plikach
        self.controller.control_panel_controller.update_button_states()

    def on_file_operation_completed(self, success_messages: list, error_messages: list):
        """Obsługuje zakończenie operacji na plikach"""
        with measure_operation(
            "file_operation_controller.file_operation_completed",
            {
                "success_count": len(success_messages),
                "error_count": len(error_messages),
            },
        ):
            # Wyłącz progress bar
            self.model.control_panel_model.set_progress(0)

            # Logowanie wyników operacji (bez wyskakujących okien)
            if success_messages and error_messages:
                logger.info(
                    f"Operacja zakończona częściowo - Pomyślnie: "
                    f"{len(success_messages)}, Błędy: {len(error_messages)}"
                )
            elif success_messages:
                logger.info(
                    f"Operacja zakończona pomyślnie - Przeniesiono: "
                    f"{len(success_messages)} plików"
                )
            elif error_messages:
                logger.error(f"Operacja zakończona z błędami: {error_messages}")

            # Usuń przeniesione/usunięte assety z listy bez ponownego skanowania
            if success_messages:
                logger.debug(f"Success messages: {success_messages}")

                # Usuń assety z modelu danych
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

                # Usuń kafelki z widoku bezpośrednio, bez przebudowy całej galerii
                asset_tiles = self.controller.asset_grid_controller.get_asset_tiles()
                logger.debug(f"Active tiles count before removal: {len(asset_tiles)}")
                for tile in asset_tiles:
                    logger.debug(
                        f"Tile asset_id: '{tile.asset_id}', in success_messages: "
                        f"{tile.asset_id in success_messages}"
                    )
                self.view.remove_asset_tiles(success_messages)

                # Usuń również z listy asset_tiles kontrolera
                updated_tiles = [
                    tile
                    for tile in asset_tiles
                    if tile.asset_id not in success_messages
                ]
                self.controller.asset_grid_controller.asset_tiles = updated_tiles
                logger.debug(f"Active tiles count after removal: {len(updated_tiles)}")

                # Sprawdź czy po usunięciu assetów galeria jest pusta
                if not updated_assets:
                    self.view.update_gallery_placeholder(
                        "Nie znaleziono assetów w tym folderze."
                    )
                else:
                    # Ukryj placeholder jeśli były assety
                    self.view.update_gallery_placeholder("")

                logger.debug(
                    "Removed %d assets from list and view without rescanning",
                    len(success_messages),
                )

            # Wyczyść zaznaczenie po operacji
            self.model.selection_model.clear_selection()

            # Aktualizuj stan przycisków po zakończeniu operacji
            self.controller.control_panel_controller.update_button_states()

            logger.info(
                "File operation completed - Success: %d, Errors: %d",
                len(success_messages),
                len(error_messages),
            )

    def on_file_operation_error(self, error_msg: str):
        """Obsługuje błędy operacji na plikach"""
        self.model.control_panel_model.set_progress(0)
        self.view.update_gallery_placeholder(f"Błąd operacji na plikach: {error_msg}")
        # Aktualizuj stan przycisków po błędzie operacji na plikach
        self.controller.control_panel_controller.update_button_states()

    def on_drag_drop_started(self, asset_ids: list):
        """Obsługuje rozpoczęcie operacji drag & drop"""
        logger.debug(
            "FileOperationController: Drag operation started for assets: %s", asset_ids
        )
        # Tutaj można dodać wizualny feedback, np. zmianę kursora
        # Aktualizuj stan przycisków po rozpoczęciu operacji drag & drop
        self.controller.control_panel_controller.update_button_states()

    def on_drag_drop_possible(self, possible: bool):
        """Obsługuje sprawdzenie możliwości drop"""
        logger.debug(f"FileOperationController: Drop possible: {possible}")
        # Tutaj można dodać wizualny feedback, np. podświetlenie celu
        # Aktualizuj stan przycisków po sprawdzeniu możliwości drop
        self.controller.control_panel_controller.update_button_states()

    def on_drag_drop_completed(self, target_path: str, asset_ids: list):
        """Obsługuje zakończenie operacji drag & drop"""
        logger.debug(
            "FileOperationController: Drop completed to %s for assets: %s",
            target_path,
            asset_ids,
        )
        assets_to_move = self.get_assets_by_ids(asset_ids)
        logger.debug(f"assets_to_move: {[a.get('name') for a in assets_to_move]}")

        if assets_to_move:
            current_folder = self.model.asset_grid_model.get_current_folder()
            logger.debug(f"Moving assets from '{current_folder}' to '{target_path}'")
            self.model.file_operations_model.move_assets(
                assets_to_move,
                current_folder,
                target_path,
            )
            logger.debug("move_assets called successfully")
            # Usunięto placeholder aby wyeliminować migotanie galerii podczas drag & drop
        else:
            logger.warning(
                "FileOperationController: No assets found for drag & drop operation."
            )
