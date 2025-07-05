import logging

logger = logging.getLogger(__name__)


class SignalConnector:
    def __init__(self, model, view, controller, main_window=None):
        self.model = model
        self.view = view
        self.controller = controller
        self.main_window = main_window

    def connect_all(self):
        # Get references to sub-controllers
        asset_grid_controller = self.controller.asset_grid_controller
        control_panel_controller = self.controller.control_panel_controller

        # --- Basic UI signals ---
        self.view.splitter_moved.connect(self.model.set_splitter_sizes)
        self.view.toggle_panel_requested.connect(self.model.toggle_left_panel)
        self.model.splitter_state_changed.connect(
            self.controller._on_splitter_state_changed
        )
        self.view.gallery_viewport_resized.connect(
            asset_grid_controller.on_gallery_resized
        )

        # --- Folder model signals ---
        folder_controller = self.controller.folder_tree_controller
        self.model.folder_system_model.folder_clicked.connect(
            folder_controller.on_folder_clicked
        )
        self.model.folder_system_model.folder_structure_updated.connect(
            folder_controller.on_folder_structure_changed
        )
        self.model.workspace_folders_model.folders_updated.connect(
            self.view.update_workspace_folder_buttons
        )
        self.view.workspace_folder_clicked.connect(
            folder_controller.on_workspace_folder_clicked
        )

        # --- Asset grid model signals ---
        asset_grid_controller = self.controller.asset_grid_controller
        self.model.asset_grid_model.assets_changed.connect(
            asset_grid_controller.on_assets_changed
        )
        self.model.asset_grid_model.loading_state_changed.connect(
            asset_grid_controller.on_loading_state_changed
        )

        # --- Control panel signals ---
        if self.main_window is not None:
            self.model.control_panel_model.progress_changed.connect(
                self.main_window.status_progress_bar.setValue
            )
        self.model.control_panel_model.thumbnail_size_changed.connect(
            asset_grid_controller.on_thumbnail_size_changed
        )
        self.view.thumbnail_size_slider.valueChanged.connect(
            self.model.control_panel_model.set_thumbnail_size
        )
        self.model.control_panel_model.selection_state_changed.connect(
            control_panel_controller.on_control_panel_selection_state_changed
        )

        self.view.select_all_button.clicked.connect(
            control_panel_controller.on_select_all_clicked
        )
        self.view.deselect_all_button.clicked.connect(
            control_panel_controller.on_deselect_all_clicked
        )
        self.view.move_selected_button.clicked.connect(
            self.controller.file_operation_controller.on_move_selected_clicked
        )
        self.view.delete_selected_button.clicked.connect(
            self.controller.file_operation_controller.on_delete_selected_clicked
        )

        # --- Star signals from the control panel ---
        for i, star_cb in enumerate(self.view.star_checkboxes):
            star_cb.setAutoExclusive(False)
            # Make sure we have the correct objectName
            star_cb.setObjectName(f"ControlPanelStar_{i+1}")
            star_cb.clicked.connect(
                lambda checked, star_index=i: control_panel_controller.on_star_filter_clicked(
                    star_index + 1
                )
            )

        # --- Text filter signal connection ---
        # Połącz sygnał filtra tekstowego
        if hasattr(self.view, 'text_input') and self.view.text_input:
            self.view.text_input.textChanged.connect(
                lambda: control_panel_controller.filter_assets()
            )

        # --- AssetGridModel signals for grid rebuild ---
        self.model.asset_grid_model.recalculate_columns_requested.connect(
            asset_grid_controller.on_recalculate_columns_requested
        )

        # --- Asset rebuild signals ---
        # Signals from the asset rebuild worker
        # (progress, finished, error) are connected in AssetRebuildController

        # --- Scan signals ---
        self.model.asset_grid_model.scan_started.connect(
            self.controller._on_scan_started
        )
        self.model.asset_grid_model.scan_progress.connect(
            self.controller._on_scan_progress
        )
        self.model.asset_grid_model.scan_completed.connect(
            self.controller._on_scan_completed
        )
        self.model.asset_grid_model.scan_error.connect(self.controller._on_scan_error)

        # --- Configuration signals ---
        self.model.config_manager.config_loaded.connect(
            self.controller._on_config_loaded
        )
        self.model.state_initialized.connect(self.controller._on_state_initialized)

        # --- SelectionModel signals ---
        self.model.selection_model.selection_changed.connect(
            control_panel_controller.on_selection_changed
        )

        # --- FileOperationsModel signals ---
        self.model.file_operations_model.operation_progress.connect(
            self.controller.file_operation_controller.on_file_operation_progress
        )
        self.model.file_operations_model.operation_completed.connect(
            self.controller.file_operation_controller.on_file_operation_completed
        )
        self.model.file_operations_model.operation_error.connect(
            self.controller.file_operation_controller.on_file_operation_error
        )

        # --- DragDropModel signals ---
        self.model.drag_drop_model.drag_started.connect(
            self.controller.file_operation_controller.on_drag_drop_started
        )
        self.model.drag_drop_model.drop_possible.connect(
            self.controller.file_operation_controller.on_drag_drop_possible
        )
        self.model.drag_drop_model.drop_completed.connect(
            self.controller.file_operation_controller.on_drag_drop_completed
        )

        # --- Tree expand/collapse signals ---
        folder_controller = self.controller.folder_tree_controller
        self.view.collapse_tree_requested.connect(
            folder_controller.on_collapse_tree_requested
        )
        self.view.expand_tree_requested.connect(
            folder_controller.on_expand_tree_requested
        )
