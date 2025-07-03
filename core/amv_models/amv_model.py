"""
AmvModel - Agregujący model dla zakładki AMV
Zarządza ogólnym stanem aplikacji i agreguje wszystkie inne modele.
"""

import logging
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from .asset_grid_model import (
    AssetGridModel,
    FolderSystemModel,
    FolderTreeModel,
    WorkspaceFoldersModel,
)
from .config_manager_model import ConfigManagerMV
from .control_panel_model import ControlPanelModel
from .drag_drop_model import DragDropModel
from .file_operations_model import FileOperationsModel
from .selection_model import SelectionModel

logger = logging.getLogger(__name__)


class AmvModel(QObject):
    """Model dla zakładki AMV - logika biznesowa"""

    config_changed = pyqtSignal(dict)
    thumbnail_size_changed = pyqtSignal(int)
    work_folder_changed = pyqtSignal(str)
    splitter_state_changed = pyqtSignal(bool)
    state_initialized = pyqtSignal()

    def __init__(
        self,
        folder_tree_model: Optional[FolderTreeModel] = None,
        asset_grid_model: Optional[AssetGridModel] = None,
        control_panel_model: Optional[ControlPanelModel] = None,
        config_manager: Optional[ConfigManagerMV] = None,
        folder_system_model: Optional[FolderSystemModel] = None,
        workspace_folders_model: Optional[WorkspaceFoldersModel] = None,
        selection_model: Optional[SelectionModel] = None,
        file_operations_model: Optional[FileOperationsModel] = None,
        drag_drop_model: Optional[DragDropModel] = None,
    ):
        super().__init__()
        self._config = {}
        self._thumbnail_size = 256
        self._work_folder = ""
        self._is_left_panel_collapsed = False
        self._last_splitter_sizes = [200, 800]

        # Wstrzykiwanie zależności z fallback do domyślnych instancji
        self.folder_tree_model = folder_tree_model or FolderTreeModel()
        self.asset_grid_model = asset_grid_model or AssetGridModel()
        self.control_panel_model = control_panel_model or ControlPanelModel()
        self.config_manager = config_manager or ConfigManagerMV()
        self.folder_system_model = folder_system_model or FolderSystemModel()
        self.workspace_folders_model = workspace_folders_model or WorkspaceFoldersModel(
            self.config_manager
        )
        self.selection_model = selection_model or SelectionModel()
        self.file_operations_model = file_operations_model or FileOperationsModel()
        self.drag_drop_model = drag_drop_model or DragDropModel()

        logger.debug("AmvModel initialized with dependency injection - ETAP 15")

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
            logger.debug("Stan aplikacji zainicjalizowany z konfiguracji")
        except Exception as e:
            logger.error(f"Błąd inicjalizacji stanu ({type(e).__name__}): {e}")
            self._config = self.config_manager._get_default_config()
            self.state_initialized.emit()

    def set_config(self, config: dict) -> None:
        self._config = config
        self.config_changed.emit(config)

    def set_thumbnail_size(self, size: int) -> None:
        self._thumbnail_size = size
        self.thumbnail_size_changed.emit(size)

    def set_work_folder(self, folder_path: str) -> None:
        self._work_folder = folder_path
        self.work_folder_changed.emit(folder_path)

    def toggle_left_panel(self) -> None:
        self._is_left_panel_collapsed = not self._is_left_panel_collapsed
        self.splitter_state_changed.emit(not self._is_left_panel_collapsed)
        status = "collapsed" if self._is_left_panel_collapsed else "expanded"
        logger.info(f"Left panel {status}")

    def set_splitter_sizes(self, sizes: list) -> None:
        if not self._is_left_panel_collapsed and len(sizes) == 2 and sizes[0] > 0:
            self._last_splitter_sizes = sizes[:]
            logger.debug(f"Splitter sizes saved: {sizes}")

    def get_splitter_sizes(self) -> list:
        if self._is_left_panel_collapsed:
            return [0, 1000]
        else:
            return self._last_splitter_sizes[:]

    def is_left_panel_collapsed(self) -> bool:
        return self._is_left_panel_collapsed
