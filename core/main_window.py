import json
import logging
import sys

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar, QTabWidget

from core.gallery_tab import GalleryTab
from core.pairing_tab import PairingTab
from core.tools_tab import ToolsTab

# Logger setup
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
logger_level = config.get("logger_level", "INFO")
logging.basicConfig(level=getattr(logging, logger_level))
logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CFAB Browser")
        self.resize(800, 600)
        self._createMenuBar()
        self._createTabs()
        logger.info("MainWindow initialized")

    def _createMenuBar(self):
        menu_bar = QMenuBar(self)
        file_menu = QMenu("Plik", self)
        exit_action = QAction("Wyjście", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        menu_bar.addMenu(file_menu)
        self.setMenuBar(menu_bar)
        logger.debug("Menu bar created")

    def _createTabs(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(GalleryTab(), "Galeria")
        self.tabs.addTab(PairingTab(), "Parowanie")
        self.tabs.addTab(ToolsTab(), "Narzędzia")
        self.setCentralWidget(self.tabs)
        logger.debug("Tabs created")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
