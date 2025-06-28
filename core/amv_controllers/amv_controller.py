"""
AmvController - Kontroler dla zakładki AMV
Łączy Model z Widokiem, obsługuje interakcje użytkownika i aktualizuje stan aplikacji.
"""

import logging
import os
import shutil
import subprocess
import sys

from PyQt6.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from ..amv_models.amv_model import AmvModel
from ..amv_models.asset_tile_model import AssetTileModel
from ..amv_views.amv_view import AmvView
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
                f"Rozpoczęcie przebudowy assetów w folderze: {self.folder_path}"
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
                f"Pomyślnie przebudowano assety w folderze: {self.folder_path}"
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
                logger.debug(f"Usunięto plik asset: {asset_file}")

            logger.info(f"Usunięto {len(asset_files)} plików .asset")
        except Exception as e:
            logger.error(f"Błąd usuwania plików .asset: {e}")
            raise

    def _remove_cache_folder(self):
        """Usuwa folder .cache jeśli istnieje"""
        try:
            cache_folder = os.path.join(self.folder_path, ".cache")
            if os.path.exists(cache_folder) and os.path.isdir(cache_folder):
                shutil.rmtree(cache_folder)
                logger.info(f"Usunięto folder .cache: {cache_folder}")
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
            logger.info(f"Scanner utworzył {len(created_assets)} nowych assetów")

        except Exception as e:
            logger.error(f"Błąd uruchamiania scanner-a: {e}")
            raise


