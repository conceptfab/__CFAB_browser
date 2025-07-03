import logging
import os

from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QStandardItem, QStandardItemModel

from core.scanner import AssetRepository

logger = logging.getLogger(__name__)


class AssetGridModel(QObject):
    """Model dla siatki assetów - architektura M/V"""

    assets_changed = pyqtSignal(list)
    grid_layout_changed = pyqtSignal(int)
    loading_state_changed = pyqtSignal(bool)
    recalculate_columns_requested = pyqtSignal(int, int)
    scan_started = pyqtSignal(str)
    scan_progress = pyqtSignal(int, int, str)
    scan_completed = pyqtSignal(list, float, str)
    scan_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._assets = []
        self._columns = 4
        self._is_loading = False
        self._current_folder_path = ""
        self._last_available_width = 0
        self._last_thumbnail_size = 0
        self._recalc_timer = QTimer(self)
        self._recalc_timer.setSingleShot(True)
        self._recalc_timer.timeout.connect(self._perform_recalculate_columns)

        logger.debug("AssetGridModel initialized")

    def set_assets(self, assets: list):
        self._assets = assets
        self.assets_changed.emit(self._assets)
        logger.debug(f"Assets set: {len(self._assets)} items")

    def get_assets(self):
        return self._assets

    def set_columns(self, columns: int):
        if self._columns != columns:
            self._columns = max(1, columns)
            self.grid_layout_changed.emit(self._columns)
            logger.debug(f"Grid columns updated to: {self._columns}")

    def get_columns(self):
        return self._columns

    def set_current_folder(self, folder_path: str):
        self._current_folder_path = folder_path
        logger.debug(f"Current folder set: {folder_path}")

    def get_current_folder(self):
        return self._current_folder_path

    def scan_folder(self, folder_path: str):
        """Skanuje folder z raportowaniem postępu"""
        import time

        start_time = time.time()

        try:
            self.scan_started.emit(folder_path)
            logger.info(f"Rozpoczynam skanowanie folderu: {folder_path}")

            if not os.path.exists(folder_path):
                error_msg = f"Folder nie istnieje: {folder_path}"
                logger.error(error_msg)
                self.scan_error.emit(error_msg)
                return

            # Załaduj istniejące assety
            asset_repository = AssetRepository()
            existing_assets = asset_repository.load_existing_assets(folder_path)
            logger.debug(f"Załadowano {len(existing_assets)} istniejących assetów")
            self.scan_progress.emit(0, 100, "Załadowano istniejące assety")

            # Skanuj folder
            def progress_callback(current, total, message):
                if total > 0:
                    # Mapuj postęp skanowania na przedział 10-90%
                    progress_percent = 10 + int((current / total) * 80)
                    self.scan_progress.emit(progress_percent, 100, message)
                else:
                    self.scan_progress.emit(50, 100, message)

            scanned_assets = asset_repository.find_and_create_assets(
                folder_path, progress_callback, use_async_thumbnails=False
            )
            logger.debug(
                f"Przeskanowano folder, znaleziono {len(scanned_assets)} assetów"
            )

            # Połącz assety, usuwając duplikaty
            all_assets = existing_assets.copy()
            existing_names = {asset.get("name", "") for asset in existing_assets}

            for asset in scanned_assets:
                if asset.get("name", "") not in existing_names:
                    all_assets.append(asset)

            # Po zakończeniu skanowania wczytaj assety z plików .asset, aby mieć aktualne pole 'thumbnail'
            all_assets = asset_repository.load_existing_assets(folder_path)

            duration = time.time() - start_time
            logger.debug(f"Skanowanie zakończone, łącznie {len(all_assets)} assetów")
            self.scan_completed.emit(all_assets, duration, "scan_folder")

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Błąd podczas skanowania: {str(e)}"
            logger.error(error_msg)
            self.scan_error.emit(error_msg)

    def request_recalculate_columns(self, available_width: int, thumbnail_size: int):
        """Żąda przeliczenia kolumn z debouncingiem."""
        logger.debug(
            f"AssetGridModel: Request recalculate columns - "
            f"width: {available_width}, thumb_size: {thumbnail_size}"
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
            self.set_columns(calculated_columns)
        self.recalculate_columns_requested.emit(
            self._last_available_width, self._last_thumbnail_size
        )

    def _calculate_columns_cached(
        self, available_width: int, thumbnail_size: int
    ) -> int:
        """Oblicza optymalną liczbę kolumn dla STAŁYCH rozmiarów kafelków."""
        # ZMIANA: STAŁA szerokość kafelka = miniatura + marginesy
        tile_width = thumbnail_size + 16  # STAŁA szerokość kafelka!
        
        # Marginesy layoutu
        layout_margins = 16
        
        # Spacing między kafelkami (8px)
        spacing = 8
        
        # Dostępna szerokość po odjęciu marginesów
        effective_width = available_width - layout_margins
        
        # Oblicz liczbę kolumn - kafelki mają STAŁĄ szerokość
        if (tile_width + spacing) > 0:
            columns_calc = (effective_width + spacing) // (tile_width + spacing)
        else:
            columns_calc = 1
        
        calculated_columns = max(1, columns_calc)
        
        # DODAJ: Logowanie dla debugowania
        logger.debug(
            f"Kalkulacja kolumn: width={available_width}, tile_width={tile_width}, "
            f"columns={calculated_columns}"
        )
        
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
        logger.debug("FolderTreeModel initialized")

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
        logger.debug("FolderSystemModel initialized")

    def get_tree_model(self):
        return self._tree_model

    def set_root_folder(self, folder_path: str):
        if self._root_folder != folder_path:
            logger.debug(
                f"FolderSystemModel set_root_folder - otrzymana ścieżka: {folder_path}"
            )
            # Normalizuj ścieżkę root folder
            normalized_path = os.path.normpath(folder_path)
            logger.debug(
                f"FolderSystemModel set_root_folder - znormalizowana ścieżka: {normalized_path}"
            )

            self._root_folder = normalized_path
            self._load_folder_structure()
            logger.debug(f"Root folder changed: {self._root_folder}")

    def get_root_folder(self):
        return self._root_folder

    def _load_folder_structure(self):
        try:
            self._set_loading_state(True)
            self._tree_model.clear()
            self._tree_model.setHorizontalHeaderLabels(["Folders"])
            logger.debug(f"_load_folder_structure - root_folder: {self._root_folder}")

            if not self._root_folder or not os.path.exists(self._root_folder):
                logger.warning(f"Root folder does not exist: {self._root_folder}")
                self._set_loading_state(False)
                return

            root_item = QStandardItem(os.path.basename(self._root_folder))
            root_item.setData(self._root_folder, Qt.ItemDataRole.UserRole)
            logger.debug(
                f"_load_folder_structure - root_item data: {root_item.data(Qt.ItemDataRole.UserRole)}"
            )
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
            logger.debug(f"_load_subfolders - folder_path: {folder_path}")
            if not os.path.exists(folder_path):
                logger.warning(f"_load_subfolders - folder nie istnieje: {folder_path}")
                return
            folders = []
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                logger.debug(f"_load_subfolders - item: {item}, item_path: {item_path}")
                if os.path.isdir(item_path) and not item.startswith("."):
                    folders.append((item, item_path))
            folders.sort(key=lambda x: x[0].lower())
            for folder_name, f_path in folders:
                logger.debug(
                    f"_load_subfolders - tworzę item dla: {folder_name} -> {f_path}"
                )
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

    def refresh_folder(self, folder_path: str):
        """Odświeża strukturę określonego folderu."""
        try:
            logger.debug(f"Odświeżanie folderu: {folder_path}")

            # Znajdź element w drzewie odpowiadający temu folderowi
            root_item = self._tree_model.item(0, 0)
            if not root_item:
                logger.warning("Brak elementu root w drzewie")
                return

            # Rekurencyjnie znajdź i odśwież folder
            self._refresh_folder_recursive(root_item, folder_path)

            # Emituj sygnał aktualizacji struktury
            self.folder_structure_updated.emit(self._tree_model)
            logger.debug(f"Pomyślnie odświeżono folder: {folder_path}")

        except Exception as e:
            logger.error(f"Błąd podczas odświeżania folderu {folder_path}: {e}")

    def _refresh_folder_recursive(self, item: QStandardItem, target_path: str):
        """Rekurencyjnie odświeża folder w drzewie."""
        try:
            item_path = item.data(Qt.ItemDataRole.UserRole)
            if item_path == target_path:
                # Znaleziono folder do odświeżenia
                logger.debug(f"Znaleziono folder do odświeżenia: {target_path}")

                # Usuń wszystkie dzieci
                item.removeRows(0, item.rowCount())

                # Załaduj ponownie podfoldery
                self._load_subfolders(item, target_path)
                return True

            # Przeszukaj dzieci
            for i in range(item.rowCount()):
                child = item.child(i, 0)
                if child and self._refresh_folder_recursive(child, target_path):
                    return True

            return False

        except Exception as e:
            logger.error(f"Błąd podczas rekurencyjnego odświeżania: {e}")
            return False


class WorkspaceFoldersModel(QObject):
    """Model dla folderów roboczych w architekturze M/V"""

    folders_updated = pyqtSignal(list)

    def __init__(self, config_manager):
        super().__init__()
        self._config_manager = config_manager
        self._folders = []
        # Połącz z sygnałem konfiguracji
        self._config_manager.config_loaded.connect(self._load_folders_from_config)
        logger.debug("WorkspaceFoldersModel initialized")

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
                self._folders.append(
                    {
                        "name": folder_name,
                        "path": folder_path,
                        "icon": folder_icon,
                        "color": folder_color,
                        "exists": folder_exists,
                        "enabled": bool(
                            folder_path and folder_exists
                        ),  # Aktywny tylko jeśli ma ścieżkę i istnieje
                    }
                )

            self.folders_updated.emit(self._folders)
            logger.debug(f"Załadowano {len(self._folders)} folderów roboczych")

        except Exception as e:
            logger.error(f"Błąd podczas ładowania folderów roboczych: {e}")
            self._folders = []
            self.folders_updated.emit(self._folders)

    def get_folders(self):
        """Zwraca listę folderów roboczych."""
        return self._folders
