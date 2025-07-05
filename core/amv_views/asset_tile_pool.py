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
        logger.info("AssetTilePool zainicjalizowany.")

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
            logger.debug("Pozyskano kafelek z puli.")
            # Zaktualizuj istniejący kafelek nowymi danymi
            tile.update_asset_data(tile_model, tile_number, total_tiles)
            return tile
        else:
            logger.debug("Pula jest pusta, tworzenie nowego kafelka.")
            # Pula jest pusta, utwórz nowy kafelek
            tile = AssetTileView(
                tile_model=tile_model,
                thumbnail_size=thumbnail_size,
                tile_number=tile_number,
                total_tiles=total_tiles,
                selection_model=self._selection_model,
            )
            # NAPRAWIONO: Ustaw rodzica dla nowego kafelka!
            if self._parent_widget:
                tile.setParent(self._parent_widget)
            return tile

    def release(self, tile: AssetTileView):
        """
        Returns the tile to the pool so it can be reused.
        """
        if tile:
            tile.hide()  # Ukryj widget, zamiast go niszczyć
            # NAPRAWIONO: Ustaw właściwego rodzica zamiast None
            if self._parent_widget:
                tile.setParent(self._parent_widget)  # Ustaw właściwego rodzica
            self._pool.append(tile)
            logger.debug(
                f"Zwrócono kafelek {tile.asset_id} do puli. "
                f"Rozmiar puli: {len(self._pool)}"
            )

    def clear(self):
        """
        Permanently removes all tiles from the pool.
        Called when closing the application to free memory.
        """
        for tile in self._pool:
            tile.deleteLater()
        self._pool.clear()
        logger.info("Pula kafelków została wyczyszczona.")
