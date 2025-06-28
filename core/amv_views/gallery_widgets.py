"""
Widoki galerii dla zakładki AMV.
Zawiera komponenty UI odpowiedzialne za wyświetlanie galerii assetów.
"""

import logging
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtWidgets import QWidget, QStyledItemDelegate

logger = logging.getLogger(__name__)


class GalleryContainerWidget(QWidget):
    """
    Kontener galerii z siatką kafelków assetów.
    Emituje sygnał resized gdy zmienia się rozmiar.
    """
    resized = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit(self.width())
        logger.debug(f"GalleryContainerWidget resized to: {self.width()}px")


class DropHighlightDelegate(QStyledItemDelegate):
    """
    Delegat do podświetlania elementów podczas operacji drag & drop.
    Rysuje niebieskie tło z żółtą ramką dla elementów będących celem drop.
    """
    
    def paint(self, painter, option, index):
        is_drop_target = index.data(Qt.ItemDataRole.UserRole + 1)
        if is_drop_target and painter:
            painter.save()
            rect = option.rect
            painter.setBrush(QBrush(QColor("#007ACC")))
            painter.setPen(QPen(QColor("#FFD700"), 2))
            painter.drawRect(rect.adjusted(1, 1, -2, -2))
            painter.restore()
            # Rysuj tekst normalnie - niebieskie tło i tak będzie widoczne
            super().paint(painter, option, index)
        else:
            super().paint(painter, option, index) 