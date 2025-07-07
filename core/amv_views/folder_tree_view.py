"""
Folder tree view with drag & drop support.
Contains a custom QTreeView with asset dragging functionality.
"""

import logging
import os

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QBrush, QColor, QIcon
from PyQt6.QtWidgets import QMenu, QTreeView

from core.file_utils import open_path_in_explorer

logger = logging.getLogger(__name__)


class CustomFolderTreeView(QTreeView):
    """
    Custom folder tree view with drag & drop and context menu support.
    Handles asset dragging between folders and asset rebuilding.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._highlighted_index = None
        self.drag_drop_model = None
        self.file_operations_model = None
        self.current_folder_path_getter = (
            None  # Function to get current folder
        )
        self.asset_grid_model = None  # Reference to asset grid model
        self.rebuild_callback = None  # Callback for asset rebuilding
        self.open_in_explorer_callback = None  # Callback for opening in explorer
        self.refresh_folder_callback = None  # Callback for folder refresh
        self._active_folder_index = None  # Active folder index

        # Enable drop support
        self.setAcceptDrops(True)

        # Connect expanded/collapsed signals
        self.expanded.connect(self._on_item_expanded)
        self.collapsed.connect(self._on_item_collapsed)

    def set_models(
        self,
        drag_drop_model,
        file_operations_model,
        current_folder_path_getter,
        asset_grid_model=None,
    ):
        """Sets models needed for drag & drop handling."""
        self.drag_drop_model = drag_drop_model
        self.file_operations_model = file_operations_model
        self.current_folder_path_getter = current_folder_path_getter
        self.asset_grid_model = asset_grid_model

    def set_rebuild_callback(self, callback):
        """Sets callback for asset rebuilding."""
        self.rebuild_callback = callback

    def set_open_in_explorer_callback(self, callback):
        """Sets callback for opening folder in explorer."""
        self.open_in_explorer_callback = callback

    def set_refresh_folder_callback(self, callback):
        """Sets callback for folder refresh."""
        self.refresh_folder_callback = callback

    def setModel(self, model):
        super().setModel(model)
        # Connect currentChanged signal with delay, so selectionModel already exists
        QTimer.singleShot(0, self._connect_selection_model)

    def _connect_selection_model(self):
        sel_model = self.selectionModel()
        if sel_model:
            sel_model.currentChanged.connect(self._on_current_folder_changed)

    def contextMenuEvent(self, event):
        """Handles the context menu for a folder."""
        try:
            index = self.indexAt(event.pos())
            logger.debug(
                f"contextMenuEvent - index: {index}, isValid: {index.isValid()}"
            )
            logger.debug(f"contextMenuEvent - mouse position: {event.pos()}")

            menu = QMenu(self)
            
            # Option to enable/disable asset counters (always available)
            show_counts = self._get_show_asset_counts()
            toggle_counts_action = QAction(
                "Hide asset counters" if show_counts else "Show asset counters", 
                self
            )
            toggle_counts_action.triggered.connect(self._toggle_asset_counts)
            menu.addAction(toggle_counts_action)
            
            # Recursive mode option (available when counters are enabled)
            if show_counts:
                recursive_counts = self._get_recursive_asset_counts()
                toggle_recursive_action = QAction(
                    "Count only in folder" if recursive_counts else "Count recursively (+)",
                    self
                )
                toggle_recursive_action.triggered.connect(self._toggle_recursive_counts)
                menu.addAction(toggle_recursive_action)
            
            # Separator
            menu.addSeparator()

            if index.isValid():
                item = self.model().itemFromIndex(index)
                logger.debug(f"contextMenuEvent - item: {item}")
                logger.debug(
                    f"contextMenuEvent - item text: {item.text() if item else 'None'}"
                )

                if item and item.data(Qt.ItemDataRole.UserRole):
                    folder_path = item.data(Qt.ItemDataRole.UserRole)
                    logger.debug(f"contextMenuEvent - folder_path: {folder_path}")
                    logger.debug(
                        f"contextMenuEvent - item row: {item.row()}, column: {item.column()}"
                    )

                    # Folder refresh option (at top)
                    refresh_folder_action = QAction("Refresh folder", self)
                    refresh_folder_action.triggered.connect(
                        lambda checked, path=folder_path: self._refresh_folder(path)
                    )
                    menu.addAction(refresh_folder_action)

                    # Separator
                    menu.addSeparator()

                    # Open in explorer option
                    open_in_explorer_action = QAction("Open in Explorer", self)
                    open_in_explorer_action.triggered.connect(
                        lambda checked, path=folder_path: self._open_folder_in_explorer(
                            path
                        )
                    )
                    menu.addAction(open_in_explorer_action)

                    # Separator
                    menu.addSeparator()

                    # Rebuild assets option
                    rebuild_action = QAction("Rebuild assets", self)
                    rebuild_action.triggered.connect(
                        lambda checked, path=folder_path: self._rebuild_assets_in_folder(
                            path
                        )
                    )
                    menu.addAction(rebuild_action)

                else:
                    logger.warning(
                        "contextMenuEvent - item or UserRole data is None"
                    )
                    if item:
                        logger.warning(
                            f"contextMenuEvent - UserRole data: {item.data(Qt.ItemDataRole.UserRole)}"
                        )
            else:
                logger.warning("contextMenuEvent - index is not valid")

            # Show menu
            menu.exec(event.globalPos())

        except Exception as e:
            logger.error(f"Error handling context menu: {e}")

    def _toggle_asset_counts(self):
        """Toggles showing asset counters in folders"""
        try:
            # Get current state
            current_state = self._get_show_asset_counts()
            new_state = not current_state
            
            # Inform controller about change
            if hasattr(self, 'folder_tree_controller'):
                self.folder_tree_controller.set_show_asset_counts(new_state)
            
            logger.debug(f"Toggled asset counts: {current_state} -> {new_state}")
            
        except Exception as e:
            logger.error(f"Error toggling asset counters: {e}")

    def _toggle_recursive_counts(self):
        """Toggles recursive asset counting mode"""
        try:
            # Get current state
            current_state = self._get_recursive_asset_counts()
            new_state = not current_state
            
            # Inform controller about change
            if hasattr(self, 'folder_tree_controller'):
                self.folder_tree_controller.set_recursive_asset_counts(new_state)
            
            logger.debug(f"Toggled recursive asset counts: {current_state} -> {new_state}")
            
        except Exception as e:
            logger.error(f"Error toggling recursive mode: {e}")

    def _get_show_asset_counts(self) -> bool:
        """Gets current state of showing asset counters"""
        try:
            if hasattr(self, 'folder_tree_controller'):
                return self.folder_tree_controller.get_show_asset_counts()
            return True  # Enabled by default
        except Exception as e:
            logger.error(f"Error getting asset counters state: {e}")
            return True

    def _get_recursive_asset_counts(self) -> bool:
        """Gets current state of recursive asset counting"""
        try:
            if hasattr(self, 'folder_tree_controller'):
                return self.folder_tree_controller.get_recursive_asset_counts()
            return True  # Enabled by default
        except Exception as e:
            logger.error(f"Error getting recursive mode state: {e}")
            return True

    def set_folder_tree_controller(self, controller):
        """Sets reference to folder tree controller"""
        self.folder_tree_controller = controller

    def _open_folder_in_explorer(self, folder_path: str):
        """Opens folder in system explorer."""
        logger.debug(f"_open_folder_in_explorer - received path: {folder_path}")
        try:
            if self.open_in_explorer_callback:
                logger.debug(
                    f"_open_folder_in_explorer - calling callback with path: {folder_path}"
                )
                self.open_in_explorer_callback(folder_path)
            else:
                logger.debug(
                    f"_open_folder_in_explorer - no callback, using direct opening: {folder_path}"
                )
                # Fallback - direct opening
                open_path_in_explorer(folder_path, self)
        except Exception as e:
            logger.error(f"Error opening folder in explorer: {e}")

    def _rebuild_assets_in_folder(self, folder_path: str):
        """Rebuilds assets in selected folder."""
        try:
            if self.rebuild_callback:
                self.rebuild_callback(folder_path)
            else:
                logger.warning("No callback for asset rebuilding")
        except Exception as e:
            logger.error(f"Error calling rebuild callback: {e}")

    def _refresh_folder(self, folder_path: str):
        """Refreshes folder."""
        try:
            if self.refresh_folder_callback:
                self.refresh_folder_callback(folder_path)
            else:
                logger.warning("No callback for folder refresh")
        except Exception as e:
            logger.error(f"Error calling refresh folder callback: {e}")

    def dragEnterEvent(self, event):
        """Handles drag enter event."""
        logger.debug(f"dragEnterEvent triggered - mimeData: {event.mimeData().text()}")
        if event.mimeData().hasText() and event.mimeData().text().startswith(
            "application/x-cfab-asset"
        ):
            event.acceptProposedAction()
            pos = event.position().toPoint()
            logger.debug(f"Accepting drag at position: {pos}")
            self._highlight_folder_at_position(pos)
        else:
            logger.debug("Ignoring drag - invalid mime data")
            event.ignore()

    def dragLeaveEvent(self, event):
        """Handles drag leave event."""
        logger.debug("dragLeaveEvent triggered")
        self._clear_folder_highlight()

    def dragMoveEvent(self, event):
        """Handles drag move event."""
        logger.debug(
            f"dragMoveEvent triggered at position: {event.position().toPoint()}"
        )
        if event.mimeData().hasText() and event.mimeData().text().startswith(
            "application/x-cfab-asset"
        ):
            index = self.indexAt(event.position().toPoint())
            if index.isValid():
                item = self.model().itemFromIndex(index)
                if item and item.data(Qt.ItemDataRole.UserRole):
                    target_path = item.data(Qt.ItemDataRole.UserRole)
                    logger.debug(f"Valid target path: {target_path}")
                    if self.drag_drop_model and self.drag_drop_model.validate_drop(
                        target_path,
                        (
                            self.current_folder_path_getter()
                            if self.current_folder_path_getter
                            else None
                        ),
                    ):
                        event.acceptProposedAction()
                        self._highlight_folder_at_position(event.position().toPoint())
                        logger.debug("Drag move accepted and highlighted")
                    else:
                        event.ignore()
                        self._clear_folder_highlight()
                        logger.debug("Drag move rejected - validation failed")
                else:
                    event.ignore()
                    self._clear_folder_highlight()
                    logger.debug("Drag move rejected - invalid item")
            else:
                event.ignore()
                self._clear_folder_highlight()
                logger.debug("Drag move rejected - invalid index")
        else:
            event.ignore()
            self._clear_folder_highlight()
            logger.debug("Drag move rejected - invalid mime data")

    def dropEvent(self, event):
        """Handles drop event."""
        try:
            logger.debug(f"DropEvent triggered - mimeData: {event.mimeData().text()}")

            # SECURITY: Check if operation is already in progress
            if (hasattr(self, 'file_operations_model') and 
                self.file_operations_model and 
                hasattr(self.file_operations_model, '_worker') and
                self.file_operations_model._worker and 
                self.file_operations_model._worker.isRunning()):
                logger.warning("File operation already in progress, rejecting drop")
                event.ignore()
                self._clear_folder_highlight()
                return

            # REFACTOR: move validation to separate methods
            if not self._validate_drop_event(event):
                return

            target_info = self._get_drop_target_info(event)
            if not target_info:
                return

            target_folder_path, asset_ids, current_folder_path = target_info

            # SECURITY: Additional asset_ids validation
            if not asset_ids or not all(asset_id.strip() for asset_id in asset_ids):
                logger.error(f"Invalid or empty asset IDs: {asset_ids}")
                event.ignore()
                self._clear_folder_highlight()
                return

            # Get full asset data from asset_grid_model
            assets_to_move = self._get_assets_to_move(asset_ids)

            if self._can_perform_drop(
                assets_to_move, asset_ids, current_folder_path, target_folder_path
            ):
                self._perform_drop_operation(
                    assets_to_move, current_folder_path, target_folder_path, asset_ids
                )
                event.acceptProposedAction()
                logger.info(f"Drop completed successfully")
            else:
                event.ignore()

            self._clear_folder_highlight()

        except Exception as e:
            logger.error(f"Error in dropEvent: {e}")
            event.ignore()
            self._clear_folder_highlight()

    def _validate_drop_event(self, event):
        """Checks if drop event is valid."""
        if not event.mimeData().hasText() or not event.mimeData().text().startswith(
            "application/x-cfab-asset"
        ):
            logger.error("Invalid mime data")
            event.ignore()
            return False
        return True

    def _get_drop_target_info(self, event):
        """Gets drop target information."""
        index = self.indexAt(event.position().toPoint())
        if not index.isValid():
            logger.error("Invalid index")
            event.ignore()
            return None

        item = self.model().itemFromIndex(index)
        if not item or not item.data(Qt.ItemDataRole.UserRole):
            logger.error("Invalid item or no UserRole data")
            event.ignore()
            return None

        target_folder_path = item.data(Qt.ItemDataRole.UserRole)
        logger.debug(f"Target folder path: {target_folder_path}")

        current_folder_path = None
        if self.current_folder_path_getter:
            current_folder_path = self.current_folder_path_getter()
            logger.debug(f"Current folder path: '{current_folder_path}'")
            logger.debug(f"Target folder path: '{target_folder_path}'")

        if not self.drag_drop_model or not self.drag_drop_model.validate_drop(
            target_folder_path,
            (
                self.current_folder_path_getter()
                if self.current_folder_path_getter
                else None
            ),
        ):
            logger.error(f"Drag drop validation failed for: {target_folder_path}")
            event.ignore()
            return None

        asset_ids_str = event.mimeData().text().replace("application/x-cfab-asset,", "")
        asset_ids = asset_ids_str.split(",")
        logger.debug(f"Asset IDs to move: {asset_ids}")

        return target_folder_path, asset_ids, current_folder_path

    def _get_assets_to_move(self, asset_ids):
        """Gets full asset data to move."""
        assets_to_move = []
        if self.asset_grid_model:
            all_assets = self.asset_grid_model.get_assets()
            logger.debug(f"All assets count: {len(all_assets)}")
            assets_to_move = [
                asset for asset in all_assets if asset.get("name") in asset_ids
            ]
            logger.debug(f"Assets to move count: {len(assets_to_move)}")
        else:
            logger.error("asset_grid_model is None!")
        return assets_to_move

    def _can_perform_drop(
        self, assets_to_move, asset_ids, current_folder_path, target_folder_path
    ):
        """Checks if drop operation can be performed."""
        if not asset_ids or not all(asset_ids):
            logger.error(
                f"[DROP ERROR] asset_ids is empty or contains empty values: {asset_ids}"
            )
            return False
        if not current_folder_path:
            logger.error(f"[DROP ERROR] current_folder_path is empty or None!")
            return False
        if not target_folder_path:
            logger.error(f"[DROP ERROR] target_folder_path is empty or None!")
            return False
        if (
            not assets_to_move
            or not self.file_operations_model
            or not self.current_folder_path_getter
        ):
            logger.error(
                f"[DROP ERROR] Missing required models: assets_to_move={len(assets_to_move)}, file_operations_model={self.file_operations_model is not None}, current_folder_path_getter={self.current_folder_path_getter is not None}"
            )
            return False
        return True

    def _perform_drop_operation(
        self, assets_to_move, current_folder_path, target_folder_path, asset_ids
    ):
        """Performs drop operation."""
        logger.debug(f"Source folder path: {current_folder_path}")
        if current_folder_path:
            try:
                # SECURITY: Check again if models are available
                if not self.file_operations_model:
                    logger.error("file_operations_model is None, cannot perform drop")
                    return
                
                if not self.drag_drop_model:
                    logger.error("drag_drop_model is None, cannot complete drop")
                    return
                
                # SECURITY: Check if folders exist
                if not os.path.exists(current_folder_path):
                    logger.error(f"Source folder does not exist: {current_folder_path}")
                    return
                
                if not os.path.exists(target_folder_path):
                    logger.warning(f"Target folder does not exist, will be created: {target_folder_path}")
                
                # Execute move operation in separate thread
                logger.info(f"Starting move operation: {len(assets_to_move)} assets from {current_folder_path} to {target_folder_path}")
                self.file_operations_model.move_assets(
                    assets_to_move,
                    current_folder_path,
                    target_folder_path,
                )
                
                # Mark drop as completed
                self.drag_drop_model.complete_drop(target_folder_path, asset_ids)
                logger.debug("Drop operation initiated successfully")
                
            except Exception as e:
                logger.error(f"Error in drop operation: {e}")
        else:
            logger.error("Source folder path is empty!")

    def _highlight_folder_at_position(self, pos):
        """Highlights folder at given position without changing working selection."""
        try:
            # First clear previous highlight
            self._clear_folder_highlight()
            index = self.indexAt(pos)
            if index.isValid():
                item = self.model().itemFromIndex(index)
                if item:
                    item.setForeground(QBrush(QColor("#717bbc")))
                self._highlighted_index = index
                self.viewport().update()
                logger.debug(f"Highlighted folder at position: {pos}")
            else:
                logger.debug(f"No valid index at position: {pos}")
        except Exception as e:
            logger.error(f"Error highlighting folder at position {pos}: {e}")

    def _clear_folder_highlight(self):
        """Clears target folder highlight."""
        try:
            if self._highlighted_index and self._highlighted_index.isValid():
                item = self.model().itemFromIndex(self._highlighted_index)
                if item:
                    item.setForeground(
                        QBrush(QColor("#a9b7c6"))
                    )  # Restore default color
                self._highlighted_index = None
                self.viewport().update()
                logger.debug("Cleared folder highlight")
        except Exception as e:
            logger.error(f"Error clearing folder highlight: {e}")

    def _on_item_expanded(self, index):
        item = self.model().itemFromIndex(index)
        if item:
            item.setIcon(QIcon("core/resources/img/open_folder_icon.png"))

    def _on_item_collapsed(self, index):
        item = self.model().itemFromIndex(index)
        if item:
            item.setIcon(QIcon("core/resources/img/folder_icon.png"))

    def _on_current_folder_changed(self, current, previous):
        # Restore icon to previous folder
        if previous.isValid():
            prev_item = self.model().itemFromIndex(previous)
            if prev_item:
                if self.isExpanded(previous):
                    prev_item.setIcon(QIcon("core/resources/img/open_folder_icon.png"))
                else:
                    prev_item.setIcon(QIcon("core/resources/img/folder_icon.png"))
        # Set icon for active folder
        if current.isValid():
            curr_item = self.model().itemFromIndex(current)
            if curr_item:
                curr_item.setIcon(QIcon("core/resources/img/workfolder_icon.png"))
        self._active_folder_index = current
