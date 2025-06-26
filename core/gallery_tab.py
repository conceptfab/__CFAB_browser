import json
import logging
import os
import subprocess
import sys
import shutil
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import (
    Qt,
    QThread,
    QTimer,
    pyqtSignal,
    QDir,
    QModelIndex,
    QPoint,
)
from PyQt6.QtGui import QPixmap, QDrag, QDragEnterEvent, QDropEvent, QDragMoveEvent, QStandardItemModel, QStandardItem, QBrush, QColor, QPen, QAction
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSlider,
    QSplitter,
    QWidget,
    QTreeView,
    QMessageBox,
    QVBoxLayout,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QStyle,
    QMenu,
)

from core.folder_scanner_worker import FolderStructureScanner
from core.thumbnail_tile import PreviewWindow, ThumbnailTile, FolderTile

# Dodanie loggera dla modułu
logger = logging.getLogger(__name__)


class ConfigManager:
    """Menedżer konfiguracji z cache'owaniem"""

    _instance = None
    _config_cache = None
    _config_timestamp = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_config(self, force_reload=False):
        """
        Pobiera konfigurację z cache'owaniem

        Args:
            force_reload (bool): Wymusza ponowne ładowanie konfiguracji

        Returns:
            dict: Konfiguracja aplikacji lub domyślna konfiguracja
        """
        config_path = Path(__file__).parent.parent / "config.json"

        try:
            # Sprawdź czy cache jest aktualny
            if not force_reload and self._is_cache_valid(config_path):
                return self._config_cache

            # Załaduj konfigurację
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Walidacja podstawowej struktury
            if not isinstance(config, dict):
                raise ValueError("Configuration must be a dictionary")

            # Zapisz do cache
            self._config_cache = config
            self._config_timestamp = config_path.stat().st_mtime

            logger.debug("Konfiguracja załadowana pomyślnie")
            return config

        except FileNotFoundError:
            logger.warning(f"Plik konfiguracji nie istnieje: {config_path}")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Niepoprawny JSON w konfiguracji: {e}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Błąd ładowania konfiguracji: {e}")
            return self._get_default_config()

    def _is_cache_valid(self, config_path):
        """Sprawdza czy cache konfiguracji jest aktualny"""
        if self._config_cache is None or self._config_timestamp is None:
            return False

        try:
            current_timestamp = config_path.stat().st_mtime
            return current_timestamp == self._config_timestamp
        except:
            return False

    def _get_default_config(self):
        """Zwraca domyślną konfigurację"""
        return {
            "thumbnail": 256,
            "work_folder1": {"path": "", "name": "", "icon": "", "color": ""},
            "logger_level": "INFO",
            "use_styles": True,
        }

    def get_thumbnail_size(self):
        """Pobiera rozmiar thumbnail z konfiguracji"""
        config = self.get_config()
        return config.get("thumbnail", 256)

    def get_work_folder_path(self):
        """Pobiera ścieżkę work_folder1 z konfiguracji"""
        config = self.get_config()
        work_folder1 = config.get("work_folder1", {})
        return work_folder1.get("path", "")


