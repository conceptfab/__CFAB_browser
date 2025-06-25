import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QVBoxLayout


class ThumbnailTile(QFrame):
    """Template kafelka z placeholder miniaturki"""

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
        self._setup_ui()

    def _setup_ui(self):
        """Setup wyglądu kafelka"""
        # Główny layout pionowy
        layout = QVBoxLayout()
        layout.setSpacing(4)
        # lewy, górny, prawy, dolny
        layout.setContentsMargins(10, 10, 10, 10)

        # Kontener na miniaturkę - przyklejony do góry
        self.thumbnail_container = QLabel()
        self.thumbnail_container.setFixedSize(self.thumbnail_size, self.thumbnail_size)
        self.thumbnail_container.setStyleSheet(
            """
            QLabel {
                background-color: #2A2D2E;
                border: 2px solid orange;
                border-radius: 4px;
            }
        """
        )

        # Placeholder miniaturki
        self._create_placeholder_thumbnail()

        # Layout poziomy dla nazwy pliku, numeru i checkboxa
        filename_layout = QHBoxLayout()
        filename_layout.setSpacing(8)
        filename_layout.setContentsMargins(0, 0, 0, 0)

        # Numer kafelka po lewej stronie
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

        # Etykieta z nazwą pliku (z efektem hover)
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
            }
        """
        )

        # Checkbox po prawej stronie
        self.checkbox = QCheckBox()
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

        # Dodanie elementów do layoutu poziomego
        filename_layout.addWidget(self.tile_number_label)
        filename_layout.addStretch()  # Przestrzeń między numerem a checkboxem
        filename_layout.addWidget(self.checkbox)

        # Layout dla gwiazdek - przyklejony do dołu
        stars_layout = QHBoxLayout()
        stars_layout.setSpacing(6)
        stars_layout.setContentsMargins(0, 0, 0, 0)
        stars_layout.addStretch()  # Wyśrodkowanie gwiazdek

        # Gwiazdki do oceny
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
            stars_layout.addWidget(star_cb)

        stars_layout.addStretch()  # Wyśrodkowanie gwiazdek

        # Dodanie elementów do głównego layoutu
        layout.addWidget(self.thumbnail_container)
        layout.addLayout(filename_layout)  # Numer i checkbox pod miniaturką

        # Kontener na samą nazwę pliku (bez numeru i checkboxa)
        filename_only_layout = QHBoxLayout()
        filename_only_layout.setContentsMargins(0, 4, 0, 4)
        filename_only_layout.addStretch()

        # Przenosimy tylko label z nazwą pliku do osobnego layoutu
        self.filename_label.setParent(None)  # Usuwamy z poprzedniego layoutu
        filename_only_layout.addWidget(self.filename_label)
        filename_only_layout.addStretch()

        layout.addLayout(filename_only_layout)  # Nazwa w środku
        layout.addStretch()  # Elastyczna przestrzeń między nazwą a gwiazdkami
        layout.addLayout(stars_layout)  # Gwiazdki na dole

        self.setLayout(layout)

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
        """Ładuje miniaturkę z pliku .thumb z folderu .cache"""
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
                print(f"Błąd ładowania thumbnail: {e}")

        return False

    def set_filename(self, filename: str):
        """Aktualizuje nazwę pliku"""
        self.filename = filename
        self.filename_label.setText(filename)

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
            }}
            ThumbnailTile:hover {{
                background-color: #2A2D2E;
                border-color: #007ACC;
            }}
        """
        )


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = ThumbnailTile(256, "test_image.jpg", 1, 10)
    w.show()
    sys.exit(app.exec())
