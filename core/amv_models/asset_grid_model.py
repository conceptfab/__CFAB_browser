import logging
import os
import time
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
            logger.info("RELOADING assets in folder: %s", folder_path)

            if not os.path.exists(folder_path):
                error_msg = f"Folder does not exist: {folder_path}"
                logger.error(error_msg)
                self.scan_error.emit(error_msg)
                return

            # Start - initialization (0-10%)
            self.scan_progress.emit(0, 100, "Initializing scan...")

            # RELOAD - first scan and create assets
            asset_repository = AssetRepository()
            
            # Scan folder and create new assets (10-80%)
            def progress_callback(current, total, message):
                if total > 0:
                    # Map scanning progress to the 10-80% range
                    progress_percent = 10 + int((current / total) * 70)
                    self.scan_progress.emit(progress_percent, 100, f"Scanning: {message}")
                else:
                    self.scan_progress.emit(40, 100, f"Scanning: {message}")

            self.scan_progress.emit(10, 100, "Starting file scan...")
            
            scanned_assets = asset_repository.find_and_create_assets(
                folder_path, progress_callback
            )
            logger.debug("Scan finished, found %d assets", len(scanned_assets))

            # Loading assets (80-95%)
            self.scan_progress.emit(80, 100, "Loading assets from files...")
            
            # RELOAD - now load all assets from .asset files
            all_assets = asset_repository.load_existing_assets(folder_path)
            logger.debug("RELOADED %d assets from .asset files", len(all_assets))

            # Finalizing (95-100%)
            self.scan_progress.emit(95, 100, "Finalizing...")
            
            duration = time.time() - start_time
            logger.debug(f"RELOADING finished, total {len(all_assets)} assets")
            
            self.scan_progress.emit(100, 100, "Finished!")
            self.scan_completed.emit(all_assets, duration, "scan_folder")

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Error during scan: {str(e)}"
            logger.error(error_msg)
            self.scan_error.emit(error_msg)

    _RECALC_DEBOUNCE_MS = 100
    _RECALC_MAX_WAIT_MS = 300

    def request_recalculate_columns(self, available_width: int, thumbnail_size: int):
        """Debounced recalculation with a hard max-wait ceiling.

        Pure debounce restarts on every call, so a continuous resize drag
        blocks recalculation until the user stops moving. The max-wait
        bound guarantees the grid reflows at least every
        `_RECALC_MAX_WAIT_MS` ms even under sustained input.
        """
        logger.debug(
            f"AssetGridModel: Request recalculate columns - "
            f"width: {available_width}, thumb_size: {thumbnail_size}"
        )
        self._last_available_width = available_width
        self._last_thumbnail_size = thumbnail_size

        now = time.monotonic()
        pending_since = getattr(self, "_recalc_pending_since", None)
        if pending_since is None:
            self._recalc_pending_since = now
            self._recalc_timer.start(self._RECALC_DEBOUNCE_MS)
            return

        elapsed_ms = (now - pending_since) * 1000.0
        if elapsed_ms >= self._RECALC_MAX_WAIT_MS:
            self._recalc_timer.stop()
            self._perform_recalculate_columns()
        else:
            remaining = self._RECALC_MAX_WAIT_MS - elapsed_ms
            self._recalc_timer.start(min(self._RECALC_DEBOUNCE_MS, int(remaining)))

    def _perform_recalculate_columns(self):
        """Performs column recalculation and emits the signal."""
        self._recalc_pending_since = None
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
        # Tile outer width is clamped by the filename row (icon+name+size = 256 px)
        # in AssetTileView._calculate_tile_dimensions. Using thumbnail_size alone
        # here under-estimates tile width and lets the grid expand past the
        # viewport, which then feeds back via gallery_container_widget.width()
        # into the next recalc and snowballs columns into a single row.
        MIN_TILE_WIDTH = 256
        tile_width = max(thumbnail_size, MIN_TILE_WIDTH)

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