class GridManager:
    """Menedżer siatki kafelków z debouncing i optymalizacjami"""

    def __init__(self, gallery_widget, gallery_layout, scroll_area):
        self.gallery_widget = gallery_widget
        self.gallery_layout = gallery_layout
        self.scroll_area = scroll_area
        self.current_tiles = []
        self.tile_spacing = 10
        self.current_folder_path = ""  # Dodane: ścieżka do aktualnego folderu
        self.selection_changed_callback = None  # Callback do aktualizacji przycisków

        # Debouncing timer
        self.grid_recreation_timer = QTimer()
        self.grid_recreation_timer.setSingleShot(True)
        self.grid_recreation_timer.timeout.connect(self._delayed_grid_recreation)
        self.grid_recreation_delay = 100  # 100ms delay

        # Cache dla column calculation
        self._last_width = 0
        self._last_tile_size = 0
        self._cached_columns = 4

    def request_grid_recreation(self, assets, thumbnail_size, folder_path=""):
        """
        Żąda recreacji grid z debouncing

        Args:
            assets (list): Lista assetów
            thumbnail_size (int): Rozmiar kafelków
            folder_path (str): Ścieżka do folderu z assetami
        """
        self.pending_assets = assets
        self.pending_thumbnail_size = thumbnail_size
        self.current_folder_path = folder_path  # Zapamiętaj ścieżkę

        # Restart timer (debouncing)
        self.grid_recreation_timer.stop()
        self.grid_recreation_timer.start(self.grid_recreation_delay)

    def _delayed_grid_recreation(self):
        """Wykonuje recreację grid po delay"""
        try:
            self._create_thumbnail_grid(
                self.pending_assets, self.pending_thumbnail_size
            )
        except Exception as e:
            logger.error(f"Błąd podczas recreacji grid: {e}")

    def _create_thumbnail_grid(self, assets, thumbnail_size):
        """Tworzy kafelki na podstawie wczytanych asset-ów"""
        try:
            # Wyczyść istniejące kafelki
            self._clear_gallery_safe()

            if not assets:
                self._create_no_assets_message()
                return

            # Oblicz ilość kolumn z cache'owaniem
            columns = self._calculate_columns_cached(thumbnail_size)

            # Tworzenie kafelków
            for i, asset in enumerate(assets):
                row = i // columns
                col = i % columns

                # Sprawdź czy to specjalny folder
                if asset.get("type") == "special_folder":
                    tile = self._create_folder_tile_safe(asset, thumbnail_size)
                else:
                    tile = self._create_asset_tile_safe(
                        asset, i + 1, len(assets), thumbnail_size
                    )
                
                if tile:
                    self.gallery_layout.addWidget(tile, row, col)
                    self.current_tiles.append(tile)

            logger.debug(f"Grid utworzony: {len(assets)} assetów w {columns} kolumnach")

        except Exception as e:
            logger.error(f"Błąd tworzenia grid: {e}")
            self._create_error_message(str(e))

    def _clear_gallery_safe(self):
        """Bezpiecznie czyści wszystkie widgety z galerii"""
        try:
            # Najpierw usuń z listy
            for tile in self.current_tiles:
                if tile and not tile.isHidden():
                    tile.hide()  # Ukryj przed usunięciem
                    tile.deleteLater()

            self.current_tiles.clear()

            # Usuń wszystkie widgety z layout-u
            while self.gallery_layout.count():
                item = self.gallery_layout.takeAt(0)
                if item and item.widget():
                    widget = item.widget()
                    widget.hide()
                    widget.deleteLater()

            # Force garbage collection hint
            import gc

            gc.collect()

        except Exception as e:
            logger.error(f"Błąd czyszczenia galerii: {e}")

    def _calculate_columns_cached(self, thumbnail_size):
        """Oblicza ilość kolumn z cache'owaniem"""
        try:
            current_width = self.scroll_area.viewport().width()
            if (
                current_width != self._last_width
                or thumbnail_size != self._last_tile_size
            ):
                # Przelicz tylko jeśli zmienił się rozmiar
                # Rzeczywisty rozmiar kafelka (z thumbnail_tile.py: max-width: {new_size + 20}px)
                tile_width = thumbnail_size + 20

                # Marginesy layoutu (8px z każdej strony)
                layout_margins = 14

                # Spacing między kafelkami (8px)
                spacing = 8

                # Dostępna szerokość po odjęciu marginesów
                available_width = current_width - layout_margins

                # Oblicz liczbę kolumn z uwzględnieniem spacing
                # Wzór: (available_width + spacing) // (tile_width + spacing)
                columns_calc = (available_width + spacing) // (tile_width + spacing)
                self._cached_columns = max(1, columns_calc)

                self._last_width = current_width
                self._last_tile_size = thumbnail_size
            return self._cached_columns
        except Exception as e:
            logger.error(f"Błąd obliczania kolumn: {e}")
            return 4

    def _create_folder_tile_safe(self, folder_asset, thumbnail_size):
        """Bezpiecznie tworzy kafelek specjalnego folderu"""
        try:
            folder_name = folder_asset["name"]
            folder_path = folder_asset["folder_path"]
            
            tile = FolderTile(thumbnail_size, folder_name, folder_path)
            
            # Połącz sygnał kliknięcia
            tile.folder_clicked.connect(self._on_folder_tile_clicked)
            
            return tile

        except Exception as e:
            logger.error(
                f"Błąd tworzenia kafelka folderu dla {folder_asset.get('name', 'unknown')}: {e}"
            )
            return None

    def _create_asset_tile_safe(self, asset, tile_number, total_tiles, thumbnail_size):
        """Bezpiecznie tworzy kafelek asset"""
        try:
            # Podstawowa nazwa z rozmiarem
            display_name = f"{asset['name']} ({asset['size_mb']:.1f} MB)"
            
            tile = ThumbnailTile(thumbnail_size, display_name, tile_number, total_tiles)

            # Ustaw dane asset-a dla dostępu do ścieżek
            tile.set_asset_data(asset)

            # Ustaw gwiazdki jeśli są w asset
            if asset.get("stars") is not None:
                tile.set_star_rating(asset["stars"])

            # Załaduj thumbnail z .cache jeśli dostępny
            if asset.get("thumbnail") is True and self.current_folder_path:
                cache_folder = os.path.join(self.current_folder_path, ".cache")
                asset_name = asset["name"]
                tile.load_thumbnail_from_cache(asset_name, cache_folder)

            # Połącz sygnały kliknięć
            tile.thumbnail_clicked.connect(
                lambda filename: self._on_thumbnail_clicked(asset)
            )
            tile.filename_clicked.connect(
                lambda filename: self._on_filename_clicked(asset)
            )
            
            # Połącz sygnał zmiany zaznaczenia (jeśli istnieje)
            if hasattr(tile, 'checkbox') and tile.checkbox:
                tile.checkbox.stateChanged.connect(self._on_selection_changed)

            return tile

        except Exception as e:
            logger.error(
                f"Błąd tworzenia kafelka dla {asset.get('name', 'unknown')}: {e}"
            )
            return None

    def _create_no_assets_message(self):
        """Tworzy komunikat o braku assetów"""
        no_assets_label = QLabel("Brak asset-ów w folderze roboczym")
        no_assets_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_assets_label.setStyleSheet(
            """
            QLabel {
                color: #888888;
                font-size: 12px;
                padding: 20px;
            }
        """
        )
        self.gallery_layout.addWidget(no_assets_label, 0, 0)

    def _create_error_message(self, error_text):
        """Tworzy komunikat o błędzie"""
        error_label = QLabel(f"Błąd ładowania galerii: {error_text}")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet(
            """
            QLabel {
                color: #FF6B6B;
                font-size: 12px;
                padding: 20px;
            }
        """
        )
        self.gallery_layout.addWidget(error_label, 0, 0)

    def update_tile_sizes_safe(self, new_size):
        """Bezpiecznie aktualizuje rozmiar wszystkich kafelków"""
        try:
            for tile in self.current_tiles:
                if tile and hasattr(tile, "update_thumbnail_size"):
                    tile.update_thumbnail_size(new_size)
        except Exception as e:
            logger.error(f"Błąd aktualizacji rozmiarów kafelków: {e}")

    def _on_thumbnail_clicked(self, asset):
        """Obsługa kliknięcia w miniaturkę - otwiera podgląd"""
        try:
            if not asset or "preview" not in asset:
                logger.warning("Brak ścieżki do podglądu w asset")
                return

            # Skonstruuj pełną ścieżkę do pliku podglądu
            preview_filename = asset["preview"]
            if self.current_folder_path:
                preview_path = os.path.join(self.current_folder_path, preview_filename)

                if os.path.exists(preview_path):
                    # Otwórz okno podglądu (pokazuje się automatycznie)
                    PreviewWindow(preview_path, self.gallery_widget)
                else:
                    logger.warning(f"Plik podglądu nie istnieje: {preview_path}")
            else:
                logger.warning("Brak ścieżki do folderu")

        except Exception as e:
            logger.error(f"Błąd otwierania podglądu: {e}")

    def _on_filename_clicked(self, asset):
        """Obsługa kliknięcia w nazwę pliku - otwiera archiwum"""
        try:
            if not asset or "archive" not in asset:
                logger.warning("Brak ścieżki do archiwum w asset")
                return

            # Skonstruuj pełną ścieżkę do pliku archiwum
            archive_filename = asset["archive"]
            if self.current_folder_path:
                archive_path = os.path.join(self.current_folder_path, archive_filename)

                if os.path.exists(archive_path):
                    # Otwórz archiwum w domyślnej aplikacji
                    if os.name == "nt":  # Windows
                        os.startfile(archive_path)
                    else:  # Linux/Mac
                        subprocess.run(["xdg-open", archive_path])
                else:
                    logger.warning(f"Plik archiwum nie istnieje: {archive_path}")
            else:
                logger.warning("Brak ścieżki do folderu")

        except Exception as e:
            logger.error(f"Błąd otwierania archiwum: {e}")

    def _on_folder_tile_clicked(self, folder_path):
        """Obsługa kliknięcia w kafelek specjalnego folderu - otwiera folder w eksploratorze"""
        try:
            if not folder_path or not os.path.exists(folder_path):
                logger.warning(f"Folder nie istnieje: {folder_path}")
                return

            logger.info(f"Otwieranie folderu w eksploratorze: {folder_path}")

            # Otwórz folder w eksploratorze systemu
            if os.name == "nt":  # Windows
                os.startfile(folder_path)
            elif os.name == "posix":  # Linux/Mac
                if sys.platform == "darwin":  # macOS
                    subprocess.run(["open", folder_path])
                else:  # Linux
                    subprocess.run(["xdg-open", folder_path])

        except Exception as e:
            logger.error(f"Błąd otwierania folderu: {e}")

    def select_all_tiles(self):
        """Zaznacza wszystkie kafelki assetów (pomija specjalne foldery)"""
        try:
            selected_count = 0
            for tile in self.current_tiles:
                if tile and hasattr(tile, 'set_checked') and hasattr(tile, 'asset_data'):
                    # Zaznacz tylko zwykłe assety, nie specjalne foldery
                    if tile.asset_data and tile.asset_data.get('type') != 'special_folder':
                        tile.set_checked(True)
                        selected_count += 1
            return selected_count
        except Exception as e:
            logger.error(f"Błąd zaznaczania wszystkich kafelków: {e}")
            return 0

    def deselect_all_tiles(self):
        """Odznacza wszystkie kafelki"""
        try:
            for tile in self.current_tiles:
                if tile and hasattr(tile, 'set_checked'):
                    tile.set_checked(False)
        except Exception as e:
            logger.error(f"Błąd odznaczania kafelków: {e}")

    def get_selected_assets(self):
        """Pobiera listę zaznaczonych assetów"""
        try:
            selected_assets = []
            for tile in self.current_tiles:
                if (tile and hasattr(tile, 'is_checked') and hasattr(tile, 'asset_data') and 
                    tile.is_checked() and tile.asset_data and 
                    tile.asset_data.get('type') != 'special_folder'):
                    selected_assets.append(tile.asset_data)
            return selected_assets
        except Exception as e:
            logger.error(f"Błąd pobierania zaznaczonych assetów: {e}")
            return []

    def delete_selected_assets(self):
        """Usuwa zaznaczone assety (wszystkie 4 pliki)"""
        try:
            deleted_count = 0
            selected_tiles = []
            
            # Zbierz zaznaczone kafelki
            for tile in self.current_tiles:
                if (tile and hasattr(tile, 'is_checked') and hasattr(tile, 'asset_data') and 
                    tile.is_checked() and tile.asset_data and 
                    tile.asset_data.get('type') != 'special_folder'):
                    selected_tiles.append(tile)
            
            # Usuń pliki dla każdego zaznaczonego asseta
            for tile in selected_tiles:
                try:
                    asset_data = tile.asset_data
                    asset_name = asset_data.get('name', '')
                    
                    if not self.current_folder_path:
                        logger.warning("Brak ścieżki do aktualnego folderu")
                        continue
                    
                    files_to_delete = []
                    
                    # 1. Plik .asset
                    asset_file = os.path.join(self.current_folder_path, f"{asset_name}.asset")
                    if os.path.exists(asset_file):
                        files_to_delete.append(asset_file)
                    
                    # 2. Plik archiwum
                    archive_file = os.path.join(self.current_folder_path, asset_data.get('archive', ''))
                    if os.path.exists(archive_file):
                        files_to_delete.append(archive_file)
                    
                    # 3. Plik podglądu
                    preview_file = os.path.join(self.current_folder_path, asset_data.get('preview', ''))
                    if os.path.exists(preview_file):
                        files_to_delete.append(preview_file)
                    
                    # 4. Plik thumb w .cache
                    cache_folder = os.path.join(self.current_folder_path, '.cache')
                    thumb_file = os.path.join(cache_folder, f"{asset_name}.thumb")
                    if os.path.exists(thumb_file):
                        files_to_delete.append(thumb_file)
                    
                    # Usuń wszystkie pliki
                    for file_path in files_to_delete:
                        try:
                            os.remove(file_path)
                            logger.debug(f"Usunięto plik: {file_path}")
                        except Exception as e:
                            logger.error(f"Błąd usuwania pliku {file_path}: {e}")
                    
                    if files_to_delete:
                        deleted_count += 1
                        logger.info(f"Usunięto asset: {asset_name}")
                    
                except Exception as e:
                    logger.error(f"Błąd usuwania asseta: {e}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Błąd usuwania zaznaczonych assetów: {e}")
            return 0

    def _on_selection_changed(self):
        """Obsługuje zmianę zaznaczenia kafelka"""
        try:
            if self.selection_changed_callback:
                # Sprawdź czy są zaznaczone kafelki
                has_selection = any(
                    tile.is_checked() for tile in self.current_tiles 
                    if tile and hasattr(tile, 'is_checked') and hasattr(tile, 'asset_data') 
                    and tile.asset_data and tile.asset_data.get('type') != 'special_folder'
                )
                self.selection_changed_callback(has_selection)
        except Exception as e:
            logger.error(f"Błąd obsługi zmiany zaznaczenia: {e}")


