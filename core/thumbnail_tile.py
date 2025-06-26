import json
import os
import sys

from PyQt6.QtCore import QMimeData, Qt, pyqtSignal
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
    """
    Template kafelka, w którym miniaturka dyktuje szerokość,
    a nazwa pliku poprawnie się zawija.
    """

    thumbnail_clicked = pyqtSignal(str)
    filename_clicked = pyqtSignal(str)
    drag_started = pyqtSignal(object)

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
        self.asset_data = None

        # Definiujemy marginesy w jednym miejscu dla spójności
        self.margins_size = 8
        self._setup_ui()

    def _setup_ui(self):
        """Setup wyglądu kafelka"""
        self.setStyleSheet(
            """
            ThumbnailTile {
                background-color: #252526;
                border: 1px solid #3F3F46;
                border-radius: 6px;
            }
            ThumbnailTile:hover {
                border-color: #007ACC;
                background-color: #2D2D30;
            }
        """
        )

        # *** KLUCZOWA ZMIANA: Polityka rozmiaru ***
        # Szerokość jest stała, a wysokość może się rozszerzać, by pomieścić tekst.
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        # Ustawiamy szerokość na sztywno, na podstawie rozmiaru miniaturki i marginesów
        self.setFixedWidth(self.thumbnail_size + (2 * self.margins_size))

        # Główny layout pionowy
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(
            self.margins_size, self.margins_size, self.margins_size, self.margins_size
        )

        # RZĄD 1: Miniaturka
        self.thumbnail_container = QLabel()
        self.thumbnail_container.setFixedSize(self.thumbnail_size, self.thumbnail_size)
        self.thumbnail_container.setStyleSheet(
            """
            QLabel {
                background-color: #2A2D2E;
                border: 2px solid transparent;
                border-radius: 4px;
            }
            QLabel:hover {
                border-color: #007ACC;
            }
        """
        )
        self.thumbnail_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.thumbnail_container.mousePressEvent = self._on_thumbnail_clicked
        self._create_placeholder_thumbnail()

        # RZĄD 2: Dolna sekcja (tekst, gwiazdki, etc.)
        # Nazwa pliku
        self.filename_label = QLabel(self.filename)
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.filename_label.setWordWrap(
            True
        )  # To teraz zadziała, bo szerokość jest ograniczona
        self.filename_label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        self.filename_label.setStyleSheet(
            """
            QLabel {
                color: #CCCCCC; background-color: transparent; font-size: 10px;
                padding: 2px;
            }
            QLabel:hover {
                font-weight: bold; color: #FFFFFF;
            }
        """
        )
        self.filename_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.filename_label.mousePressEvent = self._on_filename_clicked

        # Ikona texture (ukryta domyślnie)
        self.texture_icon = QLabel()
        self.texture_icon.setFixedSize(16, 16)
        self.texture_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.texture_icon.setVisible(False)  # Ukryta domyślnie
        self._load_texture_icon()

        # Dolny rząd z numerem, gwiazdkami i checkboxem
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(6)

        # Numer kafelka
        tile_label_text = f"{self.tile_number} / {self.total_tiles}"
        self.tile_number_label = QLabel(tile_label_text)
        self.tile_number_label.setStyleSheet(
            "color: #888888; background-color: transparent; "
            "font-size: 9px; font-weight: bold;"
        )

        # Gwiazdki
        self.star_checkboxes = []
        for i in range(6):
            star_cb = QCheckBox("★")
            star_cb.setStyleSheet(
                """
                QCheckBox { spacing: 0px; color: #888888; font-size: 14px; }
                QCheckBox::indicator { width: 0px; height: 0px; border: none; }
                QCheckBox:checked { color: #FFD700; font-weight: bold; }
                QCheckBox:hover { color: #FFA500; }
            """
            )
            self.star_checkboxes.append(star_cb)

        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setFixedSize(16, 16)
        self.checkbox.setStyleSheet(
            """
            QCheckBox::indicator {
                width: 14px; height: 14px; border: 1px solid #555;
                border-radius: 2px; background-color: #2A2D2E;
            }
            QCheckBox::indicator:checked { 
                background-color: #007ACC; border-color: #007ACC; 
            }
            QCheckBox::indicator:hover { border-color: #007ACC; }
        """
        )

        bottom_row.addWidget(self.tile_number_label)
        bottom_row.addStretch()
        for star_cb in self.star_checkboxes:
            bottom_row.addWidget(star_cb)
        bottom_row.addStretch()
        bottom_row.addWidget(self.checkbox)

        # Dodanie elementów do głównego layoutu
        layout.addWidget(self.thumbnail_container)

        # Dodajemy nazwę pliku w osobnym layoutcie poziomym dla wycentrowania
        filename_container = QHBoxLayout()
        filename_container.addStretch()
        filename_container.addWidget(self.filename_label)
        filename_container.addWidget(self.texture_icon)  # Ikona texture obok nazwy
        filename_container.addStretch()
        layout.addLayout(filename_container)

        # Dodajemy stretch, który dopycha dolny rząd do dołu
        layout.addStretch(1)

        # Dolny rząd z numerem, gwiazdkami i checkboxem - teraz przyklejony do dołu
        layout.addLayout(bottom_row)

        self.setAcceptDrops(False)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.asset_data:
            self._start_drag(event)
        else:
            super().mousePressEvent(event)

    def _start_drag(self, event):
        try:
            drag = QDrag(self)
            mime_data = QMimeData()
            asset_json = json.dumps(self.asset_data)
            mime_data.setData("application/x-cfab-asset", asset_json.encode("utf-8"))
            mime_data.setText(f"Asset: {self.asset_data.get('name', 'Unknown')}")
            drag.setMimeData(mime_data)
            pixmap = self.thumbnail_container.pixmap()
            if pixmap and not pixmap.isNull():
                drag.setPixmap(
                    pixmap.scaled(
                        64,
                        64,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                drag.setHotSpot(drag.pixmap().rect().center())
            self.drag_started.emit(self.asset_data)
            drag.exec(Qt.DropAction.MoveAction | Qt.DropAction.CopyAction)
        except Exception as e:
            print(f"Błąd podczas rozpoczęcia drag: {e}")

    def _on_thumbnail_clicked(self, ev):
        if self.asset_data:
            self.thumbnail_clicked.emit(self.asset_data.get("name", ""))

    def _on_filename_clicked(self, ev):
        if self.asset_data:
            self.filename_clicked.emit(self.asset_data.get("name", ""))

    def _create_placeholder_thumbnail(self):
        pixmap = QPixmap(self.thumbnail_size, self.thumbnail_size)
        pixmap.fill(QColor("#2A2D2E"))
        painter = QPainter(pixmap)
        painter.setPen(QColor("#CCCCCC"))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "IMG")
        painter.end()
        self.thumbnail_container.setPixmap(pixmap)

    def update_thumbnail_size(self, new_size: int):
        """Aktualizuje rozmiar miniaturki i CAŁEGO kafelka"""
        self.thumbnail_size = new_size
        self.thumbnail_container.setFixedSize(new_size, new_size)

        # *** KLUCZOWA ZMIANA: Aktualizujemy szerokość całego kafelka ***
        self.setFixedWidth(self.thumbnail_size + (2 * self.margins_size))

        # Odśwież miniaturkę z nowym rozmiarem
        # (W realnej aplikacji tu byś ponownie ładował z cache)
        self._create_placeholder_thumbnail()

        # Powiadom layout o zmianie geometrii
        self.updateGeometry()

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
        self.filename = filename
        self.filename_label.setText(filename)

    def set_asset_data(self, asset_data: dict):
        self.asset_data = asset_data
        # Pokaż ikonę texture jeśli tekstury są w archiwum
        if asset_data and asset_data.get('textures_in_the_archive', False):
            self.show_texture_icon()
        else:
            self.hide_texture_icon()

    def show_texture_icon(self):
        """Pokazuje ikonę texture"""
        self.texture_icon.setVisible(True)

    def hide_texture_icon(self):
        """Ukrywa ikonę texture"""
        self.texture_icon.setVisible(False)

    def set_tile_number(self, tile_number: int, total_tiles: int):
        self.tile_number = tile_number
        self.total_tiles = total_tiles
        self.tile_number_label.setText(f"{tile_number} / {total_tiles}")

    def is_checked(self) -> bool:
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool):
        self.checkbox.setChecked(checked)

    def get_star_rating(self) -> int:
        return sum(1 for cb in self.star_checkboxes if cb.isChecked())

    def set_star_rating(self, rating: int):
        rating = max(0, min(6, rating))
        for i, cb in enumerate(self.star_checkboxes):
            cb.setChecked(i < rating)

    def clear_stars(self):
        for cb in self.star_checkboxes:
            cb.setChecked(False)

    def _load_texture_icon(self):
        """Ładuje ikonę texture"""
        try:
            # Ścieżka do ikony texture
            icon_path = os.path.join(
                os.path.dirname(__file__), "resources", "img", "texture.png"
            )
            
            if os.path.exists(icon_path):
                # Załaduj i przeskaluj ikonę
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    # Przeskaluj do rozmiaru 16x16
                    scaled_pixmap = pixmap.scaled(
                        16,
                        16,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.texture_icon.setPixmap(scaled_pixmap)
                    # Nie pokazuj automatycznie - ikona zostanie pokazana gdy będzie potrzebna
                else:
                    self._create_fallback_texture_icon()
            else:
                self._create_fallback_texture_icon()
                
        except Exception as e:
            print(f"Błąd ładowania ikony texture: {e}")
            self._create_fallback_texture_icon()

    def _create_fallback_texture_icon(self):
        """Tworzy zapasową ikonę texture jako tekst"""
        self.texture_icon.setText("🔳")
        self.texture_icon.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                color: #888888;
            }
        """
        )


class FolderTile(QFrame):
    """
    Kafelek dla specjalnych folderów (tex, textures, maps)
    """

    folder_clicked = pyqtSignal(str)  # Sygnał z ścieżką do folderu

    def __init__(self, thumbnail_size: int, folder_name: str, folder_path: str):
        super().__init__()
        self.thumbnail_size = thumbnail_size
        self.folder_name = folder_name
        self.folder_path = folder_path
        self.margins_size = 8
        self._setup_ui()

    def _setup_ui(self):
        """Setup wyglądu kafelka folderu"""
        self.setStyleSheet(
            """
            FolderTile {
                background-color: #2D3E50;
                border: 1px solid #34495E;
                border-radius: 6px;
            }
            FolderTile:hover {
                border-color: #3498DB;
                background-color: #34495E;
            }
        """
        )

        # Polityka rozmiaru - stała szerokość
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedWidth(self.thumbnail_size + (2 * self.margins_size))
        self.setFixedHeight(self.thumbnail_size + 60)  # Dodatkowe miejsce na tekst

        # Główny layout pionowy
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(
            self.margins_size, self.margins_size, self.margins_size, self.margins_size
        )

        # Ikona folderu
        self.folder_icon = QLabel()
        self.folder_icon.setFixedSize(self.thumbnail_size, self.thumbnail_size)
        self.folder_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.folder_icon.setStyleSheet(
            """
            QLabel {
                background-color: #34495E;
                border: 2px solid transparent;
                border-radius: 4px;
            }
            QLabel:hover {
                border-color: #3498DB;
            }
        """
        )
        self.folder_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.folder_icon.mousePressEvent = self._on_folder_clicked
        self._load_folder_icon()

        # Nazwa folderu
        self.folder_label = QLabel(self.folder_name)
        self.folder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.folder_label.setWordWrap(True)
        self.folder_label.setStyleSheet(
            """
            QLabel {
                color: #ECF0F1; 
                background-color: transparent; 
                font-size: 11px;
                font-weight: bold;
                padding: 2px;
            }
            QLabel:hover {
                color: #3498DB;
            }
        """
        )
        self.folder_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.folder_label.mousePressEvent = self._on_folder_clicked

        # Dodanie elementów do layoutu
        layout.addWidget(self.folder_icon)
        
        # Wycentrowanie nazwy folderu
        filename_container = QHBoxLayout()
        filename_container.addStretch()
        filename_container.addWidget(self.folder_label)
        filename_container.addStretch()
        layout.addLayout(filename_container)

        layout.addStretch()

    def _load_folder_icon(self):
        """Ładuje ikonę folderu z resources"""
        try:
            # Ścieżka do ikony folderu
            icon_path = os.path.join(
                os.path.dirname(__file__), "resources", "img", "folder.png"
            )
            
            if os.path.exists(icon_path):
                # Załaduj i przeskaluj ikonę
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    # Przeskaluj do rozmiaru thumbnail z zachowaniem proporcji
                    scaled_pixmap = pixmap.scaled(
                        self.thumbnail_size - 20,  # Lekko mniejsza niż kontener
                        self.thumbnail_size - 20,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.folder_icon.setPixmap(scaled_pixmap)
                else:
                    self._create_fallback_icon()
            else:
                self._create_fallback_icon()
                
        except Exception as e:
            print(f"Błąd ładowania ikony folderu: {e}")
            self._create_fallback_icon()

    def _create_fallback_icon(self):
        """Tworzy zapasową ikonę folderu jako tekst"""
        self.folder_icon.setText("📁")
        self.folder_icon.setStyleSheet(
            self.folder_icon.styleSheet() + """
            QLabel {
                font-size: 48px;
                color: #3498DB;
            }
        """
        )

    def _on_folder_clicked(self, event):
        """Obsługa kliknięcia w folder - emituje sygnał"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.folder_clicked.emit(self.folder_path)

    def update_thumbnail_size(self, new_size: int):
        """Aktualizuje rozmiar kafelka folderu"""
        self.thumbnail_size = new_size
        self.setFixedWidth(new_size + (2 * self.margins_size))
        self.setFixedHeight(new_size + 60)
        self.folder_icon.setFixedSize(new_size, new_size)
        
        # Ponownie załaduj ikonę w nowym rozmiarze
        self._load_folder_icon()


