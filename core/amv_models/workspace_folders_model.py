import logging
import os
from typing import Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class WorkspaceFoldersModel(QObject):
    """Model for workspace folders in M/V architecture"""

    folders_updated = pyqtSignal(list)

    def __init__(self, config_manager):
        super().__init__()
        self._config_manager = config_manager
        self._folders = []
        self.load_folders()
        # Don't emit signal here - will be called after signals are connected
        # self.folders_updated.emit(self._folders) 
        logger.debug("WorkspaceFoldersModel initialized")

    def load_folders(self, emit_signal=False):
        """Loads workspace folders from configuration"""
        try:
            config = self._config_manager.get_config()
            self._load_folders_from_config(config, emit_signal=emit_signal)
            logger.debug("Workspace folders loaded: %d items", len(self._folders))
        except Exception as e:
            logger.error("Error loading workspace folders: %s", str(e))
            self._folders = []

    def _load_folders_from_config(self, config: dict, emit_signal=False):
        """Loads folders from configuration and optionally emits update signal."""
        try:
            self._folders = []

            # Iterate through work_folder1 to work_folder9
            for i in range(1, 10):
                folder_key = f"work_folder{i}"
                folder_config = config.get(folder_key, {})

                if not isinstance(folder_config, dict):
                    continue

                folder_name = folder_config.get("name", f"Folder {i}")
                folder_path = folder_config.get("path", "")
                folder_icon = folder_config.get("icon", "")
                folder_color = folder_config.get("color", "#007ACC")

                # Check if the folder exists (only if it has a path)
                folder_exists = os.path.exists(folder_path) if folder_path else False
                if folder_path and not folder_exists:
                    logger.warning(f"Working folder does not exist: {folder_path}")

                # Set a default icon if none is specified
                if not folder_icon:
                    if folder_name.lower().find("texture") != -1:
                        folder_icon = "texture.png"
                    else:
                        folder_icon = "workfolder_icon.png"

                # Add all folders, even empty ones
                self._folders.append(
                    {
                        "name": folder_name,
                        "path": folder_path,
                        "icon": folder_icon,
                        "color": folder_color,
                        "exists": folder_exists,
                        "enabled": bool(
                            folder_path and folder_exists
                        ),  # Active only if it has a path and exists
                    }
                )

            # ALPHABETICAL SORTING - active first, then inactive
            # Sort active folders alphabetically
            active_folders = [f for f in self._folders if f["enabled"] and f["name"]]
            active_folders.sort(key=lambda x: x["name"].lower())
            
            # Sort inactive folders alphabetically
            inactive_folders = [f for f in self._folders if not f["enabled"] and f["name"]]
            inactive_folders.sort(key=lambda x: x["name"].lower())
            
            # Empty folders at the end
            empty_folders = [f for f in self._folders if not f["name"]]
            
            # Combine everything in order: active, inactive, empty
            self._folders = active_folders + inactive_folders + empty_folders

            if emit_signal:
                self.folders_updated.emit(self._folders)
                logger.info(f"🔧 DEBUG: folders_updated signal emitted with {len(self._folders)} folders")
            logger.debug(f"Loaded {len(self._folders)} working folders (alphabetical sorting)")

        except Exception as e:
            logger.error(f"Error while loading working folders: {e}")
            self._folders = []
            if emit_signal:
                self.folders_updated.emit(self._folders)

    def get_folders(self):
        """Returns the list of workspace folders"""
        return self._folders

    def add_folder(
        self,
        name: str,
        path: str,
        icon: str = "workfolder_icon.png",
        color: str = "#717bbc",
    ) -> bool:
        """Adds a new workspace folder"""
        try:
            if not path or not os.path.exists(path):
                logger.warning("Cannot add folder - path does not exist: %s", path)
                return False

            # Check if folder already exists
            for folder in self._folders:
                if folder["path"] == path:
                    logger.warning("Folder already exists: %s", path)
                    return False

            folder_info = {
                "name": name,
                "path": path,
                "icon": icon,
                "color": color,
                "enabled": True,
            }

            self._folders.append(folder_info)
            self._folders.sort(key=lambda x: x["name"].lower())

            # Update configuration
            self._update_config()

            # Emit signal
            self.folders_updated.emit(self._folders)

            logger.info("Workspace folder added: %s (%s)", name, path)
            return True

        except Exception as e:
            logger.error("Error adding workspace folder: %s", str(e))
            return False

    def remove_folder(self, path: str) -> bool:
        """Removes a workspace folder"""
        try:
            for i, folder in enumerate(self._folders):
                if folder["path"] == path:
                    removed_folder = self._folders.pop(i)

                    # Update configuration
                    self._update_config()

                    # Emit signal
                    self.folders_updated.emit(self._folders)

                    logger.info("Workspace folder removed: %s", removed_folder["name"])
                    return True

            logger.warning("Folder not found for removal: %s", path)
            return False

        except Exception as e:
            logger.error("Error removing workspace folder: %s", str(e))
            return False

    def update_folder(
        self, old_path: str, name: str, path: str, icon: str = None, color: str = None
    ) -> bool:
        """Updates an existing workspace folder"""
        try:
            for folder in self._folders:
                if folder["path"] == old_path:
                    folder["name"] = name
                    folder["path"] = path

                    if icon is not None:
                        folder["icon"] = icon
                    if color is not None:
                        folder["color"] = color

                    folder["enabled"] = os.path.exists(path)

                    # Sort folders
                    self._folders.sort(key=lambda x: x["name"].lower())

                    # Update configuration
                    self._update_config()

                    # Emit signal
                    self.folders_updated.emit(self._folders)

                    logger.info("Workspace folder updated: %s", name)
                    return True

            logger.warning("Folder not found for update: %s", old_path)
            return False

        except Exception as e:
            logger.error("Error updating workspace folder: %s", str(e))
            return False

    def _update_config(self):
        """Updates the configuration with current folders"""
        try:
            config = self._config_manager.get_config()
            config["workspace_folders"] = self._folders
            self._config_manager.save_config(config)
            logger.debug("Configuration updated with workspace folders")
        except Exception as e:
            logger.error("Error updating configuration: %s", str(e))

    def get_folder_by_path(self, path: str) -> Optional[Dict]:
        """Returns folder information by path"""
        for folder in self._folders:
            if folder["path"] == path:
                return folder
        return None

    def get_enabled_folders(self) -> List[Dict]:
        """Returns only enabled folders"""
        return [folder for folder in self._folders if folder["enabled"]]

    def init_after_setup(self):
        """Called after signals are connected to emit initial data"""
        logger.info(f"🔧 DEBUG: init_after_setup() - emitting folders_updated with {len(self._folders)} folders")
        self.folders_updated.emit(self._folders)
