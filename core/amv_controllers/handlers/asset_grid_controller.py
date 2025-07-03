"""
AssetGridController - Kontroler zarządzający siatką assetów
Odpowiedzialny za tworzenie, przebudowę i aktualizację siatki kafelków assetów.
"""

import logging
import os

from PyQt6.QtCore import QObject

from core.amv_models.asset_tile_model import AssetTileModel
from core.amv_views.asset_tile_pool import AssetTilePool
from core.performance_monitor import measure_operation

from ...amv_views.asset_tile_view import AssetTileView

logger = logging.getLogger(__name__)


class AssetGridController(QObject):
    """Controller zarządzający siatką assetów"""

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
        """Inicjalizuje siatkę assetów"""
        logger.debug("Asset grid model connected to view - ETAP 9")

    def on_assets_changed(self, assets):
        """Obsługuje zmianę listy assetów"""
        if not assets:  # DODAJ sprawdzenie None
            self.set_original_assets([])
            return
        self.set_original_assets(assets)
        self.rebuild_asset_grid(assets, preserve_filter=False)

        # Po przebudowie siatki, jeśli jest aktywny filtr, zastosuj go
        current_star_filter = self.active_star_filter  # Nie self.controller.asset_grid_controller.active_star_filter
        if current_star_filter > 0:
            self.controller.control_panel_controller.filter_assets_by_stars(
                current_star_filter
            )

        # Aktualizuj stan przycisków po zmianie assetów
        self.controller.control_panel_controller.update_button_states()

    def rebuild_asset_grid(self, assets: list, preserve_filter: bool = True):
        """
        Inteligentnie synchronizuje siatkę z nową listą assetów, minimalizując
        operacje na UI, aby wyeliminować migotanie i błędy ładowania.
        """
        # Sortuj listę assetów alfabetycznie (A-Z)
        assets.sort(key=lambda x: x.get("name", "").lower())

        with measure_operation(
            "asset_grid_controller.rebuild_asset_grid", {"assets_count": len(assets)}
        ):
            # --- Krok 1: Przygotowanie danych ---
            new_asset_map = {asset["name"]: asset for asset in assets}
            current_tile_map = {tile.asset_id: tile for tile in self.asset_tiles}

            new_ids = set(new_asset_map.keys())
            current_ids = set(current_tile_map.keys())

            # --- Krok 2: Identyfikacja zmian ---
            ids_to_remove = current_ids - new_ids
            ids_to_add = new_ids - current_ids
            ids_to_update = current_ids.intersection(new_ids)

            # --- Krok 3: Zastosowanie zmian ---
            # Usuń niepotrzebne kafelki
            for asset_id in ids_to_remove:
                tile = current_tile_map.pop(asset_id)
                self.tile_pool.release(tile)
                self.asset_tiles.remove(tile)

            # Zaktualizuj istniejące kafelki
            for i, asset_id in enumerate(ids_to_update):
                tile = current_tile_map[asset_id]
                asset_data = new_asset_map[asset_id]
                tile_model = AssetTileModel(
                    asset_data, self._get_asset_file_path(asset_id)
                )
                tile.update_asset_data(tile_model, i + 1, len(assets))

            # Dodaj nowe kafelki
            thumb_size = self.model.control_panel_model.get_thumbnail_size()
            for i, asset_id in enumerate(ids_to_add):
                asset_data = new_asset_map[asset_id]
                tile_model = AssetTileModel(
                    asset_data, self._get_asset_file_path(asset_id)
                )
                tile = self.tile_pool.acquire(
                    tile_model, thumb_size, i + 1, len(assets)
                )
                self._connect_tile_signals(tile)
                self.asset_tiles.append(tile)
                current_tile_map[asset_id] = tile

            # --- Krok 4: Przeorganizowanie layoutu ---
            if not new_ids:
                self.view.update_gallery_placeholder(
                    "Nie znaleziono assetów w tym folderze."
                )
                return

            self.view.update_gallery_placeholder("")
            cols = self.model.asset_grid_model.get_columns()

            # Sortowanie kafelków zgodnie z nową listą assetów
            sorted_tiles = [
                current_tile_map[asset["name"]]
                for asset in assets
                if asset["name"] in current_tile_map
            ]

            # Usuń wszystkie widgety z layoutu (bez niszczenia ich)
            while self.view.gallery_layout.count():
                item = self.view.gallery_layout.takeAt(0)
                if item.widget():
                    item.widget().hide()

            # Dodaj posortowane kafelki z powrotem do layoutu
            for i, tile in enumerate(sorted_tiles):
                row, col = divmod(i, cols)
                self.view.gallery_layout.addWidget(tile, row, col)
                tile.show()

            # --- Krok 5: Finalizacja ---
            self.view.stacked_layout.setCurrentIndex(0)
            self.controller.control_panel_controller.update_button_states()

    def _get_asset_file_path(self, asset_name: str) -> str:
        """Pomocnicza funkcja do tworzenia ścieżki pliku .asset."""
        current_folder = self.model.asset_grid_model.get_current_folder()
        if current_folder and asset_name:
            return os.path.join(current_folder, f"{asset_name}.asset")
        return ""

    def _connect_tile_signals(self, tile: AssetTileView):
        """Łączy sygnały dla nowo pozyskanego kafelka."""
        try:
            tile.thumbnail_clicked.disconnect()
            tile.filename_clicked.disconnect()
        except TypeError:
            pass  # Sygnały nie były połączone

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

    def on_loading_state_changed(self, is_loading):
        """Obsługuje zmianę stanu ładowania"""
        logger.debug(f"Loading state changed: {is_loading}")
        self.drag_and_drop_enabled = not is_loading
        # Przekaż flagę do wszystkich kafelków assetów
        for tile in self.asset_tiles:
            if hasattr(tile, "set_drag_and_drop_enabled"):
                tile.set_drag_and_drop_enabled(self.drag_and_drop_enabled)

    def on_gallery_resized(self, width: int):
        """Obsługuje zmianę rozmiaru galerii i przelicza kolumny"""
        logger.debug(f"Gallery resized: {width}px, tiles: {len(self.asset_tiles)}")
        thumb_size = self.model.control_panel_model.get_thumbnail_size()
        self.model.asset_grid_model.request_recalculate_columns(width, thumb_size)
        # Aktualizuj stan przycisków po zmianie rozmiaru galerii
        self.controller.control_panel_controller.update_button_states()

    def on_thumbnail_size_changed(self, size: int):
        """Obsługuje zmianę rozmiaru miniatur."""
        logger.debug(f"Controller: Thumbnail size changed to {size}")
        gallery_width = self.view.gallery_container_widget.width()
        # Po prostu zażądaj przeliczenia kolumn z nowym rozmiarem.
        # Aktualizacja kafelków nastąpi w on_recalculate_columns_requested.
        self.model.asset_grid_model.request_recalculate_columns(gallery_width, size)

    def on_recalculate_columns_requested(
        self, available_width: int, thumbnail_size: int
    ):
        """Obsługuje żądanie przeliczenia kolumn, re-aranżując istniejące widgety."""
        logger.debug("Przeorganizowuję layout z powodu zmiany rozmiaru lub ustawień.")
        cols = self.model.asset_grid_model.get_columns()

        # Zbierz wszystkie widgety z obecnego layoutu
        widgets = []
        while self.view.gallery_layout.count() > 0:
            item = self.view.gallery_layout.takeAt(0)
            if item and item.widget():
                widgets.append(item.widget())

        # Dodaj je z powrotem w nowej konfiguracji
        for i, widget in enumerate(widgets):
            # Aktualizacja rozmiaru może być potrzebna
            widget.update_thumbnail_size(thumbnail_size)
            row, col = divmod(i, cols)
            self.view.gallery_layout.addWidget(widget, row, col)

        self.controller.control_panel_controller.update_button_states()

    def clear_asset_tiles(self):
        """Zwraca wszystkie aktywne kafelki do puli."""
        for tile_view in self.asset_tiles:
            self.tile_pool.release(tile_view)
        self.asset_tiles.clear()

    def get_asset_tiles(self):
        """Zwraca listę kafelków assetów"""
        return self.asset_tiles

    def set_original_assets(self, assets):
        """Ustawia oryginalną listę assetów (bez filtrowania)"""
        self.original_assets = assets.copy() if assets else []
        logger.debug(
            f"AssetGridController: Original assets set to {len(self.original_assets)} items."
        )

    def get_original_assets(self):
        """Zwraca oryginalną listę assetów (bez filtrowania)"""
        logger.debug(
            f"AssetGridController: get_original_assets called. Returning {len(self.original_assets)} items."
        )
        return self.original_assets

    def set_star_filter(self, min_stars: int):
        """Ustawia aktywny filtr gwiazdek"""
        self.active_star_filter = min_stars
        logger.debug(f"Ustawiono filtr gwiazdek: {min_stars}")

    def clear_star_filter(self):
        """Czyści filtr gwiazdek"""
        self.active_star_filter = 0
        logger.debug("Wyczyszczono filtr gwiazdek")
