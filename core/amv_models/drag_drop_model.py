import logging

from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class DragDropModel(QObject):
    """Model for Drag and Drop operations"""

    drag_started = pyqtSignal(list)  # Lista ID assetów przeciąganych
    drop_possible = pyqtSignal(bool)  # Czy upuszczenie jest możliwe
    drop_completed = pyqtSignal(
        str, list
    )  # Ścieżka docelowa, lista ID przeniesionych assetów

    def __init__(self):
        super().__init__()
        self._dragged_asset_ids = []
        self._operation_in_progress = False  # NOWE: zabezpieczenie przed rekurencją
        logger.info("DragDropModel initialized")

    def start_drag(self, asset_ids: list):
        # ZABEZPIECZENIE: Sprawdź czy operacja już nie jest w toku
        if self._operation_in_progress:
            logger.warning("Drag operation already in progress, ignoring new start_drag")
            return
            
        self._operation_in_progress = True
        self._dragged_asset_ids = asset_ids
        try:
            self.drag_started.emit(asset_ids)
            logger.debug(f"Drag started for assets: {asset_ids}")
        except Exception as e:
            logger.error(f"Error emitting drag_started signal: {e}")
        finally:
            self._operation_in_progress = False

    def validate_drop(self, target_path: str, current_folder_path: str = None) -> bool:
        """Validates whether dropping is possible in the given folder."""
        logger.debug(
            f"validate_drop called with target_path: '{target_path}', current_folder_path: '{current_folder_path}'"
        )

        # Normalizuj ścieżki do porównania
        def norm(path):
            if not path:
                return ""
            return path.strip().rstrip(r"/\\").lower()

        norm_target = norm(target_path)
        norm_current = norm(current_folder_path)
        logger.debug(
            f"Porównanie ścieżek: norm_target='{norm_target}', norm_current='{norm_current}'"
        )
        if norm_current and norm_target == norm_current:
            self.drop_possible.emit(False)
            logger.debug(
                f"Drop not possible: {target_path} is the same as current folder."
            )
            return False
        # Przykład: Nie zezwalaj na upuszczanie do folderów tekstur
        if any(
            folder_name in norm_target for folder_name in ["tex", "textures", "maps"]
        ):
            self.drop_possible.emit(False)
            logger.debug(f"Drop not possible: {target_path} is a texture folder.")
            return False
        self.drop_possible.emit(True)
        logger.debug(f"Drop possible: {target_path}")
        return True

    def complete_drop(self, target_path: str, asset_ids: list = None):
        """Completes the drop operation and emits a signal."""
        try:
            if asset_ids is None:
                asset_ids = self._dragged_asset_ids
                
            # ZABEZPIECZENIE: Sprawdź czy asset_ids są prawidłowe
            if not asset_ids:
                logger.warning("No asset IDs to complete drop operation")
                return
                
            # ZABEZPIECZENIE: Sprawdź czy target_path jest prawidłowy
            if not target_path or not target_path.strip():
                logger.error("Invalid target_path for complete_drop")
                return
                
            self.drop_completed.emit(target_path, asset_ids)
            self._dragged_asset_ids = []  # Wyczyść po zakończeniu operacji
            logger.debug(f"Drop completed to {target_path} for assets: {asset_ids}")
            
        except Exception as e:
            logger.error(f"Error in complete_drop: {e}")
            # W przypadku błędu, wyczyść stan
            self._dragged_asset_ids = []

    def get_dragged_asset_ids(self) -> list:
        return self._dragged_asset_ids
