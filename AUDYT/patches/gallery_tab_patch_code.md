# PATCH-CODE DLA: GALLERY_TAB.PY

**Powiązany plik z analizą:** `../corrections/gallery_tab_correction.md`
**Zasady ogólne:** `../refactoring_rules.md`

---

### PATCH 1: DODANIE PROPER LOGGING I ERROR HANDLING

**Problem:** Exception tłumiona w AssetScanner.run(), print() zamiast proper error handling
**Rozwiązanie:** Dodanie logging i proper exception handling

```python
import json
import logging
import os
from pathlib import Path

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QSlider,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from core.thumbnail_tile import ThumbnailTile

# Dodanie loggera dla modułu
logger = logging.getLogger(__name__)
```

---

### PATCH 2: REFAKTORYZACJA ASSETSCANNER Z PROPER ERROR HANDLING

**Problem:** Nieobsłużone wyjątki w AssetScanner, thread safety issues
**Rozwiązanie:** Comprehensive error handling i thread safety

```python
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
                file for file in all_files 
                if file.endswith(".asset") and not file.startswith(".")
            ]
            return asset_files
        except PermissionError as e:
            logger.error(f"Brak uprawnień do odczytu folderu {self.work_folder_path}: {e}")
            raise
        except OSError as e:
            logger.error(f"Błąd systemu podczas skanowania folderu {self.work_folder_path}: {e}")
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
        logger.info(f"Przetworzono {len(self.assets)} poprawnych assetów z {total_files} plików")
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
```

---

### PATCH 3: CENTRALIZACJA CONFIG LOADING

**Problem:** Duplicated config loading w _load_thumbnail_size() i _load_work_folder_path()
**Rozwiązanie:** Jednokrotne ładowanie konfiguracji z cache'owaniem

```python
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
            "use_styles": True
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
```

---

### PATCH 4: DEBOUNCED GRID RECREATION

**Problem:** Grid recreation przy każdej zmianie slidera powoduje performance issues
**Rozwiązanie:** Debouncing dla slider changes i grid recreation

```python
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
            self._create_thumbnail_grid(self.pending_assets, self.pending_thumbnail_size)
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

                tile = self._create_asset_tile_safe(asset, i + 1, len(assets), thumbnail_size)
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
        if (current_width == self._last_width and 
            thumbnail_size == self._last_tile_size):
            return self._cached_columns
        
        # Oblicz nową wartość
        available_width = current_width - 40  # marginesy
        tile_width = thumbnail_size + 20  # padding
        
        columns = max(1, (available_width + self.tile_spacing) // (tile_width + self.tile_spacing))
        
        # Zapisz do cache
        self._last_width = current_width
        self._last_tile_size = thumbnail_size
        self._cached_columns = columns
        
        return columns
    
    def _create_asset_tile_safe(self, asset, tile_number, total_tiles, thumbnail_size):
        """Bezpiecznie tworzy kafelek asset"""
        try:
            from core.thumbnail_tile import ThumbnailTile
            
            display_name = f"{asset['name']} ({asset['size_mb']:.1f} MB)"
            tile = ThumbnailTile(thumbnail_size, display_name, tile_number, total_tiles)
            
            # Ustaw gwiazdki jeśli są w asset
            if asset.get("stars") is not None:
                tile.set_star_rating(asset["stars"])
            
            return tile
            
        except Exception as e:
            logger.error(f"Błąd tworzenia kafelka dla {asset.get('name', 'unknown')}: {e}")
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
                if tile and hasattr(tile, 'update_thumbnail_size'):
                    tile.update_thumbnail_size(new_size)
        except Exception as e:
            logger.error(f"Błąd aktualizacji rozmiarów kafelków: {e}")
```

---

### PATCH 5: REFAKTORYZACJA GALLERYTAB - CZĘŚĆ 1

**Problem:** GalleryTab zbyt długa, mixed concerns
**Rozwiązanie:** Wydzielenie menedżerów i uproszczenie głównej klasy

```python
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
        if hasattr(self, 'gallery_widget') and hasattr(self, 'gallery_layout'):
            self.grid_manager = GridManager(
                self.gallery_widget,
                self.gallery_layout,
                self.scroll_area
            )
        else:
            raise RuntimeError("UI components not initialized before GridManager")
```

---

### PATCH 6: REFAKTORYZACJA GALLERYTAB - CZĘŚĆ 2

**Problem:** Setup UI zbyt długie, brak error handling
**Rozwiązanie:** Modularyzacja setup UI z error handling

