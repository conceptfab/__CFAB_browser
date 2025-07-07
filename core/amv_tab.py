import logging
import sys
from typing import Optional

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget

from core.amv_controllers.amv_controller import AmvController
from core.amv_models.amv_model import AmvModel
from core.amv_views.amv_view import AmvView

logger = logging.getLogger(__name__)


# ==============================================================================
# MAIN CLASS OF THE AMV TAB
# ==============================================================================


class AmvTab(QWidget):
    """
    Main class of the AMV tab
    Model/View/Controller pattern - STAGE 15 completed with dependency injection
    """

    def __init__(
        self,
        model: Optional[AmvModel] = None,
        view: Optional[AmvView] = None,
        controller: Optional[AmvController] = None,
        main_window=None,
    ):
        super().__init__()

        # Set objectName for QSS styling
        self.setObjectName("amvTab")

        # Dependency injection with fallback to default instances
        self.model = model or AmvModel()
        self.view = view or AmvView()
        self.controller = controller or AmvController(self.model, self.view, main_window)

        self.model.initialize_state()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.setLayout(layout)
        logger.debug("AmvTab initialized with dependency injection - ETAP 15 completed")

    def get_controller(self) -> AmvController:
        """Returns the controller instance for this tab."""
        return self.controller


# ==============================================================================
# TESTING AND STANDALONE EXECUTION
# ==============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AmvTab()
    w.show()
    sys.exit(app.exec())
