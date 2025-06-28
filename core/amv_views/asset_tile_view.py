"""
AssetTileView - Widok dla pojedynczego kafelka assetu
Prezentuje miniaturkę, nazwę pliku, gwiazdki i checkbox dla assetu.
"""

import logging
import os

from PyQt6.QtCore import QPoint, Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QColor, QDrag, QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..amv_models.asset_tile_model import AssetTileModel
from ..amv_models.selection_model import SelectionModel

logger = logging.getLogger(__name__)


class AssetTileView(QFrame):
    """Widok dla pojedynczego kafelka assetu - ETAP 15"""

    thumbnail_clicked = pyqtSignal(str)  # Ścieżka do pliku podglądu
    filename_clicked = pyqtSignal(str)  # Ścieżka do pliku archiwum
    checkbox_state_changed = pyqtSignal(bool)  # Czy kafelek jest zaznaczony
    drag_started = pyqtSignal(object)  # Dane assetu

    def __init__(
        self,
        tile_model: AssetTileModel,
        thumbnail_size: int,
        tile_number: int,
        total_tiles: int,
        selection_model: SelectionModel,  # Dodaj selection_model
    ):
        super().__init__()
        self.model = tile_model
        self.thumbnail_size = thumbnail_size
        self.tile_number = tile_number
        self.total_tiles = total_tiles
        self.selection_model = selection_model  # Przypisz selection_model
        self.asset_id = self.model.get_name()  # Użyj nazwy assetu jako ID
        self._drag_start_position = (
            QPoint()
        )  # Dodaj atrybut do przechowywania pozycji startowej przeciągania

        self.margins_size = 8
        self._setup_ui()
        self.model.data_changed.connect(self.update_ui)

    def _setup_ui(self):
        self.setStyleSheet(
            """
            AssetTileView {
                background-color: #252526;
                border: 1px solid #3F3F46;
                border-radius: 6px;
            }
            AssetTileView:hover {
                border-color: #007ACC;
                background-color: #2D2D30;
            }
        """
        )

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setFixedWidth(self.thumbnail_size + (2 * self.margins_size))

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

        # RZĄD 2: Dolna sekcja (tekst, gwiazdki, etc.)
        # Nazwa pliku
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        self.name_label.setStyleSheet(
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
        self.name_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.name_label.mousePressEvent = self._on_filename_clicked

        # Ikona texture (ukryta domyślnie)
        self.texture_icon = QLabel()
        self.texture_icon.setFixedSize(16, 16)
        self.texture_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.texture_icon.setVisible(False)  # Ukryta domyślnie
        self._load_texture_icon()

        # Dolny rząd z numerem, gwiazdki i checkboxem
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(6)

        # Numer kafelka
        self.tile_number_label = QLabel()
        self.tile_number_label.setStyleSheet(
            "color: #888888; background-color: transparent; "
            "font-size: 9px; font-weight: bold;"
        )

        # Gwiazdki
        self.star_checkboxes = []
        for i in range(5):
            star_cb = QCheckBox("★")
            star_cb.setStyleSheet(
                """
                QCheckBox { spacing: 0px; color: #888888; font-size: 14px; border: none; padding: 0px; background: transparent; }
                QCheckBox::indicator { width: 0px; height: 0px; border: none; }
                QCheckBox:checked { color: #FFD700; font-weight: bold; }
                QCheckBox:hover { color: #FFA500; }
            """
            )
            star_cb.clicked.connect(
                lambda checked, star_index=i: self._on_star_clicked(star_index + 1)
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
        # Połącz sygnał stateChanged z metodą obsługującą zmianę zaznaczenia w modelu
        self.checkbox.stateChanged.connect(self._on_checkbox_state_changed)

        bottom_row.addWidget(self.tile_number_label)
        bottom_row.addStretch()  # Rozpycha elementy
        for star_cb in self.star_checkboxes:
            bottom_row.addWidget(star_cb)
        bottom_row.addStretch()  # Rozpycha elementy
        bottom_row.addWidget(self.checkbox)

        # Dodanie elementów do głównego layoutu
        layout.addWidget(self.thumbnail_container)

        # Dodajemy nazwę pliku w osobnym layoutcie poziomym dla wycentrowania
        filename_container = QHBoxLayout()
        filename_container.addStretch()
        filename_container.addWidget(self.name_label)
        filename_container.addWidget(self.texture_icon)  # Ikona texture obok nazwy
        filename_container.addStretch()
        layout.addLayout(filename_container)

        # Dodajemy stretch, który dopycha dolny rząd do dołu
        layout.addStretch(1)

        # Dolny rząd z numerem, gwiazdkami i checkboxem - teraz przyklejony do dołu
        layout.addLayout(bottom_row)

        self.setAcceptDrops(False)  # D&D będzie obsługiwane przez Controller
        self.setMouseTracking(True)

        self.update_ui()
        # Ustaw początkowy stan checkboxa na podstawie SelectionModel
        self.checkbox.setChecked(self.selection_model.is_selected(self.asset_id))

    def update_ui(self):
        if self.model.is_special_folder:
            self._setup_folder_tile_ui()
        else:
            self._setup_asset_tile_ui()

    def _setup_asset_tile_ui(self):
        # Wyświetlanie nazwy i rozmiaru pliku
        file_name = self.model.get_name()
        file_size_mb = self.model.get_size_mb()
        if file_size_mb > 0:
            self.name_label.setText(f"{file_name} ({file_size_mb:.1f} MB)")
        else:
            self.name_label.setText(file_name)

        self.tile_number_label.setText(f"{self.tile_number} / {self.total_tiles}")
        self.set_star_rating(self.model.get_stars())
        self.texture_icon.setVisible(self.model.has_textures_in_archive())
        self.checkbox.setVisible(True)

        # Załaduj miniaturkę
        thumbnail_path = self.model.get_thumbnail_path()
        if thumbnail_path and os.path.exists(thumbnail_path):
            pixmap = QPixmap(thumbnail_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.thumbnail_size,
                    self.thumbnail_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.thumbnail_container.setPixmap(scaled_pixmap)
            else:
                self._create_placeholder_thumbnail()
        else:
            self._create_placeholder_thumbnail()

    def _setup_folder_tile_ui(self):
        # Wyświetlanie nazwy folderu
        folder_name = self.model.get_name()
        self.name_label.setText(folder_name)
        self.tile_number_label.setText(f"{self.tile_number} / {self.total_tiles}")
        self.set_star_rating(0)  # Foldery nie mają gwiazdek
        self.texture_icon.setVisible(False)
        self.checkbox.setVisible(False)

        # Załaduj ikonę folderu
        self._load_folder_icon()

    def _create_placeholder_thumbnail(self):
        """Tworzy placeholder miniaturkę gdy nie ma obrazka."""
        pixmap = QPixmap(self.thumbnail_size, self.thumbnail_size)
        pixmap.fill(QColor("#2A2D2E"))
        self.thumbnail_container.setPixmap(pixmap)

    def _load_folder_icon(self):
        """Ładuje ikonę folderu."""
        try:
            icon_path = os.path.join(
                os.path.dirname(__file__), "..", "resources", "img", "folder.png"
            )
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.thumbnail_size,
                        self.thumbnail_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    self.thumbnail_container.setPixmap(scaled_pixmap)
                else:
                    self._create_fallback_icon()
            else:
                self._create_fallback_icon()
        except Exception as e:
            logger.error(f"Błąd podczas ładowania ikony folderu: {e}")
            self._create_fallback_icon()

    def _create_fallback_icon(self):
        """Tworzy fallback ikonę folderu."""
        pixmap = QPixmap(self.thumbnail_size, self.thumbnail_size)
        pixmap.fill(QColor("#2A2D2E"))
        self.thumbnail_container.setPixmap(pixmap)

    def _load_texture_icon(self):
        """Ładuje ikonę texture."""
        try:
            icon_path = os.path.join(
                os.path.dirname(__file__), "..", "resources", "img", "texture.png"
            )
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                    )
                    self.texture_icon.setPixmap(scaled_pixmap)
                else:
                    self._create_fallback_texture_icon()
            else:
                self._create_fallback_texture_icon()
        except Exception as e:
            logger.error(f"Błąd podczas ładowania ikony texture: {e}")
            self._create_fallback_texture_icon()

    def _create_fallback_texture_icon(self):
        """Tworzy fallback ikonę texture."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor("#FFD700"))
        self.texture_icon.setPixmap(pixmap)

    def mousePressEvent(self, event):
        """Obsługuje naciśnięcie myszy - zapisuje pozycję startową dla drag & drop."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_position = event.position().toPoint()
            logger.debug(f"Mouse press detected, saved drag start position: {self._drag_start_position}")
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Obsługuje ruch myszy - inicjuje drag & drop."""
        if (
            event.buttons() & Qt.MouseButton.LeftButton
            and (event.position().toPoint() - self._drag_start_position).manhattanLength()
            >= QApplication.startDragDistance()
        ):
            logger.debug(f"Mouse move detected, starting drag for asset: {self.asset_id}")
            self._start_drag(event)
        super().mouseMoveEvent(event)

    def _start_drag(self, event):
        logger.debug(f"Starting drag for asset: {self.asset_id}")
        
        # Pobierz zaznaczone assety z SelectionModel
        selected_asset_ids = self.selection_model.get_selected_asset_ids()
        logger.debug(f"Selected asset IDs: {selected_asset_ids}")
        
        # Jeśli nie ma zaznaczonych assetów, przeciągnij tylko ten kafelek
        if not selected_asset_ids:
            selected_asset_ids = [self.asset_id]
            logger.debug(f"No selected assets, dragging single asset: {selected_asset_ids}")

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_text = f"application/x-cfab-asset,{','.join(selected_asset_ids)}"
        mime_data.setText(mime_text)
        drag.setMimeData(mime_data)
        
        logger.debug(f"Created mime data: {mime_text}")

        # Ustaw kursor przeciągania
        drag.setDragCursor(QPixmap(), Qt.DropAction.MoveAction)

        # Emituj sygnał rozpoczęcia przeciągania
        self.drag_started.emit(selected_asset_ids)
        logger.debug(f"Emitted drag_started signal")

        # Wykonaj przeciąganie
        result = drag.exec(Qt.DropAction.MoveAction)
        logger.debug(f"Drag exec result: {result}")

    def _on_thumbnail_clicked(self, ev):
        """Obsługuje kliknięcie w miniaturkę."""
        preview_path = self.model.get_preview_path()
        if preview_path:
            self.thumbnail_clicked.emit(preview_path)

    def _on_filename_clicked(self, ev):
        """Obsługuje kliknięcie w nazwę pliku."""
        filename_path = self.model.get_archive_path()
        if filename_path:
            self.filename_clicked.emit(filename_path)

    def update_thumbnail_size(self, new_size: int):
        """Aktualizuje rozmiar miniaturki."""
        self.thumbnail_size = new_size
        self.setFixedWidth(self.thumbnail_size + (2 * self.margins_size))
        self.thumbnail_container.setFixedSize(self.thumbnail_size, self.thumbnail_size)
        self.update_ui()

    def is_checked(self) -> bool:
        """Sprawdza czy kafelek jest zaznaczony."""
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool):
        """Ustawia stan zaznaczenia kafelka."""
        # Odłącz sygnał tymczasowo, aby uniknąć rekurencji
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(checked)
        self.checkbox.blockSignals(False)
        
        # Ręcznie wywołaj metodę obsługującą zmianę stanu, aby zaktualizować model
        self._on_checkbox_state_changed(self.checkbox.checkState().value)

    def _on_checkbox_state_changed(self, state: int):
        """Obsługuje zmianę stanu checkboxa."""
        is_checked = state == Qt.CheckState.Checked.value
        if is_checked:
            self.selection_model.add_selection(self.asset_id)
        else:
            self.selection_model.remove_selection(self.asset_id)
        self.checkbox_state_changed.emit(is_checked)

    def get_star_rating(self) -> int:
        """Pobiera ocenę gwiazdkową."""
        return sum(1 for cb in self.star_checkboxes if cb.isChecked())

    def set_star_rating(self, rating: int):
        """Ustawia ocenę gwiazdkową."""
        for i, cb in enumerate(self.star_checkboxes):
            cb.setChecked(i < rating)

    def _on_star_clicked(self, clicked_rating: int):
        """Obsługuje kliknięcie w gwiazdkę."""
        current_rating = self.get_star_rating()
        if clicked_rating == current_rating:
            # Jeśli kliknięto w ostatnią zaznaczoną gwiazdkę, odznacz wszystkie
            self.clear_stars()
            self.model.set_stars(0)
        else:
            # Ustaw nową ocenę
            self.set_star_rating(clicked_rating)
            self.model.set_stars(clicked_rating)

    def clear_stars(self):
        for cb in self.star_checkboxes:
            cb.setChecked(False) 