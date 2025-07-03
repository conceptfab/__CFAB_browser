"""
AssetRebuildController - Kontroler zarządzający przebudową assetów w tle
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
        """Przebudowuje assety w określonym folderze"""
        logger.debug("Rozpoczęto przebudowę assetów w folderze: %s", folder_path)

        # Utwórz worker do przebudowy
        self.asset_rebuilder = AssetRebuilderWorker(folder_path)

        # Połącz sygnały
        self.asset_rebuilder.progress_updated.connect(self.on_rebuild_progress)
        self.asset_rebuilder.finished.connect(self.on_rebuild_finished)
        self.asset_rebuilder.error_occurred.connect(self.on_rebuild_error)

        # Uruchom worker
        self.asset_rebuilder.start()

    def on_rebuild_progress(self, current: int, total: int, message: str):
        """Obsługuje postęp przebudowy assetów"""
        progress = int((current / total) * 100) if total > 0 else 0
        self.model.control_panel_model.set_progress(progress)
        logger.debug(f"Rebuild progress: {progress}% - {message}")
        # Aktualizuj stan przycisków podczas przebudowy
        self.controller.control_panel_controller.update_button_states()

    def on_rebuild_finished(self, message: str):
        """Obsługuje zakończenie przebudowy assetów"""
        logger.debug(f"Przebudowa zakończona: {message}")
        self.model.control_panel_model.set_progress(100)

        # Odśwież widok
        current_folder = self.model.asset_grid_model.get_current_folder()
        if current_folder:
            self.controller.folder_tree_controller.on_folder_clicked(current_folder)
        else:
            # Aktualizuj stan przycisków jeśli nie ma folderu roboczego
            self.controller.control_panel_controller.update_button_states()

    def on_rebuild_error(self, error_message: str):
        """Obsługuje błędy podczas przebudowy assetów"""
        logger.error(f"Błąd przebudowy assetów: {error_message}")

        # Zatrzymaj spinner postępu
        self.model.control_panel_model.set_progress(0)

        # Pokaż komunikat błędu użytkownikowi
        self.view.update_gallery_placeholder(
            f"Błąd przebudowy assetów: {error_message}"
        )

        # Wyczyść worker
        if self.asset_rebuilder:
            self.asset_rebuilder.deleteLater()
            self.asset_rebuilder = None

        # Aktualizuj stan przycisków po błędzie przebudowy
        self.controller.control_panel_controller.update_button_states()
