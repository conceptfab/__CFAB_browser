"""
AmvController - Kontroler dla zakładki AMV
Łączy Model z Widokiem, obsługuje interakcje użytkownika i aktualizuje stan aplikacji.
"""

import logging
import os
import subprocess
import sys
from typing import Optional

from PyQt6.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from core.amv_models.asset_grid_model import (
    AssetGridModel,
    AssetScannerModelMV,
    FolderTreeModel,
    WorkspaceFoldersModel,
)
from core.amv_models.asset_tile_model import AssetTileModel
from core.amv_models.control_panel_model import ControlPanelModel
from core.amv_models.drag_drop_model import DragDropModel
from core.amv_models.file_operations_model import FileOperationsModel
from core.amv_models.selection_model import SelectionModel
from core.performance_monitor import measure_operation

from ..amv_views.asset_tile_view import AssetTileView
from ..scanner import find_and_create_assets

# Importy widoków będą dodane po przeniesieniu klas do core/amv_views/
# from ..amv_views.amv_main_view import AmvView

logger = logging.getLogger(__name__)


class AssetRebuilderThread(QThread):
    """Worker dla przebudowy assetów w folderze"""

    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    rebuild_finished = pyqtSignal(str)  # message
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self, folder_path: str):
        super().__init__()
        self.folder_path = folder_path

    def run(self):
        """Główna metoda przebudowy assetów"""
        try:
            if not self.folder_path or not os.path.exists(self.folder_path):
                error_msg = f"Nieprawidłowy folder: {self.folder_path}"
                self.error_occurred.emit(error_msg)
                return

            logger.info(
                "Rozpoczęcie przebudowy assetów w folderze: %s",
                self.folder_path,
            )

            # Krok 1: Usuwanie plików .asset
            self.progress_updated.emit(0, 100, "Usuwanie starych plików .asset...")
            self._remove_asset_files()

            # Krok 2: Usuwanie folderu .cache
            self.progress_updated.emit(25, 100, "Usuwanie folderu .cache...")
            self._remove_cache_folder()

            # Krok 3: Uruchamianie scanner.py
            self.progress_updated.emit(
                50, 100, "Skanowanie i tworzenie nowych assetów..."
            )
            self._run_scanner()

            self.progress_updated.emit(100, 100, "Przebudowa zakończona!")
            self.rebuild_finished.emit(
                "Pomyślnie przebudowano assety w folderze: " f"{self.folder_path}"
            )

        except Exception as e:
            error_msg = f"Błąd podczas przebudowy assetów: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def _remove_asset_files(self):
        """Usuwa wszystkie pliki .asset z folderu"""
        try:
            asset_files = [
                f for f in os.listdir(self.folder_path) if f.endswith(".asset")
            ]
            for asset_file in asset_files:
                file_path = os.path.join(self.folder_path, asset_file)
                os.remove(file_path)
                logger.debug("Usunięto plik asset: %s", asset_file)

            logger.info("Usunięto %d plików .asset", len(asset_files))
        except Exception as e:
            logger.error(f"Błąd usuwania plików .asset: {e}")
            raise

    def _remove_cache_folder(self):
        """Usuwa folder .cache jeśli istnieje"""
        try:
            cache_folder = os.path.join(self.folder_path, ".cache")
            if os.path.exists(cache_folder) and os.path.isdir(cache_folder):
                import shutil  # lokalny import, zgodnie z dobrymi praktykami

                shutil.rmtree(cache_folder)
                logger.info("Usunięto folder .cache: %s", cache_folder)
            else:
                logger.debug("Folder .cache nie istnieje lub nie jest folderem")
        except Exception as e:
            logger.error(f"Błąd usuwania folderu .cache: {e}")
            raise

    def _run_scanner(self):
        """Uruchamia scanner.py w folderze"""
        try:

            def progress_callback(current, total, message):
                if total > 0:
                    # Mapuj postęp scanner-a na przedział 50-100%
                    scanner_progress = int(50 + (current / total) * 50)
                    self.progress_updated.emit(scanner_progress, 100, message)
                else:
                    self.progress_updated.emit(75, 100, message)

            created_assets = find_and_create_assets(self.folder_path, progress_callback)
            logger.info("Scanner utworzył %d nowych assetów", len(created_assets))

        except Exception as e:
            logger.error(f"Błąd uruchamiania scanner-a: {e}")
            raise


