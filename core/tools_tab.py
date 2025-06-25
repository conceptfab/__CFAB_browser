import logging

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)


class ToolsTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        logger.info("ToolsTab initialized")

    def _setup_ui(self):
        """Setup user interface for tools tab"""
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Narzędzia"))
        self.setLayout(layout)
        logger.debug("ToolsTab UI setup completed")


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = ToolsTab()
    w.show()
    sys.exit(app.exec())
