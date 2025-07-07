import logging
import os

from PyQt6.QtCore import QObject, Qt, pyqtSignal, QTimer
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
        self._show_asset_counts = True  # New option to show asset counts
        self._recursive_asset_counts = True  # New option for recursive asset counting
        self._asset_count_cache = {}  # Cache for asset counts
        self._cache_timestamps = {}   # Timestamps for cache
        logger.debug("FolderSystemModel initialized")

    def get_tree_model(self):
        return self._tree_model

    def set_show_asset_counts(self, show_counts: bool):
        """Sets whether to show asset counts in folders"""
        if self._show_asset_counts != show_counts:
            self._show_asset_counts = show_counts
            # Clear cache when mode changes
            self.clear_asset_count_cache()
            # Refresh folder tree if root folder is set
            if self._root_folder:
                self.set_root_folder(self._root_folder)

    def get_show_asset_counts(self) -> bool:
        """Returns whether asset counts are shown"""
        return self._show_asset_counts

    def set_recursive_asset_counts(self, recursive: bool):
        """Sets whether to sum assets from subfolders recursively"""
        if self._recursive_asset_counts != recursive:
            self._recursive_asset_counts = recursive
            # Clear cache when recursive mode changes
            self.clear_asset_count_cache()
            # Refresh folder tree if root folder is set
            if self._root_folder:
                self.set_root_folder(self._root_folder)

    def get_recursive_asset_counts(self) -> bool:
        """Returns whether assets are summed recursively"""
        return self._recursive_asset_counts

    def _count_assets_in_folder(self, folder_path: str) -> int:
        """Quickly counts assets in a folder (.asset files) - with cache"""
        if not os.path.exists(folder_path):
            return 0
        
        return self._get_cached_asset_count(folder_path)

    def _get_cached_asset_count(self, folder_path: str) -> int:
        """Returns asset count from cache or calculates new if needed"""
        try:
            folder_mtime = os.path.getmtime(folder_path)
            
            # Check if we have cache and if it's current
            if (folder_path in self._asset_count_cache and 
                folder_path in self._cache_timestamps and
                self._cache_timestamps[folder_path] >= folder_mtime):
                return self._asset_count_cache[folder_path]
            
            # Calculate new and save to cache
            if self._recursive_asset_counts:
                count = self._count_assets_recursive(folder_path)
            else:
                count = self._count_assets_direct(folder_path)
                
            self._asset_count_cache[folder_path] = count
            self._cache_timestamps[folder_path] = folder_mtime
            return count
            
        except (PermissionError, OSError) as e:
            logger.debug(f"Cannot get asset count for {folder_path}: {e}")
            return 0

    def _count_assets_direct(self, folder_path: str) -> int:
        """Counts assets directly in folder (without subfolders) - optimized"""
        return self._scan_folder_for_assets(folder_path, recursive=False)

    def _count_assets_recursive(self, folder_path: str, max_depth: int = 50, current_depth: int = 0) -> int:
        """Counts assets recursively in folder and all subfolders - optimized"""
        return self._scan_folder_for_assets(folder_path, recursive=True, max_depth=max_depth, current_depth=current_depth)
    
    def _scan_folder_for_assets(self, folder_path: str, recursive: bool = False, max_depth: int = 50, current_depth: int = 0) -> int:
        """Consolidated asset scanning logic for both direct and recursive counting"""
        if recursive and current_depth >= max_depth:
            logger.warning(f"Max recursion depth reached for {folder_path}")
            return 0
        
        count = 0
        
        try:
            with os.scandir(folder_path) as entries:
                for entry in entries:
                    try:
                        if entry.is_file() and entry.name.endswith(".asset"):
                            count += 1
                        elif (recursive and entry.is_dir() and 
                              not entry.name.startswith(".") and 
                              not self._is_system_folder(entry.name)):
                            # Recursive call only for recursive mode
                            subfolder_count = self._scan_folder_for_assets(
                                entry.path, recursive=True, max_depth=max_depth, current_depth=current_depth + 1
                            )
                            count += subfolder_count
                    except (PermissionError, OSError) as e:
                        logger.debug(f"Cannot access {entry.path}: {e}")
                        continue
        except (PermissionError, OSError) as e:
            logger.debug(f"Cannot scan folder {folder_path}: {e}")
            return 0
        
        return count

    def clear_asset_count_cache(self):
        """Clears asset count cache"""
        self._asset_count_cache.clear()
        self._cache_timestamps.clear()

    def _clear_cache_for_path(self, folder_path: str):
        """Clears cache for specific path and its parents"""
        paths_to_clear = []
        for cached_path in self._asset_count_cache.keys():
            if cached_path.startswith(folder_path) or folder_path.startswith(cached_path):
                paths_to_clear.append(cached_path)
        
        for path in paths_to_clear:
            self._asset_count_cache.pop(path, None)
            self._cache_timestamps.pop(path, None)

    def _format_folder_display_name(self, folder_name: str, folder_path: str) -> str:
        """Formats folder name with asset count (if enabled)"""
        if not self._show_asset_counts:
            return folder_name
        
        asset_count = self._count_assets_in_folder(folder_path)
        if asset_count > 0:
            suffix = "+" if self._recursive_asset_counts else ""
            return f"{folder_name} ({asset_count}{suffix})"
        return folder_name

    def set_root_folder(self, folder_path: str):
        if self._root_folder != folder_path:
            self._root_folder = folder_path
            # Clear cache when root folder changes
            self.clear_asset_count_cache()
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

            root_folder_name = os.path.basename(self._root_folder)
            display_name = self._format_folder_display_name(root_folder_name, self._root_folder)
            
            root_item = QStandardItem(display_name)
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

            for item_name in sorted(os.listdir(folder_path), key=str.lower):
                item_path = os.path.join(folder_path, item_name)
                if os.path.isdir(item_path) and not item_name.startswith(".") and not self._is_system_folder(item_name):
                    display_name = self._format_folder_display_name(item_name, item_path)
                    
                    child_item = QStandardItem(display_name)
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

    def _is_system_folder(self, folder_name: str) -> bool:
        """Checks if folder is a system folder that should be hidden"""
        system_folders = {
            '__pycache__', 'node_modules', '.git', '.svn', '.hg',
            'cache', '.cache', '.tmp', 'temp', '.temp',
            'System Volume Information', '$RECYCLE.BIN',
            '.vscode', '.idea', '.vs'
        }
        return folder_name.lower() in system_folders

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
            # Clear cache for refreshed folder
            self._clear_cache_for_path(folder_path)
            
            found = self._refresh_folder_recursive(
                self._tree_model.invisibleRootItem(), folder_path
            )
            if found:
                self.folder_structure_updated.emit(self._tree_model)
            else:
                # Try to refresh entire model if specific folder not found
                if self._root_folder:
                    self.set_root_folder(self._root_folder)
            logger.debug("Folder refreshed: %s", folder_path)
        except Exception as e:
            logger.error("Error refreshing folder %s: %s", folder_path, str(e))

    def _refresh_folder_recursive(self, item: QStandardItem, target_path: str):
        """Recursively refreshes a folder in the tree"""
        found = False
        
        for i in range(item.rowCount()):
            child_item = item.child(i)
            child_path = child_item.data(Qt.ItemDataRole.UserRole)

            if child_path == target_path:
                # Found the target folder, refresh it
                child_item.removeRows(0, child_item.rowCount())
                if os.path.exists(child_path):
                    self._load_subfolders(child_item, child_path)
                
                # Update folder name with new asset count
                folder_name = os.path.basename(child_path)
                display_name = self._format_folder_display_name(folder_name, child_path)
                child_item.setText(display_name)
                
                found = True
            elif child_path and target_path.startswith(child_path):
                # Target is in a subfolder, continue searching
                if self._refresh_folder_recursive(child_item, target_path):
                    found = True
                    
            # Update asset counts in each folder during refresh
            if child_path:
                folder_name = os.path.basename(child_path)
                display_name = self._format_folder_display_name(folder_name, child_path)
                if child_item.text() != display_name:
                    child_item.setText(display_name)
        
        return found

    def _get_folder_icon(self) -> QIcon:
        """Returns the folder icon"""
        try:
            icon_path = "core/resources/img/folder_icon.png"
            if os.path.exists(icon_path):
                return QIcon(icon_path)
        except Exception as e:
            logger.debug("Error loading folder icon: %s", str(e))
        return QIcon()
