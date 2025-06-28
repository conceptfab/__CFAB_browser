import logging
import os
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtCore import QModelIndex, Qt
from core.scanner import find_and_create_assets, load_existing_assets

logger = logging.getLogger(__name__)


class AssetGridModel(QObject):
    """Model dla siatki assetów - architektura M/V"""

    assets_changed = pyqtSignal(list)
    grid_layout_changed = pyqtSignal(int)
    loading_state_changed = pyqtSignal(bool)
    recalculate_columns_requested = pyqtSignal(int, int)  # Sygnał do kontrolera

    def __init__(self):
        super().__init__()
        self._assets = []
        self._columns = 4
        self._is_loading = False
        self._current_folder_path = ""
        self._last_available_width = 0  # Nowy atrybut
        self._last_thumbnail_size = 0  # Nowy atrybut
        self._recalc_timer = QTimer(self)  # Timer do debouncingu
        self._recalc_timer.setSingleShot(True)
        self._recalc_timer.timeout.connect(self._perform_recalculate_columns)
        logger.info("AssetGridModel initialized")

    def set_assets(self, assets: list):
        self._assets = assets
        self.assets_changed.emit(assets)
        logger.debug(f"Assets updated: {len(assets)} items")

    def get_assets(self):
        return self._assets

    def set_columns(self, columns: int):
        if self._columns != columns:
            self._columns = max(1, columns)
            self.grid_layout_changed.emit(self._columns)
            logger.debug(f"Grid columns updated to: {self._columns}")

    def get_columns(self):
        return self._columns

    def set_loading_state(self, is_loading: bool):
        if self._is_loading != is_loading:
            self._is_loading = is_loading
            self.loading_state_changed.emit(is_loading)
            logger.debug(f"Loading state changed: {is_loading}")

    def is_loading(self):
        return self._is_loading

    def set_current_folder(self, folder_path: str):
        self._current_folder_path = folder_path
        logger.debug(f"Current folder set: {folder_path}")

    def get_current_folder(self):
        return self._current_folder_path

    def request_recalculate_columns(self, available_width: int, thumbnail_size: int):
        """Żąda przeliczenia kolumn z debouncingiem."""
        logger.debug(
            f"AssetGridModel: Request recalculate columns - width: {available_width}, thumb_size: {thumbnail_size}"
        )
        self._last_available_width = available_width
        self._last_thumbnail_size = thumbnail_size
        self._recalc_timer.start(100)  # 100ms delay

    def _perform_recalculate_columns(self):
        """Wykonuje przeliczenie kolumn i emituje sygnał."""
        calculated_columns = self._calculate_columns_cached(
            self._last_available_width, self._last_thumbnail_size
        )

        if calculated_columns != self._columns:
            self.set_columns(
                calculated_columns
            )  # Ustawia i emituje grid_layout_changed
        self.recalculate_columns_requested.emit(
            self._last_available_width, self._last_thumbnail_size
        )

    def _calculate_columns_cached(
        self, available_width: int, thumbnail_size: int
    ) -> int:
        """Oblicza optymalną liczbę kolumn."""
        # Rzeczywisty rozmiar kafelka (z AssetTileView: thumbnail_size + (2 * margins_size) = thumbnail_size + 16)
        tile_width = thumbnail_size + 16

        # Marginesy layoutu (z gallery_layout.setContentsMargins(8, 8, 8, 8) = 16px)
        layout_margins = 16

        # Spacing między kafelkami (8px)
        spacing = 8

        # Dostępna szerokość po odjęciu marginesów
        effective_width = available_width - layout_margins

        # Oblicz liczbę kolumn z uwzględnieniem spacing
        if (tile_width + spacing) > 0:
            columns_calc = (effective_width + spacing) // (tile_width + spacing)
        else:
            columns_calc = 1  # Zapobiegaj dzieleniu przez zero

        calculated_columns = max(1, columns_calc)

        self._last_available_width = available_width
        self._last_thumbnail_size = thumbnail_size
        return calculated_columns


