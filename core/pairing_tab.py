import logging

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)


class PairingTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        logger.info("PairingTab initialized")

    def _setup_ui(self):
        """Setup user interface for pairing tab"""
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Parowanie"))
        self.setLayout(layout)
        logger.debug("PairingTab UI setup completed")


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = PairingTab()
    w.show()
    sys.exit(app.exec())
