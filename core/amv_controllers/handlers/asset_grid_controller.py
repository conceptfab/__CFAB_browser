"""
AssetGridController - Controller for managing the asset grid.
Responsible for creating, rebuilding, and updating the asset tile grid.
"""

import logging
import os

from PyQt6.QtCore import QObject

from core.amv_models.asset_tile_model import AssetTileModel
from core.amv_views.asset_tile_pool import AssetTilePool
from core.performance_monitor import measure_operation
from core.utilities import update_main_window_status

from ...amv_views.asset_tile_view import AssetTileView

logger = logging.getLogger(__name__)


class AssetGridController(QObject):
    """Controller for managing the asset grid"""

    def __init__(self, model, view, controller):
        super().__init__()
        self.model = model
        self.view = view
        self.controller = controller

        # Pool of AssetTileView objects
        self.tile_pool = AssetTilePool(
            self.model.selection_model, self.view.gallery_content_widget
        )

        # Moved from AmvController
        self.asset_tiles = []  # List of tiles
        self.original_assets = (
            []
        )  # Stores the original list of assets (unfiltered)
        self.drag_and_drop_enabled = True  # D&D lock flag

        self.active_star_filter = 0  # 0 = no filter, 1-5 = star filter
        
        # OPTIMIZATION: Throttling for rebuild_asset_grid
        from PyQt6.QtCore import QTimer
        self._rebuild_timer = QTimer()
        self._rebuild_timer.setSingleShot(True)
        self._rebuild_timer.timeout.connect(self._perform_delayed_rebuild)
        self._pending_assets = None

    def setup(self):
        """Initializes the asset grid"""
        logger.debug("Asset grid model connected to view - STAGE 9")

    def on_assets_changed(self, assets):
        """Handles asset list changes"""
        if assets is None or len(assets) == 0:  # More specific check for None
            self.set_original_assets([])
            self.clear_asset_tiles()  # Ensure gallery is cleared
            self.view.update_gallery_placeholder("No assets in this folder.")
            self.view.stacked_layout.setCurrentIndex(1)  # Show placeholder
            return
        self.set_original_assets(assets)
        self.rebuild_asset_grid(assets)

        # After rebuilding the grid, if a filter is active, apply it
        current_star_filter = (
            self.active_star_filter
        )  # Not self.controller.asset_grid_controller.active_star_filter
        if current_star_filter > 0:
            # Trigger filter by updating the grid - filter will be applied automatically
            # via signal connections, avoiding cross-controller dependencies
            pass

        # Update button states after asset change
        self.controller.control_panel_controller.update_button_states()

    def rebuild_asset_grid(self, assets: list):
        """
        Throttled version of asset grid rebuild to prevent excessive calls.
        """
        # OPTIMIZATION: Throttling - delay rebuild by 50ms
        self._pending_assets = assets
        self._rebuild_timer.start(50)  # 50ms delay
    
    def _perform_delayed_rebuild(self):
        """
        Performs the actual delayed rebuild.
        """
        if self._pending_assets is not None:
            self._rebuild_asset_grid_immediate(self._pending_assets)
            self._pending_assets = None

    def _rebuild_asset_grid_immediate(self, assets: list):
        """
        Intelligently synchronizes the grid with the new asset list, minimizing
        UI operations to eliminate flickering and loading errors.
        """
        # Check if assets list is empty
        if not assets:
            self._finalize_grid_update(empty=True)
            return
            
        # First, extract the folder tile (is_special_folder), sort the rest alphabetically
        folder_tile = [a for a in assets if a.get("type") == "special_folder"]
        other_tiles = [a for a in assets if a.get("type") != "special_folder"]
        other_tiles.sort(key=lambda x: x.get("name", "").lower())
        assets = folder_tile + other_tiles
        with measure_operation(
            "asset_grid_controller.rebuild_asset_grid", {"assets_count": len(assets)}
        ):
            (
                new_asset_map,
                current_tile_map,
                new_ids,
                current_ids,
                ids_to_remove,
                ids_to_add,
                ids_to_update,
            ) = self._prepare_asset_maps(assets)
            self._remove_unnecessary_tiles(ids_to_remove, current_tile_map)
            self._update_existing_tiles(assets, ids_to_update, current_tile_map)
            self._add_new_tiles(assets, ids_to_add, current_tile_map)
            if not new_ids and not current_ids:
                # No assets at all - show empty state
                self._finalize_grid_update(empty=True)
                return
            self._reorganize_layout(assets, current_tile_map)
            self._finalize_grid_update()

    def _prepare_asset_maps(self, assets):
        if not assets:
            return {}, {}, set(), set(), set(), set(), set()
            
        new_asset_map = {asset["name"]: asset for asset in assets}
        current_tile_map = {tile.asset_id: tile for tile in self.asset_tiles}
        new_ids = set(new_asset_map.keys())
        current_ids = set(current_tile_map.keys())
        ids_to_remove = current_ids - new_ids
        ids_to_add = new_ids - current_ids
        ids_to_update = current_ids.intersection(new_ids)
        return (
            new_asset_map,
            current_tile_map,
            new_ids,
            current_ids,
            ids_to_remove,
            ids_to_add,
            ids_to_update,
        )

    def _remove_unnecessary_tiles(self, ids_to_remove, current_tile_map):
        if not ids_to_remove:
            return
            
        for asset_id in ids_to_remove:
            tile = current_tile_map.pop(asset_id)
            self.tile_pool.release(tile)
            self.asset_tiles.remove(tile)

    def _update_existing_tiles(self, assets, ids_to_update, current_tile_map):
        if not assets or not ids_to_update:
            return
            
        for i, asset in enumerate(assets):
            asset_id = asset["name"]
            if asset_id in ids_to_update:
                tile = current_tile_map[asset_id]
                tile_model = AssetTileModel(asset, self._get_asset_file_path(asset_id))
                tile.update_asset_data(tile_model, i + 1, len(assets))

    def _add_new_tiles(self, assets, ids_to_add, current_tile_map):
        if not assets or not ids_to_add:
            return
            
        thumb_size = self.model.control_panel_model.get_thumbnail_size()
        for i, asset in enumerate(assets):
            asset_id = asset["name"]
            if asset_id in ids_to_add:
                tile_model = AssetTileModel(asset, self._get_asset_file_path(asset_id))
                tile = self.tile_pool.acquire(
                    tile_model, thumb_size, i + 1, len(assets)
                )
                self._connect_tile_signals(tile)
                self.asset_tiles.append(tile)
                current_tile_map[asset_id] = tile

    def _reorganize_layout(self, assets, current_tile_map):
        if not assets:
            self.view.update_gallery_placeholder("No assets in this folder.")
            self.view.stacked_layout.setCurrentIndex(1)  # Show placeholder
            return
            
        cols = self.model.asset_grid_model.get_columns()
        sorted_tiles = [
            current_tile_map[asset["name"]]
            for asset in assets
            if asset["name"] in current_tile_map
        ]
        
        # Check if we have any tiles to display
        if not sorted_tiles:
            self.view.update_gallery_placeholder("No assets in this folder.")
            self.view.stacked_layout.setCurrentIndex(1)  # Show placeholder
            return
        
        # OPTIMIZATION: Check if layout actually needs rebuilding using hash
        new_layout_hash = hash(tuple(asset["name"] for asset in assets))
        
        if hasattr(self, '_last_layout_hash') and self._last_layout_hash == new_layout_hash:
            logger.debug("Layout unchanged - skipping full rebuild")
            return
        
        self._last_layout_hash = new_layout_hash
        
        # Clear placeholder and show gallery
        self.view.update_gallery_placeholder("")
        
        # Full rebuild only when necessary
        logger.debug("Layout changed - performing full rebuild")
        while self.view.gallery_layout.count():
            item = self.view.gallery_layout.takeAt(0)
            if item.widget():
                item.widget().hide()
        for i, tile in enumerate(sorted_tiles):
            row, col = divmod(i, cols)
            self.view.gallery_layout.addWidget(tile, row, col)
            tile.show()
        
        # Ensure gallery is shown after rebuild
        self.view.stacked_layout.setCurrentIndex(0)

    def _finalize_grid_update(self, empty=False):
        if empty:
            self.view.update_gallery_placeholder("No assets in this folder.")
            self.view.stacked_layout.setCurrentIndex(1)  # Show placeholder
            self.controller.control_panel_controller.update_button_states()
            update_main_window_status(self.view)
            return
        self.view.update_gallery_placeholder("")  # Clear placeholder
        self.view.stacked_layout.setCurrentIndex(0)  # Show gallery
        self.controller.control_panel_controller.update_button_states()
        update_main_window_status(self.view)

    def _get_asset_file_path(self, asset_name: str) -> str:
        """Helper function to create the .asset file path."""
        current_folder = self.model.asset_grid_model.get_current_folder()
        if current_folder and asset_name:
            return os.path.join(current_folder, f"{asset_name}.asset")
        return ""

    def _connect_tile_signals(self, tile: AssetTileView):
        """Connects signals for a newly acquired tile."""
        try:
            tile.thumbnail_clicked.disconnect()
            tile.filename_clicked.disconnect()
            tile.checkbox_state_changed.disconnect()
        except TypeError:
            pass  # Signals were not connected

        tile.thumbnail_clicked.connect(
            lambda asset_id, asset_path, _: self.controller._handle_file_action(
                asset_path, "thumbnail"
            )
        )
        tile.filename_clicked.connect(
            lambda asset_id, asset_path, _: self.controller._handle_file_action(
                asset_path, "filename"
            )
        )
        tile.checkbox_state_changed.connect(
            lambda checked: self.controller.control_panel_controller.update_button_states()
        )

    def on_loading_state_changed(self, is_loading):
        """Handles loading state change"""
        logger.debug(f"Loading state changed: {is_loading}")
        self.drag_and_drop_enabled = not is_loading
        # Pass the flag to all asset tiles
        for tile in self.asset_tiles:
            if hasattr(tile, "set_drag_and_drop_enabled"):
                tile.set_drag_and_drop_enabled(self.drag_and_drop_enabled)

    def on_gallery_resized(self, width: int):
        """Handles gallery resize and recalculates columns"""
        logger.debug(f"Gallery resized: {width}px, tiles: {len(self.asset_tiles)}")
        thumb_size = self.model.control_panel_model.get_thumbnail_size()
        self.model.asset_grid_model.request_recalculate_columns(width, thumb_size)
        # Update button states after gallery resize
        self.controller.control_panel_controller.update_button_states()

    def on_thumbnail_size_changed(self, size: int):
        """Handles thumbnail size change."""
        logger.debug(f"Controller: Thumbnail size changed to {size}")
        gallery_width = self.view.gallery_container_widget.width()
        # Just request a column recalculation with the new size.
        # Tile updates will happen in on_recalculate_columns_requested.
        self.model.asset_grid_model.request_recalculate_columns(gallery_width, size)

    def on_recalculate_columns_requested(
        self, available_width: int, thumbnail_size: int
    ):
        """Handles column recalculation request, rearranging existing widgets."""
        logger.debug("Rearranging layout due to size or settings change.")
        cols = self.model.asset_grid_model.get_columns()

        # Collect all widgets from the current layout
        widgets = []
        while self.view.gallery_layout.count() > 0:
            item = self.view.gallery_layout.takeAt(0)
            if item and item.widget():
                widgets.append(item.widget())

        # Add them back in the new configuration
        for i, widget in enumerate(widgets):
            # Size update might be needed
            widget.update_thumbnail_size(thumbnail_size)
            row, col = divmod(i, cols)
            self.view.gallery_layout.addWidget(widget, row, col)

        self.controller.control_panel_controller.update_button_states()

    def clear_asset_tiles(self):
        """OPTIMIZATION: Returns all active tiles to the pool and clears the gallery layout."""
        try:
            logger.debug(f"OPTIMIZATION: Returning {len(self.asset_tiles)} tiles to the pool")
            
            # Validate tile_pool availability
            if not hasattr(self, 'tile_pool'):
                logger.warning("OPTIMIZATION: No tile_pool - skipping returning tiles")
                self.asset_tiles.clear()
                return
            
            # Clear the gallery layout first
            while self.view.gallery_layout.count():
                item = self.view.gallery_layout.takeAt(0)
                if item.widget():
                    item.widget().hide()
            
            # Return tiles to pool
            for tile_view in self.asset_tiles:
                # Check if the tile is not already in the pool
                if hasattr(tile_view, 'isVisible') and tile_view.isVisible():
                    self.tile_pool.release(tile_view)
                
            self.asset_tiles.clear()
            logger.debug("OPTIMIZATION: All tiles returned to the pool and layout cleared")
            
        except Exception as e:
            logger.error(f"Error while returning tiles to the pool: {e}")
            # Fallback - clear the list even if an error occurred
            self.asset_tiles.clear()

    def get_asset_tiles(self):
        """Returns the list of asset tiles"""
        return self.asset_tiles

    def set_original_assets(self, assets):
        """Sets the original list of assets (unfiltered)"""
        self.original_assets = assets.copy() if assets else []
        logger.debug(
            f"AssetGridController: Original assets set to {len(self.original_assets)} items."
        )

    def get_original_assets(self):
        """Returns the original list of assets (unfiltered)"""
        logger.debug(
            f"AssetGridController: get_original_assets called. Returning {len(self.original_assets)} items."
        )
        return self.original_assets

    def set_star_filter(self, min_stars: int):
        """Sets the active star filter"""
        self.active_star_filter = min_stars
        logger.debug(f"Set star filter: {min_stars}")

    def clear_star_filter(self):
        """Clears the star filter"""
        self.active_star_filter = 0
        logger.debug("Cleared star filter")
