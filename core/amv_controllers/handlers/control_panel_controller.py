"""
ControlPanelController - Kontroler zarządzający panelem kontrolnym
Odpowiedzialny za obsługę przycisków, filtrowanie, zaznaczanie assetów.
"""

import logging

from PyQt6.QtCore import QObject

logger = logging.getLogger(__name__)


class ControlPanelController(QObject):
    """Controller zarządzający panelem kontrolnym"""

    def __init__(self, model, view, controller):
        super().__init__()
        self.model = model
        self.view = view
        self.controller = controller

    def setup(self):
        """Inicjalizuje panel kontrolny"""
        logger.debug("Control panel controller initialized")

    def on_select_all_clicked(self):
        """Obsługuje kliknięcie przycisku 'Zaznacz wszystkie'."""
        logger.debug("Controller: Select all clicked")

        # Pobierz tylko te assety, które są aktualnie wyświetlane (przefiltrowane)
        visible_asset_ids = []
        asset_tiles = self.controller.asset_grid_controller.get_asset_tiles()
        for tile in asset_tiles:
            if not tile.model.is_special_folder:
                asset_id = tile.asset_id
                if asset_id:
                    visible_asset_ids.append(asset_id)
                    # Sprawdź czy asset nie jest już zaznaczony przed dodaniem
                    if (
                        asset_id
                        not in self.model.selection_model.get_selected_asset_ids()
                    ):
                        self.model.selection_model.add_selection(asset_id)

        # Aktualizuj wizualnie wszystkie kafelki
        for tile in asset_tiles:
            if not tile.model.is_special_folder:
                tile.set_checked(True)

        logger.debug(f"Zaznaczono wszystkie widoczne assety ({len(visible_asset_ids)})")

        # Aktualizuj stan przycisków po zaznaczeniu wszystkich
        self.update_button_states()

    def on_deselect_all_clicked(self):
        """Obsługuje kliknięcie przycisku 'Odznacz wszystkie'."""
        if self.model.selection_model.get_selected_asset_ids():
            self.model.selection_model.clear_selection()
            logger.debug("Deselect all button clicked, selection cleared.")

            # Aktualizuj wizualnie wszystkie kafelki
            asset_tiles = self.controller.asset_grid_controller.get_asset_tiles()
            for tile in asset_tiles:
                if not tile.model.is_special_folder:
                    tile.set_checked(False)

            # Aktualizuj stan przycisków
            self.update_button_states()

    def on_selection_changed(self, selected_asset_ids: list):
        """Obsługuje zmianę zaznaczenia w SelectionModel i aktualizuje ControlPanelModel."""
        has_selection = len(selected_asset_ids) > 0
        self.model.control_panel_model.set_has_selection(has_selection)
        # Aktualizuj stan przycisków po zmianie zaznaczenia
        self.update_button_states()

    def update_button_states(self):
        """Aktualizuje stan wszystkich przycisków kontrolnych."""
        selected_count = len(self.model.selection_model.get_selected_asset_ids())

        # Policz tylko widoczne assety (bez specjalnych folderów)
        visible_assets_count = 0
        asset_tiles = self.controller.asset_grid_controller.get_asset_tiles()
        for tile in asset_tiles:
            if not tile.model.is_special_folder:
                visible_assets_count += 1

        has_any_selection = selected_count > 0
        has_working_folder = bool(self.model.asset_grid_model.get_current_folder())

        # Aktualizuj stan przycisków
        self.view.move_selected_button.setEnabled(has_any_selection)
        self.view.delete_selected_button.setEnabled(has_any_selection)
        self.view.deselect_all_button.setEnabled(has_any_selection)
        # Przycisk "Zaznacz wszystkie" aktywny tylko gdy jest wybrany folder i są assety
        self.view.select_all_button.setEnabled(
            visible_assets_count > 0 and has_working_folder
        )

        logger.debug(
            "BUTTON STATE UPDATE: Selected: %s, Visible: %s, HasSelection: %s, HasWorkingFolder: %s",
            selected_count,
            visible_assets_count,
            has_any_selection,
            has_working_folder,
        )

    def on_control_panel_selection_state_changed(self, has_selection: bool):
        """Aktualizuje stan przycisków na podstawie zaznaczenia."""
        self.update_button_states()

    def on_star_filter_clicked(self, star_rating: int):
        """Obsługuje kliknięcie w gwiazdkę filtrowania w panelu kontrolnym"""
        logger.info(f"=== FILTROWANIE GWIAZDEK: Kliknięto gwiazdkę {star_rating} ===")
        if not hasattr(self.view, "star_checkboxes") or not self.view.star_checkboxes:
            logger.error("BŁĄD: self.view.star_checkboxes nie istnieje!")
            return

        is_clearing_filter = (
            self.controller.asset_grid_controller.active_star_filter == star_rating
        )

        if is_clearing_filter:
            for cb in self.view.star_checkboxes:
                cb.blockSignals(True)
            try:
                for i, cb in enumerate(self.view.star_checkboxes):
                    cb.setChecked(i < 0)
            finally:
                for cb in self.view.star_checkboxes:
                    cb.blockSignals(False)
            self.controller.asset_grid_controller.clear_star_filter()
            self.filter_assets_by_stars(0)
            logger.info("Odznaczono wszystkie gwiazdki - pokazano wszystkie assety")
        else:
            for cb in self.view.star_checkboxes:
                cb.blockSignals(True)
            try:
                for i, cb in enumerate(self.view.star_checkboxes):
                    cb.setChecked(i < star_rating)
            finally:
                for cb in self.view.star_checkboxes:
                    cb.blockSignals(False)
            self.controller.asset_grid_controller.set_star_filter(star_rating)
            self.filter_assets_by_stars(star_rating)
            logger.info(f"Zaznaczono {star_rating} gwiazdek - filtrowanie")
        logger.info("=== KONIEC FILTROWANIA GWIAZDEK ===")

    def filter_assets_by_stars(self, min_stars: int):
        """Filtruje assety, przebudowując siatkę z odfiltrowanymi assetami."""
        try:
            if hasattr(self.view, "star_checkboxes") and self.view.star_checkboxes:
                for cb in self.view.star_checkboxes:
                    cb.blockSignals(True)
                try:
                    for i, cb in enumerate(self.view.star_checkboxes):
                        cb.setChecked(i < min_stars)
                finally:
                    for cb in self.view.star_checkboxes:
                        cb.blockSignals(False)
            self.controller.asset_grid_controller.set_star_filter(min_stars)

            # Pobierz oryginalną, niezmodyfikowaną listę assetów
            original_assets = (
                self.controller.asset_grid_controller.get_original_assets()
            )
            if not original_assets:
                logger.debug("Brak oryginalnych assetów do filtrowania.")
                # Wyczyść siatkę, jeśli nie ma assetów
                self.controller.asset_grid_controller.rebuild_asset_grid([])
                return

            if min_stars > 0:
                # Filtruj listę, zamiast pokazywać/ukrywać kafelki
                filtered_assets = [
                    asset
                    for asset in original_assets
                    if (asset.get("stars") or 0) >= min_stars
                    or asset.get("type") == "special_folder"
                ]
                logger.debug(
                    f"Przefiltrowano {len(filtered_assets)} z {len(original_assets)} assetów dla {min_stars}+ gwiazdek."
                )
            else:
                # Jeśli filtr jest wyłączony, użyj oryginalnej listy
                filtered_assets = original_assets
                logger.debug("Filtr gwiazdek wyłączony, pokazuję wszystkie assety.")

            # Przebuduj siatkę z odfiltrowaną listą
            self.controller.asset_grid_controller.rebuild_asset_grid(
                filtered_assets, preserve_filter=False
            )

        except Exception as e:
            logger.error(f"Błąd podczas filtrowania assetów: {e}")
        finally:
            self.update_button_states()
