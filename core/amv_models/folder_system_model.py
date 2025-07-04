import logging
import os


from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QStandardItem, QStandardItemModel

logger = logging.getLogger(__name__)


class FolderSystemModel(QObject):
    """Model for the folder system in M/V architecture"""

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
            self._root_folder = folder_path
            self._tree_model.clear()
            self._tree_model.setHorizontalHeaderLabels(["Folders"])
            self._set_loading_state(True)
            self._load_folder_structure()
            logger.debug("Root folder set: %s", folder_path)

    def get_root_folder(self):
        return self._root_folder

    def _load_folder_structure(self):
        """Loads the folder structure into the tree model"""
        try:
            if not self._root_folder or not os.path.exists(self._root_folder):
                self._set_loading_state(False)
                return

            root_item = QStandardItem(os.path.basename(self._root_folder))
            root_item.setData(self._root_folder, Qt.ItemDataRole.UserRole)
            root_item.setIcon(self._get_folder_icon())
            root_item.setEditable(False)
            self._tree_model.appendRow(root_item)

            # Load subfolders
            self._load_subfolders(root_item, self._root_folder)
            self.folder_structure_updated.emit(self._tree_model)
            self._set_loading_state(False)

        except Exception as e:
            logger.error("Error loading folder structure: %s", str(e))
            self._set_loading_state(False)

    def _load_subfolders(self, parent_item, folder_path):
        """Recursively loads subfolders"""
        try:
            if not os.path.exists(folder_path):
                return

            for item_name in sorted(os.listdir(folder_path)):
                item_path = os.path.join(folder_path, item_name)
                if os.path.isdir(item_path):
                    child_item = QStandardItem(item_name)
                    child_item.setData(item_path, Qt.ItemDataRole.UserRole)
                    child_item.setIcon(self._get_folder_icon())
                    child_item.setEditable(False)
                    parent_item.appendRow(child_item)

                    # Recursively load subfolders
                    self._load_subfolders(child_item, item_path)

        except PermissionError:
            logger.warning("Permission denied accessing folder: %s", folder_path)
        except Exception as e:
            logger.error("Error loading subfolders: %s", str(e))

    def expand_folder(self, item: QStandardItem):
        """Expands a folder in the tree"""
        try:
            folder_path = item.data(Qt.ItemDataRole.UserRole)
            if folder_path:
                self.folder_expanded.emit(folder_path)
                logger.debug("Folder expanded: %s", folder_path)
        except Exception as e:
            logger.error("Error expanding folder: %s", str(e))

    def collapse_folder(self, folder_path: str):
        """Collapses a folder in the tree"""
        self.folder_collapsed.emit(folder_path)
        logger.debug("Folder collapsed: %s", folder_path)

    def _set_loading_state(self, is_loading: bool):
        """Sets the loading state"""
        self._is_loading = is_loading
        self.loading_state_changed.emit(is_loading)

    def is_loading(self):
        """Returns the current loading state"""
        return self._is_loading

    def on_folder_clicked(self, folder_path: str):
        """Handles folder click events"""
        self.folder_clicked.emit(folder_path)
        logger.debug("Folder clicked: %s", folder_path)

    def refresh_folder(self, folder_path: str):
        """Refreshes a specific folder in the tree"""
        try:
            self._refresh_folder_recursive(
                self._tree_model.invisibleRootItem(), folder_path
            )
            self.folder_structure_updated.emit(self._tree_model)
            logger.debug("Folder refreshed: %s", folder_path)
        except Exception as e:
            logger.error("Error refreshing folder: %s", str(e))

    def _refresh_folder_recursive(self, item: QStandardItem, target_path: str):
        """Recursively refreshes a folder in the tree"""
        for i in range(item.rowCount()):
            child_item = item.child(i)
            child_path = child_item.data(Qt.ItemDataRole.UserRole)

            if child_path == target_path:
                # Found the target folder, refresh it
                child_item.removeRows(0, child_item.rowCount())
                if os.path.exists(child_path):
                    self._load_subfolders(child_item, child_path)
                return True
            elif child_path and target_path.startswith(child_path):
                # Target is in a subfolder, continue searching
                if self._refresh_folder_recursive(child_item, target_path):
                    return True
        return False

    def _get_folder_icon(self) -> QIcon:
        """Returns the folder icon"""
        try:
            icon_path = "core/resources/img/folder.png"
            if os.path.exists(icon_path):
                return QIcon(icon_path)
        except Exception as e:
            logger.debug("Error loading folder icon: %s", str(e))
        return QIcon()
