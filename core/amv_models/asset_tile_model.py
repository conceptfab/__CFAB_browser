import logging
import os
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class AssetTileModel(QObject):
    """Model dla pojedynczego kafelka assetu"""

    data_changed = pyqtSignal()

    def __init__(self, asset_data: dict):
        super().__init__()
        self.data = asset_data
        self.is_special_folder = self.data.get("type") == "special_folder"

    def get_name(self) -> str:
        return self.data.get("name", "Unknown")

    def get_thumbnail_path(self) -> str:
        if self.is_special_folder:
            return ""  # Specjalne foldery nie mają miniaturek w .cache
        if not self.data.get("thumbnail"):
            return ""
        # Zakładamy, że asset_data zawiera 'folder_path' dla assetów
        folder_path = self.data.get("folder_path")
        if not folder_path:
            logger.warning(f"Brak 'folder_path' w danych assetu: {self.get_name()}")
            return ""
        cache_dir = os.path.join(folder_path, ".cache")
        return os.path.join(cache_dir, f"{self.get_name()}.thumb")

    def get_size_mb(self) -> float:
        return self.data.get("size_mb", 0.0)

    def get_stars(self) -> int:
        stars = self.data.get("stars")
        return int(stars) if stars is not None else 0

    def has_textures_in_archive(self) -> bool:
        return self.data.get("textures_in_the_archive", False)

    def get_folder_path(self) -> str:
        return self.data.get("folder_path", "")

    def get_asset_type(self) -> str:
        return self.data.get("type", "asset")

    def get_archive_path(self) -> str:
        if self.is_special_folder:
            return ""
        folder_path = self.data.get("folder_path")
        archive_filename = self.data.get("archive")
        if folder_path and archive_filename:
            return os.path.join(folder_path, archive_filename)
        return ""

    def get_preview_path(self) -> str:
        if self.is_special_folder:
            return ""
        folder_path = self.data.get("folder_path")
        preview_filename = self.data.get("preview")
        if folder_path and preview_filename:
            return os.path.join(folder_path, preview_filename)
        return ""

    def get_asset_data(self) -> dict:
        return self.data 