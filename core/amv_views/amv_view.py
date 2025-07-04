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
    QCheckBox,
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

from .gallery_widgets import GalleryContainerWidget

logger = logging.getLogger(__name__)


class AmvView(QWidget):
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

        # Utwórz przycisk krawędzi PRZED splitterem
        self._create_edge_button()

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setSizes([200, 800])
        self.splitter.splitterMoved.connect(self._on_splitter_moved)
        self._create_left_panel()
        self._create_gallery_panel()

        # Dodaj przycisk krawędzi na początku layoutu
        layout.addWidget(self.edge_button)
        layout.addWidget(self.splitter)
        self.setLayout(layout)

        # Domyślnie ukryj przycisk krawędzi (panel jest otwarty)
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

        # Przyciski Zwiń i Rozwiń - szersze o 80%, bardzo niskie
        self.collapse_button = QPushButton("Zwiń")
        self.collapse_button.setObjectName("collapseButton")
        # self.collapse_button.setFixedHeight(16)  # Mała wysokość
        self.collapse_button.setFixedWidth(35)  # Identyczna szerokość
        self.collapse_button.clicked.connect(self._on_collapse_tree_clicked)

        self.expand_button = QPushButton("Rozwiń")
        self.expand_button.setObjectName("expandButton")
        # self.expand_button.setFixedHeight(16)  # Mała wysokość
        self.expand_button.setFixedWidth(35)  # Identyczna szerokość
        self.expand_button.clicked.connect(self._on_expand_tree_clicked)

        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("panelToggleButton")  # ID dla QSS
        self.toggle_button.setFixedSize(18, 18)
        self.toggle_button.setToolTip("Zamknij panel")
        self.toggle_button.setIcon(self.collapse_icon)
        self.toggle_button.setIconSize(QSize(16, 16))
        self.toggle_button.setFlat(True)
        # POPRAWKA: Podłącz do toggle_panel_requested zamiast window().close
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
        self.buttons_frame.setFixedHeight(80)
        self.buttons_layout = QGridLayout()
        self.buttons_layout.setContentsMargins(2, 2, 2, 2)
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
            logger.debug("Workspace folder buttons updated - ETAP 7")
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

        # ZMIANA: Tylko galeria w layout - zajmuje całą przestrzeń
        gallery_vertical_layout.addWidget(self.scroll_area)

        self.gallery_panel.setLayout(gallery_vertical_layout)

        # POPRAWKA: Panel kontrolny jako dziecko scroll_area zamiast gallery_panel
        self.control_panel.setParent(self.scroll_area)

        self.splitter.addWidget(self.gallery_panel)

        # Pozycjonuj panel kontrolny po utworzeniu z większym opóźnieniem
        from PyQt6.QtCore import QTimer

        QTimer.singleShot(500, self._position_control_panel)  # Zwiększone opóźnienie

    def _position_control_panel(self):
        """Pozycjonuje panel kontrolny na dole galerii"""
        if hasattr(self, "control_panel") and hasattr(self, "gallery_panel"):
            # POPRAWKA: Użyj scroll_area jako referencji zamiast gallery_panel
            if hasattr(self, "scroll_area"):
                # Pobierz rzeczywisty rozmiar obszaru przewijania (widocznej galerii)
                scroll_geometry = self.scroll_area.geometry()
                scroll_width = scroll_geometry.width()
                scroll_height = scroll_geometry.height()
                scroll_x = scroll_geometry.x()
                scroll_y = scroll_geometry.y()

                panel_width = self.control_panel.width()
                panel_height = self.control_panel.height()

                # Wyśrodkuj w obszarze scroll_area
                x = scroll_x + (scroll_width - panel_width) // 2
                y = (
                    scroll_y + scroll_height - panel_height - 10
                )  # 10px od dołu scroll_area

                # Zabezpieczenie przed ujemnymi współrzędnymi
                x = max(scroll_x, x)
                y = max(scroll_y, y)

                self.control_panel.move(x, y)
                self.control_panel.raise_()

                logger.debug(
                    f"Panel kontrolny: pozycja=({x}, {y}), scroll_area=({scroll_x}, {scroll_y}, {scroll_width}x{scroll_height}), panel={panel_width}x{panel_height}"
                )
            else:
                # Fallback do starej metody
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
        """Tworzy przycisk przyklejony do lewej krawędzi do otwierania panelu"""
        self.edge_button = QPushButton()
        self.edge_button.setObjectName("edgePanelButton")
        self.edge_button.setFixedSize(18, 18)  # Taki sam rozmiar jak przycisk zamykania
        self.edge_button.setToolTip("Otwórz panel")
        self.edge_button.setIcon(QIcon("core/resources/img/open_panel.png"))
        self.edge_button.setIconSize(QSize(16, 16))  # Ikona mniejsza niż przycisk
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

        # DODAJ: Obsługa zmian rozmiaru scroll_area
        def on_scroll_area_resize():
            from PyQt6.QtCore import QTimer

            QTimer.singleShot(50, self._position_control_panel)

        # Podpnij zdarzenia
        original_resize = self.scroll_area.resizeEvent

        def new_resize_event(event):
            original_resize(event)
            on_scroll_area_resize()

        self.scroll_area.resizeEvent = new_resize_event

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
        self.control_panel.setFixedWidth(1000)  # Szerokość 1000px

        # ZMIANA: Półprzezroczyste tło, żeby panel był widoczny nad galerią
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
        control_layout.setContentsMargins(8, 4, 8, 4)  # Marginesy wewnętrzne
        control_layout.setSpacing(8)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(12)  # Chudszy progress bar
        self.progress_bar.setMinimumWidth(100)  # Minimalna szerokość
        self.progress_bar.setMaximumWidth(120)  # Maksymalna szerokość
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)  # Upewniamy się, że jest widoczny
        self.thumbnail_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.thumbnail_size_slider.setFixedHeight(12)  # Chudszy slider
        self.thumbnail_size_slider.setMinimum(50)
        self.thumbnail_size_slider.setMaximum(256)
        self.thumbnail_size_slider.setValue(256)
        self.thumbnail_size_slider.setFixedWidth(120)  # SZTYWNA SZEROKOŚĆ
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
        self.select_all_button = QPushButton("Zaznacz wszystkie")
        self.select_all_button.setObjectName("selectAllButton")
        self.select_all_button.setEnabled(False)  # Wyłączony domyślnie
        self.selection_buttons.append(self.select_all_button)

        self.move_selected_button = QPushButton("Przenieś zaznaczone")
        self.move_selected_button.setObjectName("moveSelectedButton")
        self.move_selected_button.setEnabled(False)  # Wyłączony domyślnie
        self.selection_buttons.append(self.move_selected_button)

        self.delete_selected_button = QPushButton("Usuń zaznaczone")
        self.delete_selected_button.setObjectName("deleteSelectedButton")
        self.delete_selected_button.setEnabled(False)  # Wyłączony domyślnie
        self.selection_buttons.append(self.delete_selected_button)

        self.deselect_all_button = QPushButton("Odznacz wszystkie")
        self.deselect_all_button.setObjectName("deselectAllButton")
        self.deselect_all_button.setEnabled(False)  # Wyłączony domyślnie
        self.selection_buttons.append(self.deselect_all_button)

        # 5 gwiazdek po przycisku "Odznacz wszystkie"
        self.star_checkboxes = []
        for i in range(5):
            star_cb = QCheckBox("★")
            star_cb.setObjectName(f"ControlPanelStar_{i+1}")
            star_cb.setProperty("class", "star")
            # Ustaw identyczne właściwości jak w kafelku
            star_cb.setFixedSize(12, 12)
            star_cb.setText("★")
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

        # POPRAWKA: Obsługa przycisku krawędzi
        if hasattr(self, "edge_button"):
            if is_panel_open:
                self.edge_button.hide()  # Ukryj przycisk krawędzi gdy panel jest otwarty
            else:
                self.edge_button.show()  # Pokaż przycisk krawędzi gdy panel jest zamknięty

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

    def showEvent(self, event):
        """Obsługuje pokazanie widoku"""
        super().showEvent(event)
        # DODAJ: Pozycjonuj panel po pokazaniu widoku
        if hasattr(self, "_position_control_panel"):
            from PyQt6.QtCore import QTimer

            QTimer.singleShot(
                100, self._position_control_panel
            )  # 100ms opóźnienia po pokazaniu

    def resizeEvent(self, event):
        """Obsługuje zmianę rozmiaru okna"""
        super().resizeEvent(event)
        # POPRAWKA: Dodaj opóźnienie dla stabilnego pozycjonowania
        if hasattr(self, "_position_control_panel"):
            # Użyj QTimer.singleShot dla opóźnionego pozycjonowania
            from PyQt6.QtCore import QTimer

            QTimer.singleShot(50, self._position_control_panel)  # 50ms opóźnienia
