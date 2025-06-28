import os
import sys
import logging

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QVBoxLayout,
)

logger = logging.getLogger(__name__)


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
            logger.error(f"Błąd ładowania obrazu: {e}")

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
    # Przykład użycia
    # window = PreviewWindow("path/to/your/image.jpg")
    # sys.exit(app.exec())
