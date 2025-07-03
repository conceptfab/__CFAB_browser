"""
AssetGridController - Kontroler zarządzający siatką assetów
Odpowiedzialny za tworzenie, przebudowę i aktualizację siatki kafelków assetów.
"""

import logging
import os

from PyQt6.QtCore import QObject

from core.amv_models.asset_tile_model import AssetTileModel
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

        # Przeniesione z AmvController
        self.asset_tiles = []  # Lista kafelków
        self.original_assets = (
            []
        )  # Przechowuje oryginalną listę assetów (bez filtrowania)

        self.active_star_filter = 0  # 0 = brak filtra, 1-5 = filtr gwiazdek

    def setup(self):
        """Inicjalizuje siatkę assetów"""
        logger.debug("Asset grid model connected to view - ETAP 9")

    def on_assets_changed(self, assets):
        """Obsługuje zmianę listy assetów"""
        logger.debug(f"Assets changed: {len(assets)} items")
        self.rebuild_asset_grid(assets)
        # Aktualizuj stan przycisków po zmianie assetów
        self.controller.control_panel_controller.update_button_states()

    def rebuild_asset_grid(self, assets: list, preserve_filter: bool = True):
        """
        Przebudowuje siatkę kafelków na podstawie listy assetów

        Args:
            assets: Lista assetów do wyświetlenia
            preserve_filter: Czy zachować aktywny filtr (domyślnie True)
        """
        with measure_operation(
            "asset_grid_controller.rebuild_asset_grid", {"assets_count": len(assets)}
        ):
            self.clear_asset_tiles()

            if preserve_filter and self.active_star_filter > 0:
                # Deleguj filtrowanie do control_panel_controller
                filtered_assets = (
                    self.controller.control_panel_controller._filter_by_star_rating(
                        assets, self.active_star_filter
                    )
                )
                logger.debug(
                    f"Zachowuję filtr gwiazdek {self.active_star_filter}, przefiltrowane assety: {len(filtered_assets)}"
                )
            else:
                filtered_assets = assets
                logger.debug(
                    f"Bez filtrowania, wszystkie assety: {len(filtered_assets)}"
                )

            if not filtered_assets:
                self.view.update_gallery_placeholder(
                    "Nie znaleziono assetów w tym folderze."
                    if not preserve_filter or self.active_star_filter == 0
                    else f"Brak assetów z {self.active_star_filter}+ gwiazdkami."
                )
                return

            self.view.update_gallery_placeholder("")

            cols = self.model.asset_grid_model.get_columns()
            thumb_size = self.model.control_panel_model.get_thumbnail_size()
            rows = (len(filtered_assets) + cols - 1) // cols if cols > 0 else 0
            logger.debug(
                "rebuild_asset_grid: Rebuilding with %d cols, %d rows.",
                cols,
                rows,
            )
            self.view.placeholder_label.hide()

            # Użyj przefiltrowanych assetów do budowy galerii
            for i, asset_stub in enumerate(filtered_assets):
                asset_data = None
                asset_name = asset_stub.get("name")

                if asset_stub.get("is_stub"):
                    asset_data = self.model.asset_grid_model.get_asset_data_lazy(
                        asset_name
                    )
                    if not asset_data:
                        logger.warning(f"Could not lazy load asset: {asset_name}")
                        continue
                else:
                    asset_data = asset_stub

                row, col = divmod(i, cols)
                asset_file_path = None
                if asset_data.get("type") != "special_folder":
                    current_folder = self.model.asset_grid_model.get_current_folder()
                    if current_folder and asset_name:
                        asset_file_path = os.path.join(
                            current_folder, f"{asset_name}.asset"
                        )

                tile_model = AssetTileModel(asset_data, asset_file_path)
                tile_view = self.create_asset_tile(
                    tile_model, thumb_size, i + 1, len(filtered_assets)
                )

                self.view.gallery_layout.addWidget(tile_view, row, col)
                self.asset_tiles.append(tile_view)
                tile_view.show()

                tile_view.thumbnail_clicked.connect(
                    self.controller._on_tile_thumbnail_clicked
                )
                tile_view.filename_clicked.connect(
                    self.controller._on_tile_filename_clicked
                )

            self.view.gallery_container_widget.update()
            self.view.gallery_container_widget.repaint()
            self.view.scroll_area.viewport().update()
            self.view.stacked_layout.setCurrentIndex(0)

            # Naprawa: aktualizuj asset_tiles po przebudowie siatki
            logger.debug(f"Asset grid rebuilt with {len(self.asset_tiles)} tiles.")

            # Aktualizuj stan przycisków po przebudowie siatki
            self.controller.control_panel_controller.update_button_states()

    def on_loading_state_changed(self, is_loading):
        """Obsługuje zmianę stanu ładowania"""
        logger.debug(f"Loading state changed: {is_loading}")
        # W przyszłości tutaj będzie obsługa wizualna ładowania

    def on_gallery_resized(self, width: int):
        """Obsługuje zmianę rozmiaru galerii i przelicza kolumny"""
        logger.debug(f"Controller: Gallery resized to {width}px")
        thumb_size = self.model.control_panel_model.get_thumbnail_size()
        self.model.asset_grid_model.request_recalculate_columns(width, thumb_size)
        # Aktualizuj stan przycisków po zmianie rozmiaru galerii
        self.controller.control_panel_controller.update_button_states()

    def on_thumbnail_size_changed(self, size: int):
        """Obsługuje zmianę rozmiaru miniatur i aktualizuje kafelki"""
        logger.debug(f"Controller: Thumbnail size changed to {size}")
        for tile in self.asset_tiles:
            tile.update_thumbnail_size(size)
        gallery_width = self.view.gallery_container_widget.width()
        self.model.asset_grid_model.request_recalculate_columns(gallery_width, size)
        # Aktualizuj stan przycisków po zmianie rozmiaru miniatur
        self.controller.control_panel_controller.update_button_states()

    def on_recalculate_columns_requested(
        self, available_width: int, thumbnail_size: int
    ):
        """Obsługuje żądanie przeliczenia kolumn z AssetGridModel"""
        # Model już przeliczył kolumny w _perform_recalculate_columns
        cols = self.model.asset_grid_model.get_columns()
        logger.debug(
            "Controller: Columns recalculated to %d (width: %d, thumb: %d)",
            cols,
            available_width,
            thumbnail_size,
        )

        # ZMIANA: Nie przebudowuj całej galerii - kafelki mają stały rozmiar
        # Tylko zaktualizuj układ jeśli potrzeba
        current_assets = self.model.asset_grid_model.get_assets()
        if current_assets:
            self.rebuild_asset_grid(current_assets, preserve_filter=True)

        # Aktualizuj stan przycisków po przeliczeniu kolumn
        self.controller.control_panel_controller.update_button_states()

    def on_grid_layout_changed(self):
        """Obsługuje zmianę układu siatki"""
        logger.debug("AssetGridController: Grid layout changed")
        self.rebuild_asset_grid(
            self.model.asset_grid_model.get_assets(), preserve_filter=True
        )

        # Można dodać dodatkowe logiki dotyczące zmiany układu siatki
        # np. aktualizację widoku, przeliczanie kolumn, itp.
        logger.debug("AssetGridController: Grid layout changed - end")

        # Aktualizuj stan przycisków po zmianie układu siatki
        self.controller.control_panel_controller.update_button_states()

    def create_asset_tile(
        self,
        tile_model: AssetTileModel,
        thumbnail_size: int,
        tile_number: int,
        total_tiles: int,
    ) -> AssetTileView:
        """Tworzy nowy kafelek assetu"""
        tile_view = AssetTileView(
            tile_model,
            thumbnail_size,
            tile_number,
            total_tiles,
            self.model.selection_model,
        )
        return tile_view

    def clear_asset_tiles(self):
        """Usuwa wszystkie kafelki assetów"""
        for tile_view in self.asset_tiles:
            try:
                if tile_view:
                    tile_view.release_resources()
                    tile_view.deleteLater()
            except RuntimeError:
                continue
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
