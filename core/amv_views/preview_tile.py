import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class PreviewTile(QWidget):
    checked = pyqtSignal(str, bool)
    clicked = pyqtSignal(str)

    def __init__(self, file_path: str, thumbnail_size: int = 128):
        super().__init__()
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.thumbnail_size = thumbnail_size
        self.init_ui()
        self.load_thumbnail()

    def init_ui(self):
        self.setContentsMargins(5, 5, 5, 5)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Thumbnail container
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(self.thumbnail_size, self.thumbnail_size)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.thumbnail_label.mousePressEvent = self._on_thumbnail_clicked
        main_layout.addWidget(self.thumbnail_label)

        # Filename label
        self.filename_label = QLabel(self.file_name)
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.filename_label.setWordWrap(True)
        self.filename_label.setFixedWidth(
            self.thumbnail_size
        )  # Ogranicz szerokość do rozmiaru miniatury
        self.filename_label.setMaximumHeight(40)  # Maksymalna wysokość dla nazwy pliku
        self.filename_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.filename_label.mousePressEvent = self._on_filename_clicked
        main_layout.addWidget(self.filename_label)

        # Checkbox
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addStretch()
        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self._on_checkbox_state_changed)
        checkbox_layout.addWidget(self.checkbox)
        checkbox_layout.addStretch()
        main_layout.addLayout(checkbox_layout)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedWidth(self.thumbnail_size + 10)  # 5px padding on each side
        self.setFixedHeight(
            self.thumbnail_size + 70
        )  # Zwiększona wysokość dla nazwy pliku + checkbox

    def load_thumbnail(self):
        if not os.path.exists(self.file_path):
            print(f"PreviewTile: File does not exist: {self.file_path}")
            self._create_placeholder_thumbnail()
            return

        # Ładuj bezpośrednio z dysku - BEZ CACHOWANIA!
        pixmap = QPixmap(self.file_path)
        if not pixmap.isNull():
            # Bezpośrednie skalowanie i ustawienie
            scaled_pixmap = pixmap.scaled(
                self.thumbnail_size,
                self.thumbnail_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.thumbnail_label.setPixmap(scaled_pixmap)
        else:
            print(f"PreviewTile: Failed to load pixmap for: {self.file_path}")
            self._create_placeholder_thumbnail()

    def _create_placeholder_thumbnail(self):
        pixmap = QPixmap(self.thumbnail_size, self.thumbnail_size)
        pixmap.fill(QColor("#2A2D2E"))
        painter = QPainter(pixmap)
        painter.setPen(QColor("#CCCCCC"))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "NO PREVIEW")
        painter.end()
        self.thumbnail_label.setPixmap(pixmap)

    def _on_thumbnail_clicked(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.file_path)

    def _on_filename_clicked(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.file_path)

    def _on_checkbox_state_changed(self, state):
        self.checked.emit(self.file_path, state == Qt.CheckState.Checked.value)

    def is_checked(self):
        return self.checkbox.isChecked()

    def set_checked(self, checked):
        self.checkbox.setChecked(checked)

    def update_thumbnail_size(self, new_size: int):
        self.thumbnail_size = new_size
        self.setFixedWidth(self.thumbnail_size + 10)
        self.setFixedHeight(self.thumbnail_size + 70)
        self.thumbnail_label.setFixedSize(self.thumbnail_size, self.thumbnail_size)
        self.filename_label.setFixedWidth(self.thumbnail_size)
        # Przeładuj bezpośrednio z dysku - BEZ CACHOWANIA!
        self.load_thumbnail()
        self.updateGeometry()
