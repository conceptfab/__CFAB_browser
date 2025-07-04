import logging
import os

from PyQt6.QtCore import QObject, pyqtSignal

from core.json_utils import save_to_file

logger = logging.getLogger(__name__)


class AssetTileModel(QObject):
    """Model for a single asset tile"""

    data_changed = pyqtSignal()

    def __init__(self, asset_data: dict, asset_file_path: str = None):
        super().__init__()
        self.data = asset_data
        self.asset_file_path = asset_file_path  # Ścieżka do pliku .asset
        self.is_special_folder = self.data.get("type") == "special_folder"

    def get_name(self) -> str:
        return self.data.get("name", "Unknown")

    def get_thumbnail_path(self) -> str:
        if self.is_special_folder or not self.data.get("thumbnail"):
            return ""
        
        folder_path = self.get_folder_path()
        if not folder_path:
            return ""
        
        cache_dir = os.path.join(folder_path, ".cache")
        return os.path.join(cache_dir, f"{self.get_name()}.thumb")

    def get_size_mb(self) -> float:
        return self.data.get("size_mb", 0.0)

    def get_stars(self) -> int:
        stars = self.data.get("stars")
        return int(stars) if stars is not None else 0

    def set_stars(self, stars: int):
        """Sets the star rating (0-5) and saves to file"""
        if 0 <= stars <= 5:
            self.data["stars"] = stars
            self._save_to_file()  # Save to .asset file
            self.data_changed.emit()
            logger.debug(f"Set {stars} stars for asset: {self.get_name()}")
        else:
            logger.warning(f"Invalid number of stars: {stars}. Allowed: 0-5")

    def _save_to_file(self):
        """Saves asset data to the .asset file"""
        try:
            if not self.asset_file_path:
                logger.error(f"Missing asset_file_path for asset: {self.get_name()}")
                return

            if not os.path.exists(self.asset_file_path):
                logger.error(f"Asset file does not exist: {self.asset_file_path}")
                return

            # Save data to file
            save_to_file(self.data, self.asset_file_path, indent=True)
            logger.debug(f"Saved asset data to file: {self.asset_file_path}")

        except Exception as e:
            logger.error(f"Error saving asset {self.get_name()}: {e}")

    def has_textures_in_archive(self) -> bool:
        return self.data.get("textures_in_the_archive", False)

    def get_folder_path(self) -> str:
        """Returns the path to the asset folder calculated from the file location"""
        if not self.asset_file_path:
            logger.warning(f"Missing asset_file_path for asset: {self.get_name()}")
            return ""
        return os.path.dirname(self.asset_file_path)

    def get_asset_type(self) -> str:
        return self.data.get("type", "asset")

    def get_archive_path(self) -> str:
        if self.is_special_folder:
            return ""
        folder_path = self.get_folder_path()
        archive_filename = self.data.get("archive")
        if folder_path and archive_filename:
            return os.path.join(folder_path, archive_filename)
        return ""

    def get_preview_path(self) -> str:
        if self.is_special_folder:
            return ""
        folder_path = self.get_folder_path()
        preview_filename = self.data.get("preview")
        if folder_path and preview_filename:
            return os.path.join(folder_path, preview_filename)
        return ""

    def get_special_folder_path(self) -> str:
        """Returns the path to a special folder (textures, tex, maps)"""
        if self.is_special_folder:
            return self.data.get("folder_path", "")
        return ""

    def get_asset_data(self) -> dict:
        return self.data
