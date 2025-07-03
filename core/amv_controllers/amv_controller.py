"""
AmvController - Kontroler dla zakładki AMV
Łączy Model z Widokiem, obsługuje interakcje użytkownika i aktualizuje stan aplikacji.
"""

import logging
import os

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from core.file_utils import open_file_in_default_app, open_path_in_explorer
from core.performance_monitor import measure_operation

# Importy widoków będą dodane po przeniesieniu klas do core/amv_views/
# from ..amv_views.amv_main_view import AmvView

logger = logging.getLogger(__name__)


class AmvController(QObject):
    """Controller dla zakładki AMV - łącznik Model-View"""

    # Sygnał emitowany przy zmianie folderu roboczego
    working_directory_changed = pyqtSignal(str)

    def __init__(self, model, view):
        """
        Simplified constructor - używa tylko głównych komponentów.
        Wszystkie sub-modele są dostępne przez model.
        """
        from ..amv_models.amv_model import AmvModel

        super().__init__()
        self.model: AmvModel = model
        self.view = view

        self.asset_rebuilder = None  # Worker dla przebudowy assetów

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
        logger.debug("AmvController initialized with dependency injection - ETAP 15")

    def _connect_signals(self):
        from .handlers.signal_connector import SignalConnector

        self.signal_connector = SignalConnector(self.model, self.view, self)
        self.signal_connector.connect_all()

    def _on_folder_structure_changed(self, tree_model):
        self.view.folder_tree_view.setModel(tree_model)
        if tree_model.rowCount() > 0:
            root_index = tree_model.index(0, 0)
            self.view.folder_tree_view.expand(root_index)
        logger.debug("Folder structure updated in view")

    def _on_splitter_state_changed(self, is_open: bool):
        sizes = self.model.get_splitter_sizes()
        self.view.update_splitter_sizes(sizes)
        self.view.update_toggle_button_text(is_open)
        state = "open" if is_open else "collapsed"
        logger.debug(f"Panel state changed: {state}")

    def _on_config_loaded(self, config: dict):
        self.model.set_config(config)
        logger.debug("Konfiguracja załadowana pomyślnie")

    def _on_state_initialized(self):
        self.model.workspace_folders_model.load_folders()
        logger.debug("Stan aplikacji zainicjalizowany")

    def _on_scan_started(self, folder_path: str):
        logger.info(f"Controller: Scan started for: {folder_path}")
        self.view.update_gallery_placeholder("Skanowanie folderu...")
        self.model.control_panel_model.set_progress(0)
        # Aktualizuj stan przycisków na początku skanowania
        self.control_panel_controller.update_button_states()

    def _on_scan_progress(self, current: int, total: int, message: str):
        """Obsługuje postęp skanowania."""
        progress = int((current / total) * 100) if total > 0 else 0
        self.model.control_panel_model.set_progress(progress)
        logger.debug(f"Scan progress: {progress}% - {message}")
        # Aktualizuj stan przycisków podczas skanowania
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

            # Zawsze przebuduj siatkę po zakończeniu skanowania
            self.model.asset_grid_model.set_assets(assets)
            # Zapisz oryginalną listę assetów (bez filtrowania)
            self.asset_grid_controller.set_original_assets(assets)
            logger.debug(f"Assets updated and grid rebuilt: {len(assets)} items")
            logger.debug(
                f"AmvController: _on_scan_completed - Original assets set: {len(assets)} items"
            )

            # Zamiast resetować filtry, zastosuj aktualny filtr do nowych danych
            current_star_filter = self.asset_grid_controller.active_star_filter
            if current_star_filter > 0:
                # Zastosuj aktualny filtr gwiazdek do nowych assetów
                logger.debug(
                    f"Stosowanie istniejącego filtra gwiazdek: {current_star_filter}"
                )
                self.control_panel_controller.filter_assets_by_stars(
                    current_star_filter
                )
            else:
                # Jeśli brak filtra, wyświetl wszystkie assety
                self.asset_grid_controller.rebuild_asset_grid(
                    assets, preserve_filter=False
                )

            # Aktualizuj stan przycisków po załadowaniu assetów
            self.control_panel_controller.update_button_states()

    def _on_scan_error(self, error_msg: str):
        logger.error(f"Controller: Scan error: {error_msg}")
        self.model.control_panel_model.set_progress(0)
        self.view.update_gallery_placeholder(f"Błąd skanowania: {error_msg}")
        # Aktualizuj stan przycisków po błędzie skanowania
        self.control_panel_controller.update_button_states()

    def _handle_file_action(self, path: str, action_type: str):
        """Wspólna logika dla obsługi kliknięć w pliki"""
        logger.debug(f"Controller: File action '{action_type}' for: {path}")
        if not path:
            return

        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    # Otwórz folder w eksploratorze
                    open_path_in_explorer(path, self.view)
                    logger.info(f"Otworzono folder w eksploratorze: {path}")
                else:
                    if action_type == "thumbnail":
                        from core.preview_window import PreviewWindow

                        PreviewWindow(path, self.view)
                        logger.info(f"Otworzono podgląd w dedykowanym oknie: {path}")
                    elif action_type == "filename":
                        open_file_in_default_app(path, self.view)
                        logger.info(f"Otworzono plik w zewnętrznej aplikacji: {path}")
            except Exception as e:
                logger.error(f"Błąd podczas otwierania {path}: {e}")
                QMessageBox.warning(self.view, "Błąd", f"Nie można otworzyć: {path}")
        else:
            logger.warning(f"Ścieżka nie istnieje: {path}")
            QMessageBox.warning(self.view, "Błąd", f"Ścieżka nie istnieje: {path}")

    def _on_tile_thumbnail_clicked(self, path: str):
        self._handle_file_action(path, "thumbnail")

    def _on_tile_filename_clicked(self, path: str):
        self._handle_file_action(path, "filename")
