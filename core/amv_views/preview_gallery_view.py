import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QScrollArea, QVBoxLayout, QWidget

from core.amv_views.preview_tile import PreviewTile

logger = logging.getLogger(__name__)


class PreviewGalleryView(QWidget):
    """Preview Gallery z Object Pooling"""

    preview_selected = pyqtSignal(str)
    preview_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_thumbnail_size = 128  # Default size
        self.selected_preview = None

        # Object Pooling dla PreviewTile
        self._tile_pool = []  # Pula nieużywanych kafelków
        self._active_tiles = []  # Lista aktywnych kafelków
        self._max_pool_size = 30  # Maksymalny rozmiar puli
        self._current_preview_paths = []  # Aktualne ścieżki podglądów

        self.init_ui()

    def _get_tile_from_pool(self, path: str, thumbnail_size: int) -> PreviewTile:
        """
        Pobiera kafelek z puli lub tworzy nowy jeśli pula jest pusta.
        """
        if self._tile_pool:
            # Pobierz kafelek z puli
            tile = self._tile_pool.pop()
            # Zaktualizuj dane kafelka
            tile.update_preview_data(path, thumbnail_size)
            logger.debug(f"Reused preview tile from pool for: {path}")
        else:
            # Utwórz nowy kafelek
            tile = PreviewTile(path, thumbnail_size)
            logger.debug(f"Created new preview tile for: {path}")

        return tile

    def _return_tile_to_pool(self, tile: PreviewTile):
        """
        Zwraca kafelek do puli do ponownego użycia.
        """
        if len(self._tile_pool) < self._max_pool_size:
            # Resetuj kafelek do stanu czystego
            if hasattr(tile, "reset_for_pool"):
                tile.reset_for_pool()

            # Usuń kafelek z layoutu
            if tile.parent():
                tile.setParent(None)

            # Dodaj do puli
            self._tile_pool.append(tile)
            logger.debug("Returned preview tile to pool")
        else:
            # Pula jest pełna, usuń kafelek
            tile.deleteLater()
            logger.debug("Preview pool full, deleted tile")

    def _clear_active_tiles(self):
        """
        Usuwa wszystkie aktywne kafelki i zwraca je do puli.
        """
        for tile in self._active_tiles:
            # Odłącz sygnały
            try:
                tile.checked.disconnect()
                tile.clicked.disconnect()
            except (TypeError, AttributeError):
                pass  # Sygnały już odłączone lub nie istnieją

            # Zwróć do puli
            self._return_tile_to_pool(tile)

        self._active_tiles.clear()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Scroll Area for gallery
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.gallery_widget = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_widget)
        self.gallery_layout.setContentsMargins(5, 5, 5, 5)
        self.gallery_layout.setSpacing(5)
        self.gallery_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        self.scroll_area.setWidget(self.gallery_widget)
        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)

    def set_previews(self, preview_paths: list[str]):
        # Zapamiętaj nowe ścieżki
        self._current_preview_paths = preview_paths[:]

        # Wyczyść aktywne kafelki (zwróć do puli)
        self._clear_active_tiles()
        self.selected_preview = None

        # Dodaj nowe kafelki używając poolingu
        col = 0
        row = 0
        for path in preview_paths:
            tile = self._get_tile_from_pool(path, self.current_thumbnail_size)
            tile.checked.connect(self._on_preview_checked)
            tile.clicked.connect(self._on_preview_clicked)
            self.gallery_layout.addWidget(tile, row, col)
            self._active_tiles.append(tile)

            col += 1
            if col >= self.get_columns_count():
                col = 0
                row += 1

        self.gallery_widget.update()

    def on_slider_value_changed(self, value: int):
        self.current_thumbnail_size = value
        self.update_tile_sizes()

    def update_tile_sizes(self):
        for tile in self._active_tiles:
            if hasattr(tile, "update_thumbnail_size"):
                tile.update_thumbnail_size(self.current_thumbnail_size)
        self.gallery_layout.invalidate()

    def _on_preview_checked(self, file_path: str, checked: bool):
        if checked:
            # Uncheck all other previews
            for tile in self._active_tiles:
                if (
                    hasattr(tile, "file_path")
                    and tile.file_path != file_path
                    and hasattr(tile, "is_checked")
                    and tile.is_checked()
                ):
                    tile.set_checked(False)
            self.selected_preview = file_path
            self.preview_selected.emit(file_path)
        else:
            if self.selected_preview == file_path:
                self.selected_preview = None
                self.preview_selected.emit("")

    def _on_preview_clicked(self, file_path: str):
        self.preview_clicked.emit(file_path)

    def get_columns_count(self) -> int:
        # Calculate number of columns based on current width and tile size
        if self.width() > 0 and self.current_thumbnail_size > 0:
            # Add some padding/margin to tile size for calculation
            tile_width_with_margin = (
                self.current_thumbnail_size + 20
            )  # Approx tile width + padding
            return max(1, self.width() // tile_width_with_margin)
        return 1  # Default to 1 column if width is not yet determined

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Optymalizacja: nie przebudowuj całej galerii, tylko zmień layout
        if hasattr(self, "_current_preview_paths"):
            # Przelicz kolumny i przeorganizuj istniejące kafelki
            cols = self.get_columns_count()
            col = 0
            row = 0

            for i, tile in enumerate(self._active_tiles):
                self.gallery_layout.addWidget(tile, row, col)
                col += 1
                if col >= cols:
                    col = 0
                    row += 1

    def get_selected_preview(self):
        return self.selected_preview
