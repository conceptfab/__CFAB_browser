import logging
import os
import sys
import time

from PyQt6.QtCore import (
    QMimeData,
    QObject,
    QPoint,
    QSize,
    Qt,
    QThread,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import QBrush  # Dodaj QBrush
from PyQt6.QtGui import QPen  # Dodaj QPen
from PyQt6.QtGui import (
    QColor,
    QDrag,
    QFont,
    QIcon,
    QPainter,
    QPixmap,
    QStandardItem,
    QStandardItemModel,
)
from PyQt6.QtWidgets import QStyledItemDelegate  # Dodaj QStyledItemDelegate
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSplitter,
    QStackedLayout,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from core.json_utils import load_from_file
from core.rules import FolderClickRules
from core.scanner import find_and_create_assets, load_existing_assets

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Wymuś poziom DEBUG dla tego loggera


# === ConfigManagerMV (ETAP 5) ===
class ConfigManagerMV(QObject):
    """Model dla zarządzania konfiguracją w architekturze M/V - ETAP 5"""

    config_loaded = pyqtSignal(dict)
    config_error = pyqtSignal(str)
    config_reloaded = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._config_cache = None
        self._config_timestamp = None
        self._config_path = "config.json"
        logger.info("ConfigManagerMV initialized - ETAP 5")

    def load_config(self, force_reload=False):
        try:
            if force_reload or not self._is_cache_valid():
                logger.debug("Ładowanie konfiguracji z pliku")
                config = load_from_file(self._config_path)
                if config:
                    self._config_cache = config
                    self._config_timestamp = (
                        os.path.getmtime(self._config_path)
                        if os.path.exists(self._config_path)
                        else 0
                    )
                    self.config_loaded.emit(config)
                    logger.info("Konfiguracja załadowana pomyślnie")
                else:
                    self._config_cache = self._get_default_config()
                    self._config_timestamp = 0
                    self.config_loaded.emit(self._config_cache)
                    logger.warning("Użyto domyślnej konfiguracji")

            return self._config_cache or self._get_default_config()

        except Exception as e:
            error_msg = f"Błąd ładowania konfiguracji: {e}"
            logger.error(error_msg)
            self.config_error.emit(error_msg)
            return self._get_default_config()

    def reload_config(self):
        config = self.load_config(force_reload=True)
        self.config_reloaded.emit(config)
        return config

    def get_config(self):
        if not self._config_cache:
            return self.load_config()
        return self._config_cache

    def _is_cache_valid(self):
        if not self._config_cache or not os.path.exists(self._config_path):
            return False
        current_timestamp = os.path.getmtime(self._config_path)
        return current_timestamp == self._config_timestamp

    def _get_default_config(self):
        return {
            "thumbnail": 256,
            "logger_level": "INFO",
            "use_styles": True,
            "work_folder1": "",
            "work_folder2": "",
            "work_folder3": "",
            "work_folder4": "",
            "work_folder5": "",
            "work_folder6": "",
            "work_folder7": "",
            "work_folder8": "",
            "work_folder9": "",
        }


# === FolderSystemModel (ETAP 6) ===
class FolderSystemModel(QObject):
    """Model dla systemu folderów w architekturze M/V - ETAP 6"""

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
        logger.info("FolderSystemModel initialized - ETAP 6")

    def get_tree_model(self):
        return self._tree_model

    def set_root_folder(self, folder_path: str):
        if self._root_folder != folder_path:
            self._root_folder = folder_path
            self._load_folder_structure()
            logger.info(f"Root folder changed: {folder_path}")

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
            logger.info(f"Folder structure loaded: {self._root_folder}")
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


# === WorkspaceFoldersModel (ETAP 7) ===
class WorkspaceFoldersModel(QObject):
    """Model dla folderów roboczych w architekturze M/V - ETAP 7"""

    folders_updated = pyqtSignal(list)

    def __init__(self, config_manager: ConfigManagerMV):
        super().__init__()
        self._config_manager = config_manager
        self._folders = []
        logger.info("WorkspaceFoldersModel initialized - ETAP 7")
        self._config_manager.config_loaded.connect(self._load_folders_from_config)
        self._config_manager.config_reloaded.connect(self._load_folders_from_config)

    def load_folders(self):
        config = self._config_manager.get_config()
        self._load_folders_from_config(config)

    def _load_folders_from_config(self, config: dict):
        folders_data = []
        for i in range(1, 10):
            folder_key = f"work_folder{i}"
            folder_config = config.get(folder_key, {})
            if not isinstance(folder_config, dict):
                log_msg = f"Invalid config for {folder_key}, expected dict, "
                log_msg += f"got {type(folder_config)}. Skipping."
                logger.warning(log_msg)
                folder_config = {}

            folders_data.append(
                {
                    "path": folder_config.get("path", ""),
                    "name": folder_config.get("name", f"Folder {i}"),
                    "icon": folder_config.get("icon", ""),
                    "color": folder_config.get("color", "#007ACC"),
                }
            )

        if self._folders != folders_data:
            self._folders = folders_data
            self.folders_updated.emit(self._folders)
            logger.info("Workspace folders updated from config.")

    def get_folders(self):
        return self._folders


# === AssetScannerModelMV (ETAP 8) ===
class AssetScannerWorker(QThread):
    """Worker do skanowania assetów w osobnym wątku - ETAP 8"""

    scan_progress = pyqtSignal(int, int, str)
    scan_finished = pyqtSignal(list, float, str)
    scan_error = pyqtSignal(str)

    def __init__(self, folder_path: str):
        super().__init__()
        self.folder_path = folder_path
        self.is_running = True

    def run(self):
        try:
            logger.info(f"AssetScannerWorker started for: {self.folder_path}")
            start_time = (
                time.perf_counter()
            )  # Rozpocznij mierzenie czasu z większą precyzją

            # Użyj FolderClickRules do podjęcia decyzji
            decision = FolderClickRules.decide_action(self.folder_path)
            action = decision.get("action")
            message = decision.get("message", "")

            assets = []

            def progress_callback(current, total, msg):
                if self.is_running:
                    progress = int((current / total) * 100) if total > 0 else 0
                    self.scan_progress.emit(progress, total, msg)

            if action == "run_scanner":
                logger.info(f"Decyzja: run_scanner. Wiadomość: {message}")
                self.scan_progress.emit(0, 100, "Skanowanie i tworzenie assetów...")
                assets = find_and_create_assets(self.folder_path, progress_callback)
                operation_type = "zeskanowano"
            elif action == "show_gallery":
                logger.info(f"Decyzja: show_gallery. Wiadomość: {message}")
                self.scan_progress.emit(0, 100, "Ładowanie istniejących assetów...")
                assets = load_existing_assets(self.folder_path)
                self.scan_progress.emit(100, 100, "Ładowanie zakończone.")
                operation_type = "wczytano"
            elif action == "no_action":
                logger.info(f"Decyzja: no_action. Wiadomość: {message}")
                self.scan_error.emit(message)
            elif action == "error":
                logger.error(f"Decyzja: error. Wiadomość: {message}")
                self.scan_error.emit(message)
            else:
                logger.warning(f"Nieznana akcja: {action}. Wiadomość: {message}")
                self.scan_error.emit(f"Nieznana akcja skanera: {action}")

            end_time = time.perf_counter()  # Zakończ mierzenie czasu z większą precyzją
            duration = end_time - start_time
            logger.debug(
                f"DEBUG: start_time={start_time}, end_time={end_time}, duration={duration}"
            )

            if self.is_running:
                self.scan_finished.emit(
                    assets, duration, operation_type
                )  # Przekaż czas trwania i typ operacji
            logger.info(
                f"AssetScannerWorker finished for: {self.folder_path} in {duration:.2f} seconds"
            )
        except Exception as e:
            error_msg = f"Błąd w AssetScannerWorker: {e}"
            logger.error(error_msg)
            if self.is_running:
                self.scan_error.emit(error_msg)

    def stop(self):
        self.is_running = False
        logger.info("AssetScannerWorker stop requested.")


class AssetScannerModelMV(QObject):
    """Model dla skanera assetów w architekturze M/V - ETAP 8"""

    scan_started = pyqtSignal(str)
    scan_progress = pyqtSignal(int, int, str)
    scan_completed = pyqtSignal(list, float, str)
    scan_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._worker = None
        self._is_scanning = False
        logger.info("AssetScannerModelMV initialized - ETAP 8")

    def scan_folder(self, folder_path: str):
        if self._is_scanning:
            logger.warning("Skanowanie jest już w toku. Anulowanie poprzedniego.")
            self.stop_scan()

        self._is_scanning = True
        self.scan_started.emit(folder_path)
        self._worker = AssetScannerWorker(folder_path)
        self._worker.scan_progress.connect(self._on_scan_progress)
        self._worker.scan_finished.connect(self._on_scan_finished)
        self._worker.scan_error.connect(self._on_scan_error)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()
        logger.info(f"Rozpoczęto skanowanie folderu: {folder_path}")

    def stop_scan(self):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.quit()
            self._worker.wait()
        self._is_scanning = False

    def _on_scan_progress(self, current, total, message):
        progress = int((current / total) * 100) if total > 0 else 0
        self.scan_progress.emit(progress, total, message)
        logger.debug(f"Scan progress: {progress}% - {message}")

    def _on_scan_finished(self, assets: list, duration: float, operation_type: str):
        self.scan_completed.emit(assets, duration, operation_type)
        self._is_scanning = False
        logger.debug(f"DEBUG: Model received duration={duration}")
        if operation_type == "wczytano":
            log_message = f"Wczytywanie assetów zakończone, {operation_type} {len(assets)} assetów w {duration:.2f} sekund."
        else:
            log_message = f"Skanowanie assetów zakończone, {operation_type} {len(assets)} assetów w {duration:.2f} sekund."
        logger.info(log_message)

    def _on_scan_error(self, error_msg: str):
        self.scan_error.emit(error_msg)
        self._is_scanning = False
        logger.error(f"Błąd skanowania: {error_msg}")

    def _on_worker_finished(self):
        self._is_scanning = False
        logger.info("Wątek skanera zakończył pracę.")


# === AssetTileModel (ETAP 9) ===
class AssetTileModel(QObject):
    """Model dla pojedynczego kafelka assetu - ETAP 9"""

    data_changed = pyqtSignal()

    def __init__(self, asset_data: dict):
        super().__init__()
        self.data = asset_data
        self.is_special_folder = self.data.get("type") == "special_folder"

    def get_name(self) -> str:
        return self.data.get("name", "Unknown")

    def get_thumbnail_path(self) -> str:
        if self.is_special_folder:
            return ""  # Specjalne foldery nie mają miniaturek w .cache
        if not self.data.get("thumbnail"):
            return ""
        # Zakładamy, że asset_data zawiera 'folder_path' dla assetów
        folder_path = self.data.get("folder_path")
        if not folder_path:
            logger.warning(f"Brak 'folder_path' w danych assetu: {self.get_name()}")
            return ""
        cache_dir = os.path.join(folder_path, ".cache")
        return os.path.join(cache_dir, f"{self.get_name()}.thumb")

    def get_size_mb(self) -> float:
        return self.data.get("size_mb", 0.0)

    def get_stars(self) -> int:
        stars = self.data.get("stars")
        return int(stars) if stars is not None else 0

    def has_textures_in_archive(self) -> bool:
        return self.data.get("textures_in_the_archive", False)

    def get_folder_path(self) -> str:
        return self.data.get("folder_path", "")

    def get_asset_type(self) -> str:
        return self.data.get("type", "asset")

    def get_archive_path(self) -> str:
        if self.is_special_folder:
            return ""
        folder_path = self.data.get("folder_path")
        archive_filename = self.data.get("archive")
        if folder_path and archive_filename:
            return os.path.join(folder_path, archive_filename)
        return ""

    def get_preview_path(self) -> str:
        if self.is_special_folder:
            return ""
        folder_path = self.data.get("folder_path")
        preview_filename = self.data.get("preview")
        if folder_path and preview_filename:
            return os.path.join(folder_path, preview_filename)
        return ""

    def get_asset_data(self) -> dict:
        return self.data


# ==============================================================================
# MODEL LAYER - Logika biznesowa
# ==============================================================================


from PyQt6.QtCore import QTimer  # Dodaj import QTimer


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
        logger.info("AssetGridModel initialized - ETAP 3")

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
        logger.info("FolderTreeModel initialized - ETAP 2")

    def get_tree_model(self):
        return self._tree_model

    def set_root_folder(self, folder_path: str):
        if self._root_folder != folder_path:
            self._root_folder = folder_path
            self._tree_model.clear()
            self._tree_model.setHorizontalHeaderLabels(["Folders"])
            self.root_folder_changed.emit(folder_path)
            self.folder_structure_changed.emit(self._tree_model)
            logger.info(f"Root folder changed: {folder_path}")

    def get_root_folder(self):
        return self._root_folder


class ControlPanelModel(QObject):
    """Model dla panelu kontrolnego - stan kontrolek (ETAP 4)"""

    progress_changed = pyqtSignal(int)
    thumbnail_size_changed = pyqtSignal(int)
    selection_state_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._progress = 0
        self._thumbnail_size = 256
        self._has_selection = False

    def set_progress(self, value: int):
        value = max(0, min(100, value))
        if self._progress != value:
            self._progress = value
            self.progress_changed.emit(value)

    def get_progress(self):
        return self._progress

    def set_thumbnail_size(self, value: int):
        if self._thumbnail_size != value:
            self._thumbnail_size = value
            self.thumbnail_size_changed.emit(value)

    def get_thumbnail_size(self):
        return self._thumbnail_size

    def set_has_selection(self, has: bool):
        logger.debug(f"ControlPanelModel: set_has_selection called with: {has}")
        if self._has_selection != has:
            self._has_selection = has
            self.selection_state_changed.emit(has)
            logger.debug(f"ControlPanelModel: selection_state_changed emitted: {has}")

    def has_selection(self):
        return self._has_selection


class SelectionModel(QObject):
    """Model dla zarządzania zaznaczeniem assetów - ETAP 12"""

    selection_changed = pyqtSignal(list)  # Emituje listę ID zaznaczonych assetów

    def __init__(self):
        super().__init__()
        self._selected_asset_ids = (
            set()
        )  # Używamy set dla szybkiego sprawdzania unikalności
        logger.info("SelectionModel initialized - ETAP 12")

    def add_selection(self, asset_id: str):
        if asset_id not in self._selected_asset_ids:
            self._selected_asset_ids.add(asset_id)
            self._emit_selection_changed()

    def remove_selection(self, asset_id: str):
        if asset_id in self._selected_asset_ids:
            self._selected_asset_ids.remove(asset_id)
            self._emit_selection_changed()

    def clear_selection(self):
        if self._selected_asset_ids:
            self._selected_asset_ids.clear()
            self._emit_selection_changed()

    def get_selected_asset_ids(self) -> list:
        return list(self._selected_asset_ids)

    def is_selected(self, asset_id: str) -> bool:
        return asset_id in self._selected_asset_ids

    def _emit_selection_changed(self):
        self.selection_changed.emit(list(self._selected_asset_ids))
        logger.debug(
            f"SelectionModel: Selection changed. Total selected: {len(self._selected_asset_ids)} items. Selected IDs: {list(self._selected_asset_ids)}"
        )


import shutil
import subprocess


class FileOperationsModel(QObject):
    """Model dla operacji na plikach (przenoszenie, usuwanie) - ETAP 13"""

    operation_progress = pyqtSignal(int, int, str)  # current, total, message
    operation_completed = pyqtSignal(list, list)  # success_messages, error_messages
    operation_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        logger.info("FileOperationsModel initialized - ETAP 13")

    def delete_assets(self, assets_data: list, current_folder_path: str):
        """Usuwa zaznaczone assety (wszystkie 4 pliki)."""
        if not assets_data:
            self.operation_completed.emit([], [])
            return

        success_messages = []
        error_messages = []
        total_assets = len(assets_data)

        for i, asset_data in enumerate(assets_data):
            asset_name = asset_data.get("name", "Unknown Asset")
            self.operation_progress.emit(i + 1, total_assets, f"Usuwanie: {asset_name}")
            try:
                files_to_delete = self._get_asset_files_paths(
                    asset_data, current_folder_path
                )
                for file_path in files_to_delete:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.debug(f"Usunięto plik: {file_path}")
                success_messages.append(f"Pomyślnie usunięto asset: {asset_name}")
                logger.info(f"Usunięto asset: {asset_name}")
            except Exception as e:
                error_messages.append(f"Błąd usuwania assetu {asset_name}: {e}")
                logger.error(f"Błąd usuwania assetu {asset_name}: {e}")

        # Po usunięciu assetów, sprawdź i usuń pusty folder .cache
        cache_dir = os.path.join(current_folder_path, ".cache")
        if os.path.exists(cache_dir) and not os.listdir(cache_dir):
            try:
                os.rmdir(cache_dir)
                logger.info(f"Usunięto pusty folder .cache: {cache_dir}")
            except Exception as e:
                logger.warning(
                    f"Nie można usunąć pustego folderu .cache {cache_dir}: {e}"
                )

        self.operation_completed.emit(success_messages, error_messages)

    def move_assets(
        self, assets_data: list, source_folder_path: str, target_folder_path: str
    ):
        """Przenosi zaznaczone assety do nowego folderu."""
        if not assets_data:
            self.operation_completed.emit([], [])
            return

        success_messages = []
        error_messages = []
        total_assets = len(assets_data)

        if not os.path.exists(target_folder_path):
            try:
                os.makedirs(target_folder_path)
                logger.info(f"Utworzono folder docelowy: {target_folder_path}")
            except Exception as e:
                self.operation_error.emit(
                    f"Nie można utworzyć folderu docelowego {target_folder_path}: {e}"
                )
                return

        for i, asset_data in enumerate(assets_data):
            asset_name = asset_data.get("name", "Unknown Asset")
            self.operation_progress.emit(
                i + 1, total_assets, f"Przenoszenie: {asset_name}"
            )
            try:
                files_to_move = self._get_asset_files_paths(
                    asset_data, source_folder_path
                )
                # Obsługa pliku .thumb w folderze .cache
                thumb_file_path = os.path.join(
                    source_folder_path, ".cache", f"{asset_name}.thumb"
                )
                if os.path.exists(thumb_file_path):
                    target_cache_dir = os.path.join(target_folder_path, ".cache")
                    os.makedirs(target_cache_dir, exist_ok=True)
                    shutil.move(thumb_file_path, target_cache_dir)
                    logger.debug(
                        f"Przeniesiono plik thumb: {thumb_file_path} do {target_cache_dir}"
                    )

                for file_path in files_to_move:
                    if os.path.exists(file_path):
                        shutil.move(file_path, target_folder_path)
                        logger.debug(
                            f"Przeniesiono plik: {file_path} do {target_folder_path}"
                        )
                success_messages.append(f"Pomyślnie przeniesiono asset: {asset_name}")
                logger.info(f"Przeniesiono asset: {asset_name}")
            except Exception as e:
                error_messages.append(f"Błąd przenoszenia assetu {asset_name}: {e}")
                logger.error(f"Błąd przenoszenia assetu {asset_name}: {e}")

        # Po przeniesieniu assetów, sprawdź i usuń pusty folder .cache w źródle
        source_cache_dir = os.path.join(source_folder_path, ".cache")
        if os.path.exists(source_cache_dir) and not os.listdir(source_cache_dir):
            try:
                os.rmdir(source_cache_dir)
                logger.info(
                    f"Usunięto pusty folder .cache w źródle: {source_cache_dir}"
                )
            except Exception as e:
                logger.warning(
                    f"Nie można usunąć pustego folderu .cache w źródle {source_cache_dir}: {e}"
                )

        self.operation_completed.emit(success_messages, error_messages)

    def _get_asset_files_paths(self, asset_data: dict, folder_path: str) -> list:
        """Zwraca listę pełnych ścieżek do plików assetu (bez thumb)."""
        files = []
        asset_name = asset_data.get("name", "")

        # Plik .asset
        asset_file = os.path.join(folder_path, f"{asset_name}.asset")
        if os.path.exists(asset_file):
            files.append(asset_file)

        # Plik archiwum
        archive_filename = asset_data.get("archive")
        if archive_filename:
            archive_file = os.path.join(folder_path, archive_filename)
            if os.path.exists(archive_file):
                files.append(archive_file)

        # Plik podglądu
        preview_filename = asset_data.get("preview")
        if preview_filename:
            preview_file = os.path.join(folder_path, preview_filename)
            if os.path.exists(preview_file):
                files.append(preview_file)

        return files


class DragDropModel(QObject):
    """Model dla operacji Drag and Drop - ETAP 14"""

    drag_started = pyqtSignal(list)  # Lista ID assetów przeciąganych
    drop_possible = pyqtSignal(bool)  # Czy upuszczenie jest możliwe
    drop_completed = pyqtSignal(
        str, list
    )  # Ścieżka docelowa, lista ID przeniesionych assetów

    def __init__(self):
        super().__init__()
        self._dragged_asset_ids = []
        logger.info("DragDropModel initialized - ETAP 14")

    def start_drag(self, asset_ids: list):
        self._dragged_asset_ids = asset_ids
        self.drag_started.emit(asset_ids)
        logger.debug(f"Drag started for assets: {asset_ids}")

    def validate_drop(self, target_path: str) -> bool:
        """Waliduje, czy upuszczenie jest możliwe w danym folderze."""
        # Przykład: Nie zezwalaj na upuszczanie do folderów tekstur
        if any(
            folder_name in target_path.lower()
            for folder_name in ["tex", "textures", "maps"]
        ):
            self.drop_possible.emit(False)
            logger.debug(f"Drop not possible: {target_path} is a texture folder.")
            return False
        # Dodaj inne warunki walidacji, np. czy to jest folder, czy użytkownik ma uprawnienia itp.
        self.drop_possible.emit(True)
        logger.debug(f"Drop possible: {target_path}")
        return True

    def complete_drop(self, target_path: str):
        self.drop_completed.emit(target_path, self._dragged_asset_ids)
        self._dragged_asset_ids = []  # Wyczyść po zakończeniu operacji
        logger.debug(
            f"Drop completed to {target_path} for assets: {self._dragged_asset_ids}"
        )

    def get_dragged_asset_ids(self) -> list:
        return self._dragged_asset_ids


class AmvModel(QObject):
    """Model dla zakładki AMV - logika biznesowa"""

    config_changed = pyqtSignal(dict)
    thumbnail_size_changed = pyqtSignal(int)
    work_folder_changed = pyqtSignal(str)
    splitter_state_changed = pyqtSignal(bool)
    state_initialized = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._config = {}
        self._thumbnail_size = 256
        self._work_folder = ""
        self._is_left_panel_collapsed = False
        self._last_splitter_sizes = [200, 800]
        self.folder_tree_model = FolderTreeModel()
        self.asset_grid_model = AssetGridModel()
        self.control_panel_model = ControlPanelModel()
        self.config_manager = ConfigManagerMV()
        self.folder_system_model = FolderSystemModel()
        self.workspace_folders_model = WorkspaceFoldersModel(self.config_manager)
        self.asset_scanner_model = AssetScannerModelMV()  # ETAP 8
        self.selection_model = SelectionModel()  # ETAP 12
        self.file_operations_model = FileOperationsModel()  # ETAP 13
        self.drag_drop_model = DragDropModel()  # ETAP 14
        logger.info("AmvModel initialized - ETAP 9")

    def initialize_state(self):
        """Inicjalizuje stan z konfiguracji. Wywoływane po utworzeniu kontrolera."""
        try:
            config = self.config_manager.load_config()
            self._config = config
            self._thumbnail_size = config.get("thumbnail", 256)
            self.control_panel_model.set_thumbnail_size(self._thumbnail_size)

            self.config_changed.emit(config)
            self.thumbnail_size_changed.emit(self._thumbnail_size)
            self.state_initialized.emit()
            logger.info("Stan aplikacji zainicjalizowany z konfiguracji")
        except Exception as e:
            logger.error(f"Błąd inicjalizacji stanu: {e}")
            self._config = self.config_manager._get_default_config()
            self.state_initialized.emit()

    def set_config(self, config: dict):
        self._config = config
        self.config_changed.emit(config)

    def set_thumbnail_size(self, size: int):
        self._thumbnail_size = size
        self.thumbnail_size_changed.emit(size)

    def set_work_folder(self, folder_path: str):
        self._work_folder = folder_path
        self.work_folder_changed.emit(folder_path)

    def toggle_left_panel(self):
        self._is_left_panel_collapsed = not self._is_left_panel_collapsed
        self.splitter_state_changed.emit(not self._is_left_panel_collapsed)
        status = "collapsed" if self._is_left_panel_collapsed else "expanded"
        logger.info(f"Left panel {status}")

    def set_splitter_sizes(self, sizes: list):
        if not self._is_left_panel_collapsed and len(sizes) == 2 and sizes[0] > 0:
            self._last_splitter_sizes = sizes[:]
            logger.debug(f"Splitter sizes saved: {sizes}")

    def get_splitter_sizes(self):
        if self._is_left_panel_collapsed:
            return [0, 1000]
        else:
            return self._last_splitter_sizes[:]

    def is_left_panel_collapsed(self):
        return self._is_left_panel_collapsed


# ==============================================================================
# VIEW LAYER - Prezentacja
# ==============================================================================


# === AssetTileView (ETAP 9) ===
class AssetTileView(QFrame):
    """Widok dla pojedynczego kafelka assetu - ETAP 9"""

    thumbnail_clicked = pyqtSignal(str)  # Ścieżka do pliku podglądu
    filename_clicked = pyqtSignal(str)  # Ścieżka do pliku archiwum
    checkbox_state_changed = pyqtSignal(bool)  # Czy kafelek jest zaznaczony
    drag_started = pyqtSignal(object)  # Dane assetu

    def __init__(
        self,
        tile_model: AssetTileModel,
        thumbnail_size: int,
        tile_number: int,
        total_tiles: int,
        selection_model: SelectionModel,  # Dodaj selection_model
    ):
        super().__init__()
        self.model = tile_model
        self.thumbnail_size = thumbnail_size
        self.tile_number = tile_number
        self.total_tiles = total_tiles
        self.selection_model = selection_model  # Przypisz selection_model
        self.asset_id = self.model.get_name()  # Użyj nazwy assetu jako ID
        self._drag_start_position = (
            QPoint()
        )  # Dodaj atrybut do przechowywania pozycji startowej przeciągania

        self.margins_size = 8
        self._setup_ui()
        self.model.data_changed.connect(self.update_ui)

    def _setup_ui(self):
        self.setStyleSheet(
            """
            AssetTileView {
                background-color: #252526;
                border: 1px solid #3F3F46;
                border-radius: 6px;
            }
            AssetTileView:hover {
                border-color: #007ACC;
                background-color: #2D2D30;
            }
        """
        )

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setFixedWidth(self.thumbnail_size + (2 * self.margins_size))

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(
            self.margins_size, self.margins_size, self.margins_size, self.margins_size
        )

        # RZĄD 1: Miniaturka
        self.thumbnail_container = QLabel()
        self.thumbnail_container.setFixedSize(self.thumbnail_size, self.thumbnail_size)
        self.thumbnail_container.setStyleSheet(
            """
            QLabel {
                background-color: #2A2D2E;
                border: 2px solid transparent;
                border-radius: 4px;
            }
            QLabel:hover {
                border-color: #007ACC;
            }
        """
        )
        self.thumbnail_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.thumbnail_container.mousePressEvent = self._on_thumbnail_clicked

        # RZĄD 2: Dolna sekcja (tekst, gwiazdki, etc.)
        # Nazwa pliku
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        self.name_label.setStyleSheet(
            """
            QLabel {
                color: #CCCCCC; background-color: transparent; font-size: 10px;
                padding: 2px;
            }
            QLabel:hover {
                font-weight: bold; color: #FFFFFF;
            }
        """
        )
        self.name_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.name_label.mousePressEvent = self._on_filename_clicked

        # Ikona texture (ukryta domyślnie)
        self.texture_icon = QLabel()
        self.texture_icon.setFixedSize(16, 16)
        self.texture_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.texture_icon.setVisible(False)  # Ukryta domyślnie
        self._load_texture_icon()

        # Dolny rząd z numerem, gwiazdki i checkboxem
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(6)

        # Numer kafelka
        self.tile_number_label = QLabel()
        self.tile_number_label.setStyleSheet(
            "color: #888888; background-color: transparent; "
            "font-size: 9px; font-weight: bold;"
        )

        # Gwiazdki
        self.star_checkboxes = []
        for i in range(5):
            star_cb = QCheckBox("★")
            star_cb.setStyleSheet(
                """
                QCheckBox { spacing: 0px; color: #888888; font-size: 14px; border: none; padding: 0px; background: transparent; }
                QCheckBox::indicator { width: 0px; height: 0px; border: none; }
                QCheckBox:checked { color: #FFD700; font-weight: bold; }
                QCheckBox:hover { color: #FFA500; }
            """
            )
            star_cb.clicked.connect(
                lambda checked, star_index=i: self._on_star_clicked(star_index + 1)
            )
            self.star_checkboxes.append(star_cb)

        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setFixedSize(16, 16)
        self.checkbox.setStyleSheet(
            """
            QCheckBox::indicator {
                width: 14px; height: 14px; border: 1px solid #555;
                border-radius: 2px; background-color: #2A2D2E;
            }
            QCheckBox::indicator:checked {
                background-color: #007ACC; border-color: #007ACC;
            }
            QCheckBox::indicator:hover { border-color: #007ACC; }
        """
        )
        # Połącz sygnał stateChanged z metodą obsługującą zmianę zaznaczenia w modelu
        self.checkbox.stateChanged.connect(self._on_checkbox_state_changed)

        bottom_row.addWidget(self.tile_number_label)
        bottom_row.addStretch()  # Rozpycha elementy
        for star_cb in self.star_checkboxes:
            bottom_row.addWidget(star_cb)
        bottom_row.addStretch()  # Rozpycha elementy
        bottom_row.addWidget(self.checkbox)

        # Dodanie elementów do głównego layoutu
        layout.addWidget(self.thumbnail_container)

        # Dodajemy nazwę pliku w osobnym layoutcie poziomym dla wycentrowania
        filename_container = QHBoxLayout()
        filename_container.addStretch()
        filename_container.addWidget(self.name_label)
        filename_container.addWidget(self.texture_icon)  # Ikona texture obok nazwy
        filename_container.addStretch()
        layout.addLayout(filename_container)

        # Dodajemy stretch, który dopycha dolny rząd do dołu
        layout.addStretch(1)

        # Dolny rząd z numerem, gwiazdkami i checkboxem - teraz przyklejony do dołu
        layout.addLayout(bottom_row)

        self.setAcceptDrops(False)  # D&D będzie obsługiwane przez Controller
        self.setMouseTracking(True)

        self.update_ui()
        # Ustaw początkowy stan checkboxa na podstawie SelectionModel
        self.checkbox.setChecked(self.selection_model.is_selected(self.asset_id))

    def update_ui(self):
        if self.model.is_special_folder:
            self._setup_folder_tile_ui()
        else:
            self._setup_asset_tile_ui()

    def _setup_asset_tile_ui(self):
        # Wyświetlanie nazwy i rozmiaru pliku
        file_name = self.model.get_name()
        file_size_mb = self.model.get_size_mb()
        if file_size_mb > 0:
            self.name_label.setText(f"{file_name} ({file_size_mb:.1f} MB)")
        else:
            self.name_label.setText(file_name)

        self.tile_number_label.setText(f"{self.tile_number} / {self.total_tiles}")
        self.set_star_rating(self.model.get_stars())
        self.texture_icon.setVisible(self.model.has_textures_in_archive())
        self.checkbox.setVisible(True)

        thumb_path = self.model.get_thumbnail_path()
        if os.path.exists(thumb_path):
            pixmap = QPixmap(thumb_path)
            scaled_pixmap = pixmap.scaled(
                self.thumbnail_size,
                self.thumbnail_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.thumbnail_container.setPixmap(scaled_pixmap)
        else:
            self._create_placeholder_thumbnail()

    def _setup_folder_tile_ui(self):
        self.setStyleSheet(
            """
            AssetTileView {
                background-color: #2D3E50;
                border: 1px solid #34495E;
                border-radius: 6px;
            }
            AssetTileView:hover {
                border-color: #3498DB;
                background-color: #34495E;
            }
        """
        )
        self.name_label.setText(self.model.get_name())
        self.tile_number_label.setText("")  # Foldery nie mają numeracji
        self.texture_icon.setVisible(False)
        self.checkbox.setVisible(False)
        for star_cb in self.star_checkboxes:
            star_cb.setVisible(False)

        self._load_folder_icon()

    def _create_placeholder_thumbnail(self):
        pixmap = QPixmap(self.thumbnail_size, self.thumbnail_size)
        pixmap.fill(QColor("#2A2D2E"))
        painter = QPainter(pixmap)
        painter.setPen(QColor("#CCCCCC"))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "IMG")
        painter.end()
        self.thumbnail_container.setPixmap(pixmap)

    def _load_folder_icon(self):
        icon_path = os.path.join(
            os.path.dirname(__file__), "resources", "img", "folder.png"
        )
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.thumbnail_size - 20,
                    self.thumbnail_size - 20,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.thumbnail_container.setPixmap(scaled_pixmap)
            else:
                self._create_fallback_icon()
        else:
            self._create_fallback_icon()

    def _create_fallback_icon(self):
        self.thumbnail_container.setText("📁")
        self.thumbnail_container.setStyleSheet(
            self.thumbnail_container.styleSheet()
            + """
            QLabel {
                font-size: 48px;
                color: #3498DB;
            }
        """
        )

    def _load_texture_icon(self):
        icon_path = os.path.join(
            os.path.dirname(__file__), "resources", "img", "texture.png"
        )
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    16,
                    16,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.texture_icon.setPixmap(scaled_pixmap)
            else:
                self._create_fallback_texture_icon()
        else:
            self._create_fallback_texture_icon()

    def _create_fallback_texture_icon(self):
        self.texture_icon.setText("🔳")
        self.texture_icon.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                color: #888888;
            }
        """
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_position = event.pos()  # Zapisz pozycję startową
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            event.buttons() == Qt.MouseButton.LeftButton
            and not self.model.is_special_folder
        ):
            if (
                event.pos() - self._drag_start_position
            ).manhattanLength() > QApplication.startDragDistance():
                self._start_drag(event)
        super().mouseMoveEvent(event)

    def _start_drag(self, event):
        # Pobierz zaznaczone assety z SelectionModel
        selected_asset_ids = self.selection_model.get_selected_asset_ids()
        if not selected_asset_ids:
            # Jeśli nic nie jest zaznaczone, przeciągnij tylko ten kafelek
            selected_asset_ids = [self.asset_id]

        # Utwórz QMimeData z listą ID assetów
        mime_data = QMimeData()
        mime_data.setText(",".join(selected_asset_ids))  # Przekaż ID jako tekst

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        # Ustaw ikonę przeciągania (opcjonalnie)
        # pixmap = self.thumbnail_container.pixmap()
        # if pixmap: drag.setPixmap(pixmap)

        # Wykonaj operację przeciągania
        drag.exec(
            Qt.DropAction.MoveAction
        )  # Możesz użyć CopyAction, MoveAction, LinkAction

    def _on_thumbnail_clicked(self, ev):
        if self.model.is_special_folder:
            self.thumbnail_clicked.emit(self.model.get_folder_path())
        else:
            self.thumbnail_clicked.emit(self.model.get_preview_path())

    def _on_filename_clicked(self, ev):
        if self.model.is_special_folder:
            self.filename_clicked.emit(self.model.get_folder_path())
        else:
            self.filename_clicked.emit(self.model.get_archive_path())

    def update_thumbnail_size(self, new_size: int):
        self.thumbnail_size = new_size
        self.thumbnail_container.setFixedSize(new_size, new_size)
        self.setFixedWidth(self.thumbnail_size + (2 * self.margins_size))
        self.update_ui()  # Odśwież UI z nowym rozmiarem
        self.updateGeometry()

    def is_checked(self) -> bool:
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool):
        # Odłącz sygnał tymczasowo, aby uniknąć rekurencji i wymusić emisję sygnału
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(checked)
        self.checkbox.blockSignals(False)
        # Ręcznie wywołaj metodę obsługującą zmianę stanu, aby zaktualizować model
        self._on_checkbox_state_changed(self.checkbox.checkState().value)

    def _on_checkbox_state_changed(self, state: int):
        logger.debug(
            f"AssetTileView: Checkbox state changed to: {state} for asset: {self.asset_id}"
        )
        if self.model.is_special_folder:  # Nie zaznaczamy folderów specjalnych
            self.checkbox.setChecked(False)
            logger.debug(
                f"AssetTileView: Special folder, checkbox unchecked for: {self.asset_id}"
            )
            return

        if state == Qt.CheckState.Checked.value:
            self.selection_model.add_selection(self.asset_id)
        else:
            self.selection_model.remove_selection(self.asset_id)

    def get_star_rating(self) -> int:
        return sum(1 for cb in self.star_checkboxes if cb.isChecked())

    def set_star_rating(self, rating: int):
        rating = max(0, min(5, rating))  # 0-5 gwiazdek
        for i, cb in enumerate(self.star_checkboxes):
            cb.setChecked(i < rating)

    def _on_star_clicked(self, clicked_rating: int):
        """Obsługuje kliknięcie gwiazdki i ustawia ocenę."""
        current_rating = self.get_star_rating()
        new_rating = clicked_rating

        # Jeśli kliknięto tę samą gwiazdkę, co aktualna ocena, ustaw na 0
        if clicked_rating == current_rating:
            new_rating = 0

        self.set_star_rating(new_rating)
        # Tutaj można by emitować sygnał do modelu, aby zapisać nową ocenę
        logger.debug(f"Asset {self.model.get_name()} rating set to: {new_rating}")

    def clear_stars(self):
        for cb in self.star_checkboxes:
            cb.setChecked(False)


class GalleryContainerWidget(QWidget):
    resized = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit(self.width())
        logger.debug(f"GalleryContainerWidget resized to: {self.width()}px")


class DropHighlightDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        is_drop_target = index.data(Qt.ItemDataRole.UserRole + 1)
        if is_drop_target and painter:
            painter.save()
            rect = option.rect
            painter.setBrush(QBrush(QColor("#007ACC")))
            painter.setPen(QPen(QColor("#FFD700"), 2))
            painter.drawRect(rect.adjusted(1, 1, -2, -2))
            painter.restore()
            # Rysuj tekst normalnie - niebieskie tło i tak będzie widoczne
            super().paint(painter, option, index)
        else:
            super().paint(painter, option, index)


class CustomFolderTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._highlighted_index = None
        self.drag_drop_model = None
        self.file_operations_model = None
        self.current_folder_path_getter = (
            None  # Funkcja do pobierania aktualnego folderu
        )

    def set_models(
        self, drag_drop_model, file_operations_model, current_folder_path_getter
    ):
        self.drag_drop_model = drag_drop_model
        self.file_operations_model = file_operations_model
        self.current_folder_path_getter = current_folder_path_getter

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith(
            "application/x-cfab-asset"
        ):
            event.acceptProposedAction()
            self._highlight_folder_at_position(event.pos())
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self._clear_folder_highlight()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith(
            "application/x-cfab-asset"
        ):
            index = self.indexAt(event.pos())
            if index.isValid():
                item = self.model().itemFromIndex(index)
                if item and item.data(Qt.ItemDataRole.UserRole):
                    target_path = item.data(Qt.ItemDataRole.UserRole)
                    if self.drag_drop_model and self.drag_drop_model.validate_drop(
                        target_path
                    ):
                        event.acceptProposedAction()
                        self._highlight_folder_at_position(event.pos())
                    else:
                        event.ignore()
                        self._clear_folder_highlight()
                else:
                    event.ignore()
                    self._clear_folder_highlight()
            else:
                event.ignore()
                self._clear_folder_highlight()
        else:
            event.ignore()
            self._clear_folder_highlight()

    def dropEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith(
            "application/x-cfab-asset"
        ):
            index = self.indexAt(event.pos())
            if index.isValid():
                item = self.model().itemFromIndex(index)
                if item and item.data(Qt.ItemDataRole.UserRole):
                    target_folder_path = item.data(Qt.ItemDataRole.UserRole)
                    if self.drag_drop_model and self.drag_drop_model.validate_drop(
                        target_folder_path
                    ):
                        asset_ids_str = (
                            event.mimeData()
                            .text()
                            .replace("application/x-cfab-asset,", "")
                        )
                        asset_ids = asset_ids_str.split(",")

                        # Pobierz pełne dane assetów
                        all_assets = (
                            self.parent().parent().model.asset_grid_model.get_assets()
                        )  # Dostęp do AmvModel przez parent
                        assets_to_move = [
                            asset
                            for asset in all_assets
                            if asset.get("name") in asset_ids
                        ]

                        if (
                            assets_to_move
                            and self.file_operations_model
                            and self.current_folder_path_getter
                        ):
                            source_folder_path = self.current_folder_path_getter()
                            self.file_operations_model.move_assets(
                                assets_to_move, source_folder_path, target_folder_path
                            )
                            self.drag_drop_model.complete_drop(
                                target_folder_path, asset_ids
                            )
                            event.acceptProposedAction()
                        else:
                            event.ignore()
                    else:
                        event.ignore()
                else:
                    event.ignore()
            else:
                event.ignore()
            self._clear_folder_highlight()
        else:
            event.ignore()
            self._clear_folder_highlight()

    def _highlight_folder_at_position(self, pos):
        index = self.indexAt(pos)
        if index.isValid():
            if self._highlighted_index and self._highlighted_index.isValid():
                self.model().setData(
                    self._highlighted_index, False, Qt.ItemDataRole.UserRole + 1
                )
            self._highlighted_index = index
            self.model().setData(
                self._highlighted_index, True, Qt.ItemDataRole.UserRole + 1
            )
            self.viewport().update()

    def _clear_folder_highlight(self):
        if self._highlighted_index and self._highlighted_index.isValid():
            self.model().setData(
                self._highlighted_index, False, Qt.ItemDataRole.UserRole + 1
            )
            self.viewport().update()
        self._highlighted_index = None


class AmvView(QWidget):
    """View dla zakładki AMV - prezentacja UI"""

    splitter_moved = pyqtSignal(list)
    toggle_panel_requested = pyqtSignal()
    workspace_folder_clicked = pyqtSignal(str)  # ETAP 7
    gallery_viewport_resized = pyqtSignal(int)  # Nowy sygnał dla szerokości viewportu

    def __init__(self):
        super().__init__()
        self._setup_ui()
        logger.info("AmvView initialized - ETAP 9")

    def _setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setSizes([200, 800])
        self.splitter.splitterMoved.connect(self._on_splitter_moved)
        self._create_left_panel()
        self._create_gallery_panel()
        layout.addWidget(self.splitter)
        self.setLayout(layout)

    def _create_left_panel(self):
        self.left_panel = QFrame()
        self.left_panel.setFrameStyle(QFrame.Shape.NoFrame)
        self.left_panel.setMinimumWidth(250)
        self.left_panel.setMaximumWidth(350)
        self.left_panel.setStyleSheet(
            """
            QFrame {
                background-color: #1E1E1E;
                border-right: 1px solid #3F3F46;
            }
        """
        )
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._create_left_panel_header(layout)
        self._create_folder_tree_view(layout)
        self._create_folder_buttons_panel(layout)
        self.left_panel.setLayout(layout)
        self.splitter.addWidget(self.left_panel)

    def _create_left_panel_header(self, layout):
        header_frame = QFrame()
        header_frame.setFixedHeight(40)
        header_frame.setStyleSheet(
            """
            QFrame {
                background-color: #252526;
                border-bottom: 1px solid #3F3F46;
            }
        """
        )
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 8, 12, 8)
        self.collapse_button = QPushButton("Zwiń")
        self.collapse_button.setFixedSize(40, 24)
        self.collapse_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2D2D30; color: #CCCCCC;
                border: 1px solid #3F3F46; border-radius: 4px;
                font-size: 10px; padding: 1px 4px; text-align: center;
            }
            QPushButton:hover { background-color: #3F3F46; border-color: #007ACC; }
            QPushButton:pressed { background-color: #007ACC; color: #FFFFFF; }
        """
        )
        self.collapse_button.clicked.connect(self._on_collapse_tree_clicked)
        self.expand_button = QPushButton("Rozwiń")
        self.expand_button.setFixedSize(40, 24)
        self.expand_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2D2D30; color: #CCCCCC;
                border: 1px solid #3F3F46; border-radius: 4px;
                font-size: 10px; padding: 1px 4px; text-align: center;
            }
            QPushButton:hover { background-color: #3F3F46; border-color: #007ACC; }
            QPushButton:pressed { background-color: #007ACC; color: #FFFFFF; }
        """
        )
        self.expand_button.clicked.connect(self._on_expand_tree_clicked)
        self.toggle_button = QPushButton("×")
        self.toggle_button.setFixedSize(24, 24)
        self.toggle_button.setToolTip("Zamknij panel")
        self.toggle_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2D2D30; color: #CCCCCC;
                border: 1px solid #3F3F46; border-radius: 12px;
                font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { background-color: #3F3F46; border-color: #007ACC; }
            QPushButton:pressed { background-color: #007ACC; color: #FFFFFF; }
        """
        )
        self.toggle_button.clicked.connect(lambda: self.toggle_panel_requested.emit())
        header_layout.addWidget(self.collapse_button)
        header_layout.addWidget(self.expand_button)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle_button)
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)

    def _create_folder_tree_view(self, layout):
        self.folder_tree_view = CustomFolderTreeView()  # Użyj CustomFolderTreeView
        self.folder_tree_view.setStyleSheet(
            """
            QTreeView {
                background-color: #1E1E1E; color: #CCCCCC;
                border: none; outline: none; font-size: 11px;
            }
            QTreeView::item { padding: 2px; border: none; }
            QTreeView::item:hover { background-color: #3F3F46; }
            QTreeView::item:selected { background-color: #007ACC; color: #FFFFFF; }
            QTreeView::branch { background-color: #1E1E1E; }
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQgNkw4IDZMOSA2TDkgNUw4IDVMNCA1TDMgNUwzIDZMNCA2WiIgZmlsbD0iI0NDQ0NDQyIvPgo8L3N2Zz4K);
            }
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTUgNEw1IDhMNiA4TDYgNEw1IDRaIiBmaWxsPSIjQ0NDQ0NDIi8+Cjwvc3ZnPgo=);
            }
            QScrollBar:vertical {
                background-color: #1E1E1E; width: 12px; border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3F3F46; border-radius: 6px; min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background-color: #52525B; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """
        )
        self.folder_tree_view.setHeaderHidden(True)
        self.folder_tree_view.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.folder_tree_view)
        logger.info("QTreeView created with GalleryTab styling")

    def _create_folder_buttons_panel(self, folder_layout):
        self.buttons_frame = QFrame()
        self.buttons_frame.setFixedHeight(140)
        self.buttons_frame.setStyleSheet(
            """
            QFrame {
                background-color: #252526;
                border-top: 1px solid #3F3F46;
            }
        """
        )
        self.buttons_layout = QGridLayout()
        self.buttons_layout.setContentsMargins(8, 8, 8, 8)
        self.buttons_layout.setSpacing(4)
        self.buttons_frame.setLayout(self.buttons_layout)
        folder_layout.addWidget(self.buttons_frame)
        self.folder_buttons = []
        logger.info("Workspace folders panel created - ETAP 7")

    def update_workspace_folder_buttons(self, folders: list):
        try:
            for button in self.folder_buttons:
                button.deleteLater()
            self.folder_buttons.clear()
            for i, folder_data in enumerate(folders):
                folder_path = folder_data.get("path", "")
                button_text = folder_data.get("name", f"Folder {i + 1}")
                folder_icon = folder_data.get("icon", "")
                folder_color = folder_data.get("color", "#007ACC")
                button = QPushButton(button_text, self)
                button.setFixedHeight(24)
                button.setEnabled(bool(folder_path))
                if folder_path:
                    icon_path = (
                        f"core/resources/img/{folder_icon}" if folder_icon else ""
                    )
                    if icon_path and os.path.exists(icon_path):
                        try:
                            icon = QIcon(icon_path)
                            button.setIcon(icon)
                            button.setIconSize(QSize(12, 12))
                        except Exception as e:
                            logger.debug(f"Icon loading failed for {icon_path}: {e}")
                    button.setStyleSheet(
                        f"""
                        QPushButton {{
                            background-color: #2D2D30; color: #CCCCCC;
                            border: 1px solid #3F3F46; border-radius: 4px;
                            font-size: 10px; padding: 1px 4px; text-align: center;
                        }}
                        QPushButton:hover {{
                            background-color: #3F3F46; border-color: {folder_color};
                        }}
                        QPushButton:pressed {{
                            background-color: {folder_color}; color: #FFFFFF;
                        }}
                        QPushButton:disabled {{
                            background-color: #1E1E1E; color: #666666;
                            border-color: #2D2D30;
                        }}
                        """
                    )
                    button.setToolTip(folder_path)
                    button.clicked.connect(
                        lambda checked, path=folder_path: self.workspace_folder_clicked.emit(
                            path
                        )
                    )
                else:
                    button.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #1E1E1E; color: #666666;
                            border: 1px solid #2D2D30; border-radius: 4px;
                        }
                        QPushButton:disabled {
                            background-color: #1E1E1E; color: #666666;
                            border-color: #2D2D30;
                        }
                        """
                    )
                row, col = divmod(i, 3)
                self.buttons_layout.addWidget(button, row, col)
                self.folder_buttons.append(button)
            logger.info("Workspace folder buttons updated - ETAP 7")
        except Exception as e:
            logger.error(f"Error updating folder buttons: {e}")

    def _create_gallery_panel(self):
        self.gallery_panel = QFrame()
        self.gallery_panel.setFrameStyle(QFrame.Shape.NoFrame)
        self.gallery_panel.setStyleSheet("background-color: #1E1E1E; border: none;")
        gallery_vertical_layout = QVBoxLayout()
        gallery_vertical_layout.setSpacing(0)
        gallery_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self._create_gallery_content_widget()  # Dodaj PRZED _create_scroll_area!
        self._create_scroll_area()
        self._create_control_panel()
        gallery_vertical_layout.addWidget(self.scroll_area)
        gallery_vertical_layout.addWidget(self.control_panel)
        self.gallery_panel.setLayout(gallery_vertical_layout)
        self.splitter.addWidget(self.gallery_panel)

    def _create_scroll_area(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setFrameStyle(QScrollArea.Shape.NoFrame)
        self.scroll_area.setStyleSheet(
            """
            QScrollArea { background-color: #1E1E1E; border: none; }
            QScrollBar:vertical {
                background-color: #2D2D30; width: 12px; border-radius: 6px; margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #424242; border-radius: 6px;
                min-height: 20px; margin: 2px;
            }
            QScrollBar::handle:vertical:hover { background-color: #535353; }
            QScrollBar::handle:vertical:pressed { background-color: #007ACC; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar:horizontal {
                background-color: #2D2D30; height: 12px; border-radius: 6px; margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #424242; border-radius: 6px;
                min-width: 20px; margin: 2px;
            }
            QScrollBar::handle:horizontal:hover { background-color: #535353; }
            QScrollBar::handle:horizontal:pressed { background-color: #007ACC; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
        """
        )
        self.scroll_area.setWidget(self.gallery_container_widget)

    def _create_gallery_content_widget(self):
        self.gallery_content_widget = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_content_widget)
        self.gallery_layout.setSpacing(8)
        self.gallery_layout.setContentsMargins(8, 8, 8, 8)

        self.placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(self.placeholder_widget)
        self.placeholder_label = QLabel(
            "Panel galerii\n(ETAP 9 - Oczekiwanie na wybór folderu)"
        )
        self.placeholder_label.setStyleSheet(
            """
            QLabel {
                color: #CCCCCC; font-size: 14px; padding: 50px;
                background-color: #1E1E1E; font-style: italic;
            }
        """
        )
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.addWidget(self.placeholder_label)

        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.gallery_content_widget)
        self.stacked_layout.addWidget(self.placeholder_widget)

        self.gallery_container_widget = GalleryContainerWidget()
        self.gallery_container_widget.setLayout(self.stacked_layout)
        self.gallery_container_widget.resized.connect(
            self.gallery_viewport_resized.emit
        )

        # Domyślnie pokaż placeholder
        self.stacked_layout.setCurrentIndex(1)

    def _create_gallery_placeholder(self):
        self.placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(self.placeholder_widget)
        self.placeholder_label = QLabel(
            "Panel galerii\n(ETAP 9 - Oczekiwanie na wybór folderu)"
        )
        self.placeholder_label.setStyleSheet(
            """
            QLabel {
                color: #CCCCCC; font-size: 14px; padding: 50px;
                background-color: #1E1E1E; font-style: italic;
            }
        """
        )
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.addWidget(self.placeholder_label)

    def update_gallery_placeholder(self, text: str):
        self.placeholder_label.setText(text)
        if text:
            self.stacked_layout.setCurrentIndex(1)  # Pokaż placeholder
        else:
            self.stacked_layout.setCurrentIndex(0)  # Pokaż siatkę

    def _create_control_panel(self):
        self.control_panel = QFrame()
        self.control_panel.setFixedHeight(50)
        self.control_panel.setStyleSheet(
            "QFrame { background-color: #252526; " "border-top: 1px solid #3F3F46; }"
        )
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(12, 6, 12, 6)
        control_layout.setSpacing(16)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #555555; background-color: #2D2D30;
                text-align: center; color: #FFFFFF; border-radius: 10px;
                font-size: 11px; font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #007ACC, stop:1 #1C97EA);
                border-radius: 9px;
            }
        """
        )
        self.thumbnail_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.thumbnail_size_slider.setFixedHeight(20)
        self.thumbnail_size_slider.setMinimum(50)
        self.thumbnail_size_slider.setMaximum(256)
        self.thumbnail_size_slider.setValue(256)
        self.thumbnail_size_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                border: 1px solid #555555; height: 10px;
                background: #2D2D30; border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1C97EA, stop:1 #007ACC);
                border: 2px solid #FFFFFF; width: 18px;
                margin: -5px 0; border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3BA3F0, stop:1 #1C97EA);
                border: 2px solid #FFD700;
            }
            QSlider::handle:horizontal:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0B7EC8, stop:1 #005A9E);
                border: 2px solid #FF6B6B;
            }
        """
        )
        self.selection_buttons = []
        button_style = """
            QPushButton {
                background-color: #3C3C3C; color: #CCCCCC;
                border: 1px solid #555555; border-radius: 4px;
                font-size: 10px; font-weight: bold; padding: 4px 8px;
                min-width: 120px; max-height: 40px;
            }
            QPushButton:hover {
                background-color: #4A4A4A; border-color: #007ACC; color: #FFFFFF;
            }
            QPushButton:pressed { background-color: #007ACC; color: #FFFFFF; }
            QPushButton:disabled {
                background-color: #2A2A2A; color: #666666; border-color: #3C3C3C;
            }
        """
        self.select_all_button = QPushButton("Zaznacz wszystkie")
        self.select_all_button.setStyleSheet(button_style)
        self.select_all_button.setMinimumWidth(120)
        self.selection_buttons.append(self.select_all_button)
        self.move_selected_button = QPushButton("Przenieś zaznaczone")
        self.move_selected_button.setStyleSheet(button_style)
        self.move_selected_button.setMinimumWidth(120)
        self.move_selected_button.setEnabled(False)
        self.selection_buttons.append(self.move_selected_button)
        self.delete_selected_button = QPushButton("Usuń zaznaczone")
        self.delete_selected_button.setStyleSheet(button_style)
        self.delete_selected_button.setMinimumWidth(120)
        self.delete_selected_button.setEnabled(False)
        self.selection_buttons.append(self.delete_selected_button)
        self.deselect_all_button = QPushButton("Odznacz wszystkie")
        self.deselect_all_button.setStyleSheet(button_style)
        self.deselect_all_button.setMinimumWidth(120)
        self.deselect_all_button.setEnabled(False)
        self.selection_buttons.append(self.deselect_all_button)
        control_layout.addWidget(self.progress_bar, 2)
        for button in self.selection_buttons:
            control_layout.addWidget(button)
        control_layout.addWidget(self.thumbnail_size_slider, 2)
        self.control_panel.setLayout(control_layout)

    def _on_splitter_moved(self, pos, index):
        sizes = self.splitter.sizes()
        self.splitter_moved.emit(sizes)

    def update_splitter_sizes(self, sizes: list):
        self.splitter.setSizes(sizes)
        logger.debug(f"Splitter sizes updated to: {sizes}")

    def update_toggle_button_text(self, is_panel_open: bool):
        if hasattr(self, "toggle_button"):
            self.toggle_button.setText("×" if is_panel_open else "⚬")
            self.toggle_button.setToolTip(
                "Zamknij panel" if is_panel_open else "Otwórz panel"
            )

    def _on_collapse_tree_clicked(self):
        logger.info("Kliknięto przycisk 'Zwiń drzewo' - placeholder")

    def _on_expand_tree_clicked(self):
        logger.info("Kliknięto przycisk 'Rozwiń drzewo' - placeholder")


# ==============================================================================
# CONTROLLER LAYER - Łącznik między Model a View
# ==============================================================================


class AmvController(QObject):
    """Controller dla zakładki AMV - łącznik Model-View"""

    def __init__(self, model: AmvModel, view: AmvView):
        super().__init__()
        self.model = model
        self.view = view
        self.asset_tiles = []  # Lista do przechowywania kafelków
        self._connect_signals()
        self._setup_folder_tree()
        self._setup_asset_grid()
        logger.info("AmvController initialized - ETAP 9")

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

        # --- Sygnały konfiguracji ---
        self.model.config_manager.config_loaded.connect(self._on_config_loaded)
        self.model.state_initialized.connect(self._on_state_initialized)

        # --- Sygnały skanera assetów (ETAP 8) ---
        scanner_model = self.model.asset_scanner_model
        scanner_model.scan_started.connect(self._on_scan_started)
        scanner_model.scan_progress.connect(self._on_scan_progress)
        scanner_model.scan_completed.connect(self._on_scan_completed)
        scanner_model.scan_error.connect(self._on_scan_error)

        # --- Sygnały SelectionModel (ETAP 12) ---
        self.model.selection_model.selection_changed.connect(self._on_selection_changed)

        # --- Sygnały FileOperationsModel (ETAP 13) ---
        self.model.file_operations_model.operation_progress.connect(
            self._on_file_operation_progress
        )
        self.model.file_operations_model.operation_completed.connect(
            self._on_file_operation_completed
        )
        self.model.file_operations_model.operation_error.connect(
            self._on_file_operation_error
        )

        # --- Sygnały DragDropModel (ETAP 14) ---
        self.model.drag_drop_model.drag_started.connect(self._on_drag_drop_started)
        self.model.drag_drop_model.drop_possible.connect(self._on_drag_drop_possible)
        self.model.drag_drop_model.drop_completed.connect(self._on_drag_drop_completed)

    def _setup_folder_tree(self):
        tree_model = self.model.folder_system_model.get_tree_model()
        self.view.folder_tree_view.setModel(tree_model)
        self.view.folder_tree_view.clicked.connect(self._on_tree_item_clicked)
        self.view.folder_tree_view.expanded.connect(self._on_tree_item_expanded)
        self.view.folder_tree_view.collapsed.connect(self._on_tree_item_collapsed)
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
        """Przebudowuje siatkę kafelków na podstawie listy assetów - ETAP 9"""
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

    # --- Metody obsługi skanera (ETAP 8) ---
    def _on_scan_started(self, folder_path: str):
        self.model.asset_grid_model.set_loading_state(True)
        self.model.control_panel_model.set_progress(0)
        self.view.update_gallery_placeholder(f"Skanowanie folderu: {folder_path}...")
        logger.info(f"Scan started in view for: {folder_path}")

    def _on_scan_progress(self, progress: int):
        self.model.control_panel_model.set_progress(progress)

    def _on_scan_completed(self, assets: list, duration: float, operation_type: str):
        self.model.asset_grid_model.set_loading_state(False)
        self.model.control_panel_model.set_progress(100)
        self.model.asset_grid_model.set_assets(assets)

        # Po załadowaniu assetów, zainicjuj przeliczenie kolumn
        current_width = self.view.gallery_container_widget.width()
        current_thumbnail_size = self.model.control_panel_model.get_thumbnail_size()
        self.model.asset_grid_model.request_recalculate_columns(
            current_width, current_thumbnail_size
        )

        if not assets:
            self.view.placeholder_label.show()
            self.view.update_gallery_placeholder(
                "Nie znaleziono assetów w tym folderze."
            )
        else:
            self.view.update_gallery_placeholder("")
        # Usunięto zduplikowany komunikat logu

    def _on_scan_error(self, error_msg: str):
        self.model.asset_grid_model.set_loading_state(False)
        self.model.control_panel_model.set_progress(0)
        self.view.update_gallery_placeholder(f"Błąd skanowania: {error_msg}")
        logger.error(f"Scan error displayed in view: {error_msg}")

    def _on_tile_thumbnail_clicked(self, path: str):
        """Obsługuje kliknięcie w miniaturkę kafelka (otwiera podgląd lub folder)."""
        if not path:
            logger.warning("Brak ścieżki do podglądu/folderu.")
            return

        if os.path.isdir(path):
            # To jest specjalny folder, otwórz w eksploratorze
            self._open_path_in_explorer(path)
        elif os.path.exists(path):
            # To jest plik podglądu, otwórz w PreviewWindow
            # Importujemy PreviewWindow lokalnie, aby uniknąć cyklicznych zależności
            from core.thumbnail_tile import PreviewWindow

            PreviewWindow(path, self.view)  # self.view jako parent
        else:
            logger.warning(f"Plik podglądu nie istnieje: {path}")

    def _on_tile_filename_clicked(self, path: str):
        """Obsługuje kliknięcie w nazwę pliku kafelka (otwiera archiwum lub folder)."""
        if not path:
            logger.warning("Brak ścieżki do archiwum/folderu.")
            return

        if os.path.isdir(path):
            # To jest specjalny folder, otwórz w eksploratorze
            self._open_path_in_explorer(path)
        elif os.path.exists(path):
            # To jest plik archiwum, otwórz w domyślnej aplikacji
            self._open_path_in_default_app(path)
        else:
            logger.warning(f"Plik archiwum nie istnieje: {path}")

    def _open_path_in_explorer(self, path: str):
        """Otwiera ścieżkę w eksploratorze plików systemu operacyjnego."""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
            logger.info(f"Otwarto folder w eksploratorze: {path}")
        except Exception as e:
            logger.error(f"Błąd otwierania folderu {path} w eksploratorze: {e}")

    def _open_path_in_default_app(self, path: str):
        """Otwiera plik w domyślnej aplikacji systemu operacyjnego."""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
            logger.info(f"Otwarto plik w domyślnej aplikacji: {path}")
        except Exception as e:
            logger.error(f"Błąd otwierania pliku {path} w domyślnej aplikacji: {e}")

    def _on_gallery_resized(self, width: int):
        """Obsługuje zmianę rozmiaru widoku galerii."""
        current_thumbnail_size = self.model.control_panel_model.get_thumbnail_size()
        self.model.asset_grid_model.request_recalculate_columns(
            width, current_thumbnail_size
        )

    def _on_thumbnail_size_changed(self, size: int):
        """Obsługuje zmianę rozmiaru miniaturek ze slidera."""
        self.view.thumbnail_size_slider.setValue(size)  # Aktualizuj slider w widoku
        current_width = (
            self.view.gallery_container_widget.width()
        )  # Pobierz aktualną szerokość
        self.model.asset_grid_model.request_recalculate_columns(current_width, size)

    def _on_recalculate_columns_requested(
        self, available_width: int, thumbnail_size: int
    ):
        """Obsługuje żądanie przeliczenia kolumn i przebudowuje siatkę."""
        self._rebuild_asset_grid(self.model.asset_grid_model.get_assets())

    def _on_select_all_clicked(self):
        """Obsługuje kliknięcie przycisku 'Zaznacz wszystkie'."""
        logger.debug("Controller: 'Zaznacz wszystkie' button clicked.")
        # Najpierw zaktualizuj SelectionModel
        for tile in self.asset_tiles:
            if not tile.model.is_special_folder:
                self.model.selection_model.add_selection(tile.asset_id)
        # Następnie wizualnie zaznacz kafelki
        for tile in self.asset_tiles:
            if not tile.model.is_special_folder:
                tile.set_checked(True)  # To tylko wizualna aktualizacja
        logger.info("Selected all assets.")

    def _on_deselect_all_clicked(self):
        """Obsługuje kliknięcie przycisku 'Odznacz wszystkie'."""
        logger.debug("Controller: 'Odznacz wszystkie' button clicked.")
        self.model.selection_model.clear_selection()
        for tile in self.asset_tiles:
            tile.set_checked(False)
        logger.info("Deselected all assets.")

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

        if error_messages:
            QMessageBox.warning(
                self.view, "Operacja zakończona z błędami", "\n".join(error_messages)
            )
        elif success_messages:
            QMessageBox.information(
                self.view,
                "Operacja zakończona pomyślnie",
                f"Pomyślnie wykonano operację na {len(success_messages)} assetach.",
            )

        # Odśwież galerię po operacji
        current_folder = self.model.asset_grid_model.get_current_folder()
        if current_folder:
            self.model.asset_scanner_model.scan_folder(current_folder)

        self.model.selection_model.clear_selection()  # Wyczyść zaznaczenie po operacji

    def _on_file_operation_error(self, error_msg: str):
        self.model.control_panel_model.set_progress(0)
        self.view.update_gallery_placeholder(f"Błąd operacji na plikach: {error_msg}")
        QMessageBox.critical(self.view, "Błąd operacji na plikach", error_msg)

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
        logger.debug(f"Control panel buttons updated. Has selection: {has_selection}")


# ==============================================================================
# GŁÓWNA KLASA ZAKŁADKI AMV
# ==============================================================================


class AmvTab(QWidget):
    """
    Główna klasa zakładki AMV
    Model/View/Controller pattern - ETAP 10 completed
    """

    def __init__(self):
        super().__init__()
        self.model = AmvModel()
        self.view = AmvView()
        self.controller = AmvController(self.model, self.view)
        self.model.initialize_state()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.setLayout(layout)
        logger.info("AmvTab initialized successfully - ETAP 10 completed")


# ==============================================================================
# TESTOWANIE I STANDALONE URUCHOMIENIE
# ==============================================================================

if __name__ == "__main__":
    # Usunięto logging.basicConfig, poziom DEBUG ustawiony globalnie dla loggera amv_tab
    app = QApplication(sys.argv)
    w = AmvTab()
    w.show()
    logger.info("=== ETAP 10 TEST START ===")
    logger.info("Aplikacja uruchomiona. Testowanie zaawansowanych kafelków assetów.")
    logger.info(
        "Proszę kliknąć na folder w drzewie, aby rozpocząć skanowanie i zobaczyć kafelki."
    )
    logger.info("=== ETAP 10 TEST COMPLETED ===")
    sys.exit(app.exec())