class AmvController(QObject):
    """Controller dla zakładki AMV - łącznik Model-View"""

    def __init__(self, model: AmvModel, view):
        super().__init__()
        self.model = model
        self.view = view
        self.asset_tiles = []  # Lista do przechowywania kafelków
        self.asset_rebuilder = None  # Worker dla przebudowy assetów
        self._connect_signals()
        self._setup_folder_tree()
        self._setup_asset_grid()
        logger.info("AmvController initialized - ETAP 14")

    def _connect_signals(self):
        # --- Podstawowe sygnały UI ---
        self.view.splitter_moved.connect(self.model.set_splitter_sizes)
        self.view.toggle_panel_requested.connect(self.model.toggle_left_panel)
        self.model.splitter_state_changed.connect(self._on_splitter_state_changed)
        self.view.gallery_viewport_resized.connect(self._on_gallery_resized)

        # --- Sygnały modelu folderów ---
        self.model.folder_system_model.folder_clicked.connect(self._on_folder_clicked)
        self.model.folder_system_model.folder_structure_updated.connect(
            self._on_folder_structure_changed
        )
        self.model.workspace_folders_model.folders_updated.connect(
            self.view.update_workspace_folder_buttons
        )
        self.view.workspace_folder_clicked.connect(self._on_workspace_folder_clicked)

        # --- Sygnały modelu siatki assetów ---
        self.model.asset_grid_model.assets_changed.connect(self._on_assets_changed)
        self.model.asset_grid_model.loading_state_changed.connect(
            self._on_loading_state_changed
        )

        # --- Sygnały panelu kontrolnego ---
        self.model.control_panel_model.progress_changed.connect(
            self.view.progress_bar.setValue
        )
        self.model.control_panel_model.thumbnail_size_changed.connect(
            self._on_thumbnail_size_changed
        )
        self.view.thumbnail_size_slider.valueChanged.connect(
            self.model.control_panel_model.set_thumbnail_size
        )
        self.model.control_panel_model.selection_state_changed.connect(
            self._on_control_panel_selection_state_changed
        )

        self.view.select_all_button.clicked.connect(self._on_select_all_clicked)
        self.view.deselect_all_button.clicked.connect(self._on_deselect_all_clicked)
        self.view.move_selected_button.clicked.connect(self._on_move_selected_clicked)
        self.view.delete_selected_button.clicked.connect(
            self._on_delete_selected_clicked
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
        logger.info("Asset grid model connected to view - ETAP 9")

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
        # Wyczyść stare kafelki
        for tile in self.asset_tiles:
            tile.deleteLater()
        self.asset_tiles.clear()

        if not assets:
            self.view.update_gallery_placeholder(
                "Nie znaleziono assetów w tym folderze."
            )
            return

        self.view.update_gallery_placeholder("")

        cols = (
            self.model.asset_grid_model.get_columns()
        )  # Pobierz aktualną liczbę kolumn z modelu
        thumb_size = self.model.control_panel_model.get_thumbnail_size()

        # Oblicz liczbę rzędów
        rows = (len(assets) + cols - 1) // cols if cols > 0 else 0
        logger.debug(
            f"_rebuild_asset_grid: Rebuilding grid with {cols} columns and {rows} rows."
        )

        # Ukryj placeholder przed dodaniem kafelków
        self.view.placeholder_label.hide()

        for i, asset_data in enumerate(assets):
            row, col = divmod(i, cols)
            tile_model = AssetTileModel(asset_data)
            tile_view = AssetTileView(
                tile_model, thumb_size, i + 1, len(assets), self.model.selection_model
            )

            self.view.gallery_layout.addWidget(tile_view, row, col)
            self.asset_tiles.append(tile_view)

            # Podłącz sygnały kliknięć
            tile_view.thumbnail_clicked.connect(self._on_tile_thumbnail_clicked)
            tile_view.filename_clicked.connect(self._on_tile_filename_clicked)

        # Wymuś odświeżenie widoku
        self.view.gallery_container_widget.update()
        self.view.gallery_container_widget.repaint()
        self.view.scroll_area.viewport().update()

        # Wymuś przełączenie na siatkę galerii
        self.view.stacked_layout.setCurrentIndex(0)

        logger.info(f"Asset grid rebuilt with {len(assets)} tiles.")

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
        logger.info("Konfiguracja załadowana pomyślnie")

    def _on_state_initialized(self):
        self.model.workspace_folders_model.load_folders()
        logger.info("Stan aplikacji zainicjalizowany")

    def _on_folder_clicked(self, folder_path: str):
        logger.info(f"Controller: Folder clicked: {folder_path}")
        self.model.asset_grid_model.set_current_folder(folder_path)
        self.model.asset_scanner_model.scan_folder(folder_path)

    def _on_workspace_folder_clicked(self, folder_path: str):
        logger.info(f"Controller: Workspace folder clicked: {folder_path}")
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
        logger.info(
            f"Controller: Scan completed - {len(assets)} assets in {duration:.2f}s ({operation_type})"
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
            f"Controller: Columns recalculated to {cols} (width: {available_width}, thumb: {thumbnail_size})"
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
        logger.debug("Controller: Deselect all clicked")
        self.model.selection_model.clear_selection()

        # Aktualizuj wizualnie wszystkie kafelki
        for tile in self.asset_tiles:
            tile.set_checked(False)

        logger.info("Odznaczono wszystkie assety")

    def _on_selection_changed(self, selected_asset_ids: list):
        """Obsługuje zmianę zaznaczenia w SelectionModel i aktualizuje ControlPanelModel."""
        has_selection = len(selected_asset_ids) > 0
        self.model.control_panel_model.set_has_selection(has_selection)

    def _on_control_panel_selection_state_changed(self, has_selection: bool):
        """Aktualizuje stan przycisków 'Przenieś' i 'Usuń' w widoku."""
        logger.debug(
            f"AmvController: _on_control_panel_selection_state_changed called with: {has_selection}"
        )
        self.view.move_selected_button.setEnabled(has_selection)
        self.view.delete_selected_button.setEnabled(has_selection)
        self.view.deselect_all_button.setEnabled(has_selection)
        logger.debug(f"Control panel buttons updated. Has selection: {has_selection}")

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
        assets_to_move = [
            asset for asset in all_assets if asset.get("name") in selected_asset_ids
        ]

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
                self.view, "Usuwanie assetów", "Brak zaznaczonych assetów do usunięcia."
            )
            return

        reply = QMessageBox.question(
            self.view,
            "Potwierdzenie usunięcia",
            f"Czy na pewno chcesz usunąć {len(selected_asset_ids)} zaznaczonych assetów?\nTa operacja jest nieodwracalna!",
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
                assets_to_delete, self.model.asset_grid_model.get_current_folder()
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
        self.model.control_panel_model.set_progress(100)
        self.view.update_gallery_placeholder("")  # Clear placeholder

        # Usuń przeniesione/usunięte assety z listy bez ponownego skanowania
        if success_messages:
            # Pobierz ID przeniesionych/usuniętych assetów z komunikatów
            moved_asset_names = []
            for msg in success_messages:
                if "przeniesiono" in msg.lower():
                    # Wyciągnij nazwę assetu z komunikatu "Pomyślnie przeniesiono asset: nazwa"
                    asset_name = msg.split("asset: ")[-1] if "asset: " in msg else None
                    if asset_name:
                        moved_asset_names.append(asset_name)
                elif "usunięto" in msg.lower():
                    # Wyciągnij nazwę assetu z komunikatu "Pomyślnie usunięto asset: nazwa"
                    asset_name = msg.split("asset: ")[-1] if "asset: " in msg else None
                    if asset_name:
                        moved_asset_names.append(asset_name)

            # Usuń przeniesione/usunięte assety z listy i z widoku
            if moved_asset_names:
                current_assets = self.model.asset_grid_model.get_assets()
                updated_assets = [
                    asset
                    for asset in current_assets
                    if asset.get("name") not in moved_asset_names
                ]
                self.model.asset_grid_model._assets = updated_assets

                # Usuń kafelki z widoku
                tiles_to_remove = []
                for tile in self.asset_tiles:
                    if tile.model.get_name() in moved_asset_names:
                        tiles_to_remove.append(tile)

                for tile in tiles_to_remove:
                    self.view.gallery_layout.removeWidget(tile)
                    tile.deleteLater()
                    self.asset_tiles.remove(tile)

                logger.debug(
                    f"Removed {len(moved_asset_names)} assets from list and view without rescanning"
                )

        self.model.selection_model.clear_selection()  # Wyczyść zaznaczenie po operacji

    def _on_file_operation_error(self, error_msg: str):
        self.model.control_panel_model.set_progress(0)
        self.view.update_gallery_placeholder(f"Błąd operacji na plikach: {error_msg}")

    def _on_drag_drop_started(self, asset_ids: list):
        logger.debug(f"AmvController: Drag operation started for assets: {asset_ids}")
        # Tutaj można dodać wizualny feedback, np. zmianę kursora

    def _on_drag_drop_possible(self, possible: bool):
        logger.debug(f"AmvController: Drop possible: {possible}")
        # Tutaj można dodać wizualny feedback, np. podświetlenie celu

    def _on_drag_drop_completed(self, target_path: str, asset_ids: list):
        logger.debug(
            f"AmvController: Drop completed to {target_path} for assets: {asset_ids}"
        )
        # Pobierz pełne dane assetów na podstawie ID
        all_assets = self.model.asset_grid_model.get_assets()
        assets_to_move = [
            asset for asset in all_assets if asset.get("name") in asset_ids
        ]

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
                f"Czy na pewno chcesz przebudować assety w folderze:\n{folder_path}\n\n"
                "Ta operacja usunie wszystkie pliki .asset, folder .cache i uruchomi ponowne skanowanie.",
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

                logger.info(f"Rozpoczęto przebudowę assetów w folderze: {folder_path}")

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
        logger.info("Rozwijanie wszystkich elementów drzewa folderów")
        try:
            self.view.folder_tree_view.expandAll()
            logger.debug("Drzewo folderów zostało rozwinięte")
        except Exception as e:
            logger.error(f"Błąd podczas rozwijania drzewa folderów: {e}")
