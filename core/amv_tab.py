import logging
import os
import sys
import time

from PyQt6.QtCore import (
    QMimeData,
    QObject,
    QPoint,
    QSize,
    Qt,
    QThread,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import QBrush  # Dodaj QBrush
from PyQt6.QtGui import QPen  # Dodaj QPen
from PyQt6.QtGui import (
    QColor,
    QDrag,
    QFont,
    QIcon,
    QPainter,
    QPixmap,
    QStandardItem,
    QStandardItemModel,
)
from PyQt6.QtWidgets import QStyledItemDelegate  # Dodaj QStyledItemDelegate
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSplitter,
    QStackedLayout,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from core.amv_controllers.amv_controller import AmvController
from core.amv_models.amv_model import AmvModel
from core.amv_models.asset_grid_model import (
    AssetGridModel,
    AssetScannerModelMV,
    FolderSystemModel,
    FolderTreeModel,
    WorkspaceFoldersModel,
)
from core.amv_models.asset_tile_model import AssetTileModel
from core.amv_models.config_manager_model import ConfigManagerMV
from core.amv_models.control_panel_model import ControlPanelModel
from core.amv_models.drag_drop_model import DragDropModel
from core.amv_models.file_operations_model import FileOperationsModel
from core.amv_models.selection_model import SelectionModel
from core.amv_views.amv_view import AmvView
from core.amv_views.asset_tile_view import AssetTileView
from core.amv_views.folder_tree_view import CustomFolderTreeView
from core.amv_views.gallery_widgets import DropHighlightDelegate, GalleryContainerWidget
from core.json_utils import load_from_file
from core.rules import FolderClickRules
from core.scanner import find_and_create_assets, load_existing_assets

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Wymuś poziom DEBUG dla tego loggera


# ==============================================================================
# MODEL LAYER - Logika biznesowa
# ==============================================================================


# ==============================================================================
# VIEW LAYER - Prezentacja
# ==============================================================================


# ==============================================================================
# GŁÓWNA KLASA ZAKŁADKI AMV
# ==============================================================================


class AmvTab(QWidget):
    """
    Główna klasa zakładki AMV
    Model/View/Controller pattern - ETAP 10 completed
    """

    def __init__(self):
        super().__init__()
        self.model = AmvModel()
        self.view = AmvView()
        self.controller = AmvController(self.model, self.view)
        self.model.initialize_state()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.setLayout(layout)
        logger.info("AmvTab initialized successfully - ETAP 14 completed")


# ==============================================================================
# TESTOWANIE I STANDALONE URUCHOMIENIE
# ==============================================================================

if __name__ == "__main__":
    # Usunięto logging.basicConfig, poziom DEBUG ustawiony globalnie dla loggera amv_tab
    app = QApplication(sys.argv)
    w = AmvTab()
    w.show()
    logger.info("=== ETAP 10 TEST START ===")
    logger.info("Aplikacja uruchomiona. Testowanie zaawansowanych kafelków assetów.")
    logger.info(
        "Proszę kliknąć na folder w drzewie, aby rozpocząć skanowanie i zobaczyć kafelki."
    )
    logger.info("=== ETAP 10 TEST COMPLETED ===")
    sys.exit(app.exec())