class PreviewWindow(QDialog):
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.original_pixmap = None
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"Podgląd - {os.path.basename(self.image_path)}")
        self.setModal(False)
        self.setStyleSheet(
            "QDialog { background-color: #1E1E1E; border: 2px solid #3F3F46; }"
        )
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        self.load_image_and_resize()
        self.show()
        self.raise_()
        self.activateWindow()

    def load_image_and_resize(self):
        try:
            self.original_pixmap = QPixmap(self.image_path)
            if not self.original_pixmap.isNull():
                screen = QApplication.primaryScreen().availableGeometry()
                max_width = screen.width() - 100
                max_height = screen.height() - 100
                scale = min(
                    max_width / self.original_pixmap.width(),
                    max_height / self.original_pixmap.height(),
                    1.0,
                )
                new_width, new_height = int(self.original_pixmap.width() * scale), int(
                    self.original_pixmap.height() * scale
                )
                self.resize(new_width, new_height)
                self.move(
                    (screen.width() - new_width) // 2,
                    (screen.height() - new_height) // 2,
                )
                self.load_image()
        except Exception as e:
            self.image_label.setText(f"Błąd ładowania obrazu: {e}")

    def load_image(self):
        if self.original_pixmap:
            self.image_label.setPixmap(
                self.original_pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.load_image()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Testowy kafelek z bardzo długą nazwą, która MUSI się złamać.
    long_filename = (
        "jebany_kurwa_bardzo_dlugi_przyklad_nazwy_pliku_ktory_musi_sie_zlamac.jpg"
    )
    w = ThumbnailTile(128, long_filename, 1, 10)
    w.show()

    # Pokażmy też drugi, większy, dla porównania skalowania
    w2 = ThumbnailTile(256, "krotka_nazwa.png", 2, 10)
    w2.move(w.pos().x() + w.width() + 20, w.pos().y())  # Przesuń drugi kafelek obok
    w2.show()

    sys.exit(app.exec())
