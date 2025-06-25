import os
import subprocess

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
)


class ThumbnailTile(QFrame):
    """Template kafelka z placeholder miniaturki"""

    # Sygnały dla komunikacji z parent widget
    thumbnail_clicked = pyqtSignal(str)  # Sygnał kliknięcia w miniaturkę
    filename_clicked = pyqtSignal(str)  # Sygnał kliknięcia w nazwę pliku

    def __init__(
        self,
        thumbnail_size: int,
        filename: str = "placeholder.jpg",
        tile_number: int = 1,
        total_tiles: int = 1,
    ):
        super().__init__()
        self.thumbnail_size = thumbnail_size
        self.filename = filename
        self.tile_number = tile_number
        self.total_tiles = total_tiles
        self.asset_data = None  # Dane asset-a dla dostępu do ścieżek
        self._setup_ui()

    def _setup_ui(self):
        """Setup wyglądu kafelka"""
        # Główny layout pionowy - 2 rzędy
        layout = QVBoxLayout()
        layout.setSpacing(22)  # Więcej przestrzeni między miniaturką a dolną częścią
        layout.setContentsMargins(10, 10, 10, 10)

        # RZĄD 1: Miniaturka
        self.thumbnail_container = QLabel()
        self.thumbnail_container.setFixedSize(self.thumbnail_size, self.thumbnail_size)
        self.thumbnail_container.setStyleSheet(
            """
            QLabel {
                background-color: #2A2D2E;
                border: 2px solid orange;
                border-radius: 4px;
            }
            QLabel:hover {
                border-color: #007ACC;
            }
        """
        )
        # Ustaw cursor pointer dla miniaturki
        self.thumbnail_container.setCursor(Qt.CursorShape.PointingHandCursor)
        # Obsługa kliknięcia w miniaturkę
        self.thumbnail_container.mousePressEvent = self._on_thumbnail_clicked

        # Placeholder miniaturki
        self._create_placeholder_thumbnail()

        # RZĄD 2: Wszystkie pozostałe elementy w 3 rzędach
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(4)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # RZĄD 2A: Numer po lewej, checkbox po prawej
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        top_row.setContentsMargins(0, 8, 0, 0)

        # Numer kafelka po lewej
        tile_label_text = f"{self.tile_number} / {self.total_tiles}"
        self.tile_number_label = QLabel(tile_label_text)
        self.tile_number_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.tile_number_label.setStyleSheet(
            """
            QLabel {
                color: #888888;
                background-color: transparent;
                font-size: 9px;
                font-weight: bold;
                padding: 2px;
                min-width: 30px;
            }
        """
        )

        # Checkbox po prawej
        self.checkbox = QCheckBox()
        self.checkbox.setFixedSize(16, 16)
        self.checkbox.setStyleSheet(
            """
            QCheckBox {
                spacing: 0px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #555555;
                border-radius: 2px;
                background-color: #2A2D2E;
            }
            QCheckBox::indicator:checked {
                background-color: #007ACC;
                border-color: #007ACC;
                image: none;
            }
            QCheckBox::indicator:hover {
                border-color: #007ACC;
            }
        """
        )

        top_row.addWidget(self.tile_number_label)
        top_row.addStretch()  # Przestrzeń między numerem a checkboxem
        top_row.addWidget(self.checkbox)

        # RZĄD 2B: Nazwa pliku w środku (skalowalna)
        middle_row = QHBoxLayout()
        middle_row.setSpacing(0)
        middle_row.setContentsMargins(0, 4, 0, 4)

        # Nazwa pliku w środku
        self.filename_label = QLabel(self.filename)
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.filename_label.setWordWrap(True)
        self.filename_label.setStyleSheet(
            """
            QLabel {
                color: #CCCCCC;
                background-color: transparent;
                font-size: 10px;
                padding: 2px;
                border-radius: 3px;
            }
            QLabel:hover {
                font-weight: bold;
                color: #FFFFFF;
                background-color: #007ACC;
            }
        """
        )
        # Ustaw cursor pointer dla nazwy pliku
        self.filename_label.setCursor(Qt.CursorShape.PointingHandCursor)
        # Obsługa kliknięcia w nazwę pliku
        self.filename_label.mousePressEvent = self._on_filename_clicked

        middle_row.addStretch()
        middle_row.addWidget(self.filename_label)
        middle_row.addStretch()

        # RZĄD 2C: Gwiazdki na dole
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(6)
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.addStretch()  # Wyśrodkowanie gwiazdek

        # Gwiazdki
        self.star_checkboxes = []
        for i in range(6):
            star_cb = QCheckBox("★")
            star_cb.setStyleSheet(
                """
                QCheckBox {
                    spacing: 0px;
                    color: #888888;
                    font-size: 14px;
                    padding: 2px;
                }
                QCheckBox::indicator {
                    width: 0px;
                    height: 0px;
                    border: none;
                }
                QCheckBox:checked {
                    color: #FFD700;
                    font-weight: bold;
                }
                QCheckBox:hover {
                    color: #FFA500;
                }
            """
            )
            self.star_checkboxes.append(star_cb)
            bottom_row.addWidget(star_cb)

        bottom_row.addStretch()  # Wyśrodkowanie gwiazdek

        # Dodanie wszystkich rzędów do dolnego layoutu
        bottom_layout.addLayout(top_row)  # Rząd 2A: Numer + Checkbox
        bottom_layout.addLayout(middle_row)  # Rząd 2B: Nazwa pliku
        bottom_layout.addLayout(bottom_row)  # Rząd 2C: Gwiazdki

        # Dodanie rzędów do głównego layoutu
        layout.addWidget(self.thumbnail_container)  # Rząd 1: Miniaturka
        layout.addLayout(bottom_layout)  # Rząd 2: 3 podrzędy

        self.setLayout(layout)

        # Ustawienie polityki rozmiaru
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Stylowanie kafelka
        self.setStyleSheet(
            f"""
            ThumbnailTile {{
                background-color: #252526;
                border: 1px solid #3F3F46;
                border-radius: 6px;
                padding: 0px;
                min-width: {self.thumbnail_size + 20}px;
                max-width: {self.thumbnail_size + 20}px;
                min-height: {self.thumbnail_size + 100}px;
                max-height: {self.thumbnail_size + 100}px;
            }}
            ThumbnailTile:hover {{
                background-color: #2A2D2E;
                border-color: #007ACC;
            }}
        """
        )

    def _create_placeholder_thumbnail(self):
        """Tworzy placeholder miniaturki z tekstem"""
        # Tworzenie pixmapy z placeholder
        pixmap = QPixmap(self.thumbnail_size, self.thumbnail_size)
        pixmap.fill(QColor("#2A2D2E"))

        # Rysowanie tekstu na placeholder
        painter = QPainter(pixmap)
        painter.setPen(QColor("#CCCCCC"))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)

        # Wyśrodkowanie tekstu
        text = "IMG"
        text_rect = pixmap.rect()
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
        painter.end()

        self.thumbnail_container.setPixmap(pixmap)

    def load_thumbnail_from_cache(self, asset_name: str, cache_folder_path: str):
        """Ładuje miniaturkę z pliku .thumb w folderze .cache"""
        if not cache_folder_path or not os.path.exists(cache_folder_path):
            return False

        # Szukaj pliku .thumb
        thumb_file = os.path.join(cache_folder_path, f"{asset_name}.thumb")

        if os.path.exists(thumb_file):
            try:
                # Wczytaj obraz z pliku
                pixmap = QPixmap(thumb_file)
                if not pixmap.isNull():
                    # Przeskaluj do aktualnego rozmiaru zachowując proporcje
                    scaled_pixmap = pixmap.scaled(
                        self.thumbnail_size,
                        self.thumbnail_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    self.thumbnail_container.setPixmap(scaled_pixmap)
                    return True
            except Exception as e:
                print(f"Błąd ładowania thumbnail {thumb_file}: {e}")

        return False

    def set_filename(self, filename: str):
        """Aktualizuje nazwę pliku"""
        self.filename = filename
        self.filename_label.setText(filename)

    def set_asset_data(self, asset_data: dict):
        """Ustawia dane asset-a dla dostępu do ścieżek"""
        self.asset_data = asset_data

    def set_tile_number(self, tile_number: int, total_tiles: int):
        """Aktualizuje numer kafelka"""
        self.tile_number = tile_number
        self.total_tiles = total_tiles
        self.tile_number_label.setText(f"{tile_number} / {total_tiles}")

    def is_checked(self) -> bool:
        """Sprawdza czy checkbox jest zaznaczony"""
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool):
        """Ustawia stan checkboxa"""
        self.checkbox.setChecked(checked)

    def get_star_rating(self) -> int:
        """Zwraca ocenę w gwiazdkach (0-6)"""
        return sum(1 for cb in self.star_checkboxes if cb.isChecked())

    def set_star_rating(self, rating: int):
        """Ustawia ocenę w gwiazdkach (0-6)"""
        rating = max(0, min(6, rating))  # Ograniczenie do 0-6
        for i, cb in enumerate(self.star_checkboxes):
            cb.setChecked(i < rating)

    def clear_stars(self):
        """Czyści wszystkie gwiazdki"""
        for cb in self.star_checkboxes:
            cb.setChecked(False)

    def update_thumbnail_size(self, new_size: int):
        """Aktualizuje rozmiar miniaturki i kafelka"""
        self.thumbnail_size = new_size

        # Aktualizuj rozmiar kontenera miniaturki
        self.thumbnail_container.setFixedSize(new_size, new_size)

        # Przerysuj placeholder z nowym rozmiarem
        self._create_placeholder_thumbnail()

        # Zachowaj politykę rozmiaru
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Aktualizuj stylowanie kafelka
        self.setStyleSheet(
            f"""
            ThumbnailTile {{
                background-color: #252526;
                border: 1px solid #3F3F46;
                border-radius: 6px;
                padding: 0px;
                min-width: {new_size + 20}px;
                max-width: {new_size + 20}px;
                min-height: {new_size + 100}px;
                max-height: {new_size + 100}px;
            }}
            ThumbnailTile:hover {{
                background-color: #2A2D2E;
                border-color: #007ACC;
            }}
        """
        )

    def _on_thumbnail_clicked(self, ev):
        """Obsługa kliknięcia w miniaturkę"""
        if ev.button() == Qt.MouseButton.LeftButton:
            self.thumbnail_clicked.emit(self.filename)

    def _on_filename_clicked(self, ev):
        """Obsługa kliknięcia w nazwę pliku"""
        if ev.button() == Qt.MouseButton.LeftButton:
            self.filename_clicked.emit(self.filename)


