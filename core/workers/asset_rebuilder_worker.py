"""
AssetRebuilderWorker - Worker dla przebudowy assetów w folderze
Przeniesiony z AmvController dla lepszej separacji odpowiedzialności.
"""

import logging
import os

from PyQt6.QtCore import QThread, pyqtSignal

from ..scanner import AssetRepository

logger = logging.getLogger(__name__)


class AssetRebuilderWorker(QThread):
    """Worker dla przebudowy assetów w folderze"""

    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(str)  # message
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self, folder_path: str):
        super().__init__()
        self.folder_path = folder_path

    def run(self):
        """Główna metoda przebudowy assetów"""
        try:
            if not self.folder_path or not os.path.exists(self.folder_path):
                error_msg = f"Nieprawidłowy folder: {self.folder_path}"
                self.error_occurred.emit(error_msg)
                return

            logger.info(
                "Rozpoczęcie przebudowy assetów w folderze: %s", self.folder_path
            )

            # Krok 1: Usuwanie plików .asset
            self.progress_updated.emit(0, 100, "Usuwanie starych plików .asset...")
            self._remove_asset_files()

            # Krok 2: Usuwanie folderu .cache
            self.progress_updated.emit(20, 100, "Usuwanie folderu .cache...")
            self._remove_cache_folder()

            # Krok 3: Uruchamianie scanner.py
            self.progress_updated.emit(
                40, 100, "Skanowanie i tworzenie nowych assetów..."
            )
            self._run_scanner()

            self.progress_updated.emit(100, 100, "Przebudowa zakończona!")
            self.finished.emit(
                f"Pomyślnie przebudowano assety w folderze: {self.folder_path}"
            )

        except Exception as e:
            error_msg = f"Błąd podczas przebudowy assetów: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def _remove_asset_files(self):
        """Usuwa wszystkie pliki .asset z folderu"""
        try:
            asset_files = [
                f for f in os.listdir(self.folder_path) if f.endswith(".asset")
            ]
            for asset_file in asset_files:
                file_path = os.path.join(self.folder_path, asset_file)
                os.remove(file_path)
                logger.debug("Usunięto plik asset: %s", asset_file)
            logger.info("Usunięto %d plików .asset", len(asset_files))
        except Exception as e:
            logger.error(f"Błąd usuwania plików .asset: {e}")
            raise

    def _remove_cache_folder(self):
        """BEZWZGLĘDNIE usuwa folder .cache - folder cache do kurwy, nie ważne co zawiera"""
        try:
            import shutil

            cache_folder = os.path.join(self.folder_path, ".cache")

            # BEZWZGLĘDNIE usuń folder .cache - nie ważne co zawiera
            if os.path.exists(cache_folder):
                shutil.rmtree(cache_folder, ignore_errors=True)
                logger.info("BEZWZGLĘDNIE usunięto folder .cache: %s", cache_folder)
            else:
                logger.info("Folder .cache nie istniał - i tak go usunęliśmy")
        except Exception as e:
            logger.error(f"Błąd usuwania folderu .cache: {e}")
            # Nawet jeśli błąd - kontynuuj, folder cache ma być usunięty
            raise

    def _run_scanner(self):
        """Uruchamia scanner.py w folderze"""
        try:

            def progress_callback(current, total, message):
                if total > 0:
                    # Mapuj postęp skanowania na przedział 40-100%
                    scanner_progress = int(40 + (current / total) * 60)
                    self.progress_updated.emit(scanner_progress, 100, message)
                else:
                    self.progress_updated.emit(100, 100, message)

            asset_repository = AssetRepository()
            created_assets = asset_repository.find_and_create_assets(
                self.folder_path, progress_callback
            )
            logger.info("Scanner utworzył %d nowych assetów", len(created_assets))

        except Exception as e:
            logger.error(f"Błąd uruchamiania scanner-a: {e}")
            raise
