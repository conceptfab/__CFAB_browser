import logging
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class DragDropModel(QObject):
    """Model dla operacji Drag and Drop"""

    drag_started = pyqtSignal(list)  # Lista ID assetów przeciąganych
    drop_possible = pyqtSignal(bool)  # Czy upuszczenie jest możliwe
    drop_completed = pyqtSignal(
        str, list
    )  # Ścieżka docelowa, lista ID przeniesionych assetów

    def __init__(self):
        super().__init__()
        self._dragged_asset_ids = []
        logger.info("DragDropModel initialized")

    def start_drag(self, asset_ids: list):
        self._dragged_asset_ids = asset_ids
        self.drag_started.emit(asset_ids)
        logger.debug(f"Drag started for assets: {asset_ids}")

    def validate_drop(self, target_path: str) -> bool:
        """Waliduje, czy upuszczenie jest możliwe w danym folderze."""
        # Przykład: Nie zezwalaj na upuszczanie do folderów tekstur
        if any(
            folder_name in target_path.lower()
            for folder_name in ["tex", "textures", "maps"]
        ):
            self.drop_possible.emit(False)
            logger.debug(f"Drop not possible: {target_path} is a texture folder.")
            return False
        # Dodaj inne warunki walidacji, np. czy to jest folder, czy użytkownik ma uprawnienia itp.
        self.drop_possible.emit(True)
        logger.debug(f"Drop possible: {target_path}")
        return True

    def complete_drop(self, target_path: str, asset_ids: list = None):
        """Kończy operację drop i emituje sygnał."""
        if asset_ids is None:
            asset_ids = self._dragged_asset_ids
        self.drop_completed.emit(target_path, asset_ids)
        self._dragged_asset_ids = []  # Wyczyść po zakończeniu operacji
        logger.debug(
            f"Drop completed to {target_path} for assets: {asset_ids}"
        )

    def get_dragged_asset_ids(self) -> list:
        return self._dragged_asset_ids 