class PreviewWindow(QDialog):
    """Okno podglądu obrazu w dużym rozmiarze"""

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path

        # Wyłącz animacje i efekty
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool
        )

        # Wyłącz animacje okna
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)

        self.setup_ui()

    def setup_ui(self):
        """Setup interfejsu okna podglądu"""
        self.setWindowTitle(f"Podgląd - {os.path.basename(self.image_path)}")
        self.setModal(False)
        self.resize(800, 600)

        # Wyłącz animacje stylu
        self.setStyleSheet(
            """
            QDialog {
                background-color: #1E1E1E;
                border: 2px solid #3F3F46;
            }
            """
        )

        # Główny layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Label z obrazem
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(
            """
            QLabel {
                background-color: #1E1E1E;
                border: none;
            }
            """
        )

        # Załaduj obraz
        self.load_image()

        layout.addWidget(self.image_label)
        self.setLayout(layout)

        # Pokaż okno natychmiast bez animacji
        self.show()
        self.raise_()
        self.activateWindow()

    def load_image(self):
        """Ładuje obraz do okna podglądu"""
        try:
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                # Przeskaluj do rozmiaru okna zachowując proporcje
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText("Nie można załadować obrazu")
        except Exception as e:
            self.image_label.setText(f"Błąd ładowania obrazu: {e}")

    def resizeEvent(self, event):
        """Obsługa zmiany rozmiaru okna"""
        super().resizeEvent(event)
        self.load_image()


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = ThumbnailTile(256, "test_image.jpg", 1, 10)
    w.show()
    sys.exit(app.exec())
