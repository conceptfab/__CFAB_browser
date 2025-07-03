"""
AssetTileView - Widok dla pojedynczego kafelka assetu
Prezentuje miniaturkę, nazwę pliku, gwiazdki i checkbox dla assetu.
"""

import logging
import os

from PyQt6.QtCore import QMimeData, QPoint, QSize, Qt, QThreadPool, pyqtSignal
from PyQt6.QtGui import QColor, QDrag, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.base_widgets import BaseCheckBox, BaseLabel, StarCheckBoxBase, TileBase
from core.thumbnail_cache import thumbnail_cache
from core.workers.thumbnail_loader_worker import ThumbnailLoaderWorker

from ..amv_models.asset_tile_model import AssetTileModel
from ..amv_models.selection_model import SelectionModel

logger = logging.getLogger(__name__)


class AssetTileView(TileBase):
    """Widok dla pojedynczego kafelka assetu - ETAP 15 + Object Pooling"""

    thumbnail_clicked = pyqtSignal(str, str, object)  # asset_id, asset_path, tile
    filename_clicked = pyqtSignal(str, str, object)  # asset_id, asset_path, tile
    checkbox_state_changed = pyqtSignal(bool)  # Czy kafelek jest zaznaczony
    drag_started = pyqtSignal(object)  # Dane assetu

    # Globalny QThreadPool do zarządzania workerami
    thread_pool = QThreadPool()

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
        self.is_loading_thumbnail = False

        self.margins_size = 8
        self.setObjectName("AssetTileViewFrame")  # Added object name
        self._setup_ui()
        self.model.data_changed.connect(self.update_ui)

        asset_name = self.asset_id
        logger.debug(f"AssetTileView data updated for asset: {asset_name}")

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
        if hasattr(self, "model") and self.model is not None:
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

        logger.debug("AssetTileView reset for pool reuse")

    def _setup_ui(self):
        # Najpierw utwórz miniaturkę!
        self.thumbnail_container = BaseLabel()
        thumb_size = self.thumbnail_size
        self.thumbnail_container.setFixedSize(thumb_size, thumb_size)
        self.thumbnail_container.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.thumbnail_container.setCursor(Qt.CursorShape.PointingHandCursor)
        # Najpierw utwórz ikonę tekstury!
        self.texture_icon = BaseLabel()
        self.texture_icon.setFixedSize(16, 16)
        self.texture_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.texture_icon.setVisible(False)
        self._load_texture_icon()
        # Najpierw utwórz label na nazwę pliku!
        self.name_label = QLabel()
        self.name_label.setObjectName("AssetNameLabel")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        self.name_label.setCursor(Qt.CursorShape.PointingHandCursor)
        # Dodaj label na rozmiar pliku
        self.size_label = QLabel()
        self.size_label.setObjectName("AssetSizeLabel")
        self.size_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.size_label.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )
        # Dodaj label na numer kafelka
        self.tile_number_label = QLabel()
        self.tile_number_label.setObjectName("AssetTileNumberLabel")
        self.tile_number_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tile_number_label.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )
        # Dodaj checkbox
        self.checkbox = BaseCheckBox()
        self.checkbox.setObjectName("AssetTileCheckBox")
        # Dodaj gwiazdki (5)
        self.star_checkboxes = [StarCheckBoxBase() for _ in range(5)]
        for i, star_cb in enumerate(self.star_checkboxes):
            star_cb.setObjectName(f"AssetTileStar_{i+1}")
            star_cb.setProperty("class", "star")
            star_cb.setText("★")
            star_cb.clicked.connect(
                lambda checked, rating=i + 1: self._on_star_clicked(rating)
            )
        self._setup_ui_without_styles()

    def _setup_ui_without_styles(self):
        # Najpierw utwórz miniaturkę!
        self.thumbnail_container = BaseLabel()
        thumb_size = self.thumbnail_size
        self.thumbnail_container.setFixedSize(thumb_size, thumb_size)
        self.thumbnail_container.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.thumbnail_container.setCursor(Qt.CursorShape.PointingHandCursor)
        # Najpierw utwórz ikonę tekstury!
        self.texture_icon = BaseLabel()
        self.texture_icon.setFixedSize(16, 16)
        self.texture_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.texture_icon.setVisible(False)
        self._load_texture_icon()
        # Najpierw utwórz label na nazwę pliku!
        self.name_label = QLabel()
        self.name_label.setObjectName("AssetNameLabel")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        self.name_label.setCursor(Qt.CursorShape.PointingHandCursor)
        # Dodaj label na rozmiar pliku
        self.size_label = QLabel()
        self.size_label.setObjectName("AssetSizeLabel")
        self.size_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.size_label.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )
        # Dodaj label na numer kafelka
        self.tile_number_label = QLabel()
        self.tile_number_label.setObjectName("AssetTileNumberLabel")
        self.tile_number_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tile_number_label.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )
        # Dodaj checkbox
        self.checkbox = BaseCheckBox()
        self.checkbox.setObjectName("AssetTileCheckBox")
        # Dodaj gwiazdki (5)
        self.star_checkboxes = [StarCheckBoxBase() for _ in range(5)]
        for i, star_cb in enumerate(self.star_checkboxes):
            star_cb.setObjectName(f"AssetTileStar_{i+1}")
            star_cb.setProperty("class", "star")
            star_cb.setText("★")
            star_cb.clicked.connect(
                lambda checked, rating=i + 1: self._on_star_clicked(rating)
            )
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Ustaw sztywny rozmiar kafelka na podstawie miniatury
        tile_width = self.thumbnail_size + (2 * self.margins_size)
        tile_height = self.thumbnail_size + 70
        self.setFixedSize(tile_width, tile_height)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)

        # MINIATURKA - najważniejsza, 10px marginesów wokół
        thumb_container = QWidget()
        thumb_layout = QVBoxLayout(thumb_container)
        thumb_layout.setContentsMargins(10, 10, 10, 10)
        thumb_layout.setSpacing(0)
        self.thumbnail_container.setContentsMargins(0, 0, 0, 0)
        thumb_layout.addWidget(self.thumbnail_container)
        layout.addWidget(thumb_container)

        # Pasek z nazwą pliku, ikonką tekstury i rozmiarem
        filename_container = QHBoxLayout()
        filename_container.setContentsMargins(12, 6, 12, 6)
        filename_container.setSpacing(8)
        filename_container.addWidget(self.texture_icon, 0, Qt.AlignmentFlag.AlignLeft)
        filename_container.addWidget(self.name_label, 1)
        filename_container.addWidget(self.size_label, 0, Qt.AlignmentFlag.AlignRight)
        filename_bg = QWidget()
        filename_bg.setLayout(filename_container)
        layout.addWidget(filename_bg)

        # Pasek z gwiazdkami, numerem i checkboxem
        bottom_row_bg = QWidget()
        bottom_row_layout = QHBoxLayout(bottom_row_bg)
        bottom_row_layout.setContentsMargins(12, 6, 12, 12)
        bottom_row_layout.setSpacing(10)
        bottom_row_layout.addWidget(self.tile_number_label)
        bottom_row_layout.addStretch()
        for star_cb in self.star_checkboxes:
            bottom_row_layout.addWidget(star_cb)
        bottom_row_layout.addStretch()
        bottom_row_layout.addWidget(self.checkbox)
        layout.addWidget(bottom_row_bg)

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
        # Ogranicz długość nazwy do 16 znaków
        if len(file_name) > 16:
            display_name = file_name[:13] + "..."
        else:
            display_name = file_name

        file_size_mb = self.model.get_size_mb()
        self.name_label.setText(display_name)
        if file_size_mb > 0:
            self.size_label.setText(f"{file_size_mb:.1f} MB")
        else:
            self.size_label.setText("")

        self.tile_number_label.setText(f"{self.tile_number} / {self.total_tiles}")

        # Sprawdź czy gwiazdki mieszczą się na kafelku
        stars_visible = self._check_stars_fit()
        for star_cb in self.star_checkboxes:
            star_cb.setVisible(stars_visible)

        self.set_star_rating(self.model.get_stars())
        self.texture_icon.setVisible(self.model.has_textures_in_archive())
        self.checkbox.setVisible(True)

        # Krok 1: Spróbuj załadować z cache
        thumbnail_path = self.model.get_thumbnail_path()
        cached_pixmap = thumbnail_cache.get(thumbnail_path)

        if cached_pixmap:
            self._set_thumbnail_pixmap(cached_pixmap)
        elif thumbnail_path and os.path.exists(thumbnail_path):
            # Krok 2: Jeśli nie ma w cache, załaduj asynchronicznie
            self._create_placeholder_thumbnail()
            self._load_thumbnail_async(thumbnail_path)
        else:
            # Krok 3: Jeśli plik nie istnieje, pokaż placeholder
            self._create_placeholder_thumbnail()

    def _load_thumbnail_async(self, path: str):
        if self.is_loading_thumbnail:
            return
        self.is_loading_thumbnail = True

        worker = ThumbnailLoaderWorker(path)
        worker.signals.finished.connect(self._on_thumbnail_loaded)
        worker.signals.error.connect(self._on_thumbnail_error)
        self.thread_pool.start(worker)

    def _on_thumbnail_loaded(self, path: str, pixmap: QPixmap):
        # Upewnij się, że ten kafelek wciąż oczekuje na tę konkretną miniaturę
        if self.model and path == self.model.get_thumbnail_path():
            thumbnail_cache.put(path, pixmap)
            self._set_thumbnail_pixmap(pixmap)
            self.is_loading_thumbnail = False

    def _on_thumbnail_error(self, path: str, error_message: str):
        if self.model and path == self.model.get_thumbnail_path():
            logger.warning(error_message)
            self._create_placeholder_thumbnail()
            self.is_loading_thumbnail = False

    def _set_thumbnail_pixmap(self, pixmap: QPixmap):
        """Ustawia QPixmap na etykiecie miniaturki, skalując go."""
        scaled_pixmap = pixmap.scaled(
            self.thumbnail_size,
            self.thumbnail_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.thumbnail_container.setPixmap(scaled_pixmap)

    def _setup_folder_tile_ui(self):
        # Wyświetlanie nazwy folderu
        folder_name = self.model.get_name()
        # Ogranicz długość nazwy do 16 znaków
        if len(folder_name) > 16:
            display_name = folder_name[:13] + "..."
        else:
            display_name = folder_name

        self.name_label.setText(display_name)
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
        self.thumbnail_container.setPixmap(
            self._load_icon_with_fallback(
                "folder.png", (self.thumbnail_size, self.thumbnail_size)
            )
        )

    def _load_texture_icon(self):
        self.texture_icon.setPixmap(
            self._load_icon_with_fallback("texture.png", (16, 16))
        )

    def mousePressEvent(self, event):
        """Obsługuje naciśnięcie myszy - kliknięcia i drag & drop."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_position = event.position().toPoint()

            # Sprawdź, który widget został kliknięty
            clicked_widget = self.childAt(event.position().toPoint())

            # Jeśli wciśnięty jest Shift, nie pokazuj podglądu ani archiwum
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                logger.debug(
                    "Shift wciśnięty - blokada podglądu/archiwum, tylko drag and drop"
                )
                super().mousePressEvent(event)
                return

            # Obsługa kliknięć na miniaturkę
            if clicked_widget == self.thumbnail_container or (
                clicked_widget and clicked_widget.parent() == self.thumbnail_container
            ):
                self._on_thumbnail_clicked(event)
                return

            # Obsługa kliknięć na nazwę pliku
            if clicked_widget == self.name_label:
                self._on_filename_clicked(event)
                return

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
        # Blokada D&D gdy trwa ładowanie galerii
        if hasattr(self, "_drag_and_drop_enabled") and not self._drag_and_drop_enabled:
            logger.info("Drag and drop zablokowane podczas ładowania galerii.")
            return
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
            folder_path = self.model.get_special_folder_path()
            self.thumbnail_clicked.emit(self.asset_id, folder_path, self)
        else:
            self.thumbnail_clicked.emit(
                self.asset_id, self.model.get_preview_path(), self
            )

    def _on_filename_clicked(self, ev):
        logger.debug(f"AssetTileView: Filename clicked for asset {self.asset_id}")
        if self.model.is_special_folder:
            folder_path = self.model.get_special_folder_path()
            self.filename_clicked.emit(self.asset_id, folder_path, self)
        else:
            self.filename_clicked.emit(
                self.asset_id, self.model.get_archive_path(), self
            )

    def update_thumbnail_size(self, new_size: int):
        """Aktualizuje rozmiar miniatury i przelicza layout."""
        self.thumbnail_size = new_size
        # Przelicz szerokość kafelka
        tile_width = new_size + (2 * self.margins_size)
        tile_height = new_size + 70
        self.setFixedSize(tile_width, tile_height)
        self.update_ui()  # Przeładuj UI, aby zastosować nowy rozmiar

    def _update_stars_visibility(self):
        """Aktualizuje widoczność gwiazdek na podstawie dostępnej przestrzeni."""
        if hasattr(self, "model") and self.model and not self.model.is_special_folder:
            stars_visible = self._check_stars_fit()
            for star_cb in self.star_checkboxes:
                star_cb.setVisible(stars_visible)

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

    def set_drag_and_drop_enabled(self, enabled: bool):
        """Ustawia możliwość drag and drop dla kafelka."""
        self._drag_and_drop_enabled = enabled

    def _check_stars_fit(self) -> bool:
        """Sprawdza czy gwiazdki mieszczą się na kafelku."""
        # Oblicz dostępną szerokość dla gwiazdek
        # Szerokość kafelka - marginesy - numer - checkbox - odstępy
        available_width = self.width() - (2 * self.margins_size) - 30 - 16 - 12

        # Szacowana szerokość 5 gwiazdek (każda ~12px) + odstępy
        stars_width = 5 * 12 + 4 * 6  # 5 gwiazdek po 12px + 4 odstępy po 6px

        return stars_width <= available_width

    def resizeEvent(self, event):
        """Obsługuje zmianę rozmiaru kafelka."""
        super().resizeEvent(event)
        # Aktualizuj widoczność gwiazdek po zmianie rozmiaru
        self._update_stars_visibility()
        # Aktualizuj rozmiar miniatury, aby wypełnić dostępną przestrzeń
        self._update_thumbnail_size()

    def _update_thumbnail_size(self):
        """Aktualizuje rozmiar miniatury na podstawie dostępnej przestrzeni."""
        if hasattr(self, "thumbnail_container"):
            # Oblicz dostępną przestrzeń dla miniatury
            available_width = self.width() - (2 * self.margins_size)
            available_height = (
                self.height() - 70
            )  # Odejmij miejsce na tekst i kontrolki

            # Użyj mniejszego wymiaru, aby zachować proporcje kwadratu
            new_size = min(available_width, available_height, self.thumbnail_size)
            new_size = max(new_size, 64)  # Minimalny rozmiar 64px

            self.thumbnail_container.setFixedSize(new_size, new_size)
