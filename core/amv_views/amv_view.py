"""
Główny widok dla zakładki AMV.
Zawiera kompletny interfejs użytkownika z panelem folderów i galerią.
"""

import logging
import os
from typing import Optional

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
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

from core.base_widgets import (
    BaseWidget,
    ControlButtonBase,
    PanelButtonBase,
    StarCheckBoxBase,
)

from .gallery_widgets import GalleryContainerWidget

logger = logging.getLogger(__name__)


class AmvView(BaseWidget):
    """View dla zakładki AMV - prezentacja UI"""

    splitter_moved = pyqtSignal(list)
    toggle_panel_requested = pyqtSignal()
    workspace_folder_clicked = pyqtSignal(str)
    gallery_viewport_resized = pyqtSignal(int)  # Nowy sygnał dla szerokości viewportu
    collapse_tree_requested = pyqtSignal()  # Sygnał do zwijania drzewa
    expand_tree_requested = pyqtSignal()  # Sygnał do rozwijania drzewa

    def __init__(self, folder_tree_view: Optional["CustomFolderTreeView"] = None):
        super().__init__()
        self._folder_tree_view = folder_tree_view
        self._load_icons()
        self._setup_ui()
        logger.debug("AmvView initialized with dependency injection - ETAP 15")

    def _load_icons(self):
        """Ładuje ikony używane w widoku."""
        self.collapse_icon = QIcon("core/resources/img/collapse_panel.png")
        self.expand_icon = QIcon("core/resources/img/expand_panel.png")

    def _setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setSizes([200, 800])
        self.splitter.splitterMoved.connect(self._on_splitter_moved)
        self._create_left_panel()
        self._create_gallery_panel()
        layout.addWidget(self.splitter)
        self.setLayout(layout)

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

        # Przyciski Zwiń i Rozwiń - szersze o 80%, bardzo niskie
        self.collapse_button = PanelButtonBase("Zwiń")
        self.collapse_button.setObjectName("collapseButton")
        self.collapse_button.setFixedHeight(16)  # Mała wysokość
        self.collapse_button.setFixedWidth(60)  # Identyczna szerokość
        self.collapse_button.clicked.connect(self._on_collapse_tree_clicked)

        self.expand_button = PanelButtonBase("Rozwiń")
        self.expand_button.setObjectName("expandButton")
        self.expand_button.setFixedHeight(16)  # Mała wysokość
        self.expand_button.setFixedWidth(60)  # Identyczna szerokość
        self.expand_button.clicked.connect(self._on_expand_tree_clicked)

        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("panelToggleButton")  # ID dla QSS
        self.toggle_button.setFixedSize(24, 24)
        self.toggle_button.setToolTip("Zamknij panel")
        self.toggle_button.setIcon(self.collapse_icon)
        self.toggle_button.setIconSize(QSize(18, 18))
        self.toggle_button.clicked.connect(lambda: self.toggle_panel_requested.emit())

        # Centrowanie przycisków Zwiń i Rozwiń
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
        # Usuwam setStyleSheet, styl jest w QSS
        self.folder_tree_view.setHeaderHidden(True)
        self.folder_tree_view.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.folder_tree_view)
        logger.debug("QTreeView created with GalleryTab styling")

    def _create_folder_buttons_panel(self, folder_layout):
        self.buttons_frame = QFrame()
        self.buttons_frame.setFixedHeight(140)
        self.buttons_layout = QGridLayout()
        self.buttons_layout.setContentsMargins(8, 8, 8, 8)
        self.buttons_layout.setSpacing(4)
        self.buttons_frame.setLayout(self.buttons_layout)
        folder_layout.addWidget(self.buttons_frame)
        self.folder_buttons = []
        logger.debug("Workspace folders panel created - ETAP 7")

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
                    # Ustawienie domyślnego koloru tła na kolor z config, jeśli jest zdefiniowany
                    default_bg_color = folder_color if folder_color else "#2D2D30"
                    button.setStyleSheet(
                        f"""
                        QPushButton {{
                            background-color: {default_bg_color}; color: #CCCCCC;
                            border: 1px solid #3F3F46; border-radius: 4px;
                            font-size: 10px; padding: 1px 4px; text-align: center;
                        }}
                        QPushButton:hover {{
                            background-color: #3F3F46; border-color: {folder_color};
                        }}
                        QPushButton:pressed {{
                            background-color: {folder_color}; color: #FFFFFF;
                        }}
                        QPushButton:disabled {{
                            background-color: #1E1E1E; color: #666666;
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
                            background-color: #1E1E1E; color: #666666;
                            border: 1px solid #3F3F46; border-radius: 4px;
                            font-size: 10px; padding: 1px 4px; text-align: center;
                        }
                    """
                    )
                row = i // 3
                col = i % 3
                self.buttons_layout.addWidget(button, row, col)
                self.folder_buttons.append(button)
            logger.debug("Workspace folder buttons updated - ETAP 7")
        except Exception as e:
            logger.error(f"Error updating workspace folder buttons: {e}")

    def _create_gallery_panel(self):
        self.gallery_panel = QFrame()
        self.gallery_panel.setFrameStyle(QFrame.Shape.NoFrame)
        gallery_vertical_layout = QVBoxLayout()
        gallery_vertical_layout.setSpacing(0)
        gallery_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self._create_gallery_content_widget()  # Dodaj PRZED _create_scroll_area!
        self._create_scroll_area()
        self._create_control_panel()
        gallery_vertical_layout.addWidget(self.scroll_area)
        # Wyśrodkowanie panelu kontrolnego
        gallery_vertical_layout.addWidget(
            self.control_panel, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.gallery_panel.setLayout(gallery_vertical_layout)
        self.splitter.addWidget(self.gallery_panel)

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

    def _create_gallery_content_widget(self):
        self.gallery_content_widget = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_content_widget)

        # DODAJ: Ustaw lepsze właściwości layoutu galerii
        self.gallery_layout.setSpacing(8)  # Stały spacing
        self.gallery_layout.setContentsMargins(8, 8, 8, 8)  # Stałe marginesy
        self.gallery_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        self.placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(self.placeholder_widget)
        self.placeholder_label = QLabel("Panel galerii\n(Oczekiwanie na wybór folderu)")
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

        # Domyślnie pokaż placeholder
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
        self.control_panel.setFixedWidth(1000)  # Stała szerokość panelu
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(8)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Wyśrodkowanie
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(12)  # Chudszy progress bar
        self.progress_bar.setMinimumWidth(200)  # Minimalna szerokość
        self.progress_bar.setMaximumWidth(400)  # Maksymalna szerokość
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)  # Upewniamy się, że jest widoczny
        self.thumbnail_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.thumbnail_size_slider.setFixedHeight(12)  # Chudszy slider
        self.thumbnail_size_slider.setMinimum(50)
        self.thumbnail_size_slider.setMaximum(256)
        self.thumbnail_size_slider.setValue(256)
        self.thumbnail_size_slider.setFixedWidth(200)  # SZTYWNA SZEROKOŚĆ
        self.selection_buttons = []
        # Styl kompaktowy jak na przyciskach Zwiń/Rozwiń
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
        self.select_all_button = ControlButtonBase("Zaznacz wszystkie")
        self.select_all_button.setObjectName("selectAllButton")
        self.select_all_button.setEnabled(False)  # Wyłączony domyślnie
        self.selection_buttons.append(self.select_all_button)

        self.move_selected_button = ControlButtonBase("Przenieś zaznaczone")
        self.move_selected_button.setObjectName("moveSelectedButton")
        self.move_selected_button.setEnabled(False)  # Wyłączony domyślnie
        self.selection_buttons.append(self.move_selected_button)

        self.delete_selected_button = ControlButtonBase("Usuń zaznaczone")
        self.delete_selected_button.setObjectName("deleteSelectedButton")
        self.delete_selected_button.setEnabled(False)  # Wyłączony domyślnie
        self.selection_buttons.append(self.delete_selected_button)

        self.deselect_all_button = ControlButtonBase("Odznacz wszystkie")
        self.deselect_all_button.setObjectName("deselectAllButton")
        self.deselect_all_button.setEnabled(False)  # Wyłączony domyślnie
        self.selection_buttons.append(self.deselect_all_button)

        # 5 gwiazdek po przycisku "Odznacz wszystkie"
        self.star_checkboxes = []
        for i in range(5):
            star_cb = StarCheckBoxBase("★")
            star_cb.setProperty("class", "star")
            self.star_checkboxes.append(star_cb)

        control_layout.addWidget(self.progress_bar, 3)  # Większy stretch factor
        for button in self.selection_buttons:
            control_layout.addWidget(button)
        for star_cb in self.star_checkboxes:
            control_layout.addWidget(star_cb)
        control_layout.addWidget(self.thumbnail_size_slider, 2)
        self.control_panel.setLayout(control_layout)

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
                "Zamknij panel" if is_panel_open else "Otwórz panel"
            )

    def _on_collapse_tree_clicked(self):
        logger.info("Żądanie zwinięcia drzewa folderów")
        self.collapse_tree_requested.emit()

    def _on_expand_tree_clicked(self):
        logger.info("Żądanie rozwinięcia drzewa folderów")
        self.expand_tree_requested.emit()

    def remove_asset_tiles(self, asset_ids_to_remove: list):
        """Usuwa kafelki assetów z widoku galerii na podstawie ich ID."""
        logger.debug(f"Attempting to remove asset tiles: {asset_ids_to_remove}")
        widgets_to_remove = []
        for i in range(self.gallery_layout.count()):
            widget = self.gallery_layout.itemAt(i).widget()
            if hasattr(widget, "asset_id") and widget.asset_id in asset_ids_to_remove:
                widgets_to_remove.append(widget)

        for widget in widgets_to_remove:
            self.gallery_layout.removeWidget(widget)
            widget.deleteLater()
            logger.debug(f"Removed asset tile: {widget.asset_id}")

        # Po usunięciu kafelków, zaktualizuj widok, aby odświeżyć układ
        self.gallery_layout.update()
        self.gallery_container_widget.update()
        self.gallery_container_widget.repaint()
        logger.info(f"Successfully removed {len(widgets_to_remove)} asset tiles.")
