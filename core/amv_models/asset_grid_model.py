import logging
import os
from typing import Any, List, Optional

from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QStandardItem, QStandardItemModel

from core.scanner import AssetRepository
from core.amv_models.folder_system_model import FolderSystemModel
from core.amv_models.workspace_folders_model import WorkspaceFoldersModel

logger = logging.getLogger(__name__)


class AssetGridModel(QObject):
    """Model for the asset grid - M/V architecture"""

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

    def set_assets(self, assets: Optional[List[Any]]) -> None:
        if assets is None:
            self._assets = []
        else:
            self._assets = assets
        self.assets_changed.emit(self._assets)
        logger.debug("Assets set: %d items", len(self._assets))

    def get_assets(self) -> List[Any]:
        return self._assets if self._assets is not None else []

    def set_columns(self, columns: int):
        if self._columns != columns:
            self._columns = max(1, columns)
            logger.debug("Grid columns updated to: %d", self._columns)

    def get_columns(self):
        return self._columns

    def set_current_folder(self, folder_path: str):
        self._current_folder_path = folder_path
        logger.debug("Current folder set: %s", folder_path)

    def get_current_folder(self):
        return self._current_folder_path

    def scan_folder(self, folder_path: str):
        """RELOADS assets in the folder - refresh = reload!"""
        import time

        start_time = time.time()

        try:
            self.scan_started.emit(folder_path)
            logger.info("WCZYTYWANIE OD NOWA assetów w folderze: %s", folder_path)

            if not os.path.exists(folder_path):
                error_msg = f"Folder does not exist: {folder_path}"
                logger.error(error_msg)
                self.scan_error.emit(error_msg)
                return

            # WCZYTAJ OD NOWA - najpierw skanuj i utwórz assety
            asset_repository = AssetRepository()
            
            # Skanuj folder i utwórz nowe assety
            def progress_callback(current, total, message):
                if total > 0:
                    # Map scan progress to the 10-90% range
                    progress_percent = 10 + int((current / total) * 80)
                    self.scan_progress.emit(progress_percent, 100, message)
                else:
                    self.scan_progress.emit(50, 100, message)

            scanned_assets = asset_repository.find_and_create_assets(
                folder_path, progress_callback, use_async_thumbnails=False
            )
            logger.debug("Skanowanie zakończone, znaleziono %d assetów", len(scanned_assets))

            # WCZYTAJ OD NOWA - teraz załaduj wszystkie assety z plików .asset
            all_assets = asset_repository.load_existing_assets(folder_path)
            logger.debug("WCZYTANO OD NOWA %d assetów z plików .asset", len(all_assets))

            duration = time.time() - start_time
            logger.debug(f"WCZYTYWANIE OD NOWA zakończone, łącznie {len(all_assets)} assetów")
            self.scan_completed.emit(all_assets, duration, "scan_folder")

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Error during scan: {str(e)}"
            logger.error(error_msg)
            self.scan_error.emit(error_msg)

    def request_recalculate_columns(self, available_width: int, thumbnail_size: int):
        """Requests column recalculation with debouncing."""
        logger.debug(
            f"AssetGridModel: Request recalculate columns - "
            f"width: {available_width}, thumb_size: {thumbnail_size}"
        )
        self._last_available_width = available_width
        self._last_thumbnail_size = thumbnail_size
        self._recalc_timer.start(100)  # 100ms delay

    def _perform_recalculate_columns(self):
        """Performs column recalculation and emits the signal."""
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
        """Calculates the optimal number of columns for FIXED tile sizes."""
        # CHANGE: FIXED tile width = thumbnail + margins
        tile_width = thumbnail_size + 16  # FIXED tile width!

        # Layout margins
        layout_margins = 16

        # Spacing between tiles (8px)
        spacing = 8

        # Available width after subtracting margins
        effective_width = available_width - layout_margins

        # Calculate the number of columns - tiles have FIXED width
        if (tile_width + spacing) > 0:
            columns_calc = (effective_width + spacing) // (tile_width + spacing)
        else:
            columns_calc = 1

        calculated_columns = max(1, columns_calc)

        # ADD: Logging for debugging
        logger.debug(
            "Column calculation: width=%d, tile_width=%d, columns=%d",
            available_width,
            tile_width,
            calculated_columns,
        )

        return calculated_columns
