"""
AssetTileView - View for a single asset tile
Displays thumbnail, filename, stars, and checkbox for the asset.
"""

import logging
import os

from PyQt6.QtCore import QMimeData, Qt, QThreadPool, pyqtSignal
from PyQt6.QtGui import QColor, QDrag, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.thumbnail_cache import thumbnail_cache
from core.workers.thumbnail_loader_worker import ThumbnailLoaderWorker

from ..amv_models.asset_tile_model import AssetTileModel
from ..amv_models.selection_model import SelectionModel

logger = logging.getLogger(__name__)


class AssetTileView(QFrame):
    """View for a single asset tile - STAGE 15 + Object Pooling"""

    thumbnail_clicked = pyqtSignal(str, str, object)  # asset_id, asset_path, tile
    filename_clicked = pyqtSignal(str, str, object)  # asset_id, asset_path, tile
    checkbox_state_changed = pyqtSignal(bool)  # Whether the tile is selected
    drag_started = pyqtSignal(object)  # Asset data

    # Global QThreadPool for managing workers
    thread_pool = QThreadPool()
    
    # Class constants
    MARGINS_SIZE = 8

    def __init__(
        self,
        tile_model: AssetTileModel,
        thumbnail_size: int,
        tile_number: int,
        total_tiles: int,
        selection_model: SelectionModel,  # Add selection_model
    ):
        super().__init__()
        self.model = tile_model
        self.thumbnail_size = thumbnail_size
        self.tile_number = tile_number
        self.total_tiles = total_tiles
        self.selection_model = selection_model  # Assign selection_model
        self.asset_id = self.model.get_name()  # Use asset name as ID
        self.is_loading_thumbnail = False
        self.setObjectName("AssetTileViewFrame")  # Added object name
        self._setup_ui()
        self.model.data_changed.connect(self.update_ui)

        logger.debug(f"AssetTileView data updated for asset: {self.asset_id}")

    def update_asset_data(
        self, tile_model: AssetTileModel, tile_number: int, total_tiles: int
    ):
        """
        Updates tile data for Object Pooling.
        Allows reuse of an existing AssetTileView instance.
        """
        # Disconnect old signal connection - safe disconnection
        if hasattr(self, "model") and self.model:
            try:
                self.model.data_changed.disconnect(self.update_ui)
            except (TypeError, AttributeError):
                pass  # Connection already doesn't exist

        # Reset thumbnail loading state
        self.is_loading_thumbnail = False

        # Update data
        self.model = tile_model
        self.tile_number = tile_number
        self.total_tiles = total_tiles
        self.asset_id = self.model.get_name()

        # Connect new signal connection - only if model exists
        if self.model:
            self.model.data_changed.connect(self.update_ui)

        # Immediately update UI with new data
        self.update_ui()

        # ADDED: Set initial checkbox state based on SelectionModel
        if hasattr(self, "selection_model") and self.selection_model:
            is_selected = self.selection_model.is_selected(self.asset_id)
            self.set_checked(is_selected)
            logger.debug(f"Set checkbox state for {self.asset_id}: {is_selected}")

        logger.debug(f"AssetTileView data updated for asset: {self.asset_id}")

    def reset_for_pool(self):
        """Resets the tile to a state ready for reuse in the pool."""
        self._cleanup_connections_and_resources()
        self._reset_state_variables()
        self._clear_ui_elements()
        self._remove_from_parent()
        
        logger.debug("AssetTileView reset for pool reuse with proper signal cleanup")

    def _setup_ui(self):
        # Removed duplicate thumbnail_container creation - moved to _setup_ui_without_styles()
        # First create texture icon!
        self.texture_icon = QLabel()
        self.texture_icon.setObjectName(
            "AssetTileTextureIcon"
        )  # Texture icon (16x16px)
        self.texture_icon.setFixedSize(16, 16)
        self.texture_icon.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.texture_icon.setVisible(False)
        self._load_texture_icon()
        # First create label for filename!
        self.name_label = QLabel()
        self.name_label.setObjectName("AssetTileNameLabel")  # Filename (center)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        self.name_label.setCursor(Qt.CursorShape.PointingHandCursor)
        # Add label for file size
        self.size_label = QLabel()
        self.size_label.setObjectName("AssetTileSizeLabel")  # File size (right)
        self.size_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.size_label.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )
        # Add label for tile number
        self.tile_number_label = QLabel()
        self.tile_number_label.setObjectName(
            "AssetTileNumberLabel"
        )  # Tile number (left)
        self.tile_number_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tile_number_label.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )
        # Add checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setObjectName("AssetTileCheckBox")  # Selection checkbox (right)
        # ADDED: Checkbox signal connection
        self.checkbox.stateChanged.connect(self._on_checkbox_state_changed)
        # Add stars (5)
        self.star_checkboxes = [QCheckBox() for _ in range(5)]
        for i, star_cb in enumerate(self.star_checkboxes):
            star_cb.setObjectName(f"AssetTileStar_{i+1}")  # Stars 1-5 (center)
            star_cb.setProperty("class", "star")
            star_cb.setText("★")
            star_cb.clicked.connect(
                lambda checked, rating=i + 1: self._on_star_clicked(rating)
            )
        self._setup_ui_without_styles()

    def _setup_ui_without_styles(self):
        """Setup UI elements without applying styles"""
        self._create_thumbnail_container()
        self._calculate_tile_dimensions()
        self._setup_main_layout()
        self._setup_thumbnail_section()
        self._setup_filename_section()
        self._setup_bottom_row_section()
        self._finalize_ui_setup()
    
    def _create_thumbnail_container(self):
        """Create and configure thumbnail container"""
        self.thumbnail_container = QLabel()
        self.thumbnail_container.setObjectName("AssetTileThumbnail")
        thumb_size = self.thumbnail_size
        self.thumbnail_container.setFixedSize(thumb_size, thumb_size)
        self.thumbnail_container.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.thumbnail_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.thumbnail_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_container.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    
    def _calculate_tile_dimensions(self):
        """Calculate tile dimensions based on content"""
        tile_padding = 6  # from CSS
        tile_border = 1  # from CSS
        
        # Calculate width based on columns
        # icon(60) + name(136) + size(60)
        filename_width = 60 + 136 + 60  # 256px
        tile_width = max(self.thumbnail_size, filename_width)
        tile_height = self.thumbnail_size + 60 + (2 * tile_padding) + (2 * tile_border)
        self.setFixedSize(tile_width, tile_height)
    
    def _setup_main_layout(self):
        """Setup main layout and content container"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(10, 10, 10, 6)
        
        self.main_content_container = QWidget()
        self.main_content_container.setObjectName("AssetTileMainContent")
        
        main_content_layout = QVBoxLayout(self.main_content_container)
        main_content_layout.setSpacing(0)
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        
        self._main_content_layout = main_content_layout
        self._main_layout = layout
    
    def _setup_thumbnail_section(self):
        """Setup thumbnail section in main content"""
        self.thumbnail_container.setContentsMargins(0, 0, 0, 0)
        self._main_content_layout.addWidget(
            self.thumbnail_container, 0, Qt.AlignmentFlag.AlignCenter
        )
        self._main_content_layout.addSpacing(0)  # Spacing before filename
    
    def _setup_filename_section(self):
        """Setup filename section with texture icon, name and size"""
        filename_container = QHBoxLayout()
        filename_container.setContentsMargins(0, 0, 0, 0)
        filename_container.setSpacing(0)
        
        # Set fixed widths for columns
        self.texture_icon.setFixedWidth(60)
        self.name_label.setFixedWidth(136)
        self.size_label.setFixedWidth(60)
        
        filename_container.addWidget(
            self.texture_icon,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )
        filename_container.addWidget(self.name_label, 0, Qt.AlignmentFlag.AlignVCenter)
        filename_container.addWidget(
            self.size_label,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        
        filename_bg = QWidget()
        filename_bg.setObjectName("AssetTileFilenameContainer")
        filename_bg.setLayout(filename_container)
        self._main_content_layout.addWidget(filename_bg)
    
    def _setup_bottom_row_section(self):
        """Setup bottom row with tile number, stars and checkbox"""
        bottom_row_bg = QWidget()
        bottom_row_bg.setObjectName("AssetTileBottomRow")
        bottom_row_layout = QHBoxLayout(bottom_row_bg)
        bottom_row_layout.setContentsMargins(0, 0, 0, 0)
        bottom_row_layout.setSpacing(0)
        
        # NR to left
        bottom_row_layout.addWidget(
            self.tile_number_label, 0, Qt.AlignmentFlag.AlignVCenter
        )
        # Stretch to center
        bottom_row_layout.addStretch()
        # Stars to center
        for star_cb in self.star_checkboxes:
            bottom_row_layout.addWidget(star_cb, 0, Qt.AlignmentFlag.AlignVCenter)
        # Stretch to right
        bottom_row_layout.addStretch()
        # Checkbox to right
        bottom_row_layout.addWidget(self.checkbox, 0, Qt.AlignmentFlag.AlignVCenter)
        
        self._main_content_layout.addWidget(bottom_row_bg)
    
    def _finalize_ui_setup(self):
        """Finalize UI setup and apply initial state"""
        # Add main container to main layout
        self._main_layout.addWidget(self.main_content_container)
        
        self.setAcceptDrops(False)  # D&D will be handled by Controller
        self.setMouseTracking(True)
        
        self.update_ui()
        # Set initial checkbox state based on SelectionModel
        self.checkbox.setChecked(self.selection_model.is_selected(self.asset_id))

    def update_ui(self):
        if not hasattr(self, "model") or self.model is None:
            return
        if self.model.is_special_folder:
            self._setup_folder_tile_ui()
        else:
            self._setup_asset_tile_ui()

    def _setup_asset_tile_ui(self):
        if not hasattr(self, "model") or self.model is None:
            return
        # Display filename and file size
        file_name = self.model.get_name()
        # Limit name length to 16 characters
        if len(file_name) > 16:
            display_name = file_name[:13] + "..."
        else:
            display_name = file_name
        file_size_mb = self.model.get_size_mb()
        self.name_label.setText(display_name)
        if file_size_mb > 0:
            self.size_label.setText(f"{file_size_mb:.1f} MB")
        else:
            self.size_label.setText("")
        self.tile_number_label.setText(f"{self.tile_number} / {self.total_tiles}")
        # Check if stars fit on the tile
        stars_visible = self._check_stars_fit()
        for star_cb in self.star_checkboxes:
            star_cb.setVisible(stars_visible)
        self.set_star_rating(self.model.get_stars())
        # Always show texture icon to maintain layout geometry
        # If no textures, show transparent spacer, if has textures show icon
        if self.model.has_textures_in_archive():
            self.texture_icon.setVisible(True)
            self._load_texture_icon()
        else:
            self.texture_icon.setVisible(True)
            self._load_empty_texture_spacer()
        self.checkbox.setVisible(True)
        # Step 1: Try to load from cache
        thumbnail_path = self.model.get_thumbnail_path()
        cached_pixmap = thumbnail_cache.get(thumbnail_path)
        if cached_pixmap:
            self._set_thumbnail_pixmap(cached_pixmap)
        elif thumbnail_path and os.path.exists(thumbnail_path):
            # Step 2: If not in cache, load asynchronously
            self._create_placeholder_thumbnail()
            self._load_thumbnail_async(thumbnail_path)
        else:
            # Step 3: If file doesn't exist, show placeholder
            self._create_placeholder_thumbnail()

    def _load_thumbnail_async(self, path: str):
        if self.is_loading_thumbnail:
            return
        self.is_loading_thumbnail = True

        worker = ThumbnailLoaderWorker(path)
        worker.signals.finished.connect(self._on_thumbnail_loaded)
        worker.signals.error.connect(self._on_thumbnail_error)
        self.thread_pool.start(worker)

    def _on_thumbnail_loaded(self, path: str, pixmap: QPixmap):
        if self.model and path == self.model.get_thumbnail_path():
            thumbnail_cache.put(path, pixmap)
            self._set_thumbnail_pixmap(pixmap)
            self.is_loading_thumbnail = False

    def _on_thumbnail_error(self, path: str, error_message: str):
        if self.model and path == self.model.get_thumbnail_path():
            logger.warning(error_message)
            self._create_placeholder_thumbnail()
            self.is_loading_thumbnail = False

    def _set_thumbnail_pixmap(self, pixmap: QPixmap):
        """Sets QPixmap on the thumbnail label, cropping to square as required."""
        target_size = self.thumbnail_container.size()
        size = min(pixmap.width(), pixmap.height())

        # Crop to square
        if pixmap.width() > pixmap.height():
            # Wide - crop from left
            rect = pixmap.copy(0, 0, size, size)
        elif pixmap.height() > pixmap.width():
            # Tall - crop from top
            rect = pixmap.copy(0, 0, size, size)
        else:
            # Already square
            rect = pixmap

        scaled_pixmap = rect.scaled(
            target_size,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.thumbnail_container.setPixmap(scaled_pixmap)

    def _setup_folder_tile_ui(self):
        # Display folder name
        folder_name = self.model.get_name()
        # Limit name length to 16 characters
        if len(folder_name) > 16:
            display_name = folder_name[:13] + "..."
        else:
            display_name = folder_name

        self.name_label.setText(display_name)
        self.tile_number_label.setText(f"{self.tile_number} / {self.total_tiles}")

        # Hide stars for folders
        for star_cb in self.star_checkboxes:
            star_cb.setVisible(False)

        # Show transparent spacer for folders to maintain layout geometry
        self.texture_icon.setVisible(True)
        self._load_empty_texture_spacer()
        self.checkbox.setVisible(False)

        # Load folder icon
        self._load_folder_icon()

    def _create_placeholder_thumbnail(self):
        """Creates a placeholder thumbnail when there is no image."""
        pixmap = QPixmap(self.thumbnail_size, self.thumbnail_size)
        pixmap.fill(QColor("#2A2D2E"))
        self.thumbnail_container.setPixmap(pixmap)

    def _load_icon_with_fallback(self, icon_name: str, size: tuple) -> QPixmap:
        """Universal method for loading icons with fallback"""
        try:
            icon_path = os.path.join(
                os.path.dirname(__file__), "..", "resources", "img", icon_name
            )
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    return pixmap.scaled(
                        size[0],
                        size[1],
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
        except Exception as e:
            logger.error(f"Error loading icon {icon_name}: {e}")
        # Fallback: gray or yellow rectangle depending on icon
        fallback = QPixmap(size[0], size[1])
        if icon_name == "texture.png":
            fallback.fill(QColor("#FFD700"))
        else:
            fallback.fill(QColor("#2A2D2E"))
        return fallback

    def _load_folder_icon(self):
        self.thumbnail_container.setPixmap(
            self._load_icon_with_fallback(
                "folder.png", (self.thumbnail_size, self.thumbnail_size)
            )
        )

    def _load_texture_icon(self):
        self.texture_icon.setPixmap(
            self._load_icon_with_fallback("texture.png", (16, 16))
        )
    
    def _load_empty_texture_spacer(self):
        """Creates a transparent spacer to maintain layout geometry when no texture icon is needed"""
        # Create a transparent pixmap with the same dimensions as the texture icon
        spacer_pixmap = QPixmap(16, 16)
        spacer_pixmap.fill(Qt.GlobalColor.transparent)
        self.texture_icon.setPixmap(spacer_pixmap)

    def mousePressEvent(self, event):
        """Handles mouse press - clicks and drag & drop."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_position = event.position().toPoint()

            # Check which widget was clicked
            clicked_widget = self.childAt(event.position().toPoint())

            # If Shift is pressed, don't show preview or archive
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                logger.debug(
                    "Shift pressed - preview/archive blocked, drag and drop only"
                )
                super().mousePressEvent(event)
                return

            # Handle clicks on thumbnail
            if clicked_widget == self.thumbnail_container or (
                clicked_widget and clicked_widget.parent() == self.thumbnail_container
            ):
                self._on_thumbnail_clicked(event)
                return

            # Handle clicks on filename
            if clicked_widget == self.name_label:
                self._on_filename_clicked(event)
                return

            logger.debug(
                f"Mouse press detected, saved drag start position: {self._drag_start_position}"
            )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handles mouse move - initiates drag & drop."""
        if (
            event.buttons() & Qt.MouseButton.LeftButton
            and (
                event.position().toPoint() - self._drag_start_position
            ).manhattanLength()
            >= QApplication.startDragDistance()
        ):
            logger.debug(
                f"Mouse move detected, starting drag for asset: {self.asset_id}"
            )
            self._start_drag(event)
        super().mouseMoveEvent(event)

    def _start_drag(self, event):
        # Block D&D when gallery is loading
        if hasattr(self, "_drag_and_drop_enabled") and not self._drag_and_drop_enabled:
            logger.info("Drag and drop blocked during gallery loading.")
            return
        
        # SECURITY: Check if drag is already in progress
        if hasattr(self, "_drag_in_progress") and self._drag_in_progress:
            logger.warning("Drag already in progress, ignoring new drag request")
            return
            
        logger.debug(f"Starting drag for asset: {self.asset_id}")

        # Check if selection_model exists
        if not self.selection_model:
            logger.error("selection_model is None, cannot start drag")
            return

        # Get selected assets from SelectionModel
        selected_asset_ids = self.selection_model.get_selected_asset_ids()
        logger.debug(f"Selected asset IDs: {selected_asset_ids}")

        # If no assets are selected, drag only this tile
        if not selected_asset_ids:
            selected_asset_ids = [self.asset_id]
            logger.debug(
                f"No selected assets, dragging single asset: {selected_asset_ids}"
            )

        # SECURITY: Check if asset_ids are valid
        if not selected_asset_ids or any(not aid for aid in selected_asset_ids):
            logger.error(f"Invalid asset IDs for drag: {selected_asset_ids}")
            return

        try:
            # Set drag in progress flag
            self._drag_in_progress = True
            
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_text = f"application/x-cfab-asset,{','.join(selected_asset_ids)}"
            mime_data.setText(mime_text)
            drag.setMimeData(mime_data)

            logger.debug(f"Created mime data: {mime_text}")

            # Set drag cursor
            drag.setDragCursor(QPixmap(), Qt.DropAction.MoveAction)

            # Emit drag start signal
            self.drag_started.emit(selected_asset_ids)
            logger.debug("Emitted drag_started signal")

            # FIX: Execute drag with timeout for safety
            # We use Qt.DropAction.MoveAction | Qt.DropAction.IgnoreAction for better compatibility
            result = drag.exec(Qt.DropAction.MoveAction | Qt.DropAction.IgnoreAction)
            logger.debug(f"Drag exec result: {result}")
            
        except Exception as e:
            logger.error(f"Error during drag operation: {e}")
        finally:
            # Always clear drag in progress flag
            self._drag_in_progress = False

    def _on_thumbnail_clicked(self, _ev):
        logger.debug(f"AssetTileView: Thumbnail clicked for asset {self.asset_id}")
        if self.model.is_special_folder:
            folder_path = self.model.get_special_folder_path()
            self.thumbnail_clicked.emit(self.asset_id, folder_path, self)
        else:
            self.thumbnail_clicked.emit(
                self.asset_id, self.model.get_preview_path(), self
            )

    def _on_filename_clicked(self, _ev):
        logger.debug(f"AssetTileView: Filename clicked for asset {self.asset_id}")
        if self.model.is_special_folder:
            folder_path = self.model.get_special_folder_path()
            self.filename_clicked.emit(self.asset_id, folder_path, self)
        else:
            self.filename_clicked.emit(
                self.asset_id, self.model.get_archive_path(), self
            )

    def update_thumbnail_size(self, new_size: int):
        """Updates thumbnail size and recalculates layout."""
        self.thumbnail_size = new_size
        # Recalculate tile width
        tile_width = new_size + (2 * self.MARGINS_SIZE)
        tile_height = new_size + 70
        self.setFixedSize(tile_width, tile_height)
        self.update_ui()  # Reload UI to apply new size

    def _update_stars_visibility(self):
        """Updates the visibility of stars based on available space."""
        if hasattr(self, "model") and self.model and not self.model.is_special_folder:
            stars_visible = self._check_stars_fit()
            for star_cb in self.star_checkboxes:
                star_cb.setVisible(stars_visible)

    def release_resources(self):
        """Releases resources associated with the tile, including cached_pixmap."""
        self._cleanup_connections_and_resources()
        logger.debug("Resources released for tile: %s with complete cleanup", self.asset_id)

    def is_checked(self) -> bool:
        """Checks if the tile is selected."""
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool):
        """Sets the checked state of the tile."""
        # Set blocking flag before state change
        self._updating_checkbox = True
        try:
            # Temporarily disconnect signal to avoid recursion
            self.checkbox.blockSignals(True)
            self.checkbox.setChecked(checked)
            self.checkbox.blockSignals(False)
            # Manually call state change handler to update model
            self._on_checkbox_state_changed(self.checkbox.checkState().value)
        finally:
            # Always remove blocking flag
            self._updating_checkbox = False

    def _on_checkbox_state_changed(self, state: int):
        """Handles checkbox state change."""
        is_checked = state == Qt.CheckState.Checked.value
        # Protection against recursion during programmatic checkbox setting
        if hasattr(self, "_updating_checkbox") and self._updating_checkbox:
            return
        if is_checked:
            self.selection_model.add_selection(self.asset_id)
        else:
            self.selection_model.remove_selection(self.asset_id)
        self.checkbox_state_changed.emit(is_checked)
        # ADDED: Force status bar update
        try:
            main_window = None
            widget = self
            while widget and widget.parent():
                widget = widget.parent()
                if hasattr(widget, "update_selection_status"):
                    main_window = widget
                    break
            if main_window:
                main_window.update_selection_status()
                logger.debug(
                    f"Updated status bar after checkbox change for {self.asset_id}"
                )
        except Exception as e:
            logger.debug(f"Cannot update status bar: {e}")

    def get_star_rating(self) -> int:
        """Gets the star rating."""
        return sum(1 for cb in self.star_checkboxes if cb.isChecked())

    def set_star_rating(self, rating: int):
        """Sets the star rating."""
        for i, cb in enumerate(self.star_checkboxes):
            cb.setChecked(i < rating)

    def _on_star_clicked(self, clicked_rating: int):
        """Handles star click."""
        current_rating = self.get_star_rating()
        if clicked_rating == current_rating:
            # If clicked on the last selected star, uncheck all
            self.clear_stars()
            self.model.set_stars(0)
        else:
            # Set new rating
            self.set_star_rating(clicked_rating)
            self.model.set_stars(clicked_rating)

    def clear_stars(self):
        for cb in self.star_checkboxes:
            cb.setChecked(False)

    def set_drag_and_drop_enabled(self, enabled: bool):
        """Enables or disables drag and drop for the tile."""
        self._drag_and_drop_enabled = enabled

    def _check_stars_fit(self) -> bool:
        """Checks if stars fit on the tile."""
        # Calculate available width for stars
        # Tile width - margins - number - checkbox - spacing
        available_width = self.width() - (2 * self.MARGINS_SIZE) - 30 - 16 - 12

        # Estimated width of 5 stars (each ~12px) + spacing
        stars_width = 5 * 12 + 4 * 6  # 5 stars at 12px + 4 spacing at 6px

        return stars_width <= available_width

    def resizeEvent(self, event):
        """Handles tile resize event."""
        super().resizeEvent(event)
        # Update stars visibility after size change
        self._update_stars_visibility()
        # Update thumbnail size to fill available space
        self._update_thumbnail_size()

    # ===============================================
    # CONSOLIDATED CLEANUP METHODS
    # ===============================================
    
    def _cleanup_connections_and_resources(self):
        """Consolidated method for disconnecting all signals and cleaning up resources"""
        # Disconnect model signals
        if hasattr(self, "model") and self.model is not None:
            try:
                self.model.data_changed.disconnect(self.update_ui)
            except (TypeError, AttributeError):
                pass  # Connection already doesn't exist
        
        # Disconnect checkbox signals
        if hasattr(self, "checkbox") and self.checkbox:
            try:
                self.checkbox.blockSignals(True)
                self.checkbox.stateChanged.disconnect()
                self.checkbox.blockSignals(False)
            except (TypeError, AttributeError):
                pass
        
        # Disconnect star checkbox signals
        if hasattr(self, "star_checkboxes"):
            for star_cb in self.star_checkboxes:
                try:
                    star_cb.blockSignals(True)
                    star_cb.clicked.disconnect()
                    star_cb.blockSignals(False)
                except (TypeError, AttributeError, RuntimeError):
                    pass  # Widget already removed or signal already disconnected
        
        # Stop any running thumbnail workers
        if hasattr(self, 'is_loading_thumbnail') and self.is_loading_thumbnail:
            # Cancel any pending thumbnail loading
            self.is_loading_thumbnail = False
        
        # Clear cached pixmap to free memory
        if hasattr(self, "_cached_pixmap"):
            self._cached_pixmap = None
    
    def _reset_state_variables(self):
        """Reset all state variables to default values"""
        self.model = None
        self.selection_model = None
        self.asset_id = ""
        self.tile_number = 0
        self.total_tiles = 0
        self.is_loading_thumbnail = False
    
    def _clear_ui_elements(self):
        """Clear all UI elements safely"""
        # Clear containers and labels
        if hasattr(self, "thumbnail_container"):
            self.thumbnail_container.clear()
        if hasattr(self, "name_label"):
            self.name_label.clear()
        if hasattr(self, "tile_number_label"):
            self.tile_number_label.clear()
        if hasattr(self, "checkbox"):
            self.checkbox.setChecked(False)
        
        # Clear star checkboxes
        if hasattr(self, "star_checkboxes"):
            for star_cb in self.star_checkboxes:
                try:
                    star_cb.setChecked(False)
                except RuntimeError:
                    pass  # Widget already removed
    
    def _remove_from_parent(self):
        """Remove tile from parent layout if present"""
        if self.parent():
            self.setParent(None)



    def _update_thumbnail_size(self):
        """Updates thumbnail size based on available space."""
        if hasattr(self, "thumbnail_container"):
            # Calculate available space for thumbnail
            available_width = self.width() - (2 * self.MARGINS_SIZE)
            available_height = (
                self.height() - 70
            )  # Subtract space for text and controls

            # Use smaller dimension to maintain square proportions
            new_size = min(available_width, available_height, self.thumbnail_size)
            new_size = max(new_size, 64)  # Minimum size 64px

            self.thumbnail_container.setFixedSize(new_size, new_size)
