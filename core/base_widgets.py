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
        self.setStyleSheet(
            f"""
            BaseFrame {{
                background-color: #252526;
                border: {BORDER_DEFAULT};
                border-radius: {BORDER_RADIUS_DEFAULT};
            }}
        """
        )


class BaseLabel(QLabel):
    """Bazowa klasa dla wszystkich etykiet z podstawowym stylowaniem"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_styles()

    def _apply_base_styles(self):
        """Aplikuje podstawowe style dla etykiet"""
        self.setStyleSheet(
            f"""
            BaseLabel {{
                color: #CCCCCC;
                background-color: transparent;
                font-size: {FONT_SIZE_DEFAULT};
                padding: 2px;
            }}
        """
        )


class BaseButton(QPushButton):
    """Bazowa klasa dla wszystkich przycisków z podstawowym stylowaniem"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_styles()

    def _apply_base_styles(self):
        """Aplikuje podstawowe style dla przycisków"""
        self.setStyleSheet(
            f"""
            BaseButton {{
                background-color: #252526;
                color: #CCCCCC;
                border: {BORDER_DEFAULT};
                border-radius: {BORDER_RADIUS_SMALL};
                padding: 4px 12px;
                min-height: 24px;
                max-height: 24px;
            }}
            BaseButton:hover {{
                background-color: #2A2D2E;
            }}
            BaseButton:pressed {{
                background-color: #3E3E40;
            }}
        """
        )


class BaseCheckBox(QCheckBox):
    """Bazowa klasa dla wszystkich checkboxów z podstawowym stylowaniem"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_styles()

    def _apply_base_styles(self):
        """Aplikuje podstawowe style dla checkboxów"""
        self.setStyleSheet(
            f"""
            BaseCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid #555555;
                border-radius: {BORDER_RADIUS_SMALL};
                background-color: #2A2D2E;
            }}
            BaseCheckBox::indicator:checked {{
                background-color: #007ACC;
                border-color: #007ACC;
            }}
            BaseCheckBox::indicator:hover {{
                border-color: #007ACC;
            }}
        """
        )


class BaseWidget(QWidget):
    """Bazowa klasa dla wszystkich widgetów z podstawowym stylowaniem"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_styles()

    def _apply_base_styles(self):
        """Aplikuje podstawowe style dla widgetów"""
        self.setStyleSheet(
            """
            BaseWidget {
                background-color: #1E1E1E;
                color: #CCCCCC;
            }
        """
        )


class TileBase(BaseFrame):
    """Bazowa klasa dla wszystkich kafelków (tiles)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tile_styles()

    def _apply_tile_styles(self):
        """Aplikuje style specyficzne dla kafelków"""
        self.setStyleSheet(
            f"""
            TileBase {{
                background-color: #252526;
                border: {BORDER_DEFAULT};
                border-radius: {BORDER_RADIUS_DEFAULT};
            }}
            TileBase:hover {{
                border-color: #007ACC;
                background-color: #2D2D30;
            }}
        """
        )


class StarCheckBoxBase(BaseCheckBox):
    """Bazowa klasa dla checkboxów gwiazdek"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_star_styles()

    def _apply_star_styles(self):
        """Aplikuje style specyficzne dla checkboxów gwiazdek"""
        self.setStyleSheet(
            f"""
            StarCheckBoxBase {{
                spacing: 0px;
                color: #888888;
                font-size: 14px;
            }}
            StarCheckBoxBase::indicator {{
                width: 0px;
                height: 0px;
                border: none;
            }}
            StarCheckBoxBase:checked {{
                color: #FFD700;
                font-weight: {FONT_WEIGHT_BOLD};
            }}
            StarCheckBoxBase:hover {{
                color: #FFA500;
            }}
        """
        )


class ControlButtonBase(BaseButton):
    """Bazowa klasa dla przycisków kontrolnych"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_control_button_styles()

    def _apply_control_button_styles(self):
        """Aplikuje style specyficzne dla przycisków kontrolnych"""
        self.setStyleSheet(
            f"""
            ControlButtonBase {{
                background-color: #3C3C3C;
                color: #CCCCCC;
                border: {BORDER_DEFAULT};
                border-radius: {BORDER_RADIUS_SMALL};
                padding: 2px 8px;
                min-height: 20px;
                max-height: 20px;
                font-size: {FONT_SIZE_SMALL};
            }}
            ControlButtonBase:hover {{
                background-color: #4A4A4A;
            }}
            ControlButtonBase:pressed {{
                background-color: #2A2A2A;
            }}
            ControlButtonBase:disabled {{
                background-color: #2A2A2A;
                color: #666666;
            }}
        """
        )


class PanelButtonBase(BaseButton):
    """Bazowa klasa dla przycisków panelowych"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_panel_button_styles()

    def _apply_panel_button_styles(self):
        """Aplikuje style specyficzne dla przycisków panelowych"""
        self.setStyleSheet(
            f"""
            PanelButtonBase {{
                background-color: #252526;
                color: #CCCCCC;
                border: {BORDER_DEFAULT};
                border-radius: {BORDER_RADIUS_SMALL};
                padding: 6px 16px;
                min-height: 28px;
                max-height: 28px;
                font-size: {FONT_SIZE_DEFAULT};
                font-weight: {FONT_WEIGHT_BOLD};
            }}
            PanelButtonBase:hover {{
                background-color: #2A2D2E;
                border-color: #007ACC;
            }}
            PanelButtonBase:pressed {{
                background-color: #3E3E40;
            }}
        """
        )