class AmvController(QObject):
    """Controller dla zakładki AMV - łącznik Model-View"""

    # Sygnał emitowany przy zmianie folderu roboczego
    working_directory_changed = pyqtSignal(str)

    def __init__(
        self,
        model,
        view,
        asset_grid_model: Optional[AssetGridModel] = None,
        control_panel_model: Optional[ControlPanelModel] = None,
        file_operations_model: Optional[FileOperationsModel] = None,
        selection_model: Optional[SelectionModel] = None,
        drag_drop_model: Optional[DragDropModel] = None,
        asset_scanner_model: Optional[AssetScannerModelMV] = None,
        folder_system_model: Optional[FolderTreeModel] = None,
        workspace_folders_model: Optional[WorkspaceFoldersModel] = None,
    ):
        from ..amv_models.amv_model import AmvModel

        super().__init__()
        self.model: AmvModel = model
        self.view = view

        # Wstrzykiwanie bezpośrednich zależności z fallback do modelu
        self.asset_grid_model = asset_grid_model or model.asset_grid_model
        self.control_panel_model = control_panel_model or model.control_panel_model
        self.file_operations_model = (
            file_operations_model or model.file_operations_model
        )
        self.selection_model = selection_model or model.selection_model
        self.drag_drop_model = drag_drop_model or model.drag_drop_model
        self.asset_scanner_model = asset_scanner_model or model.asset_scanner_model
        self.folder_system_model = folder_system_model or model.folder_system_model
        self.workspace_folders_model = (
            workspace_folders_model or model.workspace_folders_model
        )

        self.asset_tiles = []  # Lista do przechowywania kafelków
        self.asset_rebuilder = None  # Worker dla przebudowy assetów

        # Object Pooling dla AssetTileView
        self._tile_pool = []  # Pula nieużywanych kafelków
        self._active_tiles = []  # Lista aktywnych kafelków
        self._max_pool_size = 50  # Maksymalny rozmiar puli

        self._connect_signals()
        self._setup_folder_tree()
        self._setup_asset_grid()
        logger.debug("AmvController initialized with dependency injection - ETAP 15")

    def _connect_signals(self):
        # --- Podstawowe sygnały UI ---
        self.view.splitter_moved.connect(self.model.set_splitter_sizes)
        self.view.toggle_panel_requested.connect(self.model.toggle_left_panel)
        self.model.splitter_state_changed.connect(self._on_splitter_state_changed)
        self.view.gallery_viewport_resized.connect(self._on_gallery_resized)

        # --- Sygnały modelu folderów ---
        self.folder_system_model.folder_clicked.connect(self._on_folder_clicked)
        self.folder_system_model.folder_structure_updated.connect(
            self._on_folder_structure_changed
        )
        self.workspace_folders_model.folders_updated.connect(
            self.view.update_workspace_folder_buttons
        )
        self.view.workspace_folder_clicked.connect(self._on_workspace_folder_clicked)

        # --- Sygnały modelu siatki assetów ---
        self.asset_grid_model.assets_changed.connect(self._on_assets_changed)
        self.asset_grid_model.loading_state_changed.connect(
            self._on_loading_state_changed
        )

        # --- Sygnały panelu kontrolnego ---
        self.control_panel_model.progress_changed.connect(
            self.view.progress_bar.setValue
        )
        self.control_panel_model.thumbnail_size_changed.connect(
            self._on_thumbnail_size_changed
        )
        self.view.thumbnail_size_slider.valueChanged.connect(
            self.control_panel_model.set_thumbnail_size
        )
        self.control_panel_model.selection_state_changed.connect(
            self._on_control_panel_selection_state_changed
        )

        self.view.select_all_button.clicked.connect(self._on_select_all_clicked)
        self.view.deselect_all_button.clicked.connect(self._on_deselect_all_clicked)
        self.view.move_selected_button.clicked.connect(self._on_move_selected_clicked)
        self.view.delete_selected_button.clicked.connect(
            self._on_delete_selected_clicked
        )

        # --- Sygnały gwiazdek z panelu kontrolnego ---
        for i, star_cb in enumerate(self.view.star_checkboxes):
            # Blokuj automatyczną zmianę stanu checkboxa
            star_cb.setAutoExclusive(False)
            star_cb.clicked.connect(
                lambda checked, star_index=i: self._on_star_filter_clicked(
                    star_index + 1
                )
            )

        # --- Sygnały AssetGridModel dla przebudowy siatki ---
        self.model.asset_grid_model.recalculate_columns_requested.connect(
            self._on_recalculate_columns_requested
        )
        self.model.asset_grid_model.grid_layout_changed.connect(
            self._on_grid_layout_changed
        )

        # --- Sygnały konfiguracji ---
        self.model.config_manager.config_loaded.connect(self._on_config_loaded)
        self.model.state_initialized.connect(self._on_state_initialized)

        # --- Sygnały skanera assetów ---
        scanner_model = self.model.asset_scanner_model
        scanner_model.scan_started.connect(self._on_scan_started)
        scanner_model.scan_progress.connect(self._on_scan_progress)
        scanner_model.scan_completed.connect(self._on_scan_completed)
        scanner_model.scan_error.connect(self._on_scan_error)

        # --- Sygnały SelectionModel ---
        self.model.selection_model.selection_changed.connect(self._on_selection_changed)

        # --- Sygnały FileOperationsModel ---
        self.model.file_operations_model.operation_progress.connect(
            self._on_file_operation_progress
        )
        self.model.file_operations_model.operation_completed.connect(
            self._on_file_operation_completed
        )
        self.model.file_operations_model.operation_error.connect(
            self._on_file_operation_error
        )

        # --- Sygnały DragDropModel ---
        self.model.drag_drop_model.drag_started.connect(self._on_drag_drop_started)
        self.model.drag_drop_model.drop_possible.connect(self._on_drag_drop_possible)
        self.model.drag_drop_model.drop_completed.connect(self._on_drag_drop_completed)

        # --- Sygnały rozwijania/zwijania drzewa ---
        self.view.collapse_tree_requested.connect(self._on_collapse_tree_requested)
        self.view.expand_tree_requested.connect(self._on_expand_tree_requested)

    def _setup_folder_tree(self):
        tree_model = self.model.folder_system_model.get_tree_model()
        self.view.folder_tree_view.setModel(tree_model)
        self.view.folder_tree_view.clicked.connect(self._on_tree_item_clicked)
        self.view.folder_tree_view.expanded.connect(self._on_tree_item_expanded)
        self.view.folder_tree_view.collapsed.connect(self._on_tree_item_collapsed)

        # Skonfiguruj drag & drop dla folder_tree_view
        if hasattr(self.view.folder_tree_view, "set_models"):
            self.view.folder_tree_view.set_models(
                self.model.drag_drop_model,
                self.model.file_operations_model,
                self.model.asset_grid_model.get_current_folder,
                self.model.asset_grid_model,
            )

        # Ustaw callback dla przebudowy assetów
        if hasattr(self.view.folder_tree_view, "set_rebuild_callback"):
            self.view.folder_tree_view.set_rebuild_callback(
                self._rebuild_assets_in_folder
            )

        logger.info("Folder system model connected to view - ETAP 6")

    def _setup_asset_grid(self):
        logger.debug("Asset grid model connected to view - ETAP 9")

    def _on_folder_structure_changed(self, tree_model):
        self.view.folder_tree_view.setModel(tree_model)
        if tree_model.rowCount() > 0:
            root_index = tree_model.index(0, 0)
            self.view.folder_tree_view.expand(root_index)
        logger.debug("Folder structure updated in view")

    def _on_assets_changed(self, assets):
        logger.debug(f"Assets changed: {len(assets)} items")
        self._rebuild_asset_grid(assets)

    def _rebuild_asset_grid(self, assets: list):
        """Przebudowuje siatkę kafelków na podstawie listy assetów"""
        with measure_operation(
            "amv_controller.rebuild_asset_grid", {"assets_count": len(assets)}
        ):
            self._clear_active_tiles()

            if not assets:
                self.view.update_gallery_placeholder(
                    "Nie znaleziono assetów w tym folderze."
                )
                return

            self.view.update_gallery_placeholder("")

            cols = self.model.asset_grid_model.get_columns()
            thumb_size = self.model.control_panel_model.get_thumbnail_size()
            rows = (len(assets) + cols - 1) // cols if cols > 0 else 0
            logger.debug(
                "_rebuild_asset_grid: Rebuilding with %d cols, %d rows.",
                cols,
                rows,
            )
            self.view.placeholder_label.hide()

            for i, asset_stub in enumerate(assets):
                asset_data = None
                asset_name = asset_stub.get("name")

                if asset_stub.get("is_stub"):
                    asset_data = self.model.asset_grid_model.get_asset_data_lazy(
                        asset_name
                    )
                    if not asset_data:
                        logger.warning(f"Could not lazy load asset: {asset_name}")
                        continue
                else:
                    asset_data = asset_stub

                row, col = divmod(i, cols)
                asset_file_path = None
                if asset_data.get("type") != "special_folder":
                    current_folder = self.model.asset_grid_model.get_current_folder()
                    if current_folder and asset_name:
                        asset_file_path = os.path.join(
                            current_folder, f"{asset_name}.asset"
                        )

                tile_model = AssetTileModel(asset_data, asset_file_path)
                tile_view = self._get_tile_from_pool(
                    tile_model, thumb_size, i + 1, len(assets)
                )

                self.view.gallery_layout.addWidget(tile_view, row, col)
                self._active_tiles.append(tile_view)
                tile_view.show()

                tile_view.thumbnail_clicked.connect(self._on_tile_thumbnail_clicked)
                tile_view.filename_clicked.connect(self._on_tile_filename_clicked)

            self.view.gallery_container_widget.update()
            self.view.gallery_container_widget.repaint()
            self.view.scroll_area.viewport().update()
            self.view.stacked_layout.setCurrentIndex(0)

            logger.info(f"Asset grid rebuilt with {len(self._active_tiles)} tiles.")

    def _on_loading_state_changed(self, is_loading):
        logger.debug(f"Loading state changed: {is_loading}")
        # W przyszłości tutaj będzie obsługa wizualna ładowania

    def _on_splitter_state_changed(self, is_open: bool):
        sizes = self.model.get_splitter_sizes()
        self.view.update_splitter_sizes(sizes)
        self.view.update_toggle_button_text(is_open)
        state = "open" if is_open else "collapsed"
        logger.info(f"Panel state changed: {state}")

    def _on_config_loaded(self, config: dict):
        self.model.set_config(config)
        logger.debug("Konfiguracja załadowana pomyślnie")

    def _on_state_initialized(self):
        self.model.workspace_folders_model.load_folders()
        logger.debug("Stan aplikacji zainicjalizowany")

    def _on_folder_clicked(self, folder_path: str):
        """Obsługuje kliknięcie folderu w drzewie"""
        logger.info("Folder clicked: %s", folder_path)
        self.model.asset_grid_model.set_current_folder(folder_path)
        self.model.asset_scanner_model.scan_folder(folder_path)
        self.working_directory_changed.emit(folder_path)

    def _on_workspace_folder_clicked(self, folder_path: str):
        """Obsługuje kliknięcie przycisku folderu roboczego"""
        logger.info("Workspace folder clicked: %s", folder_path)
        self.model.folder_system_model.set_root_folder(folder_path)
        # Dodaj wywołanie skanowania folderu
        self.model.asset_grid_model.set_current_folder(folder_path)
        self.model.asset_scanner_model.scan_folder(folder_path)

    def _on_tree_item_clicked(self, index):
        model = self.view.folder_tree_view.model()
        item = model.itemFromIndex(index)
        if item:
            folder_path = item.data(Qt.ItemDataRole.UserRole)
            self.model.folder_system_model.on_folder_clicked(folder_path)

    def _on_tree_item_expanded(self, index):
        model = self.view.folder_tree_view.model()
        item = model.itemFromIndex(index)
        if item:
            self.model.folder_system_model.expand_folder(item)

    def _on_tree_item_collapsed(self, index):
        model = self.view.folder_tree_view.model()
        item = model.itemFromIndex(index)
        if item:
            folder_path = item.data(Qt.ItemDataRole.UserRole)
            self.model.folder_system_model.collapse_folder(folder_path)

    def _on_scan_started(self, folder_path: str):
        logger.info(f"Controller: Scan started for: {folder_path}")
        self.view.update_gallery_placeholder("Skanowanie folderu...")
        self.model.control_panel_model.set_progress(0)

    def _on_scan_progress(self, current: int, total: int, message: str):
        """Obsługuje postęp skanowania."""
        progress = int((current / total) * 100) if total > 0 else 0
        self.model.control_panel_model.set_progress(progress)
        logger.debug(f"Scan progress: {progress}% - {message}")

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
            logger.debug(f"Assets updated and grid rebuilt: {len(assets)} items")

    def _on_scan_error(self, error_msg: str):
        logger.error(f"Controller: Scan error: {error_msg}")
        self.model.control_panel_model.set_progress(0)
        self.view.update_gallery_placeholder(f"Błąd skanowania: {error_msg}")

    def _on_tile_thumbnail_clicked(self, path: str):
        """Obsługuje kliknięcie w miniaturkę kafelka."""
        logger.debug(f"Controller: Thumbnail clicked: {path}")
        if os.path.exists(path):
            try:
                # Otwórz podgląd w dedykowanym oknie aplikacji
                from core.thumbnail_tile import PreviewWindow

                PreviewWindow(path, self.view)
                logger.info(f"Otworzono podgląd w dedykowanym oknie: {path}")
            except Exception as e:
                logger.error(f"Błąd podczas otwierania podglądu {path}: {e}")
                QMessageBox.warning(
                    self.view, "Błąd", f"Nie można otworzyć podglądu: {path}"
                )
        else:
            logger.warning(f"Plik nie istnieje: {path}")
            QMessageBox.warning(self.view, "Błąd", f"Plik nie istnieje: {path}")

    def _on_tile_filename_clicked(self, path: str):
        """Obsługuje kliknięcie w nazwę pliku kafelka."""
        logger.debug(f"Controller: Filename clicked: {path}")
        if os.path.exists(path):
            try:
                # Otwórz archiwum w domyślnej aplikacji (WinRAR/7-Zip)
                if sys.platform == "win32":
                    os.startfile(path)
                elif sys.platform == "darwin":  # macOS
                    subprocess.run(["open", path])
                else:  # Linux
                    subprocess.run(["xdg-open", path])
                logger.info(f"Otworzono archiwum w zewnętrznej aplikacji: {path}")
            except Exception as e:
                logger.error(f"Błąd podczas otwierania archiwum {path}: {e}")
                QMessageBox.warning(
                    self.view, "Błąd", f"Nie można otworzyć archiwum: {path}"
                )
        else:
            logger.warning(f"Plik nie istnieje: {path}")
            QMessageBox.warning(self.view, "Błąd", f"Plik nie istnieje: {path}")

    def _open_path_in_explorer(self, path: str):
        """Otwiera ścieżkę w eksploratorze plików."""
        try:
            if sys.platform == "win32":
                subprocess.run(["explorer", path])
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", path])
            else:  # Linux
                subprocess.run(["xdg-open", path])
            logger.info(f"Otworzono ścieżkę w eksploratorze: {path}")
        except Exception as e:
            logger.error(f"Błąd podczas otwierania ścieżki {path}: {e}")
            QMessageBox.warning(
                self.view, "Błąd", f"Nie można otworzyć ścieżki: {path}"
            )

    def _open_path_in_default_app(self, path: str):
        """Otwiera plik w domyślnej aplikacji."""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", path])
            else:  # Linux
                subprocess.run(["xdg-open", path])
            logger.info(f"Otworzono plik w domyślnej aplikacji: {path}")
        except Exception as e:
            logger.error(f"Błąd podczas otwierania pliku {path}: {e}")
            QMessageBox.warning(self.view, "Błąd", f"Nie można otworzyć pliku: {path}")

    def _on_gallery_resized(self, width: int):
        """Obsługuje zmianę rozmiaru galerii i przelicza kolumny."""
        logger.debug(f"Controller: Gallery resized to {width}px")
        thumb_size = self.model.control_panel_model.get_thumbnail_size()
        self.model.asset_grid_model.request_recalculate_columns(width, thumb_size)

    def _on_thumbnail_size_changed(self, size: int):
        """Obsługuje zmianę rozmiaru miniatur i aktualizuje kafelki."""
        logger.debug(f"Controller: Thumbnail size changed to {size}")
        for tile in self.asset_tiles:
            tile.update_thumbnail_size(size)
        # Przelicz kolumny po zmianie rozmiaru miniatur
        gallery_width = self.view.gallery_container_widget.width()
        self.model.asset_grid_model.request_recalculate_columns(gallery_width, size)

    def _on_recalculate_columns_requested(
        self, available_width: int, thumbnail_size: int
    ):
        """Obsługuje żądanie przeliczenia kolumn z AssetGridModel."""
        # Model już przeliczył kolumny w _perform_recalculate_columns
        # Tutaj tylko logujemy informację
        cols = self.model.asset_grid_model.get_columns()
        logger.debug(
            "Controller: Columns recalculated to %d (width: %d, thumb: %d)",
            cols,
            available_width,
            thumbnail_size,
        )

    def _on_select_all_clicked(self):
        """Obsługuje kliknięcie przycisku 'Zaznacz wszystkie'."""
        logger.debug("Controller: Select all clicked")
        all_assets = self.model.asset_grid_model.get_assets()
        for asset in all_assets:
            asset_name = asset.get("name")
            if asset_name:
                self.model.selection_model.add_selection(asset_name)

        # Aktualizuj wizualnie wszystkie kafelki
        for tile in self.asset_tiles:
            if not tile.model.is_special_folder:
                tile.set_checked(True)

        logger.info(f"Zaznaczono wszystkie assety ({len(all_assets)})")

    def _on_deselect_all_clicked(self):
        """Obsługuje kliknięcie przycisku 'Odznacz wszystkie'."""
        if self.model.selection_model.get_selected_asset_ids():
            self.model.selection_model.clear_selection()
            logger.debug("Deselect all button clicked, selection cleared.")
            # Ręczne wywołanie aktualizacji stanu przycisków
            self._on_control_panel_selection_state_changed(has_selection=False)

    def _on_selection_changed(self, selected_asset_ids: list):
        """Obsługuje zmianę zaznaczenia w SelectionModel i aktualizuje ControlPanelModel."""
        has_selection = len(selected_asset_ids) > 0
        self.model.control_panel_model.set_has_selection(has_selection)

    def _on_control_panel_selection_state_changed(self, has_selection: bool):
        """Aktualizuje stan przycisków 'Przenieś' i 'Usuń' w widoku."""
        selected_count = len(self.model.selection_model.get_selected_asset_ids())
        total_assets = len(self.model.asset_grid_model.get_assets())

        has_any_selection = selected_count > 0
        all_assets_selected = (selected_count == total_assets) and (total_assets > 0)

        self.view.move_selected_button.setEnabled(has_any_selection)
        self.view.delete_selected_button.setEnabled(has_any_selection)
        self.view.deselect_all_button.setEnabled(has_any_selection)
        self.view.select_all_button.setEnabled(not all_assets_selected)

        logger.critical(
            "BUTTON STATE UPDATE: Selected: %s, Total: %s, HasSelection: %s, AllSelected: %s",
            selected_count,
            total_assets,
            has_any_selection,
            all_assets_selected,
        )

    def _on_move_selected_clicked(self):
        """Obsługuje kliknięcie przycisku 'Przenieś zaznaczone'."""
        selected_asset_ids = self.model.selection_model.get_selected_asset_ids()
        if not selected_asset_ids:
            QMessageBox.information(
                self.view,
                "Przenoszenie assetów",
                "Brak zaznaczonych assetów do przeniesienia.",
            )
            return

        # Pobierz pełne dane assetów na podstawie ID
        all_assets = self.model.asset_grid_model.get_assets()
        logger.debug(f"Drag&Drop asset_ids: {selected_asset_ids}")
        assets_to_move = [
            asset for asset in all_assets if asset.get("name") in selected_asset_ids
        ]
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

    def _on_delete_selected_clicked(self):
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
            # Pobierz pełne dane assetów na podstawie ID
            all_assets = self.model.asset_grid_model.get_assets()
            assets_to_delete = [
                asset for asset in all_assets if asset.get("name") in selected_asset_ids
            ]

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

    def _on_file_operation_progress(self, current: int, total: int, message: str):
        progress = int((current / total) * 100) if total > 0 else 0
        self.model.control_panel_model.set_progress(progress)
        self.view.update_gallery_placeholder(message)

    def _on_file_operation_completed(
        self, success_messages: list, error_messages: list
    ):
        with measure_operation(
            "amv_controller.file_operation_completed",
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
                    f"Operacja zakończona częściowo - Pomyślnie: {len(success_messages)}, Błędy: {len(error_messages)}"
                )
            elif success_messages:
                logger.info(
                    f"Operacja zakończona pomyślnie - Przeniesiono: {len(success_messages)} plików"
                )
            elif error_messages:
                logger.error(f"Operacja zakończona z błędami: {error_messages}")

            # Usuń przeniesione/usunięte assety z listy bez ponownego skanowania
            if success_messages:
                logger.debug(f"Success messages: {success_messages}")

                # Usuń assety z modelu danych
                current_assets = self.model.asset_grid_model.get_assets()
                logger.debug(f"Current assets count: {len(current_assets)}")

                # Debug: wyświetl wszystkie nazwy assetów
                for i, asset in enumerate(current_assets):
                    asset_name = asset.get("name")
                    logger.debug(
                        f"Asset {i}: name='{asset_name}', in success_messages: {asset_name in success_messages}"
                    )

                updated_assets = [
                    asset
                    for asset in current_assets
                    if asset.get("name") not in success_messages
                ]
                logger.debug(f"Updated assets count: {len(updated_assets)}")
                self.model.asset_grid_model._assets = updated_assets

                # Usuń kafelki z widoku
                logger.debug(
                    f"Active tiles count before removal: {len(self._active_tiles)}"
                )
                for tile in self._active_tiles:
                    logger.debug(
                        f"Tile asset_id: '{tile.asset_id}', in success_messages: {tile.asset_id in success_messages}"
                    )
                self.view.remove_asset_tiles(success_messages)

                # Usuń również z listy active_tiles kontrolera
                self._active_tiles = [
                    tile
                    for tile in self._active_tiles
                    if tile.asset_id not in success_messages
                ]
                logger.debug(
                    f"Active tiles count after removal: {len(self._active_tiles)}"
                )

                # ODBUDUJ GALERIĘ po usunięciu assetów
                self._rebuild_asset_grid(updated_assets)

                logger.debug(
                    "Removed %d assets from list and view without rescanning",
                    len(success_messages),
                )

            # Wyczyść zaznaczenie po operacji
            self.model.selection_model.clear_selection()

            logger.info(
                "File operation completed - Success: %d, Errors: %d",
                len(success_messages),
                len(error_messages),
            )

    def _on_file_operation_error(self, error_msg: str):
        self.model.control_panel_model.set_progress(0)
        self.view.update_gallery_placeholder(f"Błąd operacji na plikach: {error_msg}")

    def _on_drag_drop_started(self, asset_ids: list):
        logger.debug("AmvController: Drag operation started for assets: %s", asset_ids)
        # Tutaj można dodać wizualny feedback, np. zmianę kursora

    def _on_drag_drop_possible(self, possible: bool):
        logger.debug(f"AmvController: Drop possible: {possible}")
        # Tutaj można dodać wizualny feedback, np. podświetlenie celu

    def _on_drag_drop_completed(self, target_path: str, asset_ids: list):
        logger.debug(
            "AmvController: Drop completed to %s for assets: %s",
            target_path,
            asset_ids,
        )
        # Pobierz pełne dane assetów na podstawie ID
        all_assets = self.model.asset_grid_model.get_assets()
        logger.debug(f"Drag&Drop asset_ids: {asset_ids}")
        assets_to_move = [
            asset for asset in all_assets if asset.get("name") in asset_ids
        ]
        logger.debug(f"assets_to_move: {[a.get('name') for a in assets_to_move]}")

        if assets_to_move:
            self.model.file_operations_model.move_assets(
                assets_to_move,
                self.model.asset_grid_model.get_current_folder(),
                target_path,
            )
            self.model.control_panel_model.set_progress(0)  # Reset progress bar
            self.view.update_gallery_placeholder(
                "Przenoszenie assetów (Drag & Drop)..."
            )
        else:
            logger.warning("AmvController: No assets found for drag & drop operation.")

    def _on_grid_layout_changed(self):
        # Implementacja obsługi zmiany układu siatki
        logger.debug("AmvController: Grid layout changed")
        self._rebuild_asset_grid(self.model.asset_grid_model.get_assets())

        # Można dodać dodatkowe logiki dotyczące zmiany układu siatki
        # np. aktualizację widoku, przeliczanie kolumn, itp.
        logger.debug("AmvController: Grid layout changed - end")

    def _rebuild_assets_in_folder(self, folder_path: str):
        """Przebudowuje assety w wybranym folderze"""
        try:
            # Pokaż dialog potwierdzenia
            reply = QMessageBox.question(
                self.view,
                "Potwierdzenie przebudowy",
                (
                    f"Czy na pewno chcesz przebudować assety w folderze:\n"
                    f"{folder_path}\n\n"
                    "Ta operacja usunie wszystkie pliki .asset, folder .cache "
                    "i uruchomi ponowne skanowanie."
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Zatrzymaj poprzedni worker jeśli działa
                if self.asset_rebuilder and self.asset_rebuilder.isRunning():
                    self.asset_rebuilder.quit()
                    self.asset_rebuilder.wait()

                # Utwórz nowy worker dla przebudowy
                self.asset_rebuilder = AssetRebuilderThread(folder_path)

                # Podłącz sygnały
                self.asset_rebuilder.progress_updated.connect(self._on_rebuild_progress)
                self.asset_rebuilder.rebuild_finished.connect(self._on_rebuild_finished)
                self.asset_rebuilder.error_occurred.connect(self._on_rebuild_error)

                # Uruchom worker
                self.asset_rebuilder.start()

                logger.info("Rozpoczęto przebudowę assetów w folderze: %s", folder_path)

        except Exception as e:
            logger.error(f"Błąd inicjalizacji przebudowy assetów: {e}")
            QMessageBox.critical(
                self.view,
                "Błąd przebudowy",
                f"Wystąpił błąd podczas inicjalizacji przebudowy:\n{str(e)}",
            )

    def _on_rebuild_progress(self, current: int, total: int, message: str):
        """Obsługuje postęp przebudowy assetów"""
        try:
            if total > 0:
                progress = int((current / total) * 100)
                self.model.control_panel_model.set_progress(progress)

            logger.debug(f"Postęp przebudowy: {message}")
        except Exception as e:
            logger.error(f"Błąd aktualizacji postępu przebudowy: {e}")

    def _on_rebuild_finished(self, message: str):
        """Obsługuje zakończenie przebudowy assetów"""
        try:
            self.model.control_panel_model.set_progress(0)

            QMessageBox.information(self.view, "Przebudowa zakończona", message)

            # Odśwież scanner dla aktualnego folderu
            current_folder = self.model.asset_grid_model.get_current_folder()
            if current_folder:
                self.model.asset_scanner_model.scan_folder(current_folder)

            logger.info(f"Przebudowa zakończona: {message}")
        except Exception as e:
            logger.error(f"Błąd obsługi zakończenia przebudowy: {e}")

    def _on_rebuild_error(self, error_message: str):
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

    def _on_collapse_tree_requested(self):
        """Obsługuje żądanie zwinięcia drzewa folderów"""
        logger.info("Zwijanie wszystkich elementów drzewa folderów")
        try:
            self.view.folder_tree_view.collapseAll()
            logger.debug("Drzewo folderów zostało zwinięte")
        except Exception as e:
            logger.error(f"Błąd podczas zwijania drzewa folderów: {e}")

    def _on_expand_tree_requested(self):
        """Obsługuje żądanie rozwinięcia drzewa folderów"""
        logger.info("Rozwijanie wszystkich węzłów drzewa folderów")
        try:
            self.view.folder_tree_view.expandAll()
            logger.debug("Pomyślnie rozwinięto wszystkie węzły drzewa")
        except Exception as e:
            logger.error(f"Błąd podczas rozwijania drzewa: {e}")

    def _on_star_filter_clicked(self, star_rating: int):
        """Obsługuje kliknięcie w gwiazdkę filtrowania w panelu kontrolnym"""
        logger.info(f"=== FILTROWANIE GWIAZDEK: Kliknięto gwiazdkę {star_rating} ===")

        # Sprawdź czy star_checkboxes istnieje
        if not hasattr(self.view, "star_checkboxes") or not self.view.star_checkboxes:
            logger.error("BŁĄD: self.view.star_checkboxes nie istnieje!")
            return

        logger.debug(f"Znaleziono {len(self.view.star_checkboxes)} checkboxów gwiazdek")

        # Sprawdź aktualny stan gwiazdek PRZED zablokowaniem sygnałów
        # (checkbox już zmienił stan po kliknięciu)
        clicked_checkbox = self.view.star_checkboxes[star_rating - 1]
        was_checked_before = not clicked_checkbox.isChecked()  # Odwrócony stan
        logger.debug(f"Checkbox {star_rating} was_checked_before: {was_checked_before}")

        # Zablokuj sygnały żeby uniknąć rekurencji
        for cb in self.view.star_checkboxes:
            cb.blockSignals(True)

        # Jeśli gwiazdka była zaznaczona przed kliknięciem, odznacz wszystkie
        if was_checked_before:
            for cb in self.view.star_checkboxes:
                cb.setChecked(False)
            logger.info("Odznaczono wszystkie gwiazdki - pokazano wszystkie assety")
            # BEZPOŚREDNIE WYWOŁANIE
            self._filter_assets_by_stars(0)
        else:
            # Zaznacz gwiazdki od 1 do klikniętej (jak na kafelkach)
            for i, cb in enumerate(self.view.star_checkboxes):
                cb.setChecked(i < star_rating)
            logger.info(f"Zaznaczono {star_rating} gwiazdek - filtrowanie")
            # BEZPOŚREDNIE WYWOŁANIE
            self._filter_assets_by_stars(star_rating)

        # Odblokuj sygnały
        for cb in self.view.star_checkboxes:
            cb.blockSignals(False)

        logger.info(f"=== KONIEC FILTROWANIA GWIAZDEK ===")

    def _filter_assets_by_stars(self, min_stars: int):
        """Filtruje assety według minimalnej liczby gwiazdek"""
        try:
            all_assets = self.model.asset_grid_model.get_all_assets()
            logger.debug(
                f"Filtrowanie {len(all_assets)} assetów dla min_stars={min_stars}"
            )

            if min_stars == 0:
                # Pokaż wszystkie assety
                filtered_assets = []
                for asset_data in all_assets:
                    # Jeśli stub, pobierz pełne dane
                    if asset_data.get("is_stub"):
                        full_data = self.model.asset_grid_model.get_asset_data_lazy(
                            asset_data.get("name")
                        )
                        if full_data:
                            filtered_assets.append(full_data)
                        else:
                            filtered_assets.append(asset_data)
                    else:
                        filtered_assets.append(asset_data)
                logger.debug("Pokazano wszystkie assety (brak filtrowania)")
            else:
                # Filtruj assety z odpowiednią liczbą gwiazdek
                filtered_assets = []
                for i, asset_data in enumerate(all_assets):
                    # Jeśli stub, pobierz pełne dane
                    if asset_data.get("is_stub"):
                        asset_data_full = (
                            self.model.asset_grid_model.get_asset_data_lazy(
                                asset_data.get("name")
                            )
                        )
                        if asset_data_full:
                            asset_data = asset_data_full
                    # Zawsze dodaj specjalne foldery (nie filtruj ich)
                    if asset_data.get("type") == "special_folder":
                        filtered_assets.append(asset_data)
                        logger.debug(
                            f"Asset {i}: {asset_data.get('name')} - specjalny folder, dodany"
                        )
                        continue

                    # Filtruj tylko prawdziwe assety
                    asset_stars = asset_data.get("stars")
                    logger.debug(
                        f"Asset {i}: {asset_data.get('name')} - stars={asset_stars} (type: {type(asset_stars)})"
                    )

                    # Rzutowanie na int jeśli się da
                    try:
                        if asset_stars is None:
                            asset_stars_int = 0
                        else:
                            asset_stars_int = int(asset_stars)
                    except (ValueError, TypeError):
                        asset_stars_int = 0

                    if asset_stars_int >= min_stars:
                        filtered_assets.append(asset_data)
                        logger.debug(
                            f"Asset {i}: {asset_data.get('name')} - DODANY (stars={asset_stars_int} >= {min_stars})"
                        )
                    else:
                        logger.debug(
                            f"Asset {i}: {asset_data.get('name')} - POMINIĘTY (stars={asset_stars_int} < {min_stars})"
                        )

                logger.debug(
                    f"Przefiltrowano {len(filtered_assets)} assetów z {min_stars}+ gwiazdkami"
                )

            # Odbuduj siatkę z przefiltrowanymi assetami
            self._rebuild_asset_grid(filtered_assets)

        except Exception as e:
            logger.error(f"Błąd podczas filtrowania assetów: {e}")
            # W przypadku błędu, pokaż wszystkie assety
            self._filter_assets_by_stars(0)

    def _get_tile_from_pool(
        self,
        tile_model: AssetTileModel,
        thumbnail_size: int,
        tile_number: int,
        total_tiles: int,
    ) -> AssetTileView:
        """
        Pobiera kafelek z puli lub tworzy nowy jeśli pula jest pusta.
        """
        if self._tile_pool:
            # Pobierz kafelek z puli
            tile_view = self._tile_pool.pop()
            # Zaktualizuj dane kafelka PRZED zmianą rozmiaru miniaturki
            tile_view.update_asset_data(tile_model, tile_number, total_tiles)
            # Zaktualizuj rozmiar miniaturki jeśli się zmienił
            if tile_view.thumbnail_size != thumbnail_size:
                tile_view.update_thumbnail_size(thumbnail_size)
            asset_name = tile_model.get_name()
            logger.debug(f"Reused tile from pool for asset: {asset_name}")
        else:
            # Utwórz nowy kafelek
            tile_view = AssetTileView(
                tile_model,
                thumbnail_size,
                tile_number,
                total_tiles,
                self.model.selection_model,
            )
            asset_name = tile_model.get_name()
            logger.debug(f"Created new tile for asset: {asset_name}")

        return tile_view

    def _return_tile_to_pool(self, tile_view: AssetTileView):
        """
        Zwraca kafelek do puli do ponownego użycia.
        """
        try:
            if not tile_view:
                return

            if len(self._tile_pool) < self._max_pool_size:
                # Resetuj kafelek do stanu czystego
                tile_view.reset_for_pool()

                # Usuń kafelek z layoutu i ukryj
                if tile_view.parent():
                    tile_view.setParent(None)
                tile_view.hide()

                # Dodaj do puli
                self._tile_pool.append(tile_view)
                logger.debug(
                    f"Returned tile to pool, new pool size: {len(self._tile_pool)}"
                )
            else:
                # Pula jest pełna, usuń kafelek
                tile_view.deleteLater()
                logger.debug("Pool full, deleted tile")

        except RuntimeError as e:
            logger.warning(
                f"Error returning tile to pool: {e} - tile may be already deleted"
            )

    def _clear_active_tiles(self):
        """
        Usuwa wszystkie aktywne kafelki i zwraca je do puli.
        """
        for tile_view in self._active_tiles:
            try:
                if tile_view:
                    # Najpierw zwolnij zasoby, aby odblokować pliki
                    tile_view.release_resources()

                    # Następnie bezpiecznie odłącz sygnały
                    try:
                        tile_view.thumbnail_clicked.disconnect(
                            self._on_tile_thumbnail_clicked
                        )
                        tile_view.filename_clicked.disconnect(
                            self._on_tile_filename_clicked
                        )
                    except (TypeError, RuntimeError):
                        pass  # Sygnały już odłączone

                    # Na koniec zwróć do puli
                    self._return_tile_to_pool(tile_view)
            except RuntimeError:
                logger.warning("Tried to access a deleted tile in _clear_active_tiles")
                continue

        self._active_tiles.clear()
