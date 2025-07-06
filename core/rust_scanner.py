"""
Wrapper dla Rust Scanner - zapewnia kompatybilność z istniejącym API
"""
import scanner_rust
from typing import List, Dict, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class RustAssetRepository:
    """
    Wrapper dla Rust implementacji AssetRepository
    Zachowuje kompatybilność z istniejącym API Python
    """

    def __init__(self):
        self._rust_scanner = scanner_rust.RustAssetRepository()
        logger.info("Rust scanner zainicjalizowany")

    def find_and_create_assets(
        self,
        folder_path: str,
        progress_callback: Optional[Callable] = None,
        use_async_thumbnails: bool = False
    ) -> List[Dict]:
        """
        Znajdź i utwórz asset-y w określonym folderze

        Args:
            folder_path: Ścieżka do folderu
            progress_callback: Callback postępu
            use_async_thumbnails: Nieużywane w wersji Rust

        Returns:
            Lista asset-ów
        """
        try:
            rust_assets = self._rust_scanner.find_and_create_assets(folder_path, progress_callback)
            # Konwertuj format Rust na format Python
            return self._convert_rust_assets_to_python_format(rust_assets)
        except Exception as e:
            logger.error(f"Błąd Rust scanner: {e}")
            return []

    def load_existing_assets(self, folder_path: str) -> List[Dict]:
        """
        Ładuj istniejące asset-y z folderu

        Args:
            folder_path: Ścieżka do folderu

        Returns:
            Lista asset-ów
        """
        try:
            return self._rust_scanner.load_existing_assets(folder_path)
        except Exception as e:
            logger.error(f"Błąd ładowania asset-ów: {e}")
            return []

    def scan_folder_for_files(self, folder_path: str) -> tuple:
        """
        Skanuj folder w poszukiwaniu plików

        Args:
            folder_path: Ścieżka do folderu

        Returns:
            Tuple (archive_by_name, image_by_name)
        """
        try:
            return self._rust_scanner.scan_folder_for_files(folder_path)
        except Exception as e:
            logger.error(f"Błąd skanowania folderu: {e}")
            return ({}, {})

    # Metody pomocnicze dla kompatybilności
    @staticmethod
    def _validate_folder_path_static(folder_path: str) -> bool:
        """Walidacja ścieżki folderu"""
        import os
        return bool(folder_path and os.path.exists(folder_path) and os.path.isdir(folder_path))

    def create_thumbnail_for_asset(self, asset_path: str, image_path: str) -> Optional[str]:
        """
        Tworzenie thumbnail - pozostaje w Python
        (integracja z istniejącym kodem thumbnail)
        """
        try:
            from core.thumbnail import generate_thumbnail
            result = generate_thumbnail(image_path)
            if result and len(result) == 2:
                return result[0]
            return None
        except Exception as e:
            logger.error(f"Błąd tworzenia thumbnail: {e}")
            return None 