class FolderTreeModel(QObject):
    """Model dla drzewa folderów - architektura M/V"""

    folder_structure_changed = pyqtSignal(object)
    root_folder_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._tree_model = QStandardItemModel()
        self._tree_model.setHorizontalHeaderLabels(["Folders"])
        self._root_folder = ""
        logger.info("FolderTreeModel initialized")

    def get_tree_model(self):
        return self._tree_model

    def set_root_folder(self, folder_path: str):
        if self._root_folder != folder_path:
            self._root_folder = folder_path
            self._tree_model.clear()
            self._tree_model.setHorizontalHeaderLabels(["Folders"])
            self.root_folder_changed.emit(folder_path)
            self.folder_structure_changed.emit(self._tree_model)
            logger.debug(f"Root folder changed: {folder_path}")

    def get_root_folder(self):
        return self._root_folder


class FolderSystemModel(QObject):
    """Model dla systemu folderów w architekturze M/V"""

    folder_clicked = pyqtSignal(str)
    folder_expanded = pyqtSignal(str)
    folder_collapsed = pyqtSignal(str)
    folder_structure_updated = pyqtSignal(object)
    loading_state_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._tree_model = QStandardItemModel()
        self._tree_model.setHorizontalHeaderLabels(["Folders"])
        self._root_folder = ""
        self._is_loading = False
        logger.info("FolderSystemModel initialized")

    def get_tree_model(self):
        return self._tree_model

    def set_root_folder(self, folder_path: str):
        if self._root_folder != folder_path:
            self._root_folder = folder_path
            self._load_folder_structure()
            logger.debug(f"Root folder changed: {folder_path}")

    def get_root_folder(self):
        return self._root_folder

    def _load_folder_structure(self):
        try:
            self._set_loading_state(True)
            self._tree_model.clear()
            self._tree_model.setHorizontalHeaderLabels(["Folders"])
            if not self._root_folder or not os.path.exists(self._root_folder):
                logger.warning(f"Root folder does not exist: {self._root_folder}")
                self._set_loading_state(False)
                return

            root_item = QStandardItem(os.path.basename(self._root_folder))
            root_item.setData(self._root_folder, Qt.ItemDataRole.UserRole)
            root_item.setIcon(QIcon("core/resources/img/folder.png"))
            root_item.setEditable(False)
            self._tree_model.appendRow(root_item)
            self._load_subfolders(root_item, self._root_folder)
            self.folder_structure_updated.emit(self._tree_model)
            self._set_loading_state(False)
            logger.debug(f"Folder structure loaded: {self._root_folder}")
        except Exception as e:
            logger.error(f"Error loading folder structure: {e}")
            self._set_loading_state(False)

    def _load_subfolders(self, parent_item, folder_path):
        try:
            if not os.path.exists(folder_path):
                return
            folders = []
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path) and not item.startswith("."):
                    folders.append((item, item_path))
            folders.sort(key=lambda x: x[0].lower())
            for folder_name, f_path in folders:
                folder_item = QStandardItem(folder_name)
                folder_item.setData(f_path, Qt.ItemDataRole.UserRole)
                folder_item.setIcon(QIcon("core/resources/img/folder.png"))
                folder_item.setEditable(False)
                if any(
                    os.path.isdir(os.path.join(f_path, sub)) and not sub.startswith(".")
                    for sub in os.listdir(f_path)
                ):
                    placeholder = QStandardItem("...")
                    placeholder.setEnabled(False)
                    placeholder.setEditable(False)
                    folder_item.appendRow(placeholder)
                parent_item.appendRow(folder_item)
        except Exception as e:
            logger.error(f"Error loading subfolders for {folder_path}: {e}")

    def expand_folder(self, item: QStandardItem):
        """Rozwija element i doładowuje jego dzieci (lazy loading)."""
        try:
            if not item or item.rowCount() == 0:
                return

            # Sprawdzenie i usunięcie placeholdera
            placeholder = item.child(0)
            if placeholder and placeholder.text() == "...":
                folder_path = item.data(Qt.ItemDataRole.UserRole)
                item.removeRow(0)  # Usuń placeholder
                self._load_subfolders(item, folder_path)
                logger.debug(f"Lazy loaded children for: {folder_path}")

            # Emitowanie sygnału
            folder_path = item.data(Qt.ItemDataRole.UserRole)
            self.folder_expanded.emit(folder_path)

        except Exception as e:
            folder_path = item.data(Qt.ItemDataRole.UserRole)
            logger.error(f"Error expanding folder {folder_path}: {e}")

    def collapse_folder(self, folder_path: str):
        self.folder_collapsed.emit(folder_path)
        logger.debug(f"Folder collapsed: {folder_path}")

    def _set_loading_state(self, is_loading: bool):
        if self._is_loading != is_loading:
            self._is_loading = is_loading
            self.loading_state_changed.emit(is_loading)

    def is_loading(self):
        return self._is_loading

    def on_folder_clicked(self, folder_path: str):
        self.folder_clicked.emit(folder_path)
        logger.debug(f"Folder clicked: {folder_path}")


