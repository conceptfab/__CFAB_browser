import logging
import sys
from typing import Optional

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget

from core.amv_controllers.amv_controller import AmvController
from core.amv_models.amv_model import AmvModel
from core.amv_views.amv_view import AmvView

logger = logging.getLogger(__name__)


# ==============================================================================
# GŁÓWNA KLASA ZAKŁADKI AMV
# ==============================================================================


class AmvTab(QWidget):
    """
    Główna klasa zakładki AMV
    Model/View/Controller pattern - ETAP 15 completed with dependency injection
    """

    def __init__(
        self,
        model: Optional[AmvModel] = None,
        view: Optional[AmvView] = None,
        controller: Optional[AmvController] = None,
    ):
        super().__init__()

        # Ustaw objectName dla stylowania QSS
        self.setObjectName("amvTab")

        # Wstrzykiwanie zależności z fallback do domyślnych instancji
        self.model = model or AmvModel()
        self.view = view or AmvView()
        self.controller = controller or AmvController(self.model, self.view)

        self.model.initialize_state()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.setLayout(layout)
        logger.debug("AmvTab initialized with dependency injection - ETAP 15 completed")

    def get_controller(self) -> AmvController:
        """Zwraca instancję kontrolera dla tej zakładki."""
        return self.controller


# ==============================================================================
# TESTOWANIE I STANDALONE URUCHOMIENIE
# ==============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AmvTab()
    w.show()
    sys.exit(app.exec())
