import json
import logging
import os
from pathlib import Path

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
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
    QVBoxLayout,
    QWidget,
)

from core.folder_scanner_worker import FolderStructureScanner
from core.thumbnail_tile import ThumbnailTile

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

        # Debouncing timer
        self.grid_recreation_timer = QTimer()
        self.grid_recreation_timer.setSingleShot(True)
        self.grid_recreation_timer.timeout.connect(self._delayed_grid_recreation)
        self.grid_recreation_delay = 100  # 100ms delay

        # Cache dla column calculation
        self._last_width = 0
        self._last_tile_size = 0
        self._cached_columns = 4

    def request_grid_recreation(self, assets, thumbnail_size):
        """
        Żąda recreacji grid z debouncing

        Args:
            assets (list): Lista assetów
            thumbnail_size (int): Rozmiar kafelków
        """
        self.pending_assets = assets
        self.pending_thumbnail_size = thumbnail_size

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
        """Oblicza kolumny z cache'owaniem dla performance"""
        current_width = self.scroll_area.width()

        # Użyj cache jeśli parametry się nie zmieniły
        if current_width == self._last_width and thumbnail_size == self._last_tile_size:
            return self._cached_columns

        # Oblicz nową wartość
        available_width = current_width - 40  # marginesy
        tile_width = thumbnail_size + 20  # padding

        columns = max(
            1, (available_width + self.tile_spacing) // (tile_width + self.tile_spacing)
        )

        # Zapisz do cache
        self._last_width = current_width
        self._last_tile_size = thumbnail_size
        self._cached_columns = columns

        return columns

    def _create_asset_tile_safe(self, asset, tile_number, total_tiles, thumbnail_size):
        """Bezpiecznie tworzy kafelek asset"""
        try:
            display_name = f"{asset['name']} ({asset['size_mb']:.1f} MB)"
            tile = ThumbnailTile(thumbnail_size, display_name, tile_number, total_tiles)

            # Ustaw gwiazdki jeśli są w asset
            if asset.get("stars") is not None:
                tile.set_star_rating(asset["stars"])

            # Załaduj thumbnail z .cache jeśli dostępny
            if asset.get("thumbnail") is True:
                work_folder = self._get_work_folder_path()
                if work_folder:
                    cache_folder = os.path.join(work_folder, ".cache")
                    asset_name = asset["name"]
                    tile.load_thumbnail_from_cache(asset_name, cache_folder)

            return tile

        except Exception as e:
            logger.error(
                f"Błąd tworzenia kafelka dla {asset.get('name', 'unknown')}: {e}"
            )
            return None

    def _get_work_folder_path(self):
        """Pobiera ścieżkę work_folder z parent GalleryTab"""
        # Pobierz z parent window poprzez callback
        if hasattr(self, "work_folder_callback") and self.work_folder_callback:
            return self.work_folder_callback()
        return ""

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

            # Bezpieczne skanowanie plików
            asset_files = self._scan_asset_files()

            if not asset_files:
                logger.info("Nie znaleziono plików .asset w folderze")
                self.finished_scanning.emit()
                return

            logger.info(f"Znaleziono {len(asset_files)} plików .asset")

            # Przetwarzaj każdy plik asset z progress tracking
            self._process_asset_files(asset_files)

        except Exception as e:
            error_msg = f"Nieoczekiwany błąd podczas skanowania: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
        finally:
            self.finished_scanning.emit()

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

        # Setup UI i połączenia
        try:
            self._setup_ui()
            self._initialize_grid_manager()
            self._connect_signals()
            self._start_asset_scanning()
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
            # Przekaż callback do pobierania work_folder_path
            self.grid_manager.work_folder_callback = lambda: self.work_folder_path
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
        self.splitter.setSizes([200, 800])  # 20:80 ratio

    def _create_folder_panel(self):
        """Tworzy lewy panel folderów"""
        self.folder_tree_panel = QFrame()
        self.folder_tree_panel.setFrameStyle(QFrame.Shape.Box)
        self.folder_tree_panel.setMinimumWidth(200)
        self.folder_tree_panel.setMaximumWidth(300)

        folder_layout = QVBoxLayout()
        folder_layout.addWidget(QLabel("Drzewo folderów"))

        # Scroll area dla struktury folderów
        self.folder_scroll_area = QScrollArea()
        self.folder_scroll_area.setWidgetResizable(True)
        self.folder_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.folder_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Widget dla struktury folderów
        self.folder_structure_widget = QWidget()
        self.folder_structure_layout = QVBoxLayout()
        self.folder_structure_layout.setContentsMargins(5, 5, 5, 5)
        self.folder_structure_layout.setSpacing(2)

        # Początkowy komunikat
        initial_label = QLabel("Wybierz folder aby wyświetlić strukturę")
        initial_label.setStyleSheet(
            """
            QLabel {
                color: #888888;
                font-size: 11px;
                padding: 10px;
            }
        """
        )
        self.folder_structure_layout.addWidget(initial_label)
        self.folder_structure_layout.addStretch()

        self.folder_structure_widget.setLayout(self.folder_structure_layout)
        self.folder_scroll_area.setWidget(self.folder_structure_widget)

        folder_layout.addWidget(self.folder_scroll_area)

        # Dodanie przycisków folderów na dole
        self._create_folder_buttons(folder_layout)

        self.folder_tree_panel.setLayout(folder_layout)
        self.splitter.addWidget(self.folder_tree_panel)

    def _create_gallery_panel(self):
        """Tworzy prawy panel galerii"""
        self.gallery_panel = QFrame()
        self.gallery_panel.setFrameStyle(QFrame.Shape.Box)

        gallery_vertical_layout = QVBoxLayout()
        gallery_vertical_layout.setSpacing(4)
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
        self.control_panel.setFixedHeight(18)
        self.control_panel.setStyleSheet(
            """
            QFrame {
                background-color: #252526;
                border-top: 1px solid #3F3F46;
            }
        """
        )

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(8, 2, 8, 2)
        control_layout.setSpacing(8)

        # Progress bar
        self._create_progress_bar()

        # Thumbnail size slider
        self._create_thumbnail_slider()

        control_layout.addWidget(self.progress_bar, 1)
        control_layout.addWidget(self.thumbnail_size_slider, 1)

        self.control_panel.setLayout(control_layout)

    def _connect_signals(self):
        """Podłącza sygnały z thread safety"""
        try:
            # Slider signal
            self.thumbnail_size_slider.valueChanged.connect(self._on_slider_changed)

        except Exception as e:
            logger.error(f"Błąd podłączania sygnałów: {e}")

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

    def _on_scan_progress(self, progress: int):
        """Obsługuje aktualizację postępu skanowania - thread safe"""
        try:
            self.progress_bar.setValue(progress)
        except Exception as e:
            logger.error(f"Błąd aktualizacji postępu: {e}")

    def _on_assets_found(self, assets: list):
        """Obsługuje znalezione asset-y - thread safe"""
        try:
            self.assets = assets
            logger.info(f"Znaleziono {len(assets)} asset-ów")
        except Exception as e:
            logger.error(f"Błąd przetwarzania znalezionych assetów: {e}")

    def _on_scan_finished(self):
        """Obsługuje zakończenie skanowania - thread safe"""
        try:
            self.progress_bar.setValue(0)
            if self.grid_manager:
                current_size = self.thumbnail_size_slider.value()
                self.grid_manager.request_grid_recreation(self.assets, current_size)
        except Exception as e:
            logger.error(f"Błąd finalizacji skanowania: {e}")

    def _on_scan_error(self, error_message: str):
        """Obsługuje błędy skanowania - thread safe"""
        try:
            self.progress_bar.setValue(0)
            self._show_error_message(error_message)
        except Exception as e:
            logger.error(f"Błąd obsługi błędu skanowania: {e}")

    def _on_slider_changed(self, value):
        """Obsługuje zmianę wartości suwaka z debouncing"""
        try:
            if self.grid_manager and self.assets:
                # Update tile sizes immediately for responsive feedback
                self.grid_manager.update_tile_sizes_safe(value)

                # Request grid recreation with debouncing
                self.grid_manager.request_grid_recreation(self.assets, value)

        except Exception as e:
            logger.error(f"Błąd obsługi slidera: {e}")

    def resizeEvent(self, event):
        """Obsługuje zmianę rozmiaru okna z thread safety"""
        try:
            super().resizeEvent(event)

            # Tylko jeśli grid manager jest gotowy i mamy assety
            if (
                hasattr(self, "grid_manager")
                and self.grid_manager
                and hasattr(self, "assets")
                and self.assets
            ):

                current_size = self.thumbnail_size_slider.value()
                self.grid_manager.request_grid_recreation(self.assets, current_size)

        except Exception as e:
            logger.error(f"Błąd resize event: {e}")

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
                border: 1px solid #3F3F46;
                background-color: #1C1C1C;
                text-align: center;
                color: #CCCCCC;
            }
            QProgressBar::chunk {
                background-color: #007ACC;
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
                border: 1px solid #3F3F46;
                height: 8px;
                background: #1C1C1C;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #007ACC;
                border: 1px solid #007ACC;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #1C97EA;
            }
        """
        )

    def _create_folder_buttons(self, folder_layout):
        """Tworzy 5 przycisków folderów na dole panelu"""
        try:
            config_manager = ConfigManager()
            config = config_manager.get_config()

            for i in range(1, 6):
                folder_key = f"work_folder{i}"
                folder_config = config.get(folder_key, {})
                folder_path = folder_config.get("path", "")
                folder_name = folder_config.get("name", f"Folder {i}")

                # Użyj nazwy jeśli jest dostępna, w przeciwnym razie domyślną
                button_text = folder_name if folder_name else f"Folder {i}"

                button = QPushButton(button_text)
                button.setFixedHeight(24)
                button.setEnabled(bool(folder_path))  # Aktywny tylko gdy jest ścieżka

                # Podłącz sygnał z przekazaniem ścieżki
                if folder_path:
                    button.clicked.connect(
                        lambda checked, path=folder_path: self._on_folder_button_clicked(
                            path
                        )
                    )

                folder_layout.addWidget(button)

        except Exception as e:
            logger.error(f"Błąd tworzenia przycisków folderów: {e}")

    def _on_folder_button_clicked(self, folder_path):
        """Obsługuje kliknięcie przycisku folderu - uruchamia skanowanie struktury"""
        try:
            logger.info(f"Skanowanie struktury folderu: {folder_path}")

            # Sprawdź czy ścieżka istnieje
            if not os.path.exists(folder_path):
                logger.warning(f"Ścieżka nie istnieje: {folder_path}")
                self._show_error_message(f"Folder nie istnieje: {folder_path}")
                return

            # Zatrzymaj poprzedni folder scanner jeśli działa
            if (
                hasattr(self, "folder_scanner")
                and self.folder_scanner
                and self.folder_scanner.isRunning()
            ):
                self.folder_scanner.quit()
                self.folder_scanner.wait()

            # Wyczyść strukturę folderów w lewym panelu
            self._clear_folder_structure()

            # Utwórz i uruchom folder scanner
            self.folder_scanner = FolderStructureScanner(folder_path)
            self.folder_scanner.progress_updated.connect(self._on_folder_scan_progress)
            self.folder_scanner.folder_found.connect(self._on_folder_found)
            self.folder_scanner.finished_scanning.connect(self._on_folder_scan_finished)
            self.folder_scanner.error_occurred.connect(self._on_folder_scan_error)

            self.folder_scanner.start()

        except Exception as e:
            logger.error(f"Błąd obsługi kliknięcia przycisku folderu: {e}")
            self._show_error_message(f"Błąd skanowania folderu: {e}")

    def _clear_folder_structure(self):
        """Czyści strukturę folderów w lewym panelu"""
        try:
            # Usuń wszystkie widgety z layoutu
            while self.folder_structure_layout.count():
                child = self.folder_structure_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Dodaj komunikat o ładowaniu
            loading_label = QLabel("Ładowanie struktury folderów...")
            loading_label.setStyleSheet(
                """
                QLabel {
                    color: #CCCCCC;
                    font-size: 11px;
                    padding: 5px;
                }
            """
            )
            self.folder_structure_layout.addWidget(loading_label)

        except Exception as e:
            logger.error(f"Błąd czyszczenia struktury folderów: {e}")

    def _on_folder_scan_progress(self, progress: int):
        """Obsługuje postęp skanowania folderów"""
        try:
            self.progress_bar.setValue(progress)
        except Exception as e:
            logger.error(f"Błąd aktualizacji postępu skanowania folderów: {e}")

    def _on_folder_found(self, folder_path: str, level: int):
        """Obsługuje znalezienie folderu - dodaje do lewego panelu"""
        try:
            folder_name = os.path.basename(folder_path)

            # Twórz wcięcie dla drzewa
            if level == 0:
                display_text = f"📁 {folder_name}"
            else:
                indent = "  " * (level - 1)
                display_text = f"{indent}└─ 📂 {folder_name}"

            folder_label = QLabel(display_text)
            folder_label.setStyleSheet(
                """
                QLabel {
                    color: #CCCCCC;
                    font-size: 10px;
                    padding: 1px 5px;
                    font-family: monospace;
                }
                QLabel:hover {
                    background-color: #3F3F46;
                }
            """
            )

            # Usuń komunikat o ładowaniu jeśli to pierwszy folder
            if level == 0 and self.folder_structure_layout.count() > 0:
                first_item = self.folder_structure_layout.itemAt(0)
                if first_item and first_item.widget():
                    first_item.widget().deleteLater()

            # Dodaj do layoutu
            self.folder_structure_layout.addWidget(folder_label)

        except Exception as e:
            logger.error(f"Błąd dodawania folderu do wyświetlania: {e}")

    def _on_folder_scan_finished(self):
        """Obsługuje zakończenie skanowania folderów"""
        try:
            self.progress_bar.setValue(0)

            # Dodaj stretch na końcu
            self.folder_structure_layout.addStretch()

            logger.info("Skanowanie struktury folderów zakończone")
        except Exception as e:
            logger.error(f"Błąd finalizacji skanowania folderów: {e}")

    def _on_folder_scan_error(self, error_message: str):
        """Obsługuje błędy skanowania folderów"""
        try:
            self.progress_bar.setValue(0)

            # Wyczyść i pokaż błąd w lewym panelu
            self._clear_folder_structure()
            error_label = QLabel(f"Błąd: {error_message}")
            error_label.setStyleSheet(
                """
                QLabel {
                    color: #FF6B6B;
                    font-size: 10px;
                    padding: 5px;
                }
            """
            )
            self.folder_structure_layout.addWidget(error_label)
            self.folder_structure_layout.addStretch()

        except Exception as e:
            logger.error(f"Błąd obsługi błędu skanowania folderów: {e}")


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = GalleryTab()
    w.show()
    sys.exit(app.exec())
