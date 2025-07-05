"""
Base classes for styling based on inheritance.
Contains common styles and functionality for all widgets in the application.
"""

from PyQt6.QtWidgets import QCheckBox, QFrame, QLabel, QPushButton, QWidget

# --- Obramowania i promienie --- #
BORDER_DEFAULT = "1px solid #3F3F46"
BORDER_RADIUS_DEFAULT = "6px"
BORDER_RADIUS_SMALL = "2px"

# --- Czcionki --- #
FONT_SIZE_DEFAULT = "10px"
FONT_SIZE_SMALL = "9px"
FONT_WEIGHT_BOLD = "bold"


class BaseFrame(QFrame):
    """Base class for all frames with basic styling"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_styles()

    def _apply_base_styles(self):
        """Applies basic styles for frames"""
        pass


class BaseLabel(QLabel):
    """Base class for all labels with basic styling"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_styles()

    def _apply_base_styles(self):
        """Applies basic styles for labels"""
        pass


class BaseButton(QPushButton):
    """Base class for all buttons with basic styling"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_styles()

    def _apply_base_styles(self):
        """Applies basic styles for buttons"""
        pass


class BaseCheckBox(QCheckBox):
    """Base class for all checkboxes with basic styling"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_styles()

    def _apply_base_styles(self):
        """Applies basic styles for checkboxes"""
        pass


class BaseWidget(QWidget):
    """Base class for all widgets with basic styling"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_styles()

    def _apply_base_styles(self):
        """Applies basic styles for widgets"""
        pass


class TileBase(BaseFrame):
    """Base class for all tiles"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tile_styles()

    def _apply_tile_styles(self):
        """Applies tile-specific styles"""
        pass


class StarCheckBoxBase(BaseCheckBox):
    """Base class for star checkboxes"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_star_styles()

    def _apply_star_styles(self):
        """Applies star checkbox-specific styles"""
        pass


class ControlButtonBase(BaseButton):
    """Base class for control buttons"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_control_button_styles()

    def _apply_control_button_styles(self):
        """Applies control button-specific styles"""
        pass


class PanelButtonBase(BaseButton):
    """Base class for panel buttons"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_panel_button_styles()

    def _apply_panel_button_styles(self):
        """Applies panel button-specific styles"""
        pass
