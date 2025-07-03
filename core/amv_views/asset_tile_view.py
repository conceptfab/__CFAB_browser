"""
AssetTileView - Widok dla pojedynczego kafelka assetu
Prezentuje miniaturkę, nazwę pliku, gwiazdki i checkbox dla assetu.
"""

import logging
import os

from PyQt6.QtCore import QMimeData, QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QDrag, QPixmap
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout

from core.base_widgets import BaseCheckBox, BaseLabel, StarCheckBoxBase, TileBase

from ..amv_models.asset_tile_model import AssetTileModel
from ..amv_models.selection_model import SelectionModel

logger = logging.getLogger(__name__)


class AssetTileView(TileBase):
    """Widok dla pojedynczego kafelka assetu - ETAP 15 + Object Pooling"""

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
        self.setObjectName("AssetTileViewFrame")  # Added object name
        self._setup_ui()
        self.model.data_changed.connect(self.update_ui)

    def update_asset_data(
        self, tile_model: AssetTileModel, tile_number: int, total_tiles: int
    ):
        """
        Aktualizuje dane kafelka dla Object Pooling.
        Pozwala na ponowne wykorzystanie istniejącej instancji AssetTileView.
        """
        # Odłącz stare połączenie sygnału
        if hasattr(self, "model") and self.model:
            try:
                self.model.data_changed.disconnect(self.update_ui)
            except TypeError:
                pass  # Połączenie już nie istnieje

        # Zaktualizuj dane
        self.model = tile_model
        self.tile_number = tile_number
        self.total_tiles = total_tiles
        self.asset_id = self.model.get_name()

        # Podłącz nowe połączenie sygnału
        self.model.data_changed.connect(self.update_ui)

        # Natychmiast zaktualizuj UI z nowymi danymi
        self.update_ui()

        asset_name = self.asset_id
        logger.debug(f"AssetTileView data updated for asset: {asset_name}")

    def reset_for_pool(self):
        """
        Resetuje kafelek do stanu gotowego do ponownego użycia w puli.
        """
        try:
            # Odłącz połączenia sygnałów
            if hasattr(self, "model") and self.model:
                try:
                    self.model.data_changed.disconnect(self.update_ui)
                except (TypeError, RuntimeError):
                    pass  # Połączenie już odłączone lub obiekt usunięty

            # Wyczyść dane
            self.model = None
            self.asset_id = ""
            self.tile_number = 0
            self.total_tiles = 0

            # Wyczyść UI - z zabezpieczeniami
            try:
                if hasattr(self, "thumbnail_container"):
                    self.thumbnail_container.clear()
                if hasattr(self, "name_label"):
                    self.name_label.clear()
                if hasattr(self, "tile_number_label"):
                    self.tile_number_label.clear()
                if hasattr(self, "checkbox"):
                    self.checkbox.setChecked(False)

                # Wyczyść gwiazdki
                if hasattr(self, "star_checkboxes"):
                    for star_cb in self.star_checkboxes:
                        try:
                            star_cb.setChecked(False)
                        except RuntimeError:
                            pass  # Widget już usunięty

            except RuntimeError:
                pass  # Widget już usunięty

            logger.debug("AssetTileView reset for pool reuse")

        except RuntimeError as e:
            logger.debug(f"Error in reset_for_pool: {e} - object already deleted")

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

        # ZMIANA: Szerokość kafelka ZAWSZE = rozmiar miniatury + stałe marginesy
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # Ustaw STAŁĄ szerokość i wysokość kafelka
        tile_width = self.thumbnail_size + (2 * self.margins_size)
        tile_height = self.thumbnail_size + 120
        
        self.setFixedWidth(tile_width)  # STAŁA szerokość!
        self.setFixedHeight(tile_height)  # STAŁA wysokość!

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        margins = self.margins_size
        layout.setContentsMargins(margins, margins, margins, margins)

        # RZĄD 1: Miniaturka
        self.thumbnail_container = BaseLabel()
        thumb_size = self.thumbnail_size
        self.thumbnail_container.setFixedSize(thumb_size, thumb_size)
        self.thumbnail_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.thumbnail_container.mousePressEvent = self._on_thumbnail_clicked

        # RZĄD 2: Dolna sekcja (tekst, gwiazdki, etc.)
        # Nazwa pliku
        self.name_label = QLabel()
        self.name_label.setObjectName("AssetNameLabel")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        self.name_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.name_label.mousePressEvent = self._on_filename_clicked

        # Ikona texture (ukryta domyślnie)
        self.texture_icon = BaseLabel()
        self.texture_icon.setFixedSize(16, 16)
        self.texture_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.texture_icon.setVisible(False)  # Ukryta domyślnie
        self._load_texture_icon()

        # Dolny rząd z numerem, gwiazdki i checkboxem
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(6)

        # Numer kafelka
        self.tile_number_label = BaseLabel()
        style = (
            "color: #888888; background-color: transparent; "
            "font-size: 9px; font-weight: bold;"
        )
        self.tile_number_label.setStyleSheet(style)

        # Gwiazdki
        self.star_checkboxes = []
        for i in range(5):
            star_cb = StarCheckBoxBase("★")
            star_cb.clicked.connect(
                lambda checked, star_index=i: self._on_star_clicked(star_index + 1)
            )
            self.star_checkboxes.append(star_cb)

        # Checkbox
        self.checkbox = BaseCheckBox()
        self.checkbox.setFixedSize(16, 16)
        self.checkbox.stateChanged.connect(self._on_checkbox_state_changed)

        bottom_row.addWidget(self.tile_number_label)
        bottom_row.addStretch()  # Rozpycha elementy
        for star_cb in self.star_checkboxes:
            bottom_row.addWidget(star_cb)
        bottom_row.addStretch()  # Rozpycha elementy
        bottom_row.addWidget(self.checkbox)

        # Dodanie elementów do głównego layoutu
        layout.addWidget(self.thumbnail_container)

        # Dodajemy nazwę pliku w osobnym layoutcie poziomym
        filename_container = QHBoxLayout()
        filename_container.addStretch()
        filename_container.addWidget(self.name_label)
        filename_container.addWidget(self.texture_icon)
        filename_container.addStretch()
        layout.addLayout(filename_container)

        # Dodajemy mały stretch, ale nie rozciągamy na całą wysokość
        layout.addStretch(0)

        # Dolny rząd z numerem, gwiazdkami i checkboxem
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

        # Pokaż gwiazdki dla assetów
        for star_cb in self.star_checkboxes:
            star_cb.setVisible(True)

        self.set_star_rating(self.model.get_stars())
        self.texture_icon.setVisible(self.model.has_textures_in_archive())
        self.checkbox.setVisible(True)

        # Załaduj miniaturkę
        thumbnail_path = self.model.get_thumbnail_path()
        logger.debug(
            f"AssetTileView: Loading thumbnail for {self.model.get_name()}, path: {thumbnail_path}"
        )
        if thumbnail_path and os.path.exists(thumbnail_path):
            logger.debug(f"AssetTileView: Thumbnail exists: {thumbnail_path}")
            pixmap = QPixmap(thumbnail_path)
            if not pixmap.isNull():
                logger.debug(
                    f"AssetTileView: Thumbnail loaded successfully: {thumbnail_path}"
                )
                scaled_pixmap = pixmap.scaled(
                    self.thumbnail_size,
                    self.thumbnail_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.thumbnail_container.setPixmap(scaled_pixmap)
            else:
                logger.warning(
                    f"AssetTileView: Failed to load thumbnail: {thumbnail_path}"
                )
                self._create_placeholder_thumbnail()
        else:
            logger.warning(
                f"AssetTileView: Thumbnail path not found or doesn't exist: {thumbnail_path}"
            )
            self._create_placeholder_thumbnail()

    def _setup_folder_tile_ui(self):
        # Wyświetlanie nazwy folderu
        folder_name = self.model.get_name()
        self.name_label.setText(folder_name)
        self.tile_number_label.setText(f"{self.tile_number} / {self.total_tiles}")

        # Ukryj gwiazdki dla folderów
        for star_cb in self.star_checkboxes:
            star_cb.setVisible(False)

        self.texture_icon.setVisible(False)
        self.checkbox.setVisible(False)

        # Załaduj ikonę folderu
        self._load_folder_icon()

    def _create_placeholder_thumbnail(self):
        """Tworzy placeholder miniaturkę gdy nie ma obrazka."""
        pixmap = QPixmap(self.thumbnail_size, self.thumbnail_size)
        pixmap.fill(QColor("#2A2D2E"))
        self.thumbnail_container.setPixmap(pixmap)

    def _load_icon_with_fallback(self, icon_name: str, size: tuple) -> QPixmap:
        """Uniwersalna metoda ładowania ikon z fallback"""
        try:
            icon_path = os.path.join(
                os.path.dirname(__file__), "..", "resources", "img", icon_name
            )
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    return pixmap.scaled(
                        size[0],
                        size[1],
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
        except Exception as e:
            logger.error(f"Błąd podczas ładowania ikony {icon_name}: {e}")
        # Fallback: szary lub żółty prostokąt zależnie od ikony
        fallback = QPixmap(size[0], size[1])
        if icon_name == "texture.png":
            fallback.fill(QColor("#FFD700"))
        else:
            fallback.fill(QColor("#2A2D2E"))
        return fallback

    def _load_folder_icon(self):
        self.thumbnail_container.setPixmap(self._load_icon_with_fallback(
            "folder.png", (self.thumbnail_size, self.thumbnail_size)
        ))

    def _load_texture_icon(self):
        self.texture_icon.setPixmap(self._load_icon_with_fallback("texture.png", (16, 16)))

    def mousePressEvent(self, event):
        """Obsługuje naciśnięcie myszy - zapisuje pozycję startową dla drag & drop."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_position = event.position().toPoint()
            logger.debug(
                f"Mouse press detected, saved drag start position: {self._drag_start_position}"
            )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Obsługuje ruch myszy - inicjuje drag & drop."""
        if (
            event.buttons() & Qt.MouseButton.LeftButton
            and (
                event.position().toPoint() - self._drag_start_position
            ).manhattanLength()
            >= QApplication.startDragDistance()
        ):
            logger.debug(
                f"Mouse move detected, starting drag for asset: {self.asset_id}"
            )
            self._start_drag(event)
        super().mouseMoveEvent(event)

    def _start_drag(self, event):
        logger.debug(f"Starting drag for asset: {self.asset_id}")

        # Sprawdź czy selection_model istnieje
        if not self.selection_model:
            logger.error("selection_model is None, cannot start drag")
            return

        # Pobierz zaznaczone assety z SelectionModel
        selected_asset_ids = self.selection_model.get_selected_asset_ids()
        logger.debug(f"Selected asset IDs: {selected_asset_ids}")

        # Jeśli nie ma zaznaczonych assetów, przeciągnij tylko ten kafelek
        if not selected_asset_ids:
            selected_asset_ids = [self.asset_id]
            logger.debug(
                f"No selected assets, dragging single asset: {selected_asset_ids}"
            )

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
        logger.debug("Emitted drag_started signal")

        # Wykonaj przeciąganie
        result = drag.exec(Qt.DropAction.MoveAction)
        logger.debug(f"Drag exec result: {result}")

    def _on_thumbnail_clicked(self, ev):
        logger.debug(f"AssetTileView: Thumbnail clicked for asset {self.asset_id}")
        if self.model.is_special_folder:
            # Dla specjalnych folderów emituj ścieżkę do folderu
            folder_path = self.model.get_special_folder_path()
            self.thumbnail_clicked.emit(folder_path)
        else:
            # Dla zwykłych assetów emituj ścieżkę do podglądu
            self.thumbnail_clicked.emit(self.model.get_preview_path())

    def _on_filename_clicked(self, ev):
        logger.debug(f"AssetTileView: Filename clicked for asset {self.asset_id}")
        if self.model.is_special_folder:
            # Dla specjalnych folderów emituj ścieżkę do folderu
            folder_path = self.model.get_special_folder_path()
            self.filename_clicked.emit(folder_path)
        else:
            # Dla zwykłych assetów emituj ścieżkę do archiwum
            self.filename_clicked.emit(self.model.get_archive_path())

    def update_thumbnail_size(self, new_size: int):
        """Aktualizuje rozmiar miniaturki."""
        self.thumbnail_size = new_size
        self.setFixedWidth(new_size + (2 * self.margins_size))
        self.thumbnail_container.setFixedSize(self.thumbnail_size, self.thumbnail_size)
        self.update_ui()  # Przeładuj UI, aby zastosować nowy rozmiar

    def release_resources(self):
        """
        Zwalnia zasoby (np. QPixmap) przed umieszczeniem w puli lub usunięciem.
        """
        if hasattr(self, "thumbnail_container"):
            self.thumbnail_container.clear()
        logger.debug(f"Resources released for tile: {self.asset_id}")

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
