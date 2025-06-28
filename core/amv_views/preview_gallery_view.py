from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from core.amv_views.preview_tile import PreviewTile


class PreviewGalleryView(QWidget):
    preview_selected = pyqtSignal(str)
    preview_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_thumbnail_size = 128  # Default size
        self.selected_preview = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Slider for thumbnail size
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(64)
        self.size_slider.setMaximum(256)
        self.size_slider.setValue(self.current_thumbnail_size)
        self.size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.size_slider.setTickInterval(32)
        self.size_slider.valueChanged.connect(self.on_slider_value_changed)
        main_layout.addWidget(self.size_slider)

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
        # Clear existing tiles
        for i in reversed(range(self.gallery_layout.count())):
            widget_to_remove = self.gallery_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)
                widget_to_remove.deleteLater()
        self.selected_preview = None

        # Add new tiles
        col = 0
        row = 0
        for path in preview_paths:
            tile = PreviewTile(path, self.current_thumbnail_size)
            tile.checked.connect(self._on_preview_checked)
            tile.clicked.connect(self._on_preview_clicked)
            self.gallery_layout.addWidget(tile, row, col)
            col += 1
            if col >= self.get_columns_count():  # Calculate columns dynamically
                col = 0
                row += 1
        self.gallery_widget.update()

    def on_slider_value_changed(self, value: int):
        self.current_thumbnail_size = value
        self.update_tile_sizes()

    def update_tile_sizes(self):
        for i in range(self.gallery_layout.count()):
            item = self.gallery_layout.itemAt(i)
            if item and item.widget():
                tile = item.widget()
                if isinstance(tile, PreviewTile):
                    tile.update_thumbnail_size(self.current_thumbnail_size)
        self.gallery_layout.invalidate()

    def _on_preview_checked(self, file_path: str, checked: bool):
        if checked:
            # Uncheck all other previews
            for i in range(self.gallery_layout.count()):
                item = self.gallery_layout.itemAt(i)
                if item and item.widget():
                    tile = item.widget()
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
                self.preview_selected.emit(
                    ""
                )  # Emit empty string when no preview is selected

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
        # Recalculate layout when resized to adjust columns
        self.set_previews(
            [
                self.gallery_layout.itemAt(i).widget().file_path
                for i in range(self.gallery_layout.count())
                if self.gallery_layout.itemAt(i).widget()
            ]
        )

    def get_selected_preview(self):
        return self.selected_preview
