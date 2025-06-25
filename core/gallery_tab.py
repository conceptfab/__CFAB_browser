import json
import os
from pathlib import Path

from PyQt6.QtCore import Qt, QThread, pyqtSignal
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


class AssetScanner(QThread):
    """Worker dla skanowania plików asset w folderze roboczym"""

    progress_updated = pyqtSignal(int)  # Sygnał postępu
    assets_found = pyqtSignal(list)  # Sygnał z listą znalezionych asset-ów
    finished_scanning = pyqtSignal()  # Sygnał zakończenia skanowania

    def __init__(self, work_folder_path: str):
        super().__init__()
        self.work_folder_path = work_folder_path
        self.assets = []

    def run(self):
        """Główna metoda worker-a"""
        self.assets = []

        print(f"Skanowanie folderu: {self.work_folder_path}")

        if not os.path.exists(self.work_folder_path):
            print(f"Folder nie istnieje: {self.work_folder_path}")
            self.finished_scanning.emit()
            return

        # Skanuj pliki .asset w folderze roboczym
        asset_files = []
        all_files = os.listdir(self.work_folder_path)
        print(f"Wszystkie pliki w folderze: {all_files}")

        for file in all_files:
            if file.endswith(".asset") and not file.startswith("."):
                asset_files.append(file)

        print(f"Znalezione pliki .asset: {asset_files}")

        total_files = len(asset_files)
        if total_files == 0:
            self.finished_scanning.emit()
            return

        # Przetwarzaj każdy plik asset
        for i, asset_file in enumerate(asset_files):
            try:
                asset_path = os.path.join(self.work_folder_path, asset_file)
                with open(asset_path, "r", encoding="utf-8") as f:
                    asset_data = json.load(f)

                # Sprawdź czy to poprawny asset
                if self._is_valid_asset(asset_data):
                    self.assets.append(asset_data)

            except Exception as e:
                print(f"Błąd wczytywania asset: {asset_file}, error: {e}")

            # Aktualizuj postęp
            progress = int((i + 1) / total_files * 100)
            self.progress_updated.emit(progress)

        # Prześlij wyniki
        self.assets_found.emit(self.assets)
        self.finished_scanning.emit()

    def _is_valid_asset(self, data: dict) -> bool:
        """Sprawdza czy JSON zawiera poprawną strukturę asset"""
        required_fields = ["name", "archive", "preview", "size_mb", "thumbnail"]
        return all(field in data for field in required_fields)


class GalleryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.thumbnail_size = self._load_thumbnail_size()
        self.min_thumbnail_size = 50  # Minimalny rozmiar przy 0%
        self.max_thumbnail_size = self.thumbnail_size  # Maksymalny rozmiar
        self.current_tiles = []  # Lista aktualnych kafelków
        self.assets = []  # Lista wczytanych asset-ów
        self.work_folder_path = self._load_work_folder_path()
        self.scanner = None  # Worker do skanowania asset-ów
        self.tile_spacing = 10  # Odstęp między kaflami (stała 10px)
        self._setup_ui()
        self._connect_signals()
        self._start_asset_scanning()

    def _load_thumbnail_size(self) -> int:
        """Wczytuje rozmiar thumbnail z config.json"""
        config_path = Path(__file__).parent.parent / "config.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            # Domyślnie 512 jeśli nie ma w config
            return config.get("thumbnail", 512)
        except Exception as e:
            print(f"Błąd wczytywania config.json: {e}")
            return 512

    def _load_work_folder_path(self) -> str:
        """Wczytuje ścieżkę work_folder1 z config.json"""
        config_path = Path(__file__).parent.parent / "config.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            # Pobierz ścieżkę work_folder1
            work_folder1 = config.get("work_folder1", {})
            return work_folder1.get("path", "")
        except Exception as e:
            print(f"Błąd wczytywania work_folder1 z config.json: {e}")
            return ""

    def _setup_ui(self):
        """Setup user interface for gallery tab"""
        # Główny layout poziomy
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Splitter do zmiany szerokości paneli
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Lewy panel - przyszłe drzewo folderów
        self.folder_tree_panel = QFrame()
        self.folder_tree_panel.setFrameStyle(QFrame.Shape.Box)
        self.folder_tree_panel.setMinimumWidth(200)
        self.folder_tree_panel.setMaximumWidth(300)

        folder_layout = QVBoxLayout()
        folder_layout.addWidget(QLabel("Drzewo folderów"))
        folder_layout.addStretch()
        self.folder_tree_panel.setLayout(folder_layout)

        # Prawy panel - galeria miniatur z scroll area i paskiem kontrolnym
        self.gallery_panel = QFrame()
        self.gallery_panel.setFrameStyle(QFrame.Shape.Box)

        # Layout pionowy dla galerii i paska kontrolnego
        gallery_vertical_layout = QVBoxLayout()
        gallery_vertical_layout.setSpacing(4)
        gallery_vertical_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area dla galerii
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Widget z kafelkami
        self.gallery_widget = QWidget()
        self.gallery_layout = QGridLayout()
        self.gallery_layout.setSpacing(8)
        self.gallery_layout.setContentsMargins(8, 8, 8, 8)

        # Placeholder info o ładowaniu
        self._create_loading_placeholder()

        self.gallery_widget.setLayout(self.gallery_layout)
        self.scroll_area.setWidget(self.gallery_widget)

        # Pasek kontrolny na dole (24px wysokości)
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

        # Layout poziomy dla paska kontrolnego
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(8, 2, 8, 2)
        control_layout.setSpacing(8)

        # Lewa połowa - placeholder na progress bar
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

        # Prawa połowa - suwak wielkości kafelka
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

        # Dodanie elementów do layoutu kontrolnego
        control_layout.addWidget(self.progress_bar, 1)  # 1 = rozciąga się
        control_layout.addWidget(self.thumbnail_size_slider, 1)  # 1 = rozciąga się

        self.control_panel.setLayout(control_layout)

        # Dodanie elementów do layoutu pionowego galerii
        gallery_vertical_layout.addWidget(self.scroll_area)
        gallery_vertical_layout.addWidget(self.control_panel)

        self.gallery_panel.setLayout(gallery_vertical_layout)

        # Dodanie paneli do splittera
        self.splitter.addWidget(self.folder_tree_panel)
        self.splitter.addWidget(self.gallery_panel)

        # Ustawienie początkowych proporcji (20:80)
        self.splitter.setSizes([200, 800])

        # Dodanie splittera do głównego layoutu
        main_layout.addWidget(self.splitter)

        self.setLayout(main_layout)

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

    def _create_thumbnail_grid(self):
        """Tworzy kafelki na podstawie wczytanych asset-ów"""
        # Wyczyść istniejące kafelki
        self._clear_gallery()

        if not self.assets:
            # Brak asset-ów - pokaż komunikat
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
            return

        # Oblicz ilość kolumn na podstawie szerokości scroll area
        columns = self._calculate_columns()

        # Tworzenie kafelków na podstawie asset-ów
        for i, asset in enumerate(self.assets):
            row = i // columns
            col = i % columns

            # Użyj aktualnego rozmiaru z suwaka
            current_size = self.thumbnail_size_slider.value()

            # Utwórz kafelek z danymi asset
            tile = self._create_asset_tile(asset, i + 1, len(self.assets), current_size)
            self.gallery_layout.addWidget(tile, row, col)
            self.current_tiles.append(tile)

    def _clear_gallery(self):
        """Czyści wszystkie widgety z galerii"""
        for tile in self.current_tiles:
            tile.deleteLater()
        self.current_tiles.clear()

        # Usuń wszystkie widgety z layout-u
        while self.gallery_layout.count():
            item = self.gallery_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _calculate_columns(self) -> int:
        """Oblicza optymalną ilość kolumn na podstawie szerokości scroll area"""
        if not hasattr(self, "scroll_area"):
            return 4  # Domyślna wartość

        # Pobierz aktualny rozmiar kafelka z suwaka
        current_tile_size = self.thumbnail_size_slider.value()

        # Szerokość scroll area minus marginesy
        available_width = self.scroll_area.width() - 40  # 20px z każdej strony

        # Szerokość kafelka = rozmiar thumbnail + padding (20px)
        tile_width = current_tile_size + 20

        # Oblicz ile kolumn się zmieści (z odstępem 10px między kaflami)
        columns = max(
            1, (available_width + self.tile_spacing) // (tile_width + self.tile_spacing)
        )

        return columns

    def _create_asset_tile(
        self, asset: dict, tile_number: int, total_tiles: int, thumbnail_size: int
    ):
        """Tworzy kafelek na podstawie danych asset"""
        # Utwórz nazwę wyświetlaną z rozmiarem
        display_name = f"{asset['name']} ({asset['size_mb']:.1f} MB)"

        # Utwórz kafelek
        tile = ThumbnailTile(thumbnail_size, display_name, tile_number, total_tiles)

        # Ustaw gwiazdki jeśli są w asset
        if asset.get("stars") is not None:
            tile.set_star_rating(asset["stars"])

        # Załaduj thumbnail z .cache jeśli dostępny
        if asset.get("thumbnail") is True:
            cache_folder = os.path.join(self.work_folder_path, ".cache")
            asset_name = asset["name"]
            tile.load_thumbnail_from_cache(asset_name, cache_folder)

        # TODO: Dodać obsługę kliknięć w archiwum i preview

        return tile

    def _start_asset_scanning(self):
        """Rozpoczyna skanowanie asset-ów w tle"""
        if not self.work_folder_path:
            print("Brak ścieżki do folderu roboczego")
            return

        # Utwórz i uruchom worker
        self.scanner = AssetScanner(self.work_folder_path)
        self.scanner.progress_updated.connect(self._on_scan_progress)
        self.scanner.assets_found.connect(self._on_assets_found)
        self.scanner.finished_scanning.connect(self._on_scan_finished)
        self.scanner.start()

    def _on_scan_progress(self, progress: int):
        """Obsługuje aktualizację postępu skanowania"""
        self.progress_bar.setValue(progress)

    def _on_assets_found(self, assets: list):
        """Obsługuje znalezione asset-y"""
        self.assets = assets
        print(f"Znaleziono {len(assets)} asset-ów")

    def _on_scan_finished(self):
        """Obsługuje zakończenie skanowania"""
        self.progress_bar.setValue(0)  # Ukryj progress bar
        self._create_thumbnail_grid()  # Utwórz kafelki

    def _connect_signals(self):
        """Podłącza sygnały suwaka"""
        self.thumbnail_size_slider.valueChanged.connect(self._on_slider_changed)

    def _on_slider_changed(self, value):
        """Obsługuje zmianę wartości suwaka"""
        # Wartość suwaka to bezpośrednio rozmiar w pikselach
        new_size = value

        # Aktualizuj rozmiar wszystkich kafelków
        self._update_tile_sizes(new_size)

        # Przelicz layout kolumn po zmianie rozmiaru
        if self.assets:
            self._create_thumbnail_grid()

    def _update_tile_sizes(self, new_size):
        """Aktualizuje rozmiar wszystkich kafelków"""
        for tile in self.current_tiles:
            tile.update_thumbnail_size(new_size)

    def resizeEvent(self, event):
        """Obsługuje zmianę rozmiaru okna - przelicza kolumny"""
        super().resizeEvent(event)
        # Przelicz layout kolumn po zmianie rozmiaru okna
        if hasattr(self, "assets") and self.assets:
            self._create_thumbnail_grid()


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = GalleryTab()
    w.show()
    sys.exit(app.exec())
