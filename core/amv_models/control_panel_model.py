import logging
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class ControlPanelModel(QObject):
    """Model dla panelu kontrolnego - stan kontrolek"""

    progress_changed = pyqtSignal(int)
    thumbnail_size_changed = pyqtSignal(int)
    selection_state_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._progress = 0
        self._thumbnail_size = 256
        self._has_selection = False

    def set_progress(self, value: int):
        value = max(0, min(100, value))
        if self._progress != value:
            self._progress = value
            self.progress_changed.emit(value)

    def get_progress(self):
        return self._progress

    def set_thumbnail_size(self, value: int):
        if self._thumbnail_size != value:
            self._thumbnail_size = value
            self.thumbnail_size_changed.emit(value)

    def get_thumbnail_size(self):
        return self._thumbnail_size

    def set_has_selection(self, has: bool):
        logger.debug(f"ControlPanelModel: set_has_selection called with: {has}")
        if self._has_selection != has:
            self._has_selection = has
            self.selection_state_changed.emit(has)
            logger.debug(f"ControlPanelModel: selection_state_changed emitted: {has}")

    def has_selection(self):
        return self._has_selection 