class WorkspaceFoldersModel(QObject):
    """Model dla folderów roboczych w architekturze M/V"""

    folders_updated = pyqtSignal(list)

    def __init__(self, config_manager):
        super().__init__()
        self._config_manager = config_manager
        self._folders = []
        # Połącz z sygnałem konfiguracji
        self._config_manager.config_loaded.connect(self._load_folders_from_config)
        logger.info("WorkspaceFoldersModel initialized")

    def load_folders(self):
        """Ładuje foldery robocze z konfiguracji."""
        self._config_manager.load_config()

    def _load_folders_from_config(self, config: dict):
        """Ładuje foldery z konfiguracji i emituje sygnał aktualizacji."""
        try:
            self._folders = []
            
            # Przeiteruj przez work_folder1 do work_folder9
            for i in range(1, 10):
                folder_key = f"work_folder{i}"
                folder_config = config.get(folder_key, {})
                
                if not isinstance(folder_config, dict):
                    continue
                    
                folder_name = folder_config.get("name", f"Folder {i}")
                folder_path = folder_config.get("path", "")
                folder_icon = folder_config.get("icon", "")
                folder_color = folder_config.get("color", "#007ACC")
                
                # Sprawdź, czy folder istnieje (tylko jeśli ma ścieżkę)
                folder_exists = os.path.exists(folder_path) if folder_path else False
                if folder_path and not folder_exists:
                    logger.warning(f"Folder roboczy nie istnieje: {folder_path}")
                
                # Dodaj wszystkie foldery, nawet puste
                self._folders.append({
                    "name": folder_name,
                    "path": folder_path,
                    "icon": folder_icon,
                    "color": folder_color,
                    "exists": folder_exists,
                    "enabled": bool(folder_path and folder_exists)  # Aktywny tylko jeśli ma ścieżkę i istnieje
                })

            self.folders_updated.emit(self._folders)
            logger.debug(f"Załadowano {len(self._folders)} folderów roboczych")

        except Exception as e:
            logger.error(f"Błąd podczas ładowania folderów roboczych: {e}")
            self._folders = []
            self.folders_updated.emit(self._folders)

    def get_folders(self):
        """Zwraca listę folderów roboczych."""
        return self._folders


