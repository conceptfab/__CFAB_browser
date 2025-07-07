"""
Main view for the AMV tab.
Contains the complete user interface with folder panel and gallery.
"""

import logging
import os
from typing import Optional

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSlider,
    QSplitter,
    QStackedLayout,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from .gallery_widgets import GalleryContainerWidget

logger = logging.getLogger(__name__)


class AmvView(QWidget):
    """View for the AMV tab - UI presentation"""

    splitter_moved = pyqtSignal(list)
    toggle_panel_requested = pyqtSignal()
    workspace_folder_clicked = pyqtSignal(str)
    gallery_viewport_resized = pyqtSignal(int)  # New signal for viewport width
    collapse_tree_requested = pyqtSignal()  # Signal to collapse tree
    expand_tree_requested = pyqtSignal()  # Signal to expand tree

    def __init__(self, folder_tree_view: Optional["CustomFolderTreeView"] = None):
        super().__init__()
        self._folder_tree_view = folder_tree_view
        self._load_icons()
        self._setup_ui()
        logger.debug("AmvView initialized with dependency injection - ETAP 15")

    def _load_icons(self):
        """Loads icons used in the view."""
        self.collapse_icon = QIcon("core/resources/img/collapse_panel.png")
        self.expand_icon = QIcon("core/resources/img/open_panel.png")

    def _setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create edge button BEFORE splitter
        self._create_edge_button()

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setSizes([200, 800])
        self.splitter.splitterMoved.connect(self._on_splitter_moved)
        self._create_left_panel()
        self._create_gallery_panel()

        # Add edge button at the beginning of the layout
        layout.addWidget(self.edge_button)
        layout.addWidget(self.splitter)
        self.setLayout(layout)

        # Hide edge button by default (panel is open)
        self.edge_button.hide()

    def _create_left_panel(self):
        self.left_panel = QFrame()
        self.left_panel.setFrameStyle(QFrame.Shape.NoFrame)
        self.left_panel.setMinimumWidth(250)
        self.left_panel.setMaximumWidth(350)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._create_left_panel_header(layout)
        self._create_folder_tree_view(layout)
        self._create_folder_buttons_panel(layout)
        self.left_panel.setLayout(layout)
        self.splitter.addWidget(self.left_panel)

    def _create_left_panel_header(self, layout):
        header_frame = QFrame()
        header_frame.setFixedHeight(40)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 8, 12, 8)

        # Collapse and Expand buttons - 80% wider, very short
        self.collapse_button = QPushButton("Collapse")
        self.collapse_button.setObjectName("collapseButton")
        # self.collapse_button.setFixedHeight(16)  # Small height
        self.collapse_button.setFixedWidth(35)  # Identical width
        self.collapse_button.clicked.connect(self._on_collapse_tree_clicked)

        self.expand_button = QPushButton("Expand")
        self.expand_button.setObjectName("expandButton")
        # self.expand_button.setFixedHeight(16)  # Small height
        self.expand_button.setFixedWidth(35)  # Identical width
        self.expand_button.clicked.connect(self._on_expand_tree_clicked)

        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("panelToggleButton")  # ID for QSS
        self.toggle_button.setFixedSize(18, 18)
        self.toggle_button.setToolTip("Close panel")
        self.toggle_button.setIcon(self.collapse_icon)
        self.toggle_button.setIconSize(QSize(16, 16))
        self.toggle_button.setFlat(True)
        # FIX: Connect to toggle_panel_requested instead of window().close
        self.toggle_button.clicked.connect(lambda: self.toggle_panel_requested.emit())

        # Centering Collapse and Expand buttons
        header_layout.addStretch(1)
        header_layout.addWidget(self.collapse_button)
        header_layout.addWidget(self.expand_button)
        header_layout.addStretch(1)
        header_layout.addWidget(self.toggle_button)
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)

    def _create_folder_tree_view(self, layout):
        # Import tutaj aby uniknąć cyklicznych importów
        from .folder_tree_view import CustomFolderTreeView

        # Użyj wstrzykniętego widżetu lub utwórz nowy
        self.folder_tree_view = self._folder_tree_view or CustomFolderTreeView()
        self.folder_tree_view.setObjectName("cfabFolderTree")
        self.folder_tree_view.setProperty("class", "cfab-folder-tree")
        # Remove setStyleSheet, style is in QSS
        self.folder_tree_view.setHeaderHidden(True)
        self.folder_tree_view.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.folder_tree_view)
        logger.debug("QTreeView created with GalleryTab styling")

    def _create_folder_buttons_panel(self, folder_layout):
        self.buttons_frame = QFrame()
        self.buttons_frame.setFixedHeight(80)
        self.buttons_layout = QGridLayout()
        self.buttons_layout.setContentsMargins(2, 2, 2, 2)
        self.buttons_layout.setSpacing(4)
        self.buttons_frame.setLayout(self.buttons_layout)
        folder_layout.addWidget(self.buttons_frame)
        self.folder_buttons = []
        logger.debug("Workspace folders panel created - STAGE 7")

    def update_workspace_folder_buttons(self, folders: list):
        try:
            for button in self.folder_buttons:
                button.deleteLater()
            self.folder_buttons.clear()
            for i, folder_data in enumerate(folders):
                folder_path = folder_data.get("path", "")
                button_text = folder_data.get("name", f"Folder {i + 1}")
                folder_icon = folder_data.get("icon", "")
                folder_color = folder_data.get("color", "#007ACC")
                button = QPushButton(button_text, self)
                button.setFixedHeight(24)
                button.setEnabled(bool(folder_path))
                if folder_path:
                    icon_path = (
                        f"core/resources/img/{folder_icon}" if folder_icon else ""
                    )
                    if icon_path and os.path.exists(icon_path):
                        try:
                            icon = QIcon(icon_path)
                            button.setIcon(icon)
                            button.setIconSize(QSize(12, 12))
                        except Exception as e:
                            logger.debug(f"Icon loading failed for {icon_path}: {e}")
                    # Set default background color from config, if defined
                    default_bg_color = folder_color if folder_color else "#717bbc"
                    button.setStyleSheet(
                        f"""
                        QPushButton {{
                            background-color: {default_bg_color}; color: #CCCCCC;
                            border: 1px solid #3F3F46; border-radius: 4px;
                            font-size: 10px; padding: 1px 4px; text-align: center;
                        }}
                        QPushButton:hover {{
                            background-color: #717bbc; border-color: {folder_color};
                        }}
                        QPushButton:pressed {{
                            background-color: {folder_color}; color: #FFFFFF;
                        }}
                        QPushButton:disabled {{
                            background-color: transparent; color: #666666; border: none;
                            border-color: #3F3F46;
                        }}
                    """
                    )
                    button.clicked.connect(
                        lambda checked, path=folder_path: self.workspace_folder_clicked.emit(
                            path
                        )
                    )
                else:
                    button.setStyleSheet(
                        """
                        QPushButton {
                            background-color: transparent; color: #666666;
                            border: 1px solid #3F3F46; border-radius: 4px;
                            font-size: 10px; padding: 1px 4px; text-align: center;
                        }
                    """
                    )
                row = i // 3
                col = i % 3
                self.buttons_layout.addWidget(button, row, col)
                self.folder_buttons.append(button)
            logger.debug("Workspace folder buttons updated - STAGE 7")
        except Exception as e:
            logger.error(f"Error updating workspace folder buttons: {e}")

    def _create_gallery_panel(self):
        self.gallery_panel = QFrame()
        self.gallery_panel.setFrameStyle(QFrame.Shape.NoFrame)
        gallery_vertical_layout = QVBoxLayout()
        gallery_vertical_layout.setSpacing(0)
        gallery_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self._create_gallery_content_widget()
        self._create_scroll_area()
        self._create_control_panel()

        # CHANGE: Only gallery in layout - takes up entire space
        gallery_vertical_layout.addWidget(self.scroll_area)

        self.gallery_panel.setLayout(gallery_vertical_layout)

        # FIX: Control panel as child of scroll_area instead of gallery_panel
        self.control_panel.setParent(self.scroll_area)

        self.splitter.addWidget(self.gallery_panel)

        # Position control panel after creation with a longer delay
        from PyQt6.QtCore import QTimer

        QTimer.singleShot(500, self._position_control_panel)  # Increased delay

    def _position_control_panel(self):
        """Positions the control panel at the bottom of the gallery."""
        if hasattr(self, "control_panel") and hasattr(self, "gallery_panel"):
            # FIX: Use scroll_area as reference instead of gallery_panel
            if hasattr(self, "scroll_area"):
                # Get actual size of scroll area (visible gallery)
                scroll_geometry = self.scroll_area.geometry()
                scroll_width = scroll_geometry.width()
                scroll_height = scroll_geometry.height()
                scroll_x = scroll_geometry.x()
                scroll_y = scroll_geometry.y()

                panel_width = self.control_panel.width()
                panel_height = self.control_panel.height()

                # Center in scroll_area
                x = scroll_x + (scroll_width - panel_width) // 2
                y = (
                    scroll_y + scroll_height - panel_height - 10
                )  # 10px from bottom of scroll_area

                # Protection against negative coordinates
                x = max(scroll_x, x)
                y = max(scroll_y, y)

                self.control_panel.move(x, y)
                self.control_panel.raise_()

                logger.debug(
                    f"Control panel: position=({x}, {y}), scroll_area=({scroll_x}, {scroll_y}, {scroll_width}x{scroll_height}), panel={panel_width}x{panel_height}"
                )
            else:
                # Fallback to old method
                gallery_rect = self.gallery_panel.geometry()
                gallery_width = gallery_rect.width()
                gallery_height = gallery_rect.height()

                panel_width = self.control_panel.width()
                panel_height = self.control_panel.height()

                x = (gallery_width - panel_width) // 2
                y = gallery_height - panel_height - 10

                x = max(0, x)
                y = max(0, y)

                self.control_panel.move(x, y)
                self.control_panel.raise_()

    def _create_edge_button(self):
        """Creates a button attached to the left edge for opening the panel."""
        self.edge_button = QPushButton()
        self.edge_button.setObjectName("edgePanelButton")
        self.edge_button.setFixedSize(18, 18)  # Same size as close button
        self.edge_button.setToolTip("Open panel")
        self.edge_button.setIcon(QIcon("core/resources/img/open_panel.png"))
        self.edge_button.setIconSize(QSize(16, 16))  # Icon smaller than button
        self.edge_button.setFlat(True)
        self.edge_button.clicked.connect(lambda: self.toggle_panel_requested.emit())

    def _create_scroll_area(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setFrameStyle(QScrollArea.Shape.NoFrame)
        self.scroll_area.setWidget(self.gallery_container_widget)

        # ADD: Handle scroll_area resize changes
        def on_scroll_area_resize():
            from PyQt6.QtCore import QTimer

            QTimer.singleShot(50, self._position_control_panel)

        # Connect events
        original_resize = self.scroll_area.resizeEvent

        def new_resize_event(event):
            original_resize(event)
            on_scroll_area_resize()

        self.scroll_area.resizeEvent = new_resize_event

    def _create_gallery_content_widget(self):
        self.gallery_content_widget = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_content_widget)

        # ADD: Set better gallery layout properties
        self.gallery_layout.setSpacing(8)  # Fixed spacing
        self.gallery_layout.setContentsMargins(8, 8, 8, 8)  # Fixed margins
        self.gallery_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        self.placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(self.placeholder_widget)
        self.placeholder_label = QLabel("Gallery Panel\n(Waiting for folder selection)")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.addWidget(self.placeholder_label)

        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.gallery_content_widget)
        self.stacked_layout.addWidget(self.placeholder_widget)

        self.gallery_container_widget = GalleryContainerWidget()
        self.gallery_container_widget.setLayout(self.stacked_layout)
        self.gallery_container_widget.resized.connect(
            self.gallery_viewport_resized.emit
        )

        # Default to show placeholder
        self.stacked_layout.setCurrentIndex(1)

    def update_gallery_placeholder(self, text: str):
        self.placeholder_label.setText(text)
        if text:
            self.stacked_layout.setCurrentIndex(1)  # Pokaż placeholder
        else:
            self.stacked_layout.setCurrentIndex(0)  # Pokaż siatkę

    def _create_control_panel(self):
        self.control_panel = QFrame()
        self.control_panel.setFixedHeight(32)
        self.control_panel.setFixedWidth(1000)  # 1000px width

        # CHANGE: Semi-transparent background so the panel is visible over the gallery
        self.control_panel.setStyleSheet(
            """
            QFrame {
                background-color: rgba(40, 41, 53, 220);
                border: 1px solid #717bbc;
                border-radius: 4px;
            }
        """
        )

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(8, 4, 8, 4)  # Internal margins
        control_layout.setSpacing(8)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        # Placeholder for icon before QLineEdit - wyrównane z polem tekstowym
        self.icon_placeholder = QWidget()
        self.icon_placeholder.setFixedSize(24, 22)  # 24px szerokość, 22px wysokość (16px + 4px padding + 2px border)
        self.icon_placeholder.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.icon_placeholder.setStyleSheet("background: transparent; border: none;")
        icon_layout = QVBoxLayout(self.icon_placeholder)
        icon_layout.setContentsMargins(0, 0, 0, 0)  # Brak marginesów dla precyzyjnego wyrównania
        icon_layout.setSpacing(0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Wyrównanie layoutu
        icon_label = QLabel()
        icon_label.setObjectName("ControlPanelIcon")  # ID dla CSS
        icon_label.setPixmap(QPixmap("core/resources/img/search.png"))  # Bez skalowania - CSS kontroluje rozmiar
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setScaledContents(True)  # Pozwala CSS kontrolować skalowanie
        icon_layout.addWidget(icon_label)
        control_layout.addWidget(self.icon_placeholder)

        self.text_input = QLineEdit()
        self.text_input.setObjectName("ControlPanelTextInput")
        self.text_input.setMinimumWidth(120)
        # Usunięto setFixedHeight(14) - CSS kontroluje wysokość (16px)
        self.text_input.setPlaceholderText("Enter text...")
        control_layout.addWidget(self.text_input, 3)
        # Add stars between QLineEdit and buttons
        self.star_checkboxes = []
        for i in range(5):
            star_cb = QCheckBox("★")
            star_cb.setObjectName(f"ControlPanelStar_{i+1}")
            star_cb.setProperty("class", "star")
            # Set identical properties as in tile
            star_cb.setFixedSize(12, 12)
            star_cb.setText("★")
            self.star_checkboxes.append(star_cb)
            control_layout.addWidget(star_cb)
        self.selection_buttons = []
        # Compact style like on Collapse/Expand buttons
        button_style = """
            QPushButton {
                background-color: #2D2D30;
                color: #CCCCCC;
                border: 1px solid #3F3F46;
                border-radius: 2px;
                font-size: 9px;
                font-weight: bold;
                padding: 0px 4px;
                margin-bottom: 5px;
                text-align: center;
                min-width: 120px;
                max-height: 14px;
            }
            QPushButton:hover {
                background-color: #3F3F46;
                border-color: #007ACC;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #007ACC;
                color: #FFFFFF;
                border-color: #005A9E;
            }
            QPushButton:disabled {
                background-color: #1E1E1E;
                color: #666666;
                border-color: #3F3F46;
            }
        """
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.setObjectName("selectAllButton")
        self.select_all_button.setEnabled(False)  # Disabled by default
        self.selection_buttons.append(self.select_all_button)

        self.move_selected_button = QPushButton("Move Selected")
        self.move_selected_button.setObjectName("moveSelectedButton")
        self.move_selected_button.setEnabled(False)  # Disabled by default
        self.selection_buttons.append(self.move_selected_button)

        self.delete_selected_button = QPushButton("Delete Selected")
        self.delete_selected_button.setObjectName("deleteSelectedButton")
        self.delete_selected_button.setEnabled(False)  # Disabled by default
        self.selection_buttons.append(self.delete_selected_button)

        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.setObjectName("deselectAllButton")
        self.deselect_all_button.setEnabled(False)  # Disabled by default
        self.selection_buttons.append(self.deselect_all_button)

        for button in self.selection_buttons:
            control_layout.addWidget(button)
        self.thumbnail_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.thumbnail_size_slider.setFixedHeight(12)  # Thinner slider
        self.thumbnail_size_slider.setMinimum(50)
        self.thumbnail_size_slider.setMaximum(256)
        self.thumbnail_size_slider.setValue(256)
        self.thumbnail_size_slider.setFixedWidth(120)  # FIXED WIDTH
        control_layout.addWidget(self.thumbnail_size_slider, 2)
        self.control_panel.setLayout(control_layout)

        # Signal will be connected in signal_connector.py - according to MVC pattern

    def _on_splitter_moved(self, pos, index):
        sizes = self.splitter.sizes()
        self.splitter_moved.emit(sizes)

    def update_splitter_sizes(self, sizes: list):
        self.splitter.setSizes(sizes)
        logger.debug(f"Splitter sizes updated to: {sizes}")

    def update_toggle_button_text(self, is_panel_open: bool):
        if hasattr(self, "toggle_button"):
            icon = self.collapse_icon if is_panel_open else self.expand_icon
            self.toggle_button.setIcon(icon)
            self.toggle_button.setToolTip(
                "Close panel" if is_panel_open else "Open panel"
            )

        # FIX: Edge button handling
        if hasattr(self, "edge_button"):
            if is_panel_open:
                self.edge_button.hide()  # Hide edge button when panel is open
            else:
                self.edge_button.show()  # Show edge button when panel is closed

    def _on_collapse_tree_clicked(self):
        logger.debug("Request to collapse folder tree")
        self.collapse_tree_requested.emit()

    def _on_expand_tree_clicked(self):
        logger.debug("Request to expand folder tree")
        self.expand_tree_requested.emit()

    def remove_asset_tiles(self, asset_ids_to_remove: list):
        """OPTYMALIZACJA: Usuwanie kafelków assetów z galerii bez przebudowy layoutu."""
        logger.debug(f"OPTYMALIZACJA: Usuwanie kafelków: {asset_ids_to_remove}")
        
        try:
            # Walidacja danych wejściowych
            if not asset_ids_to_remove:
                logger.debug("OPTYMALIZACJA: Brak ID assetów do usunięcia")
                return
            
            if not hasattr(self, 'gallery_container_widget') or not hasattr(self, 'gallery_layout'):
                logger.warning("OPTYMALIZACJA: Brak wymaganych komponentów widoku")
                return
            
            # Wyłącz aktualizacje dla lepszej wydajności
            self.gallery_container_widget.setUpdatesEnabled(False)
            
            widgets_to_remove = []
            
            # Znajdź widżety do usunięcia
            for i in range(self.gallery_layout.count()):
                item = self.gallery_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if hasattr(widget, "asset_id") and widget.asset_id in asset_ids_to_remove:
                        widgets_to_remove.append(widget)

            # Usuń widżety z layoutu
            for widget in widgets_to_remove:
                self.gallery_layout.removeWidget(widget)
                widget.hide()  # Ukryj zamiast deleteLater dla lepszej wydajności
                logger.debug(f"OPTYMALIZACJA: Usunięto kafelek: {widget.asset_id}")

            logger.debug(f"OPTYMALIZACJA: Usunięto {len(widgets_to_remove)} kafelków bez przebudowy galerii")

        except Exception as e:
            logger.error(f"Błąd podczas optymalizowanego usuwania kafelków: {e}")
        finally:
            # Ponownie włącz aktualizacje
            if hasattr(self, 'gallery_container_widget'):
                self.gallery_container_widget.setUpdatesEnabled(True)
                # Jednorazowa aktualizacja widoku
                if hasattr(self, 'gallery_layout'):
                    self.gallery_layout.update()
                self.gallery_container_widget.update()

    def showEvent(self, event):
        """Handles showing the view"""
        super().showEvent(event)
        # ADD: Position panel after showing view
        if hasattr(self, "_position_control_panel"):
            from PyQt6.QtCore import QTimer

            QTimer.singleShot(
                100, self._position_control_panel
            )  # 100ms delay after showing

    def resizeEvent(self, event):
        """Handles window resize event"""
        super().resizeEvent(event)
        # FIX: Add delay for stable positioning
        if hasattr(self, "_position_control_panel"):
            # Use QTimer.singleShot for delayed positioning
            from PyQt6.QtCore import QTimer

            QTimer.singleShot(50, self._position_control_panel)  # 50ms delay