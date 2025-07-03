import logging
import os
import sys
from typing import Optional

from PyQt6.QtCore import QObject, QSize, Qt, QThreadPool, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout

logger = logging.getLogger(__name__)


class ImageLoader(QObject):
    """Worker class for asynchronous image loading."""

    image_loaded = pyqtSignal(QPixmap, str)  # pixmap, error_message
    image_scaled = pyqtSignal(QPixmap)

    def __init__(self, image_path: str, max_size: QSize):
        super().__init__()
        self.image_path = image_path
        self.max_size = max_size

    def load_image(self) -> None:
        """Load and pre-scale image asynchronously."""
        try:
            absolute_image_path = os.path.abspath(self.image_path)
            pixmap = QPixmap(absolute_image_path)

            if pixmap.isNull():
                error_msg = f"Nie można załadować obrazu: " f"{self.image_path}"
                self.image_loaded.emit(QPixmap(), error_msg)
                return

            # Pre-scale to maximum size to avoid expensive scaling in resizeEvent
            scaled_pixmap = self._pre_scale_pixmap(pixmap)
            self.image_loaded.emit(scaled_pixmap, "")

        except Exception as e:
            logger.error(f"Błąd ładowania obrazu: {e}")
            self.image_loaded.emit(QPixmap(), f"Błąd ładowania obrazu: {e}")

    def scale_image(self, pixmap: QPixmap, target_size: QSize) -> None:
        """Scale image to target size asynchronously."""
        try:
            scaled_pixmap = pixmap.scaled(
                target_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_scaled.emit(scaled_pixmap)
        except Exception as e:
            logger.error(f"Błąd skalowania obrazu: {e}")
            self.image_scaled.emit(QPixmap())

    def _pre_scale_pixmap(self, pixmap: QPixmap) -> QPixmap:
        """Pre-scale pixmap to maximum display size to optimize performance."""
        if (
            pixmap.width() <= self.max_size.width()
            and pixmap.height() <= self.max_size.height()
        ):
            return pixmap

        scale = min(
            self.max_size.width() / pixmap.width(),
            self.max_size.height() / pixmap.height(),
            1.0,
        )

        new_width = int(pixmap.width() * scale)
        new_height = int(pixmap.height() * scale)

        return pixmap.scaled(
            new_width,
            new_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )


class PreviewWindow(QDialog):
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.original_pixmap: Optional[QPixmap] = None
        self.pre_scaled_pixmap: Optional[QPixmap] = None
        self.thread_pool = QThreadPool()
        self.image_loader: Optional[ImageLoader] = None
        self.scale_timer = QTimer()
        self.scale_timer.setSingleShot(True)
        self.scale_timer.timeout.connect(self._perform_scaling)

        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the user interface."""
        self.setWindowTitle(f"Podgląd - {os.path.basename(self.image_path)}")
        self.setModal(False)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText("Ładowanie obrazu...")
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        self.load_image_and_resize()
        # USUNIĘTO AUTOMATYCZNE POKAZANIE OKNA - wywołane świadomie z controllera

    def show_window(self):
        """Pokazuje okno podglądu."""
        self.show()
        self.raise_()
        self.activateWindow()

    def load_image_and_resize(self) -> None:
        """Load image asynchronously and resize window."""
        try:
            # Calculate maximum display size
            screen = QApplication.primaryScreen().availableGeometry()
            max_width = screen.width() - 100
            max_height = screen.height() - 100
            max_size = QSize(max_width, max_height)

            # Create and start async image loader
            self.image_loader = ImageLoader(self.image_path, max_size)
            self.image_loader.image_loaded.connect(self._on_image_loaded)
            self.image_loader.image_scaled.connect(self._on_image_scaled)

            # Start loading in background thread
            self.thread_pool.start(self.image_loader.load_image)

        except Exception as e:
            self.image_label.setText(f"Błąd ładowania obrazu: {e}")
            logger.error(f"Błąd ładowania obrazu: {e}")

    def _on_image_loaded(self, pixmap: QPixmap, error_message: str) -> None:
        """Handle image loaded signal."""
        if error_message:
            self.image_label.setText(error_message)
            return

        self.pre_scaled_pixmap = pixmap

        # Calculate window size based on pre-scaled image
        screen = QApplication.primaryScreen().availableGeometry()
        max_width = screen.width() - 100
        max_height = screen.height() - 100

        scale = min(
            max_width / pixmap.width(),
            max_height / pixmap.height(),
            1.0,
        )

        new_width = int(pixmap.width() * scale)
        new_height = int(pixmap.height() * scale)

        self.resize(new_width, new_height)
        self.move(
            (screen.width() - new_width) // 2,
            (screen.height() - new_height) // 2,
        )

        # Load initial image
        self.load_image()

    def _on_image_scaled(self, scaled_pixmap: QPixmap) -> None:
        """Handle image scaled signal."""
        if not scaled_pixmap.isNull():
            self.image_label.setPixmap(scaled_pixmap)

    def load_image(self) -> None:
        """Load and display image at current window size."""
        if self.pre_scaled_pixmap:
            # Use pre-scaled pixmap for better performance
            self.image_label.setPixmap(
                self.pre_scaled_pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    def resizeEvent(self, event) -> None:
        """Handle window resize event with debounced scaling."""
        super().resizeEvent(event)

        # Debounce resize events to avoid excessive scaling
        self.scale_timer.stop()
        self.scale_timer.start(50)  # 50ms delay

    def _perform_scaling(self) -> None:
        """Perform actual scaling after resize debounce."""
        if self.pre_scaled_pixmap and self.image_loader:
            # Scale asynchronously to avoid blocking UI
            self.image_loader.scale_image(self.pre_scaled_pixmap, self.size())

    def closeEvent(self, event) -> None:
        """Clean up resources when window is closed."""
        # Stop any pending operations
        self.scale_timer.stop()

        # Clear pixmaps to free memory
        self.original_pixmap = None
        self.pre_scaled_pixmap = None

        # Wait for background threads to finish
        self.thread_pool.waitForDone(1000)  # Wait up to 1 second

        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    sys.exit(app.exec())
