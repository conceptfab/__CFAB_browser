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

        # Pula obiektów AssetTileView
        self.tile_pool = AssetTilePool(
            self.model.selection_model, self.view.gallery_content_widget
        )

        # Przeniesione z AmvController
        self.asset_tiles = []  # Lista kafelków
        self.original_assets = (
            []
        )  # Przechowuje oryginalną listę assetów (bez filtrowania)
        self.drag_and_drop_enabled = True  # Flaga blokady D&D

        self.active_star_filter = 0  # 0 = brak filtra, 1-5 = filtr gwiazdek

    def setup(self):
        """Initializes the asset grid"""
        logger.debug("Asset grid model connected to view - STAGE 9")

    def on_assets_changed(self, assets):
        """Handles asset list changes"""
        if not assets:  # ADD check for None
            self.set_original_assets([])
            return
        self.set_original_assets(assets)
        self.rebuild_asset_grid(assets)

        # After rebuilding the grid, if a filter is active, apply it
        current_star_filter = (
            self.active_star_filter
        )  # Not self.controller.asset_grid_controller.active_star_filter
        if current_star_filter > 0:
            self.controller.control_panel_controller.filter_assets_by_stars(
                current_star_filter
            )

        # Update button states after asset change
        self.controller.control_panel_controller.update_button_states()

    def rebuild_asset_grid(self, assets: list):
        """
        Intelligently synchronizes the grid with the new asset list, minimizing
        UI operations to eliminate flickering and loading errors.
        """
        assets.sort(key=lambda x: x.get("name", "").lower())
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
            if not new_ids:
                self._finalize_grid_update(empty=True)
                return
            self._reorganize_layout(assets, current_tile_map)
            self._finalize_grid_update()

    def _prepare_asset_maps(self, assets):
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
        for asset_id in ids_to_remove:
            tile = current_tile_map.pop(asset_id)
            self.tile_pool.release(tile)
            self.asset_tiles.remove(tile)

    def _update_existing_tiles(self, assets, ids_to_update, current_tile_map):
        for i, asset in enumerate(assets):
            asset_id = asset["name"]
            if asset_id in ids_to_update:
                tile = current_tile_map[asset_id]
                tile_model = AssetTileModel(asset, self._get_asset_file_path(asset_id))
                tile.update_asset_data(tile_model, i + 1, len(assets))

    def _add_new_tiles(self, assets, ids_to_add, current_tile_map):
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
        self.view.update_gallery_placeholder("")
        cols = self.model.asset_grid_model.get_columns()
        sorted_tiles = [
            current_tile_map[asset["name"]]
            for asset in assets
            if asset["name"] in current_tile_map
        ]
        while self.view.gallery_layout.count():
            item = self.view.gallery_layout.takeAt(0)
            if item.widget():
                item.widget().hide()
        for i, tile in enumerate(sorted_tiles):
            row, col = divmod(i, cols)
            self.view.gallery_layout.addWidget(tile, row, col)
            tile.show()

    def _finalize_grid_update(self, empty=False):
        if empty:
            self.view.update_gallery_placeholder("No assets found in this folder.")
            update_main_window_status(self.view)
            return
        self.view.stacked_layout.setCurrentIndex(0)
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
            lambda asset_id, asset_path, t: self.controller._handle_file_action(
                asset_path, "thumbnail"
            )
        )
        tile.filename_clicked.connect(
            lambda asset_id, asset_path, t: self.controller._handle_file_action(
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
        """Returns all active tiles to the pool."""
        for tile_view in self.asset_tiles:
            self.tile_pool.release(tile_view)
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
