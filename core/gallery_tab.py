import json
import logging
import os
import subprocess
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
from core.thumbnail_tile import PreviewWindow, ThumbnailTile

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
                layout_margins = 16

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

    def _create_asset_tile_safe(self, asset, tile_number, total_tiles, thumbnail_size):
        """Bezpiecznie tworzy kafelek asset"""
        try:
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


class FolderButton(QPushButton):
    """Przycisk folderu z obsługą drag and drop"""

    def __init__(self, text, folder_path, parent=None):
        super().__init__(text, parent)
        self.folder_path = folder_path
        self.setAcceptDrops(True)

        # Normalny styl
        self.normal_style = """
            QPushButton {
                color: #CCCCCC;
                font-size: 11px;
                padding: 4px 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                text-align: left;
                border: none;
                background: transparent;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3F3F46;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #007ACC;
                color: #FFFFFF;
            }
        """

        # Styl podczas drag
        self.drag_style = """
            QPushButton {
                color: #FFFFFF;
                font-size: 11px;
                padding: 4px 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                text-align: left;
                border: 2px solid #007ACC;
                background-color: #007ACC;
                border-radius: 4px;
            }
        """

        self.setStyleSheet(self.normal_style)

    def dragEnterEvent(self, event):
        """Obsługa wejścia drag nad folderem"""
        try:
            print(f"DEBUG: dragEnterEvent - folder: {self.folder_path}")
            print(f"DEBUG: MIME formats: {event.mimeData().formats()}")

            # Sprawdź czy MIME data zawiera dane asset-a
            if event.mimeData().hasFormat("application/x-cfab-asset"):
                print(
                    f"DEBUG: Akceptuję drag - format application/x-cfab-asset znaleziony"
                )
                event.acceptProposedAction()
                # Podświetl przycisk
                self.setStyleSheet(self.drag_style)
            else:
                print(f"DEBUG: Ignoruję drag - brak formatu application/x-cfab-asset")
                event.ignore()
        except Exception as e:
            print(f"Błąd obsługi drag enter: {e}")
            logger.error(f"Błąd obsługi drag enter: {e}")
            event.ignore()

    def dragLeaveEvent(self, event):
        """Obsługa wyjścia drag z folderu"""
        try:
            print(f"DEBUG: dragLeaveEvent - folder: {self.folder_path}")
            # Przywróć normalny styl
            self.setStyleSheet(self.normal_style)
        except Exception as e:
            print(f"Błąd obsługi drag leave: {e}")
            logger.error(f"Błąd obsługi drag leave: {e}")

    def dropEvent(self, event):
        """Obsługa upuszczenia asset-a na folder"""
        try:
            print(f"DEBUG: dropEvent - folder: {self.folder_path}")
            print(f"DEBUG: MIME formats: {event.mimeData().formats()}")

            # Sprawdź czy MIME data zawiera dane asset-a
            if event.mimeData().hasFormat("application/x-cfab-asset"):
                print(
                    f"DEBUG: Przetwarzam drop - format application/x-cfab-asset znaleziony"
                )

                # Pobierz dane asset-a
                asset_data_bytes = event.mimeData().data("application/x-cfab-asset")
                asset_data = json.loads(asset_data_bytes.data().decode("utf-8"))
                print(f"DEBUG: Asset data: {asset_data.get('name', 'Unknown')}")

                # Emituj sygnał do parent widget
                if hasattr(self.parent(), "_on_folder_drop"):
                    print(f"DEBUG: Wywołuję _on_folder_drop")
                    self.parent()._on_folder_drop(asset_data, self.folder_path)
                else:
                    print(f"DEBUG: BŁĄD - parent nie ma metody _on_folder_drop")
                    # Spróbuj wywołać bezpośrednio na parent
                    try:
                        parent = self.parent()
                        if parent and hasattr(parent, "_on_folder_drop"):
                            parent._on_folder_drop(asset_data, self.folder_path)
                        else:
                            print(f"DEBUG: Parent type: {type(parent)}")
                            print(
                                f"DEBUG: Parent methods: {dir(parent) if parent else 'None'}"
                            )
                    except Exception as e:
                        print(f"DEBUG: Błąd wywołania _on_folder_drop: {e}")

                event.acceptProposedAction()
            else:
                print(f"DEBUG: Ignoruję drop - brak formatu application/x-cfab-asset")
                event.ignore()

        except Exception as e:
            print(f"Błąd obsługi drop: {e}")
            logger.error(f"Błąd obsługi drop: {e}")
            event.ignore()

        finally:
            # Przywróć normalny styl
            self.setStyleSheet(self.normal_style)


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
        """Tworzy lewy panel folderów z profesjonalnym wyglądem"""
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
                font-size: 16px;
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

        # Scroll area dla struktury folderów
        self.folder_scroll_area = QScrollArea()
        self.folder_scroll_area.setWidgetResizable(True)
        self.folder_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.folder_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.folder_scroll_area.setStyleSheet(
            """
            QScrollArea {
                background-color: #1E1E1E;
                border: none;
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

        # Widget dla struktury folderów
        self.folder_structure_widget = QWidget()
        self.folder_structure_layout = QVBoxLayout()
        self.folder_structure_layout.setContentsMargins(8, 8, 8, 8)
        self.folder_structure_layout.setSpacing(2)

        # Początkowy komunikat
        initial_label = QLabel("Wybierz folder aby wyświetlić strukturę")
        initial_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        initial_label.setStyleSheet(
            """
            QLabel {
                color: #888888;
                font-size: 11px;
                padding: 20px;
                background-color: #252526;
                border-radius: 6px;
                margin: 8px;
            }
        """
        )
        self.folder_structure_layout.addWidget(initial_label)
        self.folder_structure_layout.addStretch()

        self.folder_structure_widget.setLayout(self.folder_structure_layout)
        self.folder_scroll_area.setWidget(self.folder_structure_widget)

        folder_layout.addWidget(self.folder_scroll_area)

        # Panel przycisków folderów na dole
        self._create_folder_buttons_panel(folder_layout)

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
        """Obsługuje znalezienie asset-ów - aktualizuje galerię"""
        try:
            self.assets = assets
            current_size = self.thumbnail_size_slider.value()

            # Przekaż ścieżkę do folderu z assetami
            folder_path = getattr(self.scanner, "work_folder_path", "")
            self.grid_manager.request_grid_recreation(
                self.assets, current_size, folder_path
            )

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

            buttons_layout = QVBoxLayout()
            buttons_layout.setContentsMargins(8, 8, 8, 8)
            buttons_layout.setSpacing(4)

            # Nagłówek przycisków
            buttons_header = QLabel("Szybki dostęp")
            buttons_header.setStyleSheet(
                """
                QLabel {
                    color: #CCCCCC;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px 0px;
                }
            """
            )
            buttons_layout.addWidget(buttons_header)

            config_manager = ConfigManager()
            config = config_manager.get_config()

            for i in range(1, 6):
                folder_key = f"work_folder{i}"
                folder_config = config.get(folder_key, {})
                folder_path = folder_config.get("path", "")
                folder_name = folder_config.get("name", f"Folder {i}")

                # Użyj nazwy jeśli jest dostępna, w przeciwnym razie domyślną
                button_text = folder_name if folder_name else f"Folder {i}"

                button = FolderButton(button_text, folder_path, self)
                button.setFixedHeight(22)
                button.setEnabled(bool(folder_path))

                # Włącz obsługę drag and drop dla przycisków folderów w strukturze
                button.setAcceptDrops(True)
                button.dragEnterEvent = (
                    lambda event, path=folder_path: self._on_folder_drag_enter(
                        event, path
                    )
                )
                button.dragLeaveEvent = (
                    lambda event, path=folder_path: self._on_folder_drag_leave(
                        event, path
                    )
                )
                button.dropEvent = (
                    lambda event, path=folder_path: self._on_folder_drop_event(
                        event, path
                    )
                )

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
                            padding: 4px 8px;
                            text-align: left;
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
                            padding: 4px 8px;
                            text-align: left;
                        }
                        QPushButton:disabled {
                            background-color: #1E1E1E;
                            color: #666666;
                            border-color: #2D2D30;
                        }
                    """
                    )

                buttons_layout.addWidget(button)

            buttons_frame.setLayout(buttons_layout)
            folder_layout.addWidget(buttons_frame)

        except Exception as e:
            logger.error(f"Błąd tworzenia panelu przycisków folderów: {e}")

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
            self.folder_scanner.assets_folder_found.connect(
                self._on_assets_folder_found
            )
            self.folder_scanner.subfolders_only_found.connect(
                self._on_subfolders_only_found
            )
            self.folder_scanner.scanner_started.connect(self._on_scanner_started)
            self.folder_scanner.scanner_finished.connect(self._on_scanner_finished)
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
        """Obsługuje znalezienie folderu - dodaje klikalny przycisk do lewego panelu"""
        try:
            folder_name = os.path.basename(folder_path)

            # Twórz wcięcie dla drzewa
            if level == 0:
                display_text = f"📁 {folder_name}"
            else:
                indent = "  " * (level - 1)
                display_text = f"{indent}└─ 📂 {folder_name}"

            # Twórz klikalny przycisk zamiast QLabel
            folder_button = FolderButton(display_text, folder_path, self)
            folder_button.setFixedHeight(24)

            # Włącz obsługę drag and drop dla przycisków folderów w strukturze
            folder_button.setAcceptDrops(True)
            folder_button.dragEnterEvent = (
                lambda event, path=folder_path: self._on_folder_drag_enter(event, path)
            )
            folder_button.dragLeaveEvent = (
                lambda event, path=folder_path: self._on_folder_drag_leave(event, path)
            )
            folder_button.dropEvent = (
                lambda event, path=folder_path: self._on_folder_drop_event(event, path)
            )

            # Podłącz kliknięcie do handle_folder_click workera
            folder_button.clicked.connect(
                lambda checked, path=folder_path: self._on_folder_click(path)
            )

            # Usuń komunikat o ładowaniu jeśli to pierwszy folder
            if level == 0 and self.folder_structure_layout.count() > 0:
                first_item = self.folder_structure_layout.itemAt(0)
                if first_item and first_item.widget():
                    first_item.widget().deleteLater()

            # Dodaj do layoutu
            self.folder_structure_layout.addWidget(folder_button)

        except Exception as e:
            logger.error(f"Błąd dodawania folderu do wyświetlania: {e}")

    def _on_folder_click(self, folder_path: str):
        """Obsługuje kliknięcie w folder w strukturze - wywołuje handle_folder_click workera"""
        try:
            logger.info(f"Kliknięto folder w strukturze: {folder_path}")

            # Wywołaj handle_folder_click workera
            if hasattr(self, "folder_scanner") and self.folder_scanner:
                self.folder_scanner.handle_folder_click(folder_path)
            else:
                logger.warning("Folder scanner nie jest dostępny")

        except Exception as e:
            logger.error(f"Błąd obsługi kliknięcia folderu: {e}")
            self._show_error_message(f"Błąd obsługi folderu: {e}")

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

    def _on_subfolders_only_found(self, folder_path: str):
        """Obsługuje znalezienie folderu tylko z podfolderami - czeka na reakcję"""
        try:
            logger.info(f"Folder zawiera tylko podfoldery: {folder_path}")

            # Można tutaj dodać logikę oczekiwania na reakcję użytkownika
            # Na razie logujemy informację

        except Exception as e:
            logger.error(f"Błąd obsługi folderu z podfolderami: {e}")

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

    def _on_folder_drag_enter(self, event, folder_path):
        """Obsługa wejścia drag nad folderem"""
        try:
            # Sprawdź czy MIME data zawiera dane asset-a
            if event.mimeData().hasFormat("application/x-cfab-asset"):
                event.acceptProposedAction()

                # Podświetl przycisk folderu - znajdź widget po ścieżce
                widget = self._find_folder_button_by_path(folder_path)

                if widget:
                    widget.setStyleSheet(
                        """
                        QPushButton {
                            color: #FFFFFF;
                            font-size: 11px;
                            padding: 4px 8px;
                            font-family: 'Segoe UI', Arial, sans-serif;
                            text-align: left;
                            border: 2px solid #007ACC;
                            background-color: #007ACC;
                            border-radius: 4px;
                        }
                    """
                    )
            else:
                event.ignore()
        except Exception as e:
            logger.error(f"Błąd obsługi drag enter: {e}")
            event.ignore()

    def _on_folder_drag_leave(self, event, folder_path):
        """Obsługa wyjścia drag z folderu"""
        try:
            # Przywróć normalny styl przycisku - znajdź widget po ścieżce
            widget = self._find_folder_button_by_path(folder_path)

            if widget:
                widget.setStyleSheet(
                    """
                    QPushButton {
                        color: #CCCCCC;
                        font-size: 11px;
                        padding: 4px 8px;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        text-align: left;
                        border: none;
                        background: transparent;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #3F3F46;
                        color: #FFFFFF;
                    }
                    QPushButton:pressed {
                        background-color: #007ACC;
                        color: #FFFFFF;
                    }
                """
                )
        except Exception as e:
            logger.error(f"Błąd obsługi drag leave: {e}")

    def _find_folder_button_by_path(self, folder_path):
        """Znajduje przycisk folderu po ścieżce"""
        try:
            # Sprawdź w panelu szybkiego dostępu (folder_buttons_layout)
            if hasattr(self, "folder_buttons_layout"):
                for i in range(self.folder_buttons_layout.count()):
                    item = self.folder_buttons_layout.itemAt(i)
                    if item and item.widget():
                        widget = item.widget()
                        if (
                            hasattr(widget, "folder_path")
                            and widget.folder_path == folder_path
                        ):
                            return widget

            # Sprawdź w strukturze folderów
            for i in range(self.folder_structure_layout.count()):
                item = self.folder_structure_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if (
                        hasattr(widget, "folder_path")
                        and widget.folder_path == folder_path
                    ):
                        return widget

            return None
        except Exception as e:
            logger.error(f"Błąd wyszukiwania przycisku folderu: {e}")
            return None

    def _on_folder_drop(self, asset_data, folder_path):
        """Obsługa upuszczenia asset-a na folder"""
        try:
            # Wykonaj przeniesienie asset-a
            self._move_asset_to_folder(asset_data, folder_path)
        except Exception as e:
            logger.error(f"Błąd obsługi drop: {e}")

    def _on_folder_drop_event(self, event, folder_path):
        """Obsługa upuszczenia asset-a na folder (dla przycisków w panelu szybkiego dostępu)"""
        try:
            print(f"DEBUG: _on_folder_drop_event - folder: {folder_path}")
            print(f"DEBUG: MIME formats: {event.mimeData().formats()}")

            # Sprawdź czy MIME data zawiera dane asset-a
            if event.mimeData().hasFormat("application/x-cfab-asset"):
                print(
                    f"DEBUG: Przetwarzam drop - format application/x-cfab-asset znaleziony"
                )

                # Pobierz dane asset-a
                asset_data_bytes = event.mimeData().data("application/x-cfab-asset")
                asset_data = json.loads(asset_data_bytes.data().decode("utf-8"))
                print(f"DEBUG: Asset data: {asset_data.get('name', 'Unknown')}")

                # Wykonaj przeniesienie asset-a
                self._move_asset_to_folder(asset_data, folder_path)

                event.acceptProposedAction()
            else:
                print(f"DEBUG: Ignoruję drop - brak formatu application/x-cfab-asset")
                event.ignore()

        except Exception as e:
            print(f"Błąd obsługi drop: {e}")
            logger.error(f"Błąd obsługi drop: {e}")
            event.ignore()

    def _move_asset_to_folder(self, asset_data, target_folder_path):
        """Przenosi asset do nowego folderu"""
        try:
            logger.info(
                f"Przenoszenie asset-a {asset_data.get('name')} do {target_folder_path}"
            )

            # Sprawdź czy folder docelowy istnieje
            if not os.path.exists(target_folder_path):
                logger.error(f"Folder docelowy nie istnieje: {target_folder_path}")
                return

            # Pobierz ścieżkę do folderu źródłowego (aktualnie wyświetlanego)
            source_folder_path = self.grid_manager.current_folder_path
            if not source_folder_path:
                logger.error("Brak ścieżki do folderu źródłowego")
                return

            # Sprawdź czy folder docelowy nie jest tym samym co źródłowy
            if source_folder_path == target_folder_path:
                logger.info("Folder docelowy jest tym samym co źródłowy")
                return

            # Pobierz nazwę asset-a
            asset_name = asset_data.get("name")
            if not asset_name:
                logger.error("Brak nazwy asset-a")
                return

            # Lista plików do przeniesienia
            files_to_move = []

            # 1. Plik archiwum
            archive_filename = asset_data.get("archive")
            if archive_filename:
                archive_path = os.path.join(source_folder_path, archive_filename)
                if os.path.exists(archive_path):
                    files_to_move.append(("archive", archive_path, archive_filename))

            # 2. Plik podglądu
            preview_filename = asset_data.get("preview")
            if preview_filename:
                preview_path = os.path.join(source_folder_path, preview_filename)
                if os.path.exists(preview_path):
                    files_to_move.append(("preview", preview_path, preview_filename))

            # 3. Plik asset
            asset_filename = f"{asset_name}.asset"
            asset_path = os.path.join(source_folder_path, asset_filename)
            if os.path.exists(asset_path):
                files_to_move.append(("asset", asset_path, asset_filename))

            # 4. Plik thumbnail
            cache_folder = os.path.join(source_folder_path, ".cache")
            thumb_filename = f"{asset_name}.thumb"
            thumb_path = os.path.join(cache_folder, thumb_filename)
            if os.path.exists(thumb_path):
                files_to_move.append(("thumbnail", thumb_path, thumb_filename))

            # Sprawdź czy wszystkie pliki istnieją
            if len(files_to_move) < 4:
                logger.warning(
                    f"Nie wszystkie pliki asset-a {asset_name} zostały znalezione"
                )

            # Przenieś pliki
            moved_files = []
            for file_type, source_path, filename in files_to_move:
                try:
                    target_path = os.path.join(target_folder_path, filename)

                    # Dla thumbnail, utwórz folder .cache w folderze docelowym
                    if file_type == "thumbnail":
                        target_cache_folder = os.path.join(target_folder_path, ".cache")
                        if not os.path.exists(target_cache_folder):
                            os.makedirs(target_cache_folder)
                        target_path = os.path.join(target_cache_folder, filename)

                    # Przenieś plik
                    import shutil

                    shutil.move(source_path, target_path)
                    moved_files.append((file_type, filename))
                    logger.info(f"Przeniesiono {file_type}: {filename}")

                except Exception as e:
                    logger.error(f"Błąd przenoszenia {file_type} {filename}: {e}")

            # Aktualizuj galerię po przeniesieniu
            if moved_files:
                logger.info(
                    f"Przeniesiono {len(moved_files)} plików asset-a {asset_name}"
                )
                # Odśwież galerię
                self._refresh_gallery_after_move()
            else:
                logger.error(
                    f"Nie udało się przenieść żadnych plików asset-a {asset_name}"
                )

        except Exception as e:
            logger.error(f"Błąd przenoszenia asset-a: {e}")

    def _refresh_gallery_after_move(self):
        """Odświeża galerię po przeniesieniu asset-a"""
        try:
            # Sprawdź czy mamy aktywny folder scanner
            if hasattr(self, "folder_scanner") and self.folder_scanner:
                # Wywołaj ponownie handle_folder_click dla aktualnego folderu
                current_folder = self.grid_manager.current_folder_path
                if current_folder:
                    self.folder_scanner.handle_folder_click(current_folder)
        except Exception as e:
            logger.error(f"Błąd odświeżania galerii: {e}")


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = GalleryTab()
    w.show()
    sys.exit(app.exec())
