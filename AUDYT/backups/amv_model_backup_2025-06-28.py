"""
AmvModel - Agregujący model dla zakładki AMV
Zarządza ogólnym stanem aplikacji i agreguje wszystkie inne modele.
"""

import logging
from PyQt6.QtCore import QObject, pyqtSignal

from .config_manager_model import ConfigManagerMV
from .control_panel_model import ControlPanelModel
from .selection_model import SelectionModel
from .drag_drop_model import DragDropModel
from .file_operations_model import FileOperationsModel
from .asset_tile_model import AssetTileModel
from .asset_grid_model import (
    AssetGridModel, 
    FolderTreeModel, 
    FolderSystemModel, 
    WorkspaceFoldersModel, 
    AssetScannerModelMV
)

logger = logging.getLogger(__name__)


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
        
        # Inicjalizacja wszystkich modeli
        self.folder_tree_model = FolderTreeModel()
        self.asset_grid_model = AssetGridModel()
        self.control_panel_model = ControlPanelModel()
        self.config_manager = ConfigManagerMV()
        self.folder_system_model = FolderSystemModel()
        self.workspace_folders_model = WorkspaceFoldersModel(self.config_manager)
        self.asset_scanner_model = AssetScannerModelMV()
        self.selection_model = SelectionModel()
        self.file_operations_model = FileOperationsModel()
        self.drag_drop_model = DragDropModel()
        
        logger.info("AmvModel initialized - ETAP 13")

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