class AssetScanner(QThread):
    """Worker dla skanowania plików asset w folderze roboczym"""

    progress_updated = pyqtSignal(int)  # Sygnał postępu
    assets_found = pyqtSignal(list)  # Sygnał z listą znalezionych asset-ów
    finished_scanning = pyqtSignal()  # Sygnał zakończenia skanowania
    error_occurred = pyqtSignal(str)  # Sygnał błędu

    def __init__(self, work_folder_path: str):
        super().__init__()
        self.work_folder_path = work_folder_path
        self.assets = []

    def run(self):
        """Główna metoda worker-a z proper error handling"""
        try:
            self.assets = []

            if not self.work_folder_path:
                self.error_occurred.emit("Brak ścieżki do folderu roboczego")
                self.finished_scanning.emit()
                return

            logger.info(f"Rozpoczęcie skanowania folderu: {self.work_folder_path}")

            if not os.path.exists(self.work_folder_path):
                error_msg = f"Folder nie istnieje: {self.work_folder_path}"
                logger.warning(error_msg)
                self.error_occurred.emit(error_msg)
                self.finished_scanning.emit()
                return

            # Najpierw sprawdź specjalne foldery
            special_folders = self._scan_special_folders()
            
            # Dodaj specjalne foldery na początek listy
            for folder_data in special_folders:
                self.assets.append(folder_data)

            # Bezpieczne skanowanie plików asset
            asset_files = self._scan_asset_files()

            if not asset_files and not special_folders:
                logger.info("Nie znaleziono plików .asset ani specjalnych folderów")
                self.finished_scanning.emit()
                return

            logger.info(f"Znaleziono {len(asset_files)} plików .asset i {len(special_folders)} specjalnych folderów")

            # Przetwarzaj każdy plik asset z progress tracking
            if asset_files:
                self._process_asset_files(asset_files)
            else:
                # Jeśli tylko specjalne foldery, prześlij wyniki natychmiast
                self.assets_found.emit(self.assets)

        except Exception as e:
            error_msg = f"Nieoczekiwany błąd podczas skanowania: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
        finally:
            self.finished_scanning.emit()

    def _scan_special_folders(self):
        """Skanuje specjalne foldery (tex, textures, maps)"""
        special_folders = []
        special_folder_names = ["tex", "textures", "maps"]
        
        try:
            for folder_name in special_folder_names:
                folder_path = os.path.join(self.work_folder_path, folder_name)
                if os.path.isdir(folder_path):
                    folder_data = {
                        "type": "special_folder",
                        "name": folder_name,
                        "folder_path": folder_path,
                        "size_mb": 0.0,  # Foldery nie mają rozmiaru
                        "thumbnail": False,
                        "archive": "",
                        "preview": "",
                        "stars": None
                    }
                    special_folders.append(folder_data)
                    logger.info(f"Znaleziono specjalny folder: {folder_name}")
            
            return special_folders
            
        except Exception as e:
            logger.error(f"Błąd skanowania specjalnych folderów: {e}")
            return []

    def _scan_asset_files(self):
        """Bezpiecznie skanuje pliki .asset w folderze"""
        try:
            all_files = os.listdir(self.work_folder_path)
            asset_files = [
                file
                for file in all_files
                if file.endswith(".asset") and not file.startswith(".")
            ]
            return asset_files
        except PermissionError as e:
            logger.error(
                f"Brak uprawnień do odczytu folderu {self.work_folder_path}: {e}"
            )
            raise
        except OSError as e:
            logger.error(
                f"Błąd systemu podczas skanowania folderu {self.work_folder_path}: {e}"
            )
            raise

    def _process_asset_files(self, asset_files):
        """Przetwarza pliki .asset z progress tracking"""
        total_files = len(asset_files)

        for i, asset_file in enumerate(asset_files):
            try:
                asset_path = os.path.join(self.work_folder_path, asset_file)
                asset_data = self._load_asset_file(asset_path)

                if asset_data and self._is_valid_asset(asset_data):
                    self.assets.append(asset_data)
                    logger.debug(f"Załadowano asset: {asset_file}")
                else:
                    logger.warning(f"Niepoprawny asset: {asset_file}")

            except Exception as e:
                logger.error(f"Błąd przetwarzania asset {asset_file}: {e}")
                # Kontynuuj przetwarzanie innych plików

            # Aktualizuj postęp
            progress = int((i + 1) / total_files * 100)
            self.progress_updated.emit(progress)

        # Prześlij wyniki
        logger.info(
            f"Przetworzono {len(self.assets)} poprawnych assetów z {total_files} plików"
        )
        self.assets_found.emit(self.assets)

    def _load_asset_file(self, asset_path):
        """Bezpiecznie ładuje plik .asset"""
        try:
            with open(asset_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Niepoprawny JSON w pliku {asset_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Błąd czytania pliku {asset_path}: {e}")
            return None

    def _is_valid_asset(self, data: dict) -> bool:
        """Sprawdza czy JSON zawiera poprawną strukturę asset z walidacją"""
        if not isinstance(data, dict):
            return False

        required_fields = ["name", "archive", "preview", "size_mb", "thumbnail"]

        for field in required_fields:
            if field not in data:
                logger.warning(f"Brakujące pole w asset: {field}")
                return False

        return True


class AssetRebuilderThread(QThread):
    """Worker dla przebudowy assetów w folderze"""

    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    rebuild_finished = pyqtSignal(str)  # message
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self, folder_path: str):
        super().__init__()
        self.folder_path = folder_path

    def run(self):
        """Główna metoda przebudowy assetów"""
        try:
            if not self.folder_path or not os.path.exists(self.folder_path):
                self.error_occurred.emit(f"Nieprawidłowy folder: {self.folder_path}")
                return

            logger.info(f"Rozpoczęcie przebudowy assetów w folderze: {self.folder_path}")

            # Krok 1: Usuwanie plików .asset
            self.progress_updated.emit(0, 100, "Usuwanie starych plików .asset...")
            self._remove_asset_files()

            # Krok 2: Usuwanie folderu .cache
            self.progress_updated.emit(25, 100, "Usuwanie folderu .cache...")
            self._remove_cache_folder()

            # Krok 3: Uruchamianie scanner.py
            self.progress_updated.emit(50, 100, "Skanowanie i tworzenie nowych assetów...")
            self._run_scanner()

            self.progress_updated.emit(100, 100, "Przebudowa zakończona!")
            self.rebuild_finished.emit(f"Pomyślnie przebudowano assety w folderze: {self.folder_path}")

        except Exception as e:
            error_msg = f"Błąd podczas przebudowy assetów: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def _remove_asset_files(self):
        """Usuwa wszystkie pliki .asset z folderu"""
        try:
            asset_files = [f for f in os.listdir(self.folder_path) if f.endswith('.asset')]
            for asset_file in asset_files:
                file_path = os.path.join(self.folder_path, asset_file)
                os.remove(file_path)
                logger.debug(f"Usunięto plik asset: {asset_file}")
            
            logger.info(f"Usunięto {len(asset_files)} plików .asset")
        except Exception as e:
            logger.error(f"Błąd usuwania plików .asset: {e}")
            raise

    def _remove_cache_folder(self):
        """Usuwa folder .cache jeśli istnieje"""
        try:
            cache_folder = os.path.join(self.folder_path, '.cache')
            if os.path.exists(cache_folder) and os.path.isdir(cache_folder):
                shutil.rmtree(cache_folder)
                logger.info(f"Usunięto folder .cache: {cache_folder}")
            else:
                logger.debug("Folder .cache nie istnieje lub nie jest folderem")
        except Exception as e:
            logger.error(f"Błąd usuwania folderu .cache: {e}")
            raise

    def _run_scanner(self):
        """Uruchamia scanner.py w folderze"""
        try:
            from core.scanner import find_and_create_assets
            
            def progress_callback(current, total, message):
                if total > 0:
                    # Mapuj postęp scanner-a na przedział 50-100%
                    scanner_progress = int(50 + (current / total) * 50)
                    self.progress_updated.emit(scanner_progress, 100, message)
                else:
                    self.progress_updated.emit(75, 100, message)

            created_assets = find_and_create_assets(self.folder_path, progress_callback)
            logger.info(f"Scanner utworzył {len(created_assets)} nowych assetów")
            
        except Exception as e:
            logger.error(f"Błąd uruchamiania scanner-a: {e}")
            raise


class DropHighlightDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        is_drop_target = index.data(Qt.ItemDataRole.UserRole + 1)
        if is_drop_target and painter:
            painter.save()
            rect = option.rect
            painter.setBrush(QBrush(QColor("#007ACC")))
            painter.setPen(QPen(QColor("#FFD700"), 2))
            painter.drawRect(rect.adjusted(1, 1, -2, -2))
            painter.restore()
            # Rysuj tekst normalnie - niebieskie tło i tak będzie widoczne
            super().paint(painter, option, index)
        else:
            super().paint(painter, option, index)


class CustomTreeView(QTreeView):
    """Rozszerzona klasa QTreeView z obsługą menu kontekstowego i drag-and-drop"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gallery_tab = None  # Referencja do GalleryTab
        self._highlighted_index = None
        
    def set_gallery_tab(self, gallery_tab):
        """Ustawia referencję do GalleryTab"""
        self.gallery_tab = gallery_tab
    
    def contextMenuEvent(self, event):
        """Obsługuje menu kontekstowe"""
        try:
            index = self.indexAt(event.pos())
            if index.isValid() and self.gallery_tab and isinstance(self.model(), QStandardItemModel):
                item = self.model().itemFromIndex(index)
                if item and hasattr(item, 'folder_path'):
                    folder_path = getattr(item, 'folder_path')
                    
                    # Utwórz menu kontekstowe
                    menu = QMenu(self)
                    
                    rebuild_action = QAction("Przebuduj assety", self)
                    rebuild_action.triggered.connect(
                        lambda: self.gallery_tab._rebuild_assets_in_folder(folder_path)
                    )
                    menu.addAction(rebuild_action)
                    
                    # Pokaż menu
                    menu.exec(event.globalPos())
                    
        except Exception as e:
            logger.error(f"Błąd obsługi menu kontekstowego: {e}")

    def dragEnterEvent(self, event):
        """Obsługuje wejście drag nad drzewem folderów"""
        try:
            if event.mimeData().hasFormat("application/x-cfab-asset"):
                event.acceptProposedAction()
                pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                self._highlight_folder_at_position(pos)
        except Exception as e:
            logger.error(f"Błąd obsługi drag enter w drzewie: {e}")
            event.ignore()

    def dragLeaveEvent(self, event):
        """Obsługuje wyjście drag z drzewa folderów"""
        try:
            # Usuń podświetlenie
            self._clear_folder_highlight()
        except Exception as e:
            logger.error(f"Błąd obsługi drag leave w drzewie: {e}")

    def dragMoveEvent(self, event):
        """Obsługuje przeciąganie elementów w drzewie folderów"""
        try:
            if event.mimeData().hasFormat("application/x-cfab-asset"):
                event.acceptProposedAction()
                pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                self._highlight_folder_at_position(pos)
        except Exception as e:
            logger.error(f"Błąd obsługi drag move w drzewie: {e}")
            event.ignore()

    def dropEvent(self, event):
        """Obsługuje drop na drzewie folderów"""
        try:
            if event.mimeData().hasFormat("application/x-cfab-asset"):
                pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                index = self.indexAt(pos)
                if index.isValid() and isinstance(self.model(), QStandardItemModel):
                    item = self.model().itemFromIndex(index)
                    if item and hasattr(item, 'folder_path'):
                        folder_path = item.folder_path
                        if os.path.isdir(folder_path):
                            # Obsłuż drop asset-a do folderu
                            if self.gallery_tab:
                                self.gallery_tab._handle_asset_drop_to_folder(folder_path, event.mimeData())
                            event.acceptProposedAction()
                # Usuń podświetlenie po drop
                self._clear_folder_highlight()
        except Exception as e:
            logger.error(f"Błąd obsługi drop w drzewie: {e}")

    def _highlight_folder_at_position(self, pos):
        """Podświetla folder pod określoną pozycją"""
        try:
            index = self.folder_tree_view.indexAt(pos)
            if index.isValid():
                self._clear_folder_highlight()
                item = self.folder_model.itemFromIndex(index)
                if item:
                    item.setData(True, Qt.ItemDataRole.UserRole + 1)
                    self._highlighted_index = index
        except Exception as e:
            logger.error(f"Błąd podświetlania folderu: {e}")

    def _clear_folder_highlight(self):
        """Usuwa podświetlenie folderu (usuwa property dropTarget)"""
        try:
            if hasattr(self, '_highlighted_index') and self._highlighted_index:
                item = self.folder_model.itemFromIndex(self._highlighted_index)
                if item:
                    item.setData(False, Qt.ItemDataRole.UserRole + 1)
                self._highlighted_index = None
        except Exception as e:
            logger.error(f"Błąd usuwania podświetlenia: {e}")


class GalleryTab(QWidget):
    def __init__(self):
        super().__init__()

        # Inicjalizacja menedżerów
        self.config_manager = ConfigManager()
        self.grid_manager = None  # Będzie zainicjalizowany po utworzeniu UI

        # Konfiguracja
        self.thumbnail_size = self.config_manager.get_thumbnail_size()
        self.min_thumbnail_size = 50
        self.max_thumbnail_size = self.thumbnail_size
        self.work_folder_path = self.config_manager.get_work_folder_path()

        # Dane
        self.assets = []
        self.scanner = None
        self.asset_rebuilder = None  # Worker dla przebudowy assetów

        # Setup UI i połączenia
        try:
            self._setup_ui()
            self._initialize_grid_manager()
            self._connect_signals()
            self._show_waiting_for_folder_message()
            logger.info("GalleryTab zainicjalizowany pomyślnie")
        except Exception as e:
            logger.error(f"Błąd inicjalizacji GalleryTab: {e}")
            raise

    def _initialize_grid_manager(self):
        """Inicjalizuje grid manager po utworzeniu UI"""
        if hasattr(self, "gallery_widget") and hasattr(self, "gallery_layout"):
            self.grid_manager = GridManager(
                self.gallery_widget, self.gallery_layout, self.scroll_area
            )
            # Przekaż callback do aktualizacji przycisków zaznaczenia
            self.grid_manager.selection_changed_callback = self._update_selection_buttons_state
        else:
            raise RuntimeError("UI components not initialized before GridManager")

    def _setup_ui(self):
        """Setup user interface for gallery tab z error handling"""
        try:
            # Główny layout
            main_layout = QHBoxLayout()
            main_layout.setContentsMargins(8, 8, 8, 8)
            main_layout.setSpacing(8)

            # Tworzenie komponentów
            self._create_splitter()
            self._create_folder_panel()
            self._create_gallery_panel()

            # Finalizacja
            main_layout.addWidget(self.splitter)
            self.setLayout(main_layout)

        except Exception as e:
            logger.error(f"Błąd setup UI: {e}")
            raise

    def _create_splitter(self):
        """Tworzy główny splitter"""
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setSizes([200, 800])  # 2:80 ratio

    def _create_folder_panel(self):
        """Tworzy lewy panel folderów z systemową kontrolką QTreeView"""
        self.folder_tree_panel = QFrame()
        self.folder_tree_panel.setFrameStyle(QFrame.Shape.NoFrame)
        self.folder_tree_panel.setMinimumWidth(250)
        self.folder_tree_panel.setMaximumWidth(350)
        self.folder_tree_panel.setStyleSheet(
            """
            QFrame {
                background-color: #1E1E1E;
                border-right: 1px solid #3F3F46;
            }
        """
        )

        folder_layout = QVBoxLayout()
        folder_layout.setContentsMargins(0, 0, 0, 0)
        folder_layout.setSpacing(0)

        # Nagłówek panelu
        header_frame = QFrame()
        header_frame.setFixedHeight(40)
        header_frame.setStyleSheet(
            """
            QFrame {
                background-color: #252526;
                border-bottom: 1px solid #3F3F46;
            }
        """
        )

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 8, 12, 8)

        # Ikona folderów
        folder_icon = QLabel("📁")
        folder_icon.setStyleSheet(
            """
            QLabel {
                color: #007ACC;
                font-size: 12px;
                padding: 0px;
            }
        """
        )

        # Tytuł
        title_label = QLabel("Eksplorator folderów")
        title_label.setStyleSheet(
            """
            QLabel {
                color: #CCCCCC;
                font-size: 13px;
                font-weight: bold;
                padding: 0px;
            }
        """
        )

        header_layout.addWidget(folder_icon)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        header_frame.setLayout(header_layout)
        folder_layout.addWidget(header_frame)

        # Systemowa kontrolka drzewa folderów
        self.folder_tree_view = CustomTreeView()
        self.folder_tree_view.set_gallery_tab(self)  # Ustaw referencję do GalleryTab
        self.folder_tree_view.setStyleSheet(
            """
            QTreeView {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: none;
                outline: none;
                font-size: 11px;
            }
            QTreeView::item {
                padding: 2px;
                border: none;
            }
            QTreeView::item:hover {
                background-color: #3F3F46;
            }
            QTreeView::item:selected {
                background-color: #007ACC;
                color: #FFFFFF;
            }
            QTreeView::branch {
                background-color: #1E1E1E;
            }
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQgNkw4IDZMOSA2TDkgNUw4IDVMNCA1TDMgNUwzIDZMNCA2WiIgZmlsbD0iI0NDQ0NDQyIvPgo8L3N2Zz4K);
            }
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTUgNEw1IDhMNiA4TDYgNEw1IDRaIiBmaWxsPSIjQ0NDQ0NDIi8+Cjwvc3ZnPgo=);
            }
            QScrollBar:vertical {
                background-color: #1E1E1E;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3F3F46;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #52525B;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """
        )

        # Model drzewa folderów
        self.folder_model = QStandardItemModel()
        self.folder_model.setHorizontalHeaderLabels(["Folders"])
        
        # Włącz obsługę drop dla każdego itemu
        self.folder_tree_view.setDragDropMode(QTreeView.DragDropMode.DropOnly)
        self.folder_tree_view.setDefaultDropAction(Qt.DropAction.CopyAction)
        
        # Ustaw model w widoku
        self.folder_tree_view.setModel(self.folder_model)
        
        # Ukryj nagłówek
        self.folder_tree_view.setHeaderHidden(True)
        
        # Włącz automatyczne rozwijanie folderów
        self.folder_tree_view.setExpandsOnDoubleClick(True)
        self.folder_tree_view.setItemsExpandable(True)
        
        # Wymuś ładowanie wszystkich elementów
        self.folder_tree_view.setUniformRowHeights(False)
        
        # Podłącz sygnał kliknięcia
        self.folder_tree_view.clicked.connect(self._on_tree_item_clicked)
        
        # Włącz obsługę drag and drop - zastąp metody przez subklasę
        self.folder_tree_view.setAcceptDrops(True)

        # Ustaw własny delegate do podświetlania drop targetu
        self.folder_tree_view.setItemDelegate(DropHighlightDelegate(self.folder_tree_view))

        folder_layout.addWidget(self.folder_tree_view)

        # Panel przycisków folderów na dole
        self._create_folder_buttons_panel(folder_layout)

        self.folder_tree_panel.setLayout(folder_layout)
        self.splitter.addWidget(self.folder_tree_panel)

    def _create_gallery_panel(self):
        """Tworzy prawy panel galerii"""
        self.gallery_panel = QFrame()
        self.gallery_panel.setFrameStyle(QFrame.Shape.NoFrame)
        self.gallery_panel.setStyleSheet(
            """
            QFrame {
                background-color: #1E1E1E;
                border: none;
            }
        """
        )

        gallery_vertical_layout = QVBoxLayout()
        gallery_vertical_layout.setSpacing(0)
        gallery_vertical_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area
        self._create_scroll_area()

        # Control panel
        self._create_control_panel()

        # Dodanie do layoutu
        gallery_vertical_layout.addWidget(self.scroll_area)
        gallery_vertical_layout.addWidget(self.control_panel)

        self.gallery_panel.setLayout(gallery_vertical_layout)
        self.splitter.addWidget(self.gallery_panel)

    def _create_scroll_area(self):
        """Tworzy scroll area z gallery widget"""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setFrameStyle(QScrollArea.Shape.NoFrame)
        self.scroll_area.setStyleSheet(
            """
            QScrollArea {
                background-color: #1E1E1E;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2D2D30;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #424242;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #535353;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #007ACC;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background-color: #2D2D30;
                height: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #424242;
                border-radius: 6px;
                min-width: 20px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #535353;
            }
            QScrollBar::handle:horizontal:pressed {
                background-color: #007ACC;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """
        )

        # Gallery widget
        self.gallery_widget = QWidget()
        self.gallery_layout = QGridLayout()
        self.gallery_layout.setSpacing(8)
        self.gallery_layout.setContentsMargins(8, 8, 8, 8)

        # Loading placeholder
        self._create_loading_placeholder()

        self.gallery_widget.setLayout(self.gallery_layout)
        self.scroll_area.setWidget(self.gallery_widget)

    def _create_control_panel(self):
        """Tworzy dolny panel kontrolny"""
        self.control_panel = QFrame()
        self.control_panel.setFixedHeight(50)
        self.control_panel.setStyleSheet(
            """
            QFrame {
                background-color: #252526;
                border-top: 1px solid #3F3F46;
            }
        """
        )

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(12, 6, 12, 6)
        control_layout.setSpacing(16)

        # Progress bar z etykietą
        self._create_progress_bar()

        # Thumbnail size slider z etykietą
        self._create_thumbnail_slider()

        # Przyciski zarządzania zaznaczeniem
        self._create_selection_buttons()

        # Dodanie kontrolek bez etykiet
        control_layout.addWidget(self.progress_bar, 2)
        
        # Dodanie przycisków zarządzania
        for button in self.selection_buttons:
            control_layout.addWidget(button)
        
        control_layout.addWidget(self.thumbnail_size_slider, 2)

        self.control_panel.setLayout(control_layout)

    def _create_selection_buttons(self):
        """Tworzy przyciski zarządzania zaznaczeniem"""
        self.selection_buttons = []
        
        # Style dla przycisków
        button_style = """
            QPushButton {
                background-color: #3C3C3C;
                color: #CCCCCC;
                border: 1px solid #555555;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                padding: 4px 8px;
                min-width: 120px;
                max-height: 40px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
                border-color: #007ACC;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #007ACC;
                color: #FFFFFF;
            }
            QPushButton:disabled {
                background-color: #2A2A2A;
                color: #666666;
                border-color: #3C3C3C;
            }
        """
        
        # Przycisk "Zaznacz wszystkie"
        self.select_all_button = QPushButton("Zaznacz wszystkie")
        self.select_all_button.setStyleSheet(button_style)
        self.select_all_button.setMinimumWidth(120)  # Wymusza szerokość
        self.select_all_button.clicked.connect(self._on_select_all)
        self.selection_buttons.append(self.select_all_button)
        
        # Przycisk "Przenieś zaznaczone"
        self.move_selected_button = QPushButton("Przenieś zaznaczone")
        self.move_selected_button.setStyleSheet(button_style)
        self.move_selected_button.setMinimumWidth(120)  # Wymusza szerokość
        self.move_selected_button.clicked.connect(self._on_move_selected)
        self.move_selected_button.setEnabled(False)
        self.selection_buttons.append(self.move_selected_button)
        
        # Przycisk "Usuń zaznaczone"
        self.delete_selected_button = QPushButton("Usuń zaznaczone")
        self.delete_selected_button.setStyleSheet(button_style)
        self.delete_selected_button.setMinimumWidth(120)  # Wymusza szerokość
        self.delete_selected_button.clicked.connect(self._on_delete_selected)
        self.delete_selected_button.setEnabled(False)
        self.selection_buttons.append(self.delete_selected_button)
        
        # Przycisk "Odznacz wszystkie"
        self.deselect_all_button = QPushButton("Odznacz wszystkie")
        self.deselect_all_button.setStyleSheet(button_style)
        self.deselect_all_button.setMinimumWidth(120)  # Wymusza szerokość
        self.deselect_all_button.clicked.connect(self._on_deselect_all)
        self.deselect_all_button.setEnabled(False)
        self.selection_buttons.append(self.deselect_all_button)

    def _connect_signals(self):
        """Podłącza sygnały z thread safety"""
        try:
            # Slider signal
            self.thumbnail_size_slider.valueChanged.connect(self._on_slider_changed)

        except Exception as e:
            logger.error(f"Błąd podłączania sygnałów: {e}")

    def _on_select_all(self):
        """Zaznacza wszystkie kafelki assetów"""
        try:
            if hasattr(self, 'grid_manager') and self.grid_manager:
                selected_count = self.grid_manager.select_all_tiles()
                self._update_selection_buttons_state(selected_count > 0)
                logger.info(f"Zaznaczono {selected_count} kafelków")
        except Exception as e:
            logger.error(f"Błąd zaznaczania wszystkich kafelków: {e}")

    def _on_deselect_all(self):
        """Odznacza wszystkie kafelki"""
        try:
            if hasattr(self, 'grid_manager') and self.grid_manager:
                self.grid_manager.deselect_all_tiles()
                self._update_selection_buttons_state(False)
                logger.info("Odznaczono wszystkie kafelki")
        except Exception as e:
            logger.error(f"Błąd odznaczania kafelków: {e}")

    def _on_move_selected(self):
        """Przenosi zaznaczone kafelki do wybranego folderu"""
        try:
            if hasattr(self, 'grid_manager') and self.grid_manager:
                selected_assets = self.grid_manager.get_selected_assets()
                if selected_assets:
                    # Pokaż dialog wyboru folderu docelowego
                    from PyQt6.QtWidgets import QFileDialog
                    
                    # Pobierz aktualny folder jako punkt startowy
                    current_folder = getattr(self.grid_manager, 'current_folder_path', '')
                    start_folder = os.path.dirname(current_folder) if current_folder else ""
                    
                    # Dialog wyboru folderu
                    target_folder = QFileDialog.getExistingDirectory(
                        self,
                        "Wybierz folder docelowy",
                        start_folder,
                        QFileDialog.Option.ShowDirsOnly
                    )
                    
                    if target_folder:
                        # Przenoszenie każdego zaznaczonego asseta
                        self._move_selected_assets_to_folder(selected_assets, target_folder)
                        
                        # Odznacz wszystkie po przeniesieniu
                        self.grid_manager.deselect_all_tiles()
                        self._update_selection_buttons_state(False)
                        
                        # Odśwież galerię
                        if current_folder:
                            self._refresh_gallery_for_folder(current_folder)
                    
        except Exception as e:
            logger.error(f"Błąd przenoszenia zaznaczonych kafelków: {e}")
            QMessageBox.critical(
                self,
                "Błąd przenoszenia",
                f"Wystąpił błąd podczas przenoszenia assetów:\n{str(e)}"
            )

    def _on_delete_selected(self):
        """Usuwa zaznaczone kafelki"""
        try:
            if hasattr(self, 'grid_manager') and self.grid_manager:
                selected_assets = self.grid_manager.get_selected_assets()
                if selected_assets:
                    # Pokaż dialog potwierdzenia
                    reply = QMessageBox.question(
                        self,
                        "Potwierdzenie usunięcia",
                        f"Czy na pewno chcesz usunąć {len(selected_assets)} zaznaczonych assetów?\n"
                        "Ta operacja jest nieodwracalna!",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        deleted_count = self.grid_manager.delete_selected_assets()
                        self._update_selection_buttons_state(False)
                        
                        # Odśwież galerię
                        current_folder = getattr(self.grid_manager, 'current_folder_path', '')
                        if current_folder:
                            self._refresh_gallery_for_folder(current_folder)
                        
                        QMessageBox.information(
                            self,
                            "Usunięcie zakończone",
                            f"Usunięto {deleted_count} assetów."
                        )
                        logger.info(f"Usunięto {deleted_count} zaznaczonych assetów")
        except Exception as e:
            logger.error(f"Błąd usuwania zaznaczonych kafelków: {e}")

    def _update_selection_buttons_state(self, has_selection):
        """Aktualizuje stan przycisków zarządzania zaznaczeniem"""
        try:
            if hasattr(self, 'move_selected_button'):
                # Sprawdź czy są foldery tekstur w aktualnym folderze
                current_folder = getattr(self.grid_manager, 'current_folder_path', '') if hasattr(self, 'grid_manager') and self.grid_manager else ""
                has_texture_folders = self._check_texture_folders_presence(current_folder) if current_folder else False
                
                # Przycisk przenoszenia aktywny tylko jeśli są zaznaczone assety I nie ma folderów tekstur
                self.move_selected_button.setEnabled(has_selection and not has_texture_folders)
                
            if hasattr(self, 'delete_selected_button'):
                self.delete_selected_button.setEnabled(has_selection)
            if hasattr(self, 'deselect_all_button'):
                self.deselect_all_button.setEnabled(has_selection)
        except Exception as e:
            logger.error(f"Błąd aktualizacji stanu przycisków: {e}")

    def _move_selected_assets_to_folder(self, selected_assets, target_folder):
        """Przenosi listę assetów do docelowego folderu"""
        try:
            import shutil
            moved_count = 0
            errors = []
            current_folder = getattr(self.grid_manager, 'current_folder_path', '')
            
            if not current_folder:
                raise Exception("Nie można ustalić folderu źródłowego assetów!")
            
            for asset_data in selected_assets:
                try:
                    asset_name = asset_data.get('name', '')
                    if not asset_name:
                        continue
                    
                    files_to_move = []
                    
                    # 1. Plik .asset
                    asset_file = os.path.join(current_folder, f"{asset_name}.asset")
                    if os.path.exists(asset_file):
                        files_to_move.append(asset_file)
                    
                    # 2. Plik archiwum
                    archive_file = os.path.join(current_folder, asset_data.get('archive', ''))
                    if os.path.exists(archive_file):
                        files_to_move.append(archive_file)
                    
                    # 3. Plik podglądu
                    preview_file = os.path.join(current_folder, asset_data.get('preview', ''))
                    if os.path.exists(preview_file):
                        files_to_move.append(preview_file)
                    
                    # 4. Plik thumb (w .cache)
                    if asset_data.get("thumbnail") is True:
                        cache_folder = os.path.join(current_folder, ".cache")
                        thumb_file = os.path.join(cache_folder, f"{asset_name}.thumb")
                        if os.path.exists(thumb_file):
                            # Upewnij się że folder .cache istnieje w docelowym folderze
                            target_cache = os.path.join(target_folder, ".cache")
                            os.makedirs(target_cache, exist_ok=True)
                            files_to_move.append((thumb_file, target_cache))
                    
                    # Przenoszenie plików
                    for file_info in files_to_move:
                        if isinstance(file_info, tuple):
                            # Specjalne przetwarzanie dla pliku thumb
                            file_path, dest_folder = file_info
                            shutil.move(file_path, dest_folder)
                        else:
                            # Zwykłe pliki - przenieś do głównego folderu docelowego
                            shutil.move(file_info, target_folder)
                    
                    if files_to_move:
                        moved_count += 1
                        logger.info(f"Przeniesiono asset: {asset_name} do {target_folder}")
                    
                except Exception as e:
                    error_msg = f"Asset '{asset_data.get('name', 'Unknown')}': {str(e)}"
                    errors.append(error_msg)
                    logger.error(f"Błąd przenoszenia asseta: {error_msg}")
            
            # Pokaż wyniki
            if errors:
                error_text = "\n".join(errors[:5])  # Pokaż max 5 błędów
                if len(errors) > 5:
                    error_text += f"\n... i {len(errors) - 5} innych błędów"
                    
                QMessageBox.warning(
                    self,
                    "Przenoszenie z błędami",
                    f"Przeniesiono {moved_count} assetów.\n\nBłędy:\n{error_text}"
                )
            else:
                QMessageBox.information(
                    self,
                    "Przenoszenie zakończone",
                    f"Pomyślnie przeniesiono {moved_count} assetów do:\n{target_folder}"
                )
                
            logger.info(f"Przenoszenie zakończone: {moved_count} assetów, {len(errors)} błędów")
            
        except Exception as e:
            logger.error(f"Błąd globalny podczas przenoszenia assetów: {e}")
            raise

    def _start_asset_scanning(self):
        """Rozpoczyna skanowanie asset-ów w tle z error handling"""
        if not self.work_folder_path:
            logger.warning("Brak ścieżki do folderu roboczego")
            self._show_no_folder_message()
            return

        try:
            # Utwórz i uruchom worker
            self.scanner = AssetScanner(self.work_folder_path)
            self.scanner.progress_updated.connect(self._on_scan_progress)
            self.scanner.assets_found.connect(self._on_assets_found)
            self.scanner.finished_scanning.connect(self._on_scan_finished)
            self.scanner.error_occurred.connect(self._on_scan_error)
            self.scanner.start()

        except Exception as e:
            logger.error(f"Błąd rozpoczynania skanowania: {e}")
            self._show_error_message(f"Nie można rozpocząć skanowania: {e}")

    def _refresh_gallery_for_folder(self, folder_path: str):
        """Odświeża galerię dla określonego folderu"""
        try:
            logger.info(f"Odświeżanie galerii dla folderu: {folder_path}")
            
            # Zatrzymaj poprzedni scanner jeśli działa
            if hasattr(self, "scanner") and self.scanner and self.scanner.isRunning():
                self.scanner.quit()
                self.scanner.wait()

            # Utwórz i uruchom asset scanner dla tego folderu
            self.scanner = AssetScanner(folder_path)
            self.scanner.progress_updated.connect(self._on_scan_progress)
            self.scanner.assets_found.connect(self._on_assets_found)
            self.scanner.finished_scanning.connect(self._on_scan_finished)
            self.scanner.error_occurred.connect(self._on_scan_error)
            self.scanner.start()

        except Exception as e:
            logger.error(f"Błąd odświeżania galerii dla folderu {folder_path}: {e}")
            self._show_error_message(f"Błąd odświeżania galerii: {e}")

    def _on_scan_progress(self, progress: int):
        """Obsługuje aktualizację postępu skanowania - thread safe"""
        try:
            self.progress_bar.setValue(progress)
        except Exception as e:
            logger.error(f"Błąd aktualizacji postępu: {e}")

    def _on_assets_found(self, assets: list):
        """Obsługuje znalezienie asset-ów - aktualizuje galerię"""
        try:
            self.assets = assets
            current_size = self.thumbnail_size_slider.value()

            # Przekaż ścieżkę do folderu z assetami
            folder_path = getattr(self.scanner, "work_folder_path", "")
            self.grid_manager.request_grid_recreation(
                self.assets, current_size, folder_path
            )
            
            # Aktualizuj stan drag-and-drop na podstawie obecności folderów tekstur
            if folder_path:
                self._update_drag_drop_state(folder_path)

        except Exception as e:
            logger.error(f"Błąd aktualizacji galerii: {e}")

    def _on_scan_finished(self):
        """Obsługuje zakończenie skanowania"""
        try:
            self.progress_bar.setValue(0)
            logger.info("Skanowanie zakończone")
        except Exception as e:
            logger.error(f"Błąd finalizacji skanowania: {e}")

    def _on_scan_error(self, error_message: str):
        """Obsługuje błędy skanowania"""
        try:
            self.progress_bar.setValue(0)
            self._show_error_message(error_message)
        except Exception as e:
            logger.error(f"Błąd obsługi błędu skanowania: {e}")

    def _on_slider_changed(self, value):
        """Obsługuje zmianę rozmiaru miniaturek"""
        try:
            # Aktualizuj rozmiar wszystkich kafelków
            self.grid_manager.update_tile_sizes_safe(value)

            # Przekaż ścieżkę do folderu z assetami
            folder_path = getattr(self.scanner, "work_folder_path", "")
            self.grid_manager.request_grid_recreation(self.assets, value, folder_path)

        except Exception as e:
            logger.error(f"Błąd zmiany rozmiaru miniaturek: {e}")

    def resizeEvent(self, event):
        """Obsługuje zmianę rozmiaru okna"""
        try:
            super().resizeEvent(event)

            # Przelicz grid po zmianie rozmiaru
            if hasattr(self, "assets") and self.assets:
                current_size = self.thumbnail_size_slider.value()

                # Przekaż ścieżkę do folderu z assetami
                folder_path = getattr(self.scanner, "work_folder_path", "")
                self.grid_manager.request_grid_recreation(
                    self.assets, current_size, folder_path
                )

        except Exception as e:
            logger.error(f"Błąd obsługi zmiany rozmiaru: {e}")

    def _show_error_message(self, error_text):
        """Pokazuje komunikat o błędzie w galerii"""
        try:
            if self.grid_manager:
                self.grid_manager._clear_gallery_safe()
                self.grid_manager._create_error_message(error_text)
        except Exception as e:
            logger.error(f"Błąd pokazywania komunikatu błędu: {e}")

    def _show_no_folder_message(self):
        """Pokazuje komunikat o braku folderu roboczego"""
        self._show_error_message("Nie skonfigurowano folderu roboczego w config.json")

    def _show_waiting_for_folder_message(self):
        """Pokazuje komunikat oczekiwania na wybór folderu"""
        try:
            if self.grid_manager:
                self.grid_manager._clear_gallery_safe()

            waiting_label = QLabel(
                "Wybierz folder z lewego panelu aby wyświetlić assety"
            )
            waiting_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            waiting_label.setStyleSheet(
                """
                QLabel {
                    color: #CCCCCC;
                    font-size: 14px;
                    padding: 50px;
                    font-style: italic;
                }
            """
            )
            self.gallery_layout.addWidget(waiting_label, 0, 0)

        except Exception as e:
            logger.error(f"Błąd pokazywania komunikatu oczekiwania: {e}")

    def _create_loading_placeholder(self):
        """Tworzy placeholder podczas ładowania asset-ów"""
        loading_label = QLabel("Ładowanie asset-ów...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setStyleSheet(
            """
            QLabel {
                color: #CCCCCC;
                font-size: 14px;
                padding: 20px;
            }
        """
        )
        self.gallery_layout.addWidget(loading_label, 0, 0)

    def _create_progress_bar(self):
        """Tworzy progress bar z styling"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #555555;
                background-color: #2D2D30;
                text-align: center;
                color: #FFFFFF;
                border-radius: 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #007ACC, stop:1 #1C97EA);
                border-radius: 9px;
            }
        """
        )

    def _create_thumbnail_slider(self):
        """Tworzy slider dla rozmiaru kafelków"""
        self.thumbnail_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.thumbnail_size_slider.setFixedHeight(20)
        self.thumbnail_size_slider.setMinimum(self.min_thumbnail_size)
        self.thumbnail_size_slider.setMaximum(self.max_thumbnail_size)
        self.thumbnail_size_slider.setValue(self.max_thumbnail_size)
        self.thumbnail_size_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                border: 1px solid #555555;
                height: 10px;
                background: #2D2D30;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1C97EA, stop:1 #007ACC);
                border: 2px solid #FFFFFF;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3BA3F0, stop:1 #1C97EA);
                border: 2px solid #FFD700;
            }
            QSlider::handle:horizontal:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0B7EC8, stop:1 #005A9E);
                border: 2px solid #FF6B6B;
            }
        """
        )

    def _create_folder_buttons_panel(self, folder_layout):
        """Tworzy panel przycisków folderów na dole"""
        try:
            # Panel przycisków
            buttons_frame = QFrame()
            buttons_frame.setFixedHeight(140)
            buttons_frame.setStyleSheet(
                """
                QFrame {
                    background-color: #252526;
                    border-top: 1px solid #3F3F46;
                }
            """
            )

            # Zmiana na QGridLayout dla 2 rzędów po 4 przyciski
            buttons_layout = QGridLayout()
            buttons_layout.setContentsMargins(8, 8, 8, 8)
            buttons_layout.setSpacing(4)

            config_manager = ConfigManager()
            config = config_manager.get_config()

            # 9 przycisków w 3 rzędach po 3
            for i in range(1, 10):
                folder_key = f"work_folder{i}"
                folder_config = config.get(folder_key, {})
                folder_path = folder_config.get("path", "")
                folder_name = folder_config.get("name", f"Folder {i}")

                # Użyj nazwy jeśli jest dostępna, w przeciwnym razie domyślną
                button_text = folder_name if folder_name else f"Folder {i}"

                # Użyj zwykłego QPushButton zamiast FolderButton
                button = QPushButton(button_text, self)
                button.setFixedHeight(14)
                button.setEnabled(bool(folder_path))

                # Profesjonalne stylowanie przycisków
                if folder_path:
                    button.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #2D2D30;
                            color: #CCCCCC;
                            border: 1px solid #3F3F46;
                            border-radius: 4px;
                            font-size: 10px;
                            padding: 1px 4px;
                            text-align: center;
                        }
                        QPushButton:hover {
                            background-color: #3F3F46;
                            border-color: #007ACC;
                        }
                        QPushButton:pressed {
                            background-color: #007ACC;
                            color: #FFFFFF;
                        }
                        QPushButton:disabled {
                            background-color: #1E1E1E;
                            color: #666666;
                            border-color: #2D2D30;
                        }
                    """
                    )

                    # Podłącz sygnał z przekazaniem ścieżki
                    button.clicked.connect(
                        lambda checked, path=folder_path: self._on_folder_button_clicked(
                            path
                        )
                    )
                else:
                    button.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #1E1E1E;
                            color: #666666;
                            border: 1px solid #2D2D30;
                            border-radius: 4px;
                            font-size: 10px;
                            padding: 1px 4px;
                            text-align: center;
                        }
                        QPushButton:disabled {
                            background-color: #1E1E1E;
                            color: #666666;
                            border-color: #2D2D30;
                        }
                    """
                    )

                # Umieść przycisk w siatce: 3 rzędy po 3 kolumny
                row = (i - 1) // 3  # 0, 1 lub 2
                col = (i - 1) % 3   # 0, 1, 2
                buttons_layout.addWidget(button, row, col)

            buttons_frame.setLayout(buttons_layout)
            folder_layout.addWidget(buttons_frame)

        except Exception as e:
            logger.error(f"Błąd tworzenia panelu przycisków folderów: {e}")

    def _on_folder_button_clicked(self, folder_path):
        """Obsługuje kliknięcie przycisku folderu"""
        try:
            if not folder_path or not os.path.exists(folder_path):
                QMessageBox.warning(
                    self,
                    "Błąd",
                    f"Folder nie istnieje: {folder_path}",
                )
                return

            logger.info(f"Kliknięto przycisk folderu: {folder_path}")

            # Ustaw folder w drzewie
            self.set_root_folder(folder_path)

            # Uruchom skanowanie struktury folderów
            self._start_folder_scanning(folder_path)
            
            # Sprawdź foldery tekstur i zaktualizuj stan drag-and-drop
            self._update_drag_drop_state(folder_path)

        except Exception as e:
            logger.error(f"Błąd obsługi kliknięcia przycisku folderu: {e}")

    def _start_folder_scanning(self, folder_path: str):
        """Uruchamia skanowanie struktury folderów"""
        try:
            # Zatrzymaj poprzedni worker jeśli działa
            if hasattr(self, "folder_scanner_worker") and self.folder_scanner_worker.isRunning():
                self.folder_scanner_worker.quit()
                self.folder_scanner_worker.wait()

            # Utwórz nowy worker
            self.folder_scanner_worker = FolderStructureScanner(folder_path)

            # Podłącz sygnały
            self.folder_scanner_worker.progress_updated.connect(self._on_folder_scan_progress)
            self.folder_scanner_worker.folder_found.connect(self._on_folder_found)
            self.folder_scanner_worker.assets_folder_found.connect(self._on_assets_folder_found)
            self.folder_scanner_worker.scanner_started.connect(self._on_scanner_started)
            self.folder_scanner_worker.scanner_finished.connect(self._on_scanner_finished)
            self.folder_scanner_worker.finished_scanning.connect(self._on_finished_scanning)
            self.folder_scanner_worker.error_occurred.connect(self._on_scan_error)

            # Uruchom worker
            self.folder_scanner_worker.start()

        except Exception as e:
            logger.error(f"Błąd uruchamiania skanowania folderów: {e}")

    def _on_folder_found(self, folder_path: str, level: int):
        """Obsługuje znalezienie folderu - teraz tylko loguje, bo drzewo jest systemowe"""
        try:
            logger.debug(f"Znaleziono folder: {folder_path} (poziom: {level})")
            # Nie musimy już tworzyć przycisków, bo drzewo jest systemowe
        except Exception as e:
            logger.error(f"Błąd obsługi znalezienia folderu: {e}")

    def _on_folder_scan_progress(self, progress: int):
        """Obsługuje postęp skanowania folderów"""
        try:
            self.progress_bar.setValue(progress)
        except Exception as e:
            logger.error(f"Błąd aktualizacji postępu skanowania folderów: {e}")

    def _on_scanner_started(self, folder_path: str):
        """Obsługuje rozpoczęcie skanowania folderu"""
        try:
            logger.info(f"Rozpoczęto skanowanie folderu: {folder_path}")
        except Exception as e:
            logger.error(f"Błąd obsługi rozpoczęcia skanowania folderu: {e}")

    def _on_scanner_finished(self, folder_path: str):
        """Obsługuje zakończenie skanowania folderu"""
        try:
            logger.info(f"Skanowanie folderu zakończone: {folder_path}")
        except Exception as e:
            logger.error(f"Błąd obsługi zakończenia skanowania folderu: {e}")

    def _on_finished_scanning(self):
        """Obsługuje zakończenie skanowania folderów"""
        try:
            self.progress_bar.setValue(0)
            logger.info("Skanowanie struktury folderów zakończone")
        except Exception as e:
            logger.error(f"Błąd finalizacji skanowania folderów: {e}")

    def _on_scan_error(self, error_message: str):
        """Obsługuje błędy skanowania folderów"""
        try:
            self.progress_bar.setValue(0)
            self._show_error_message(error_message)
        except Exception as e:
            logger.error(f"Błąd obsługi błędu skanowania folderów: {e}")

    def _on_tree_item_clicked(self, index: QModelIndex):
        """Obsługuje kliknięcie elementu w drzewie folderów"""
        try:
            item = self.folder_model.itemFromIndex(index)
            if item and hasattr(item, 'folder_path'):
                folder_path = item.folder_path
                if os.path.isdir(folder_path):
                    # Jeśli nie ma jeszcze dzieci, załaduj podfoldery
                    if item.rowCount() == 0:
                        self._load_subfolders(item, folder_path)
                        self._expand_first_level_subfolders(index)
                    logger.info(f"Kliknięto folder w drzewie: {folder_path}")
                    self._on_folder_click(folder_path)
        except Exception as e:
            logger.error(f"Błąd obsługi kliknięcia w drzewie: {e}")

    def _on_tree_drag_enter(self, event):
        """Obsługuje wejście drag nad drzewem folderów"""
        try:
            if event.mimeData().hasFormat("application/x-cfab-asset"):
                event.acceptProposedAction()
                # Poprawka: QDragEnterEvent nie ma pos(), użyj position()
                pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                self._highlight_folder_at_position(pos)
        except Exception as e:
            logger.error(f"Błąd obsługi drag enter w drzewie: {e}")
            event.ignore()

    def _on_tree_drag_leave(self, event):
        """Obsługuje wyjście drag z drzewa folderów"""
        try:
            # Usuń podświetlenie
            self._clear_folder_highlight()
        except Exception as e:
            logger.error(f"Błąd obsługi drag leave w drzewie: {e}")

    def _on_tree_drag_move(self, event):
        """Obsługuje przeciąganie elementów w drzewie folderów"""
        try:
            if event.mimeData().hasFormat("application/x-cfab-asset"):
                event.acceptProposedAction()
                pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                self._highlight_folder_at_position(pos)
        except Exception as e:
            logger.error(f"Błąd obsługi drag move w drzewie: {e}")
            event.ignore()

    def _on_tree_drop(self, event):
        """Obsługuje drop na drzewie folderów"""
        try:
            if event.mimeData().hasFormat("application/x-cfab-asset"):
                pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                index = self.folder_tree_view.indexAt(pos)
                if index.isValid():
                    item = self.folder_model.itemFromIndex(index)
                    if item and hasattr(item, 'folder_path'):
                        folder_path = item.folder_path
                        if os.path.isdir(folder_path):
                            # Obsłuż drop asset-a do folderu
                            self._handle_asset_drop_to_folder(folder_path, event.mimeData())
                            event.acceptProposedAction()
                # Usuń podświetlenie po drop
                self._clear_folder_highlight()
        except Exception as e:
            logger.error(f"Błąd obsługi drop w drzewie: {e}")

    def _highlight_folder_at_position(self, pos):
        """Podświetla folder pod określoną pozycją"""
        try:
            index = self.folder_tree_view.indexAt(pos)
            if index.isValid():
                self._clear_folder_highlight()
                item = self.folder_model.itemFromIndex(index)
                if item:
                    item.setData(True, Qt.ItemDataRole.UserRole + 1)
                    self._highlighted_index = index
        except Exception as e:
            logger.error(f"Błąd podświetlania folderu: {e}")

    def _clear_folder_highlight(self):
        """Usuwa podświetlenie folderu (usuwa property dropTarget)"""
        try:
            if hasattr(self, '_highlighted_index') and self._highlighted_index:
                item = self.folder_model.itemFromIndex(self._highlighted_index)
                if item:
                    item.setData(False, Qt.ItemDataRole.UserRole + 1)
                self._highlighted_index = None
        except Exception as e:
            logger.error(f"Błąd usuwania podświetlenia: {e}")

    def _handle_asset_drop_to_folder(self, folder_path: str, mime_data):
        """Obsługuje drop asset-a do folderu"""
        try:
            import shutil
            asset_data_bytes = mime_data.data("application/x-cfab-asset")
            asset_data = json.loads(asset_data_bytes.data().decode("utf-8"))

            logger.info(f"Drop asset-a '{asset_data.get('name', 'Unknown')}' do folderu: {folder_path}")

            # Lista plików do przeniesienia
            files_to_move = []
            current_folder = self.grid_manager.current_folder_path
            if not current_folder:
                self._show_error_message("Nie można ustalić folderu źródłowego asseta!")
                return

            # Plik .asset
            asset_file = os.path.join(current_folder, asset_data.get("name", "") + ".asset")
            if os.path.exists(asset_file):
                files_to_move.append(asset_file)
            # Plik archiwum
            archive_file = os.path.join(current_folder, asset_data.get("archive", ""))
            if os.path.exists(archive_file):
                files_to_move.append(archive_file)
            # Plik podglądu
            preview_file = os.path.join(current_folder, asset_data.get("preview", ""))
            if os.path.exists(preview_file):
                files_to_move.append(preview_file)
            # Plik thumb (w .cache)
            thumb_file = None
            if asset_data.get("thumbnail") is True:
                cache_folder = os.path.join(current_folder, ".cache")
                thumb_file = os.path.join(cache_folder, asset_data.get("name", "") + ".thumb")
                if os.path.exists(thumb_file):
                    files_to_move.append(thumb_file)

            # Przenoszenie plików
            errors = []
            for file_path in files_to_move:
                try:
                    dest_folder = folder_path
                    # Jeśli thumb, to przenieś do .cache w folderze docelowym
                    if thumb_file and file_path == thumb_file:
                        dest_folder = os.path.join(folder_path, ".cache")
                        os.makedirs(dest_folder, exist_ok=True)
                    shutil.move(file_path, dest_folder)
                except Exception as e:
                    errors.append(f"{os.path.basename(file_path)}: {e}")

            if errors:
                self._show_error_message("Błędy podczas przenoszenia plików:\n" + "\n".join(errors))
            else:
                # Odśwież galerię - użyj aktualnego folderu galerii, nie konfiguracji
                current_folder = self.grid_manager.current_folder_path
                if current_folder:
                    self._refresh_gallery_for_folder(current_folder)
                else:
                    logger.warning("Brak aktualnego folderu galerii do odświeżenia")
                
                # Opcjonalnie: odśwież docelowy folder jeśli jest wyświetlany
                logger.info(f"Przeniesiono asset '{asset_data.get('name', 'Unknown')}' do {folder_path}")
        except Exception as e:
            logger.error(f"Błąd obsługi drop asset-a: {e}")
            self._show_error_message(f"Błąd przenoszenia asseta: {e}")

    def set_root_folder(self, folder_path: str):
        """Ustawia główny folder w drzewie"""
        try:
            if folder_path and os.path.exists(folder_path):
                # Wyczyść model
                self.folder_model.clear()
                
                # Dodaj główny folder
                root_item = self._create_folder_item(folder_path)
                self.folder_model.appendRow(root_item)
                
                # Rozwiń główny folder
                root_index = self.folder_model.indexFromItem(root_item)
                self.folder_tree_view.expand(root_index)
                
                # Załaduj podfoldery
                self._load_subfolders(root_item, folder_path)
                
                # Automatycznie rozwiń pierwszy poziom podfolderów
                self._expand_first_level_subfolders(root_index)
                
                logger.info(f"Ustawiono główny folder w drzewie: {folder_path}")
            else:
                # Wyczyść drzewo
                self.folder_model.clear()
                logger.warning(f"Nieprawidłowa ścieżka folderu: {folder_path}")
        except Exception as e:
            logger.error(f"Błąd ustawiania głównego folderu: {e}")

    def _create_folder_item(self, folder_path: str) -> QStandardItem:
        """Tworzy element drzewa dla folderu"""
        try:
            folder_name = os.path.basename(folder_path)
            item = QStandardItem(f"📁 {folder_name}")
            item.folder_path = folder_path  # Dodaj ścieżkę jako atrybut
            item.setEditable(False)
            item.setDropEnabled(True)  # Włącz drop na itemie
            return item
        except Exception as e:
            logger.error(f"Błąd tworzenia elementu folderu: {e}")
            return QStandardItem("Error")

    def _load_subfolders(self, parent_item: QStandardItem, folder_path: str):
        """Ładuje podfoldery do elementu drzewa"""
        try:
            if not os.path.exists(folder_path):
                logger.warning(f"Folder nie istnieje: {folder_path}")
                return
                
            logger.info(f"Ładowanie podfolderów dla: {folder_path}")
            
            # Pobierz listę podfolderów
            subfolders = []
            for item_name in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item_name)
                if os.path.isdir(item_path) and not item_name.startswith('.'):
                    subfolders.append((item_name, item_path))
            
            logger.info(f"Znaleziono {len(subfolders)} podfolderów: {[name for name, path in subfolders]}")
            
            # Sortuj alfabetycznie
            subfolders.sort(key=lambda x: x[0].lower())
            
            # Dodaj podfoldery do drzewa
            for folder_name, subfolder_path in subfolders:
                subfolder_item = self._create_folder_item(subfolder_path)
                parent_item.appendRow(subfolder_item)
                logger.debug(f"Dodano podfolder: {folder_name} -> {subfolder_path}")
                
                # Rekurencyjnie załaduj podfoldery (opcjonalnie)
                # self._load_subfolders(subfolder_item, subfolder_path)
                
            logger.info(f"Załadowano {len(subfolders)} podfolderów dla: {folder_path}")
            
        except Exception as e:
            logger.error(f"Błąd ładowania podfolderów: {e}")

    def _expand_first_level_subfolders(self, parent_index: QModelIndex):
        """Rozwija pierwszy poziom podfolderów"""
        try:
            # Poczekaj chwilę na załadowanie modelu
            import time
            time.sleep(0.1)
            
            item = self.folder_model.itemFromIndex(parent_index)
            if item:
                row_count = item.rowCount()
                logger.debug(f"Znaleziono {row_count} elementów w folderze")
                
                for row in range(row_count):
                    child_item = item.child(row)
                    if child_item and hasattr(child_item, 'folder_path'):
                        child_index = self.folder_model.indexFromItem(child_item)
                        self.folder_tree_view.expand(child_index)
                        logger.debug(f"Rozwinięto podfolder: {child_item.folder_path}")
                        
        except Exception as e:
            logger.error(f"Błąd rozwijania podfolderów: {e}")

    def _force_load_subfolders(self, folder_path: str):
        """Wymusza ładowanie wszystkich podfolderów"""
        try:
            # Sprawdź czy folder istnieje
            if not os.path.exists(folder_path):
                return
                
            # Pobierz listę wszystkich podfolderów
            subfolders = []
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    subfolders.append(item_path)
            
            logger.info(f"Znaleziono {len(subfolders)} podfolderów w {folder_path}")
            
            # Podfoldery są już ładowane w _load_subfolders
                
        except Exception as e:
            logger.error(f"Błąd wymuszania ładowania podfolderów: {e}")

    def _on_folder_click(self, folder_path: str):
        """Obsługuje kliknięcie w folder - wywołuje handle_folder_click workera"""
        try:
            logger.info(f"Kliknięto folder: {folder_path}")

            # Wywołaj handle_folder_click workera
            if hasattr(self, "folder_scanner_worker") and self.folder_scanner_worker:
                self.folder_scanner_worker.handle_folder_click(folder_path)
            else:
                logger.warning("Folder scanner worker nie jest dostępny")

        except Exception as e:
            logger.error(f"Błąd obsługi kliknięcia folderu: {e}")
            self._show_error_message(f"Błąd obsługi folderu: {e}")

    def _on_assets_folder_found(self, folder_path: str):
        """Obsługuje znalezienie folderu z plikami asset - wyświetla w galerii"""
        try:
            logger.info(f"Wyświetlanie assetów z folderu: {folder_path}")

            # Zatrzymaj poprzedni asset scanner jeśli działa
            if hasattr(self, "scanner") and self.scanner and self.scanner.isRunning():
                self.scanner.quit()
                self.scanner.wait()

            # Utwórz i uruchom asset scanner dla tego folderu
            self.scanner = AssetScanner(folder_path)
            self.scanner.progress_updated.connect(self._on_scan_progress)
            self.scanner.assets_found.connect(self._on_assets_found)
            self.scanner.finished_scanning.connect(self._on_scan_finished)
            self.scanner.error_occurred.connect(self._on_scan_error)

            self.scanner.start()

        except Exception as e:
            logger.error(f"Błąd wyświetlania assetów z folderu: {e}")

    def _rebuild_assets_in_folder(self, folder_path: str):
        """Przebudowuje assety w wybranym folderze"""
        try:
            # Pokaż dialog potwierdzenia
            reply = QMessageBox.question(
                self,
                "Potwierdzenie przebudowy",
                f"Czy na pewno chcesz przebudować assety w folderze:\n{folder_path}\n\n"
                "Ta operacja usunie wszystkie pliki .asset, folder .cache i uruchomi ponowne skanowanie.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Zatrzymaj poprzedni worker jeśli działa
                if hasattr(self, "asset_rebuilder") and self.asset_rebuilder and self.asset_rebuilder.isRunning():
                    self.asset_rebuilder.quit()
                    self.asset_rebuilder.wait()

                # Utwórz nowy worker dla przebudowy
                self.asset_rebuilder = AssetRebuilderThread(folder_path)
                
                # Podłącz sygnały
                self.asset_rebuilder.progress_updated.connect(self._on_rebuild_progress)
                self.asset_rebuilder.rebuild_finished.connect(self._on_rebuild_finished)
                self.asset_rebuilder.error_occurred.connect(self._on_rebuild_error)
                
                # Uruchom worker
                self.asset_rebuilder.start()
                
                logger.info(f"Rozpoczęto przebudowę assetów w folderze: {folder_path}")
                
        except Exception as e:
            logger.error(f"Błąd inicjalizacji przebudowy assetów: {e}")
            QMessageBox.critical(
                self,
                "Błąd przebudowy",
                f"Wystąpił błąd podczas inicjalizacji przebudowy:\n{str(e)}"
            )

    def _on_rebuild_progress(self, current: int, total: int, message: str):
        """Obsługuje postęp przebudowy assetów"""
        try:
            if total > 0:
                progress = int((current / total) * 100)
                self.progress_bar.setValue(progress)
            
            logger.debug(f"Postęp przebudowy: {message}")
        except Exception as e:
            logger.error(f"Błąd aktualizacji postępu przebudowy: {e}")

    def _on_rebuild_finished(self, message: str):
        """Obsługuje zakończenie przebudowy assetów"""
        try:
            self.progress_bar.setValue(0)
            
            QMessageBox.information(
                self,
                "Przebudowa zakończona",
                message
            )
            
            # Odśwież galerię jeśli aktualny folder został przebudowany
            if (hasattr(self, 'grid_manager') and self.grid_manager and 
                hasattr(self.grid_manager, 'current_folder_path') and 
                self.grid_manager.current_folder_path):
                current_folder = self.grid_manager.current_folder_path
                self._refresh_gallery_for_folder(current_folder)
            
            logger.info(f"Przebudowa zakończona: {message}")
        except Exception as e:
            logger.error(f"Błąd obsługi zakończenia przebudowy: {e}")

    def _on_rebuild_error(self, error_message: str):
        """Obsługuje błędy przebudowy assetów"""
        try:
            self.progress_bar.setValue(0)
            
            QMessageBox.critical(
                self,
                "Błąd przebudowy",
                f"Wystąpił błąd podczas przebudowy assetów:\n{error_message}"
            )
            
            logger.error(f"Błąd przebudowy assetów: {error_message}")
        except Exception as e:
            logger.error(f"Błąd obsługi błędu przebudowy: {e}")

    def _check_texture_folders_presence(self, folder_path: str) -> bool:
        """Sprawdza obecność folderów tekstur w folderze roboczym"""
        try:
            if not folder_path or not os.path.exists(folder_path):
                return False
                
            texture_folder_names = ["tex", "textures", "maps"]
            
            for folder_name in texture_folder_names:
                texture_folder_path = os.path.join(folder_path, folder_name)
                if os.path.isdir(texture_folder_path):
                    logger.debug(f"Znaleziono folder tekstur: {folder_name} w {folder_path}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Błąd sprawdzania folderów tekstur: {e}")
            return False

    def _update_drag_drop_state(self, folder_path: str):
        """Aktualizuje stan drag-and-drop na podstawie obecności folderów tekstur"""
        try:
            has_texture_folders = self._check_texture_folders_presence(folder_path)
            
            # Dezaktywuj/aktywuj drag-and-drop w drzewie folderów
            if hasattr(self, 'folder_tree_view'):
                self.folder_tree_view.setAcceptDrops(not has_texture_folders)
                if has_texture_folders:
                    logger.info(f"Drag-and-drop wyłączone - znaleziono foldery tekstur w {folder_path}")
                else:
                    logger.info(f"Drag-and-drop włączone - brak folderów tekstur w {folder_path}")
            
            # Dezaktywuj/aktywuj przyciski masowego przenoszenia
            if hasattr(self, 'move_selected_button'):
                self.move_selected_button.setEnabled(not has_texture_folders)
                if has_texture_folders:
                    self.move_selected_button.setToolTip("Funkcja niedostępna - folder zawiera tekstury")
                else:
                    self.move_selected_button.setToolTip("Przenieś zaznaczone assety do innego folderu")
                    
        except Exception as e:
            logger.error(f"Błąd aktualizacji stanu drag-and-drop: {e}")


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = GalleryTab()
    w.show()
    sys.exit(app.exec())
