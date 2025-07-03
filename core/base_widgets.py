"""
Klasy bazowe dla stylowania opartego na dziedziczeniu.
Zawiera wspólne style i funkcjonalność dla wszystkich widgetów w aplikacji.
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
    """Bazowa klasa dla wszystkich ramek z podstawowym stylowaniem"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_styles()

    def _apply_base_styles(self):
        """Aplikuje podstawowe style dla ramek"""
        pass


class BaseLabel(QLabel):
    """Bazowa klasa dla wszystkich etykiet z podstawowym stylowaniem"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_styles()

    def _apply_base_styles(self):
        """Aplikuje podstawowe style dla etykiet"""
        pass


class BaseButton(QPushButton):
    """Bazowa klasa dla wszystkich przycisków z podstawowym stylowaniem"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_styles()

    def _apply_base_styles(self):
        """Aplikuje podstawowe style dla przycisków"""
        pass


class BaseCheckBox(QCheckBox):
    """Bazowa klasa dla wszystkich checkboxów z podstawowym stylowaniem"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_styles()

    def _apply_base_styles(self):
        """Aplikuje podstawowe style dla checkboxów"""
        pass


class BaseWidget(QWidget):
    """Bazowa klasa dla wszystkich widgetów z podstawowym stylowaniem"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_styles()

    def _apply_base_styles(self):
        """Aplikuje podstawowe style dla widgetów"""
        pass


class TileBase(BaseFrame):
    """Bazowa klasa dla wszystkich kafelków (tiles)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tile_styles()

    def _apply_tile_styles(self):
        """Aplikuje style specyficzne dla kafelków"""
        pass


class StarCheckBoxBase(BaseCheckBox):
    """Bazowa klasa dla checkboxów gwiazdek"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_star_styles()

    def _apply_star_styles(self):
        """Aplikuje style specyficzne dla checkboxów gwiazdek"""
        pass


class ControlButtonBase(BaseButton):
    """Bazowa klasa dla przycisków kontrolnych"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_control_button_styles()

    def _apply_control_button_styles(self):
        """Aplikuje style specyficzne dla przycisków kontrolnych"""
        pass


class PanelButtonBase(BaseButton):
    """Bazowa klasa dla przycisków panelowych"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_panel_button_styles()

    def _apply_panel_button_styles(self):
        """Aplikuje style specyficzne dla przycisków panelowych"""
        pass
