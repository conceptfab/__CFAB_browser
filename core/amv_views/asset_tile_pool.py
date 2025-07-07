"""
AssetTilePool - Manages the pool of AssetTileView objects.
"""

import logging
from typing import List

from ..amv_models.asset_tile_model import AssetTileModel
from ..amv_models.selection_model import SelectionModel
from .asset_tile_view import AssetTileView

logger = logging.getLogger(__name__)


class AssetTilePool:
    """
    Manages the pool of AssetTileView objects to avoid costly creation
    and destruction of widgets. Implements the Object Pooling pattern.
    """

    def __init__(self, selection_model: SelectionModel, parent_widget=None):
        self._pool: List[AssetTileView] = []
        self._selection_model = selection_model
        self._parent_widget = parent_widget
        logger.info("AssetTilePool initialized.")

    def acquire(
        self,
        tile_model: AssetTileModel,
        thumbnail_size: int,
        tile_number: int,
        total_tiles: int,
    ) -> AssetTileView:
        """
        Acquires a tile from the pool or creates a new one if the pool is empty.
        """
        if self._pool:
            tile = self._pool.pop()
            logger.debug("Tile acquired from pool.")
            # Update existing tile with new data
            tile.update_asset_data(tile_model, tile_number, total_tiles)
            return tile
        else:
            logger.debug("Pool is empty, creating new tile.")
            # Pool is empty, create new tile
            tile = AssetTileView(
                tile_model=tile_model,
                thumbnail_size=thumbnail_size,
                tile_number=tile_number,
                total_tiles=total_tiles,
                selection_model=self._selection_model,
            )
            # FIXED: Set parent for new tile!
            if self._parent_widget:
                tile.setParent(self._parent_widget)
            return tile

    def release(self, tile: AssetTileView):
        """
        Returns the tile to the pool so it can be reused.
        """
        if tile:
            tile.hide()  # Hide widget, instead of destroying it
            # FIXED: Do not change parent if not necessary
            # Avoid potential memory issues by unnecessary parent changes
            if tile.parent() != self._parent_widget and self._parent_widget:
                tile.setParent(self._parent_widget)
            self._pool.append(tile)
            logger.debug(
                f"Returned tile {tile.asset_id} to pool. "
                f"Pool size: {len(self._pool)}"
            )

    def clear(self):
        """Returns all tiles to the pool."""
        for tile in self._pool:
            tile.hide()
        self._pool.clear()
        logger.info("AssetTilePool has been cleared.")
