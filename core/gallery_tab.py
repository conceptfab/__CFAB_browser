import json
from pathlib import Path

from PyQt6.QtCore import Qt
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


class GalleryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.thumbnail_size = self._load_thumbnail_size()
        self.min_thumbnail_size = 50  # Minimalny rozmiar przy 0%
        self.max_thumbnail_size = self.thumbnail_size  # Maksymalny rozmiar z config
        self.current_tiles = []  # Lista aktualnych kafelków
        self._setup_ui()
        self._connect_signals()

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

        # Szkic 32 kafelków
        self._create_thumbnail_grid()

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

    def _create_thumbnail_grid(self):
        """Tworzy szkic 32 kafelków w siatce"""
        # Przykładowe nazwy plików
        sample_files = [
            "image_001.jpg",
            "image_002.png",
            "image_003.webp",
            "image_004.jpg",
            "image_005.png",
            "image_006.webp",
            "image_007.jpg",
            "image_008.png",
            "image_009.webp",
            "image_010.jpg",
            "image_011.png",
            "image_012.webp",
            "image_013.jpg",
            "image_014.png",
            "image_015.webp",
            "image_016.jpg",
            "image_017.png",
            "image_018.webp",
            "image_019.jpg",
            "image_020.png",
            "image_021.webp",
            "image_022.jpg",
            "image_023.png",
            "image_024.webp",
            "image_025.jpg",
            "image_026.png",
            "image_027.webp",
            "image_028.jpg",
            "image_029.png",
            "image_030.webp",
            "image_031.jpg",
            "image_032.png",
        ]

        # Tworzenie 32 kafelków w siatce 8x4
        for i in range(32):
            row = i // 8  # 8 kolumn
            col = i % 8

            tile = ThumbnailTile(self.thumbnail_size, sample_files[i])
            self.gallery_layout.addWidget(tile, row, col)
            self.current_tiles.append(tile)

    def _connect_signals(self):
        """Podłącza sygnały suwaka"""
        self.thumbnail_size_slider.valueChanged.connect(self._on_slider_changed)

    def _on_slider_changed(self, value):
        """Obsługuje zmianę wartości suwaka"""
        # Wartość suwaka to bezpośrednio rozmiar w pikselach
        new_size = value

        # Aktualizuj rozmiar wszystkich kafelków
        self._update_tile_sizes(new_size)

    def _update_tile_sizes(self, new_size):
        """Aktualizuje rozmiar wszystkich kafelków"""
        for tile in self.current_tiles:
            tile.update_thumbnail_size(new_size)


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = GalleryTab()
    w.show()
    sys.exit(app.exec())
