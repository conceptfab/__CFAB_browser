import logging
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class SelectionModel(QObject):
    """Model for managing asset selection"""

    selection_changed = pyqtSignal(list)  # Emits a list of selected asset IDs

    def __init__(self):
        super().__init__()
        self._selected_asset_ids = (
            set()
        )  # We use a set for fast uniqueness checking
        logger.info("SelectionModel initialized")

    def add_selection(self, asset_id: str):
        if asset_id not in self._selected_asset_ids:
            self._selected_asset_ids.add(asset_id)
            self._emit_selection_changed()

    def remove_selection(self, asset_id: str):
        if asset_id in self._selected_asset_ids:
            self._selected_asset_ids.remove(asset_id)
            self._emit_selection_changed()

    def clear_selection(self):
        if self._selected_asset_ids:
            self._selected_asset_ids.clear()
            self._emit_selection_changed()

    def get_selected_asset_ids(self) -> list:
        return list(self._selected_asset_ids)

    def is_selected(self, asset_id: str) -> bool:
        return asset_id in self._selected_asset_ids

    def _emit_selection_changed(self):
        self.selection_changed.emit(list(self._selected_asset_ids))
        logger.debug(
            f"SelectionModel: Selection changed. Total selected: {len(self._selected_asset_ids)} items. Selected IDs: {list(self._selected_asset_ids)}"
        ) 