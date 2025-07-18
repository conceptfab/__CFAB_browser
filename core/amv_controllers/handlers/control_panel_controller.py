"""
ControlPanelController - Controller for managing the control panel.
Responsible for handling buttons, filtering, and asset selection.
"""

import logging
import os

from PyQt6.QtCore import QObject, QTimer

from core.utilities import update_main_window_status

logger = logging.getLogger(__name__)


class ControlPanelController(QObject):
    """Controller for managing the control panel"""

    def __init__(self, model, view, controller):
        super().__init__()
        self.model = model
        self.view = view
        self.controller = controller
        
        # Debouncing timer for update_button_states
        self._update_button_states_timer = QTimer()
        self._update_button_states_timer.setSingleShot(True)
        self._update_button_states_timer.timeout.connect(self._perform_update_button_states)

    def setup(self):
        """Initializes the control panel"""
        logger.debug("Control panel controller initialized")

    def on_select_all_clicked(self):
        """Handles the 'Select All' button click."""
        logger.debug("Controller: Select all clicked")

        # Get only the assets that are currently displayed (filtered)
        visible_asset_ids = []
        asset_tiles = self.controller.asset_grid_controller.get_asset_tiles()
        for tile in asset_tiles:
            if not tile.model.is_special_folder:
                asset_id = tile.asset_id
                if asset_id:
                    visible_asset_ids.append(asset_id)
                    # Check if the asset is not already selected before adding
                    if (
                        asset_id
                        not in self.model.selection_model.get_selected_asset_ids()
                    ):
                        self.model.selection_model.add_selection(asset_id)

        # Visually update all tiles
        for tile in asset_tiles:
            if not tile.model.is_special_folder:
                tile.set_checked(True)

        logger.debug(f"Selected all visible assets ({len(visible_asset_ids)})")

        # Update button states after selecting all
        self.update_button_states()

        # ADDED: Force status bar update
        update_main_window_status(self.view)

    def on_deselect_all_clicked(self):
        """Handles the 'Deselect All' button click."""
        if self.model.selection_model.get_selected_asset_ids():
            self.model.selection_model.clear_selection()
            logger.debug("Deselect all button clicked, selection cleared.")

            # Visually update all tiles
            asset_tiles = self.controller.asset_grid_controller.get_asset_tiles()
            for tile in asset_tiles:
                if not tile.model.is_special_folder:
                    tile.set_checked(False)

            # Update button states
            self.update_button_states()

            # ADDED: Force status bar update
            update_main_window_status(self.view)

    def on_selection_changed(self, selected_asset_ids: list):
        """Handles selection changes in SelectionModel and updates ControlPanelModel."""
        has_selection = len(selected_asset_ids) > 0
        self.model.control_panel_model.set_has_selection(has_selection)
        # Update button states after selection change
        self.update_button_states()

    def update_button_states(self):
        """Updates the state of all control buttons with debouncing."""
        # Use debouncing to prevent excessive updates
        self._update_button_states_timer.start(50)  # 50ms delay
        
    def _perform_update_button_states(self):
        """Performs the actual button state update."""
        selected_count = len(self.model.selection_model.get_selected_asset_ids())

        # Count only visible assets (excluding special folders)
        visible_assets_count = 0
        asset_tiles = self.controller.asset_grid_controller.get_asset_tiles()
        for tile in asset_tiles:
            if not tile.model.is_special_folder:
                visible_assets_count += 1

        has_any_selection = selected_count > 0
        has_working_folder = bool(self.model.asset_grid_model.get_current_folder())

        # Update button states
        self.view.move_selected_button.setEnabled(has_any_selection)
        self.view.delete_selected_button.setEnabled(has_any_selection)
        self.view.deselect_all_button.setEnabled(has_any_selection)
        # 'Select All' button is active only when a folder is selected and there are assets
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
        """Updates button states based on selection."""
        self.update_button_states()

    def on_star_filter_clicked(self, star_rating: int):
        """Handles clicking on a filter star in the control panel"""
        logger.info(f"=== STAR FILTERING: Clicked star {star_rating} ===")
        if not hasattr(self.view, "star_checkboxes") or not self.view.star_checkboxes:
            logger.error("ERROR: self.view.star_checkboxes does not exist!")
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
            self.filter_assets()
            logger.info("Deselected all stars - showing all assets")
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
            self.filter_assets()
            logger.info(f"Selected {star_rating} stars - filtering")
        logger.info("=== END OF STAR FILTERING ===")

    def filter_assets(self):
        """Filters assets by stars and text at once."""
        min_stars = self.controller.asset_grid_controller.active_star_filter
        text = self.view.text_input.text().strip().lower() if hasattr(self.view, 'text_input') else ''
        original_assets = self.controller.asset_grid_controller.get_original_assets()
        filtered_assets = []
        for asset in original_assets:
            if asset.get("type") == "special_folder":
                filtered_assets.append(asset)
                continue
            stars = asset.get("stars") or 0
            name = asset.get("name", "")
            name_no_ext = os.path.splitext(name)[0].lower()
            if (min_stars == 0 or stars >= min_stars) and (not text or text in name_no_ext):
                filtered_assets.append(asset)
        self.controller.asset_grid_controller.rebuild_asset_grid(filtered_assets)
