import os

from PyQt6.QtCore import QMimeData, QRect, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QDrag, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
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
    drag_started = pyqtSignal(object)  # Sygnał rozpoczęcia przeciągania

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
        # Więcej przestrzeni między miniaturką a dolną częścią
        layout.setSpacing(22)
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

        # RZĄD 2: Wszystkie pozostałe elementy w 2 rzędach
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(4)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # RZĄD 2A: Nazwa pliku w środku (skalowalna)
        middle_row = QHBoxLayout()
        middle_row.setSpacing(0)
        middle_row.setContentsMargins(0, 8, 0, 4)

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

        # RZĄD 2B: Numer (lewo) + Gwiazdki (środek) + Checkbox (prawo)
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(6)
        bottom_row.setContentsMargins(0, 0, 0, 0)

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
            }
        """
        )

        # Gwiazdki na środku
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

        # Dodanie elementów do rzędu: numer + gwiazdki + checkbox
        bottom_row.addWidget(self.tile_number_label)  # Numer po lewej
        bottom_row.addStretch()  # Przestrzeń między numerem a gwiazdkami

        # Gwiazdki na środku
        for star_cb in self.star_checkboxes:
            bottom_row.addWidget(star_cb)

        bottom_row.addStretch()  # Przestrzeń między gwiazdkami a checkboxem
        bottom_row.addWidget(self.checkbox)  # Checkbox po prawej

        # Dodanie rzędów do dolnego layoutu
        bottom_layout.addLayout(middle_row)  # Rząd 2A: Nazwa pliku
        bottom_layout.addLayout(bottom_row)  # Rząd 2B: Numer + Gwiazdki + Checkbox

        # Dodanie do głównego layoutu
        layout.addWidget(self.thumbnail_container)  # Rząd 1: Miniaturka
        # Rząd 2: Wszystkie pozostałe elementy
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

        # Ustawienie stylu kafelka
        self.setStyleSheet(
            """
            QFrame {
                background-color: #252526;
                border: 1px solid #3F3F46;
                border-radius: 6px;
                padding: 0px;
            }
            QFrame:hover {
                border-color: #007ACC;
                background-color: #2D2D30;
            }
        """
        )

        # Włącz obsługę drag and drop
        self.setAcceptDrops(False)  # Kafelki nie przyjmują drop
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        """Obsługa naciśnięcia myszy - rozpoczęcie drag and drop"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Sprawdź czy mamy dane asset-a
            if self.asset_data:
                # Rozpocznij drag and drop
                self._start_drag(event)
            else:
                # Jeśli nie ma danych asset-a, przekaż event dalej
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def _start_drag(self, event):
        """Rozpoczyna operację drag and drop"""
        try:
            print(
                f"DEBUG: Rozpoczynanie drag dla asset: {self.asset_data.get('name', 'Unknown')}"
            )

            # Utwórz obiekt drag
            drag = QDrag(self)

            # Utwórz MIME data z informacjami o asset
            mime_data = QMimeData()

            # Dodaj dane asset-a jako JSON string
            import json

            asset_json = json.dumps(self.asset_data)
            mime_data.setData("application/x-cfab-asset", asset_json.encode("utf-8"))

            # Dodaj tekst dla kompatybilności
            asset_name = self.asset_data.get("name", "Unknown")
            mime_data.setText(f"Asset: {asset_name}")

            drag.setMimeData(mime_data)

            # Ustaw ikonę drag (miniaturka)
            if (
                hasattr(self.thumbnail_container, "pixmap")
                and self.thumbnail_container.pixmap()
            ):
                drag.setPixmap(self.thumbnail_container.pixmap())
                drag.setHotSpot(self.thumbnail_container.pixmap().rect().center())

            # Emituj sygnał rozpoczęcia drag
            self.drag_started.emit(self.asset_data)
            print(f"DEBUG: Sygnał drag_started wyemitowany")

            # Wykonaj drag
            result = drag.exec(Qt.DropAction.MoveAction)
            print(f"DEBUG: Drag zakończony z wynikiem: {result}")

        except Exception as e:
            print(f"Błąd podczas rozpoczęcia drag: {e}")
            import traceback

            traceback.print_exc()

    def _on_thumbnail_clicked(self, ev):
        """Obsługa kliknięcia w miniaturkę"""
        if self.asset_data:
            self.thumbnail_clicked.emit(self.asset_data.get("name", ""))

    def _on_filename_clicked(self, ev):
        """Obsługa kliknięcia w nazwę pliku"""
        if self.asset_data:
            self.filename_clicked.emit(self.asset_data.get("name", ""))

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


class PreviewWindow(QDialog):
    """Okno podglądu obrazu w dużym rozmiarze"""

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.original_pixmap = None

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

        layout.addWidget(self.image_label)
        self.setLayout(layout)

        # Załaduj obraz i ustaw rozmiar okna
        self.load_image_and_resize()

        # Pokaż okno natychmiast bez animacji
        self.show()
        self.raise_()
        self.activateWindow()

    def load_image_and_resize(self):
        """Ładuje obraz i ustawia optymalny rozmiar okna"""
        try:
            self.original_pixmap = QPixmap(self.image_path)
            if not self.original_pixmap.isNull():
                # Pobierz rozmiar ekranu
                screen = QApplication.primaryScreen()
                screen_geometry = screen.availableGeometry()
                screen_width = screen_geometry.width()
                screen_height = screen_geometry.height()

                # Pobierz oryginalny rozmiar obrazu
                image_width = self.original_pixmap.width()
                image_height = self.original_pixmap.height()

                # Oblicz optymalny rozmiar okna
                # Zostaw margines 50px z każdej strony
                max_width = screen_width - 100
                max_height = screen_height - 100

                # Oblicz skalę zachowując proporcje
                scale_x = max_width / image_width
                scale_y = max_height / image_height
                scale = min(scale_x, scale_y, 1.0)  # Nie powiększaj obrazu

                # Oblicz nowy rozmiar
                new_width = int(image_width * scale)
                new_height = int(image_height * scale)

                # Ustaw rozmiar okna
                self.resize(new_width, new_height)

                # Wyśrodkuj okno na ekranie
                x = (screen_width - new_width) // 2
                y = (screen_height - new_height) // 2
                self.move(x, y)

                # Przeskaluj obraz do rozmiaru okna
                scaled_pixmap = self.original_pixmap.scaled(
                    new_width,
                    new_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText("Nie można załadować obrazu")
                self.resize(400, 300)
        except Exception as e:
            self.image_label.setText(f"Błąd ładowania obrazu: {e}")
            self.resize(400, 300)

    def load_image(self):
        """Ładuje obraz do okna podglądu (zachowana dla kompatybilności)"""
        if self.original_pixmap:
            scaled_pixmap = self.original_pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        """Obsługa zmiany rozmiaru okna"""
        super().resizeEvent(event)
        self.load_image()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = ThumbnailTile(256, "test_image.jpg", 1, 10)
    w.show()
    sys.exit(app.exec())