class AssetScannerWorker(QThread):
    """Worker do skanowania assetów w osobnym wątku"""

    scan_progress = pyqtSignal(int, int, str)
    scan_finished = pyqtSignal(list, float, str)
    scan_error = pyqtSignal(str)

    def __init__(self, folder_path: str):
        super().__init__()
        self.folder_path = folder_path
        self._should_stop = False

    def run(self):
        try:
            import time
            start_time = time.time()

            logger.debug(f"AssetScannerWorker: Rozpoczynam skanowanie folderu: {self.folder_path}")

            if not os.path.exists(self.folder_path):
                self.scan_error.emit(f"Folder nie istnieje: {self.folder_path}")
                return

            if self._should_stop:
                return

            # Callback dla aktualizacji progress
            def progress_callback(current, total, msg):
                if not self._should_stop:
                    self.scan_progress.emit(current, total, msg)

            # Najpierw spróbuj załadować istniejące assety
            existing_assets = load_existing_assets(self.folder_path)
            logger.debug(f"Załadowano {len(existing_assets)} istniejących assetów")

            if self._should_stop:
                return

            # Zawsze skanuj folder, nawet jeśli są istniejące assety
            # To zapewni, że nowe pliki zostaną wykryte
            scanned_assets = find_and_create_assets(
                self.folder_path, 
                progress_callback=progress_callback
            )
            logger.debug(f"Przeskanowano folder, znaleziono {len(scanned_assets)} assetów")

            if self._should_stop:
                return

            # Połącz istniejące i nowe assety, usuwając duplikaty
            all_assets = existing_assets.copy()
            
            # Dodaj nowe assety, które nie istnieją już w existing_assets
            existing_names = {asset.get('name', '') for asset in existing_assets}
            for asset in scanned_assets:
                if asset.get('name', '') not in existing_names:
                    all_assets.append(asset)

            duration = time.time() - start_time
            operation_type = "scan_completed"

            # Dodaj ścieżkę folderu do każdego assetu
            for asset in all_assets:
                asset['folder_path'] = self.folder_path

            self.scan_finished.emit(all_assets, duration, operation_type)
            logger.debug(f"AssetScannerWorker: Skanowanie zakończone w {duration:.2f}s, znaleziono {len(all_assets)} assetów")

        except Exception as e:
            error_msg = f"Błąd podczas skanowania: {str(e)}"
            logger.error(error_msg)
            self.scan_error.emit(error_msg)

    def stop(self):
        """Zatrzymuje skanowanie."""
        self._should_stop = True
        logger.debug("AssetScannerWorker: Żądanie zatrzymania skanowania")


class AssetScannerModelMV(QObject):
    """Model dla skanera assetów w architekturze M/V"""

    scan_started = pyqtSignal(str)
    scan_progress = pyqtSignal(int, int, str)
    scan_completed = pyqtSignal(list, float, str)
    scan_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._current_worker = None
        logger.info("AssetScannerModelMV initialized")

    def scan_folder(self, folder_path: str):
        """Rozpoczyna skanowanie folderu w osobnym wątku."""
        if self._current_worker and self._current_worker.isRunning():
            logger.warning("Skanowanie już w toku, zatrzymuję poprzednie")
            self.stop_scan()

        self._current_worker = AssetScannerWorker(folder_path)
        self._current_worker.scan_progress.connect(self._on_scan_progress)
        self._current_worker.scan_finished.connect(self._on_scan_finished)
        self._current_worker.scan_error.connect(self._on_scan_error)
        self._current_worker.finished.connect(self._on_worker_finished)

        self._current_worker.start()
        self.scan_started.emit(folder_path)
        logger.debug(f"AssetScannerModelMV: Rozpoczęto skanowanie {folder_path}")

    def stop_scan(self):
        """Zatrzymuje aktywne skanowanie."""
        if self._current_worker and self._current_worker.isRunning():
            self._current_worker.stop()
            self._current_worker.wait(3000)  # Czekaj maksymalnie 3 sekundy
            if self._current_worker.isRunning():
                self._current_worker.terminate()
            logger.debug("AssetScannerModelMV: Skanowanie zatrzymane")

    def _on_scan_progress(self, current, total, message):
        """Przekazuje sygnał progress dalej."""
        self.scan_progress.emit(current, total, message)

    def _on_scan_finished(self, assets: list, duration: float, operation_type: str):
        """Obsługuje zakończenie skanowania."""
        self.scan_completed.emit(assets, duration, operation_type)
        logger.debug(f"AssetScannerModelMV: Skanowanie zakończone - {len(assets)} assetów w {duration:.2f}s")

    def _on_scan_error(self, error_msg: str):
        """Obsługuje błąd skanowania."""
        self.scan_error.emit(error_msg)
        logger.error(f"AssetScannerModelMV: Błąd skanowania - {error_msg}")

    def _on_worker_finished(self):
        """Czyści referencję do worker'a po zakończeniu."""
        self._current_worker = None 