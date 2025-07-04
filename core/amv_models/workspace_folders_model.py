import logging
import os
from typing import Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class WorkspaceFoldersModel(QObject):
    """Model dla folderów roboczych w architekturze M/V"""

    folders_updated = pyqtSignal(list)

    def __init__(self, config_manager):
        super().__init__()
        self._config_manager = config_manager
        self._folders = []
        self.load_folders()
        logger.debug("WorkspaceFoldersModel initialized")

    def load_folders(self):
        """Loads workspace folders from configuration"""
        try:
            config = self._config_manager.get_config()
            self._load_folders_from_config(config)
            logger.debug("Workspace folders loaded: %d items", len(self._folders))
        except Exception as e:
            logger.error("Error loading workspace folders: %s", str(e))
            self._folders = []

    def _load_folders_from_config(self, config: dict):
        """Loads folders from configuration data"""
        try:
            workspace_folders = config.get("workspace_folders", [])
            self._folders = []

            for folder_data in workspace_folders:
                if isinstance(folder_data, dict):
                    folder_info = {
                        "name": folder_data.get("name", "Unknown Folder"),
                        "path": folder_data.get("path", ""),
                        "icon": folder_data.get("icon", "workfolder_icon.png"),
                        "color": folder_data.get("color", "#717bbc"),
                        "enabled": folder_data.get("enabled", True),
                    }

                    # Validate path
                    if folder_info["path"] and os.path.exists(folder_info["path"]):
                        self._folders.append(folder_info)
                    else:
                        logger.warning(
                            "Workspace folder path does not exist: %s",
                            folder_info["path"],
                        )
                        # Add disabled folder for UI consistency
                        folder_info["enabled"] = False
                        self._folders.append(folder_info)

            # Sort folders by name
            self._folders.sort(key=lambda x: x["name"].lower())

            # Emit signal
            self.folders_updated.emit(self._folders)

        except Exception as e:
            logger.error("Error processing workspace folders config: %s", str(e))
            self._folders = []

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
