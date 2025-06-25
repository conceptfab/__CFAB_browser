import logging
import os
import sys
import unittest

from PyQt6.QtWidgets import QApplication, QWidget

# Add core directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../core")))

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import zakładki z osobnego pliku
from tools_tab import ToolsTab


class TestToolsTab(unittest.TestCase):
    def setUp(self):
        """Setup test environment"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        self.tab = ToolsTab()
        logger.info("TestToolsTab setup completed")

    def test_tools_tab_creation(self):
        """Test czy zakładka Narzędzia zostaje poprawnie utworzona"""
        self.assertIsInstance(self.tab, QWidget)
        self.assertIsInstance(self.tab, ToolsTab)
        logger.debug("Tools tab creation test passed")

    def test_tools_tab_layout(self):
        """Test czy zakładka Narzędzia ma poprawny layout"""
        self.assertIsNotNone(self.tab.layout())
        logger.debug("Tools tab layout test passed")

    def test_tools_tab_ui_setup(self):
        """Test czy UI zostało poprawnie skonfigurowane"""
        self.assertTrue(hasattr(self.tab, "_setup_ui"))
        logger.debug("Tools tab UI setup test passed")

    def tearDown(self):
        """Cleanup after test"""
        self.tab.close()
        logger.info("TestToolsTab cleanup completed")


if __name__ == "__main__":
    unittest.main()