```python
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
        folder_layout.addStretch()
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
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

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
        self.control_panel.setFixedHeight(24)
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
```

---

### PATCH 7: THREAD SAFETY FIXES

**Problem:** resizeEvent może modyfikować UI z nieprawidłowego wątku
**Rozwiązanie:** Proper thread safety checks i Qt thread operations

```python
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
            if (hasattr(self, "grid_manager") and self.grid_manager and 
                hasattr(self, "assets") and self.assets):
                
                current_size = self.thumbnail_size_slider.value()
                self.grid_manager.request_grid_recreation(self.assets, current_size)
                
        except Exception as e:
            logger.error(f"Błąd resize event: {e}")
```

---

### PATCH 8: HELPER METHODS Z ERROR HANDLING

**Problem:** Brak helper methods dla error messages i proper cleanup
**Rozwiązanie:** Dodanie helper methods z proper error handling

```python
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
```

---

## ✅ CHECKLISTA WERYFIKACYJNA (DO WYPEŁNIENIA PRZED WDROŻENIEM)

#### **FUNKCJONALNOŚCI DO WERYFIKACJI:**

- [ ] **Funkcjonalność podstawowa** - czy galeria nadal ładuje i wyświetla assety poprawnie
- [ ] **API kompatybilność** - czy GalleryTab() działa identycznie dla main_window.py
- [ ] **Obsługa błędów** - czy błędy skanowania i UI są prawidłowo obsługiwane i logowane
- [ ] **Walidacja danych** - czy niepoprawne pliki .asset są odrzucane z komunikatami
- [ ] **Logowanie** - czy system logowania działa bez spamowania, appropriate levels
- [ ] **Konfiguracja** - czy centralized config loading działa z cache'owaniem
- [ ] **Cache** - czy ConfigManager cache działa poprawnie i invaliduje się
- [ ] **Thread safety** - czy wszystkie UI operations są wykonywane z proper thread
- [ ] **Memory management** - czy grid recreation nie powoduje memory leaks
- [ ] **Performance** - czy debounced grid recreation poprawia responsywność

#### **ZALEŻNOŚCI DO WERYFIKACJI:**

- [ ] **Importy** - czy wszystkie Qt imports i core modules działają poprawnie
- [ ] **Zależności zewnętrzne** - czy PyQt6 threading jest używane prawidłowo
- [ ] **Zależności wewnętrzne** - czy main_window.py nadal może utworzyć GalleryTab
- [ ] **Cykl zależności** - czy nie wprowadzono cyklicznych importów
- [ ] **Backward compatibility** - czy API GalleryTab jest 100% kompatybilne wstecz
- [ ] **Interface contracts** - czy signature konstruktora nie uległ zmianie
- [ ] **Event handling** - czy Qt events (resize, slider) działają poprawnie
- [ ] **Signal/slot connections** - czy AssetScanner signals działają thread-safe
- [ ] **File I/O** - czy ładowanie .asset files działa z proper error handling

#### **SPECJALNE TESTY PERFORMANCE:**

- [ ] **Grid recreation speed** - czy debouncing poprawia performance przy slider changes
- [ ] **Memory usage** - czy memory cleanup w _clear_gallery_safe() jest effective
- [ ] **Large dataset handling** - czy galeria radzi sobie z >100 assetami
- [ ] **Responsive UI** - czy UI pozostaje responsive podczas intensive operations
- [ ] **Config caching** - czy ConfigManager cache rzeczywiście usprawnia loading

#### **SPECJALNE TESTY THREAD SAFETY:**

- [ ] **AssetScanner threading** - czy worker thread nie blokuje UI
- [ ] **UI updates from threads** - czy wszystkie UI updates są thread-safe
- [ ] **Signal emissions** - czy signals są emitowane z proper threads
- [ ] **Resize events** - czy resizeEvent nie powoduje race conditions
- [ ] **Slider responsiveness** - czy slider changes nie blokują UI

#### **KRYTERIA SUKCESU:**

- [ ] **WSZYSTKIE CHECKLISTY MUSZĄ BYĆ ZAZNACZONE** przed wdrożeniem
- [ ] **BRAK FAILED TESTS** - wszystkie testy muszą przejść
- [ ] **PERFORMANCE BUDGET** - grid recreation co najmniej 30% szybsza
- [ ] **MEMORY BUDGET** - brak memory leaks przy długotrwałym użytkowaniu
- [ ] **THREAD SAFETY** - zero thread safety violations w UI operations