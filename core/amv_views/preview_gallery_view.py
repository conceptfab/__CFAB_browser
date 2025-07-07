import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QScrollArea, QVBoxLayout, QWidget

from core.amv_views.preview_tile import PreviewTile

logger = logging.getLogger(__name__)


class PreviewGalleryView(QWidget):
    """Preview Gallery - simplified version without Object Pooling"""

    preview_selected = pyqtSignal(str)
    preview_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_thumbnail_size = 128  # Default size
        self.selected_preview = None
        self._current_preview_paths = []  # Current preview paths

        self.init_ui()

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

    def _clear_gallery(self):
        """Removes all widgets from the gallery in an optimized way."""
        self.setUpdatesEnabled(False)
        for i in reversed(range(self.gallery_layout.count())):
            item = self.gallery_layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                self.gallery_layout.removeWidget(widget)
                widget.deleteLater()
        self.setUpdatesEnabled(True)

    def set_previews(self, preview_paths: list[str]):
        logger.info(
            f"PreviewGalleryView.set_previews() called with {len(preview_paths)} paths"
        )

        self._current_preview_paths = preview_paths[:]
        self.selected_preview = None

        self._clear_gallery()

        col = 0
        row = 0
        for path in preview_paths:
            tile = PreviewTile(path, self.current_thumbnail_size)
            tile.checked.connect(self._on_preview_checked)
            tile.clicked.connect(self._on_preview_clicked)
            self.gallery_layout.addWidget(tile, row, col)

            col += 1
            if col >= self.get_columns_count():
                col = 0
                row += 1

        logger.info(f"Created {len(self._current_preview_paths)} preview tiles")
        self.gallery_widget.update()

    def on_slider_value_changed(self, value: int):
        self.current_thumbnail_size = value
        self.update_tile_sizes()

    def update_tile_sizes(self):
        for i in range(self.gallery_layout.count()):
            tile = self.gallery_layout.itemAt(i).widget()
            if isinstance(tile, PreviewTile):
                tile.update_thumbnail_size(self.current_thumbnail_size)
        self.gallery_layout.invalidate()

    def _on_preview_checked(self, file_path: str, checked: bool):
        if checked:
            # Uncheck all other previews
            for i in range(self.gallery_layout.count()):
                tile = self.gallery_layout.itemAt(i).widget()
                if (
                    isinstance(tile, PreviewTile)
                    and tile.file_path != file_path
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
        if self.width() > 0 and self.current_thumbnail_size > 0:
            tile_width_with_margin = self.current_thumbnail_size + 20
            return max(1, self.width() // tile_width_with_margin)
        return 1

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reorganize_tiles()

    def get_selected_preview(self):
        return self.selected_preview

    def remove_preview_by_path(self, path_to_remove: str):
        logger.info(f"Removing preview from gallery: {path_to_remove}")

        tile_to_remove = None
        for i in range(self.gallery_layout.count()):
            tile = self.gallery_layout.itemAt(i).widget()
            if isinstance(tile, PreviewTile) and tile.file_path == path_to_remove:
                tile_to_remove = tile
                break

        if tile_to_remove:
            self.gallery_layout.removeWidget(tile_to_remove)
            tile_to_remove.deleteLater()

            if path_to_remove in self._current_preview_paths:
                self._current_preview_paths.remove(path_to_remove)

            self._reorganize_tiles()
            logger.info(f"Successfully removed preview: {path_to_remove}")
        else:
            logger.warning(f"Preview not found in gallery: {path_to_remove}")

    def _reorganize_tiles(self):
        """Reorganizes tiles in the layout after resizing or removing an item"""
        widgets = []
        while self.gallery_layout.count():
            child = self.gallery_layout.takeAt(0)
            if child.widget():
                widgets.append(child.widget())

        col = 0
        row = 0
        cols = self.get_columns_count()

        for widget in widgets:
            self.gallery_layout.addWidget(widget, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1

        self.gallery_widget.update()
