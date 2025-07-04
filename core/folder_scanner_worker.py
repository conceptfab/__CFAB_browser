import logging
import os

from PyQt6.QtCore import QThread, pyqtSignal

from core.rules import FolderClickRules

# from core.scanner import find_and_create_assets  # USUNIĘTO: Skanowanie assetów będzie delegowane

logger = logging.getLogger(__name__)


class FolderStructureScanner(QThread):
    """Worker do skanowania struktury folderów i wykrywania plików asset"""

    progress_updated = pyqtSignal(int)  # Sygnał postępu
    folder_found = pyqtSignal(str, int)  # Sygnał z folderem (ścieżka, poziom)
    assets_folder_found = pyqtSignal(str)  # Sygnał gdy folder zawiera pliki asset
    subfolders_only_found = pyqtSignal(str)  # Sygnał gdy folder ma tylko podfoldery
    scanner_started = pyqtSignal(str)  # Sygnał uruchomienia scannera
    scanner_finished = pyqtSignal(str)  # Sygnał zakończenia scannera
    finished_scanning = pyqtSignal()  # Sygnał zakończenia
    error_occurred = pyqtSignal(str)  # Sygnał błędu

    def __init__(self, folder_path: str):
        super().__init__()
        self.folder_path = folder_path
        self.folders_found = []
        self.total_folders = 0
        self.processed_folders = 0

    def run(self):
        """Główna metoda workera do skanowania folderów"""
        try:
            self.folders_found = []
            self.processed_folders = 0

            if not self.folder_path:
                self.error_occurred.emit("Brak ścieżki do folderu")
                self.finished_scanning.emit()
                return

            logger.info(f"Rozpoczęcie skanowania folderu: {self.folder_path}")

            if not os.path.exists(self.folder_path):
                error_msg = f"Folder nie istnieje: {self.folder_path}"
                logger.warning(error_msg)
                self.error_occurred.emit(error_msg)
                self.finished_scanning.emit()
                return

            # Najpierw policz wszystkie foldery dla postępu
            self._count_total_folders()

            if self.total_folders == 0:
                logger.info("Nie znaleziono podfolderów")
                self.finished_scanning.emit()
                return

            logger.info(f"Znaleziono {self.total_folders} folderów")

            # Skanuj strukturę folderów
            self._scan_folder_structure(self.folder_path, 0)

        except Exception as e:
            error_msg = f"Nieoczekiwany błąd podczas skanowania: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
        finally:
            self.finished_scanning.emit()

    def _count_total_folders(self):
        """Liczy wszystkie foldery dla obliczenia postępu"""
        try:
            self.total_folders = 0
            for root, dirs, files in os.walk(self.folder_path):
                # Filtruj ukryte foldery
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                self.total_folders += len(dirs)
            # Dodaj główny folder
            self.total_folders += 1
        except Exception as e:
            logger.error(f"Błąd liczenia folderów: {e}")
            self.total_folders = 1

    def _scan_folder_structure(self, current_path: str, level: int):
        """Rekurencyjnie skanuje strukturę folderów"""
        try:
            # Wyślij informację o aktualnym folderze
            self.folder_found.emit(current_path, level)
            self.processed_folders += 1

            # Aktualizuj postęp
            if self.total_folders > 0:
                progress = int((self.processed_folders / self.total_folders) * 100)
                self.progress_updated.emit(min(progress, 100))

            # Pobierz listę podfolderów
            try:
                items = os.listdir(current_path)
                subfolders = []

                for item in items:
                    if not item.startswith("."):
                        item_path = os.path.join(current_path, item)
                        if os.path.isdir(item_path):
                            subfolders.append(item_path)

                # Sortuj foldery alfabetycznie
                subfolders.sort()

                # REKURENCYJNIE SKANUJ KAŻDY PODFOLDER
                # DRZEWO MA BYĆ ZAWSZE WIDOCZNE!
                for subfolder_path in subfolders:
                    self._scan_folder_structure(subfolder_path, level + 1)

            except PermissionError:
                logger.warning(f"Brak uprawnień do folderu: {current_path}")
            except Exception as e:
                logger.error(f"Błąd skanowania folderu {current_path}: {e}")

        except Exception as e:
            logger.error(f"Błąd w _scan_folder_structure: {e}")

    def handle_folder_click(self, folder_path: str):
        pass
