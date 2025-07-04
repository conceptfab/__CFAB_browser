# 📊 Raport Radon (Złożoność)

**Data generowania:** 2025-07-05 01:19:09

---

## Złożoność Cyklomatyczna (CC)

```text
core\amv_tab.py
    C 19:0 AmvTab - A
    M 25:4 AmvTab.__init__ - A
    M 48:4 AmvTab.get_controller - A
core\base_widgets.py
    C 19:0 BaseFrame - A
    C 31:0 BaseLabel - A
    C 43:0 BaseButton - A
    C 55:0 BaseCheckBox - A
    C 67:0 BaseWidget - A
    C 79:0 TileBase - A
    C 91:0 StarCheckBoxBase - A
    C 103:0 ControlButtonBase - A
    C 115:0 PanelButtonBase - A
    M 22:4 BaseFrame.__init__ - A
    M 26:4 BaseFrame._apply_base_styles - A
    M 34:4 BaseLabel.__init__ - A
    M 38:4 BaseLabel._apply_base_styles - A
    M 46:4 BaseButton.__init__ - A
    M 50:4 BaseButton._apply_base_styles - A
    M 58:4 BaseCheckBox.__init__ - A
    M 62:4 BaseCheckBox._apply_base_styles - A
    M 70:4 BaseWidget.__init__ - A
    M 74:4 BaseWidget._apply_base_styles - A
    M 82:4 TileBase.__init__ - A
    M 86:4 TileBase._apply_tile_styles - A
    M 94:4 StarCheckBoxBase.__init__ - A
    M 98:4 StarCheckBoxBase._apply_star_styles - A
    M 106:4 ControlButtonBase.__init__ - A
    M 110:4 ControlButtonBase._apply_control_button_styles - A
    M 118:4 PanelButtonBase.__init__ - A
    M 122:4 PanelButtonBase._apply_panel_button_styles - A
core\file_utils.py
    F 16:0 open_path_in_explorer - A
    F 56:0 open_file_in_default_app - A
core\json_utils.py
    F 75:0 load_from_file - B
    F 33:0 loads - A
    F 53:0 dumps - A
    F 121:0 save_to_file - A
core\main_window.py
    M 576:4 MainWindow.closeEvent - D
    M 304:4 MainWindow.update_selection_status - D
    M 483:4 MainWindow._on_selection_changed - C
    M 531:4 MainWindow._on_assets_changed - C
    M 159:4 MainWindow._createTabs - B
    M 71:4 MainWindow._load_config_safe - B
    C 23:0 MainWindow - B
    M 278:4 MainWindow.update_working_directory_status - A
    M 443:4 MainWindow._connect_amv_signals - A
    M 113:4 MainWindow._setup_logger - A
    M 233:4 MainWindow.update_status - A
    M 248:4 MainWindow.show_log_info - A
    M 428:4 MainWindow._connect_signals - A
    M 25:4 MainWindow.__init__ - A
    M 141:4 MainWindow._createMenuBar - A
    M 219:4 MainWindow._createStatusBar - A
    M 354:4 MainWindow.show_operation_status - A
    M 377:4 MainWindow.setup_log_interceptor - A
    M 477:4 MainWindow._connect_tools_signals - A
    M 472:4 MainWindow._connect_status_signals - A
core\pairing_tab.py
    M 287:4 PairingTab._update_button_states - C
    M 319:4 PairingTab._on_create_asset_button_clicked - B
    M 177:4 PairingTab.load_data - B
    M 225:4 PairingTab._on_archive_checked - B
    M 239:4 PairingTab._on_archive_clicked - B
    C 86:0 PairingTab - A
    M 405:4 PairingTab._on_rebuild_assets_clicked - A
    M 271:4 PairingTab._remove_paired_items_from_ui - A
    M 262:4 PairingTab._on_preview_clicked - A
    M 361:4 PairingTab._on_delete_unpaired_images_clicked - A
    M 383:4 PairingTab._on_delete_unpaired_archives_clicked - A
    C 30:0 ArchiveListItem - A
    M 258:4 PairingTab._on_preview_selected - A
    M 36:4 ArchiveListItem.__init__ - A
    M 41:4 ArchiveListItem.init_ui - A
    M 57:4 ArchiveListItem.contextMenuEvent - A
    M 65:4 ArchiveListItem._on_checkbox_state_changed - A
    M 68:4 ArchiveListItem._handle_open - A
    M 72:4 ArchiveListItem.is_checked - A
    M 75:4 ArchiveListItem.set_checked - A
    M 78:4 ArchiveListItem.sizeHint - A
    M 87:4 PairingTab.__init__ - A
    M 94:4 PairingTab.on_working_directory_changed - A
    M 101:4 PairingTab.init_ui - A
    M 315:4 PairingTab._update_create_asset_button_state - A
    M 437:4 PairingTab._on_rebuild_finished - A
    M 441:4 PairingTab._on_rebuild_error - A
core\performance_monitor.py
    M 107:4 PerformanceMonitor._log_metrics - B
    M 42:4 PerformanceMetrics.finish - A
    C 83:0 PerformanceMonitor - A
    C 27:0 PerformanceMetrics - A
    M 144:4 PerformanceMonitor._get_memory_usage - A
    M 157:4 PerformanceMonitor.measure_operation - A
    F 237:0 get_performance_monitor - A
    M 101:4 PerformanceMonitor._setup_logging - A
    F 249:0 measure_operation - A
    F 256:0 measure_function - A
    M 30:4 PerformanceMetrics.__init__ - A
    M 66:4 PerformanceMetrics.to_dict - A
    M 86:4 PerformanceMonitor.__init__ - A
    M 188:4 PerformanceMonitor.measure_function - A
core\preview_window.py
    C 13:0 ImageLoader - A
    M 24:4 ImageLoader.load_image - A
    M 56:4 ImageLoader._pre_scale_pixmap - A
    M 196:4 PreviewWindow._perform_scaling - A
    M 43:4 ImageLoader.scale_image - A
    C 81:0 PreviewWindow - A
    M 119:4 PreviewWindow.load_image_and_resize - A
    M 140:4 PreviewWindow._on_image_loaded - A
    M 171:4 PreviewWindow._on_image_scaled - A
    M 176:4 PreviewWindow.load_image - A
    M 19:4 ImageLoader.__init__ - A
    M 82:4 PreviewWindow.__init__ - A
    M 99:4 PreviewWindow.setup_ui - A
    M 113:4 PreviewWindow.show_window - A
    M 188:4 PreviewWindow.resizeEvent - A
    M 202:4 PreviewWindow.closeEvent - A
core\rules.py
    M 654:4 FolderClickRules.decide_action - C
    M 231:4 FolderClickRules.analyze_folder_content - B
    M 64:4 FolderClickRules._validate_folder_path - B
    M 149:4 FolderClickRules._categorize_file - B
    M 180:4 FolderClickRules._analyze_cache_folder - B
    C 29:0 FolderClickRules - A
    M 116:4 FolderClickRules._get_cached_analysis - A
    M 97:4 FolderClickRules._is_cache_valid - A
    M 333:4 FolderClickRules._log_folder_analysis - A
    M 616:4 FolderClickRules._handle_default_case - A
    M 136:4 FolderClickRules._cache_analysis - A
    M 210:4 FolderClickRules._create_error_result - A
    M 350:4 FolderClickRules._handle_condition_1 - A
    M 383:4 FolderClickRules._handle_condition_2a - A
    M 417:4 FolderClickRules._handle_condition_2b - A
    M 458:4 FolderClickRules._handle_condition_2c - A
    M 499:4 FolderClickRules._handle_additional_case_no_cache - A
    M 533:4 FolderClickRules._handle_additional_case_mismatch - A
    M 575:4 FolderClickRules._handle_additional_case_ready - A
core\scanner.py
    M 174:4 AssetRepository._create_single_asset - C
    M 106:4 AssetRepository._check_texture_folders_presence - B
    M 271:4 AssetRepository.create_thumbnail_for_asset - B
    M 474:4 AssetRepository.load_existing_assets - B
    M 40:4 AssetRepository._get_files_by_extensions - B
    C 19:0 AssetRepository - A
    M 440:4 AssetRepository._create_assets_from_groups - A
    M 325:4 AssetRepository._create_unpair_files_json - A
    M 61:4 AssetRepository._scan_folder_for_files - A
    M 151:4 AssetRepository._scan_for_named_folders - A
    M 375:4 AssetRepository.find_and_create_assets - A
    M 31:4 AssetRepository._handle_error - A
    M 147:4 AssetRepository._validate_folder_path_static - A
    M 427:4 AssetRepository._scan_and_group_files - A
    M 27:4 AssetRepository.__init__ - A
    M 169:4 AssetRepository._scan_for_special_folders - A
    M 267:4 AssetRepository._get_file_size_mb - A
core\thumbnail.py
    M 52:4 ThumbnailGenerator.generate_thumbnail - B
    C 39:0 ThumbnailGenerator - A
    M 111:4 ThumbnailGenerator._is_thumbnail_current - A
    M 123:4 ThumbnailGenerator._resize_to_square - A
    F 158:0 get_config - A
    F 175:0 get_generator - A
    F 184:0 generate_thumbnail - A
    M 42:4 ThumbnailGenerator.__init__ - A
core\thumbnail_cache.py
    C 15:0 ThumbnailCache - A
    M 23:4 ThumbnailCache.__new__ - A
    M 62:4 ThumbnailCache.put - A
    M 30:4 ThumbnailCache.__init__ - A
    M 44:4 ThumbnailCache.get - A
    M 87:4 ThumbnailCache._evict_oldest - A
    M 100:4 ThumbnailCache.clear - A
    M 106:4 ThumbnailCache.get_current_size_mb - A
core\tools_tab.py
    M 523:4 FileRenamerWorker._perform_renaming - C
    M 733:4 PrefixSuffixRemoverWorker._run_operation - C
    M 1163:4 ToolsTab.closeEvent - C
    M 614:4 FileRenamerWorker._analyze_files - C
    M 122:4 WebPConverterWorker._run_operation - B
    C 722:0 PrefixSuffixRemoverWorker - B
    M 297:4 ImageResizerWorker._run_operation - B
    C 113:0 WebPConverterWorker - B
    M 239:4 WebPConverterWorker._convert_to_webp - B
    M 1021:4 ToolsTab.scan_working_directory - B
    M 1127:4 ToolsTab._update_button_states - B
    M 1230:4 ToolsTab._on_archive_double_clicked - B
    M 1254:4 ToolsTab._on_preview_double_clicked - B
    M 1463:4 ToolsTab._show_pairs_dialog - B
    C 288:0 ImageResizerWorker - B
    M 440:4 ImageResizerWorker._calculate_new_size - B
    C 476:0 FileRenamerWorker - B
    M 215:4 WebPConverterWorker._find_files_to_convert - A
    M 365:4 ImageResizerWorker._find_files_to_resize - A
    M 393:4 ImageResizerWorker._resize_image - A
    M 494:4 FileRenamerWorker._run_operation - A
    M 1334:4 ToolsTab._on_remove_clicked - A
    M 84:4 BaseWorker.run - A
    C 822:0 ToolsTab - A
    M 843:4 ToolsTab._validate_working_directory - A
    M 1098:4 ToolsTab._get_image_resolution - A
    C 33:0 WorkerManager - A
    C 72:0 BaseWorker - A
    M 695:4 FileRenamerWorker._rename_file - A
    M 892:4 ToolsTab._start_operation_with_confirmation - A
    M 1002:4 ToolsTab.set_working_directory - A
    M 1301:4 ToolsTab._on_file_renaming_clicked - A
    M 37:4 WorkerManager.handle_progress - A
    M 44:4 WorkerManager.handle_finished - A
    M 65:4 WorkerManager.reset_button_state - A
    M 104:4 BaseWorker.stop - A
    M 862:4 ToolsTab._handle_worker_lifecycle - A
    M 1078:4 ToolsTab._update_archive_list - A
    M 1086:4 ToolsTab._update_preview_list - A
    M 1422:4 ToolsTab._start_remove - A
    M 58:4 WorkerManager.handle_error - A
    M 79:4 BaseWorker.__init__ - A
    M 98:4 BaseWorker._run_operation - A
    M 119:4 WebPConverterWorker.__init__ - A
    M 294:4 ImageResizerWorker.__init__ - A
    M 484:4 FileRenamerWorker.__init__ - A
    M 490:4 FileRenamerWorker.confirm_operation - A
    M 685:4 FileRenamerWorker._generate_random_name - A
    M 728:4 PrefixSuffixRemoverWorker.__init__ - A
    M 828:4 ToolsTab.__init__ - A
    M 929:4 ToolsTab._setup_ui - A
    M 1122:4 ToolsTab.clear_lists - A
    M 1145:4 ToolsTab._handle_worker_progress - A
    M 1150:4 ToolsTab._handle_worker_finished - A
    M 1155:4 ToolsTab._handle_worker_error - A
    M 1160:4 ToolsTab._reset_button_state - A
    M 1196:4 ToolsTab._on_webp_conversion_clicked - A
    M 1216:4 ToolsTab._on_rebuild_assets_clicked - A
    M 1280:4 ToolsTab._on_image_resizing_clicked - A
    M 1319:4 ToolsTab._start_file_renaming - A
    M 1516:4 ToolsTab.clear_working_directory - A
core\utilities.py
    F 34:0 update_main_window_status - A
    F 11:0 get_file_size_mb - A
core\amv_controllers\amv_controller.py
    M 132:4 AmvController._handle_file_action - B
    C 21:0 AmvController - A
    M 74:4 AmvController._on_splitter_state_changed - A
    M 96:4 AmvController._on_scan_progress - A
    M 27:4 AmvController.__init__ - A
    M 68:4 AmvController._connect_signals - A
    M 81:4 AmvController._on_config_loaded - A
    M 85:4 AmvController._on_state_initialized - A
    M 89:4 AmvController._on_scan_started - A
    M 104:4 AmvController._on_scan_completed - A
    M 125:4 AmvController._on_scan_error - A
core\amv_controllers\handlers\asset_grid_controller.py
    M 140:4 AssetGridController._reorganize_layout - B
    M 221:4 AssetGridController.on_recalculate_columns_requested - A
    C 21:0 AssetGridController - A
    M 48:4 AssetGridController.on_assets_changed - A
    M 95:4 AssetGridController._prepare_asset_maps - A
    M 119:4 AssetGridController._update_existing_tiles - A
    M 127:4 AssetGridController._add_new_tiles - A
    M 166:4 AssetGridController._get_asset_file_path - A
    M 196:4 AssetGridController.on_loading_state_changed - A
    M 68:4 AssetGridController.rebuild_asset_grid - A
    M 113:4 AssetGridController._remove_unnecessary_tiles - A
    M 157:4 AssetGridController._finalize_grid_update - A
    M 173:4 AssetGridController._connect_tile_signals - A
    M 244:4 AssetGridController.clear_asset_tiles - A
    M 254:4 AssetGridController.set_original_assets - A
    M 24:4 AssetGridController.__init__ - A
    M 44:4 AssetGridController.setup - A
    M 205:4 AssetGridController.on_gallery_resized - A
    M 213:4 AssetGridController.on_thumbnail_size_changed - A
    M 250:4 AssetGridController.get_asset_tiles - A
    M 261:4 AssetGridController.get_original_assets - A
    M 268:4 AssetGridController.set_star_filter - A
    M 273:4 AssetGridController.clear_star_filter - A
core\amv_controllers\handlers\asset_rebuild_controller.py
    C 14:0 AssetRebuildController - A
    M 37:4 AssetRebuildController.on_rebuild_progress - A
    M 45:4 AssetRebuildController.on_rebuild_finished - A
    M 59:4 AssetRebuildController.on_rebuild_error - A
    M 15:4 AssetRebuildController.__init__ - A
    M 22:4 AssetRebuildController.rebuild_assets_in_folder - A
core\amv_controllers\handlers\control_panel_controller.py
    M 120:4 ControlPanelController.on_star_filter_clicked - B
    M 28:4 ControlPanelController.on_select_all_clicked - B
    M 183:4 ControlPanelController._get_filtered_assets - B
    M 170:4 ControlPanelController._update_star_checkboxes - B
    C 15:0 ControlPanelController - A
    M 60:4 ControlPanelController.on_deselect_all_clicked - A
    M 85:4 ControlPanelController.update_button_states - A
    M 157:4 ControlPanelController.filter_assets_by_stars - A
    M 18:4 ControlPanelController.__init__ - A
    M 24:4 ControlPanelController.setup - A
    M 78:4 ControlPanelController.on_selection_changed - A
    M 116:4 ControlPanelController.on_control_panel_selection_state_changed - A
core\amv_controllers\handlers\file_operation_controller.py
    M 106:4 FileOperationController.on_file_operation_completed - C
    C 16:0 FileOperationController - A
    M 29:4 FileOperationController._get_assets_by_ids - A
    M 34:4 FileOperationController._validate_selection - A
    M 56:4 FileOperationController.on_move_selected_clicked - A
    M 75:4 FileOperationController.on_delete_selected_clicked - A
    M 98:4 FileOperationController.on_file_operation_progress - A
    M 223:4 FileOperationController.on_drag_drop_completed - A
    M 19:4 FileOperationController.__init__ - A
    M 25:4 FileOperationController.setup - A
    M 200:4 FileOperationController.on_file_operation_error - A
    M 207:4 FileOperationController.on_drag_drop_started - A
    M 216:4 FileOperationController.on_drag_drop_possible - A
core\amv_controllers\handlers\folder_tree_controller.py
    M 15:4 FolderTreeController.setup - B
    C 8:0 FolderTreeController - A
    M 57:4 FolderTreeController.on_folder_structure_changed - A
    M 80:4 FolderTreeController.on_tree_item_clicked - A
    M 87:4 FolderTreeController.on_tree_item_expanded - A
    M 93:4 FolderTreeController.on_tree_item_collapsed - A
    M 100:4 FolderTreeController.on_collapse_tree_requested - A
    M 109:4 FolderTreeController.on_expand_tree_requested - A
    M 118:4 FolderTreeController.on_folder_refresh_requested - A
    M 9:4 FolderTreeController.__init__ - A
    M 64:4 FolderTreeController.on_folder_clicked - A
    M 73:4 FolderTreeController.on_workspace_folder_clicked - A
core\amv_controllers\handlers\signal_connector.py
    C 6:0 SignalConnector - A
    M 12:4 SignalConnector.connect_all - A
    M 7:4 SignalConnector.__init__ - A
core\amv_models\amv_model.py
    M 30:4 AmvModel.__init__ - B
    M 91:4 AmvModel.set_splitter_sizes - A
    C 21:0 AmvModel - A
    M 60:4 AmvModel.initialize_state - A
    M 85:4 AmvModel.toggle_left_panel - A
    M 96:4 AmvModel.get_splitter_sizes - A
    M 75:4 AmvModel.set_config - A
    M 78:4 AmvModel.set_thumbnail_size - A
    M 82:4 AmvModel.set_work_folder - A
    M 102:4 AmvModel.is_left_panel_collapsed - A
core\amv_models\asset_grid_model.py
    M 239:4 FolderSystemModel._load_subfolders - B
    M 376:4 WorkspaceFoldersModel._load_folders_from_config - B
    M 272:4 FolderSystemModel.expand_folder - B
    M 331:4 FolderSystemModel._refresh_folder_recursive - B
    C 172:0 FolderSystemModel - A
    M 211:4 FolderSystemModel._load_folder_structure - A
    C 359:0 WorkspaceFoldersModel - A
    M 65:4 AssetGridModel.scan_folder - A
    M 310:4 FolderSystemModel.refresh_folder - A
    C 13:0 AssetGridModel - A
    M 39:4 AssetGridModel.set_assets - A
    M 47:4 AssetGridModel.get_assets - A
    M 50:4 AssetGridModel.set_columns - A
    M 122:4 AssetGridModel._perform_recalculate_columns - A
    M 134:4 AssetGridModel._calculate_columns_cached - A
    M 192:4 FolderSystemModel.set_root_folder - A
    M 298:4 FolderSystemModel._set_loading_state - A
    M 25:4 AssetGridModel.__init__ - A
    M 55:4 AssetGridModel.get_columns - A
    M 58:4 AssetGridModel.set_current_folder - A
    M 62:4 AssetGridModel.get_current_folder - A
    M 112:4 AssetGridModel.request_recalculate_columns - A
    M 181:4 FolderSystemModel.__init__ - A
    M 189:4 FolderSystemModel.get_tree_model - A
    M 208:4 FolderSystemModel.get_root_folder - A
    M 294:4 FolderSystemModel.collapse_folder - A
    M 303:4 FolderSystemModel.is_loading - A
    M 306:4 FolderSystemModel.on_folder_clicked - A
    M 364:4 WorkspaceFoldersModel.__init__ - A
    M 372:4 WorkspaceFoldersModel.load_folders - A
    M 421:4 WorkspaceFoldersModel.get_folders - A
core\amv_models\asset_tile_model.py
    M 25:4 AssetTileModel.get_thumbnail_path - A
    M 53:4 AssetTileModel._save_to_file - A
    M 84:4 AssetTileModel.get_archive_path - A
    M 93:4 AssetTileModel.get_preview_path - A
    C 11:0 AssetTileModel - A
    M 39:4 AssetTileModel.get_stars - A
    M 43:4 AssetTileModel.set_stars - A
    M 74:4 AssetTileModel.get_folder_path - A
    M 102:4 AssetTileModel.get_special_folder_path - A
    M 16:4 AssetTileModel.__init__ - A
    M 22:4 AssetTileModel.get_name - A
    M 36:4 AssetTileModel.get_size_mb - A
    M 71:4 AssetTileModel.has_textures_in_archive - A
    M 81:4 AssetTileModel.get_asset_type - A
    M 108:4 AssetTileModel.get_asset_data - A
core\amv_models\config_manager_model.py
    M 26:4 ConfigManagerMV.load_config - B
    C 12:0 ConfigManagerMV - A
    M 64:4 ConfigManagerMV._is_cache_valid - A
    M 59:4 ConfigManagerMV.get_config - A
    M 19:4 ConfigManagerMV.__init__ - A
    M 54:4 ConfigManagerMV.reload_config - A
    M 70:4 ConfigManagerMV._get_default_config - A
core\amv_models\control_panel_model.py
    C 8:0 ControlPanelModel - A
    M 21:4 ControlPanelModel.set_progress - A
    M 30:4 ControlPanelModel.set_thumbnail_size - A
    M 15:4 ControlPanelModel.__init__ - A
    M 27:4 ControlPanelModel.get_progress - A
    M 35:4 ControlPanelModel.get_thumbnail_size - A
    M 38:4 ControlPanelModel.set_has_selection - A
    M 43:4 ControlPanelModel.get_has_selection - A
core\amv_models\drag_drop_model.py
    M 27:4 DragDropModel.validate_drop - A
    C 8:0 DragDropModel - A
    M 61:4 DragDropModel.complete_drop - A
    M 17:4 DragDropModel.__init__ - A
    M 22:4 DragDropModel.start_drag - A
    M 69:4 DragDropModel.get_dragged_asset_ids - A
core\amv_models\file_operations_model.py
    M 38:4 FileOperationsWorker._move_assets - B
    M 253:4 FileOperationsWorker._delete_assets - B
    M 136:4 FileOperationsWorker._prepare_files_to_move - B
    C 11:0 FileOperationsWorker - A
    M 193:4 FileOperationsWorker._update_asset_file_after_rename - A
    M 27:4 FileOperationsWorker.run - A
    M 89:4 FileOperationsWorker._generate_unique_asset_name - A
    M 228:4 FileOperationsWorker._mark_asset_as_duplicate - A
    M 380:4 FileOperationsModel.stop_operation - A
    M 178:4 FileOperationsWorker._handle_post_move - A
    M 300:4 FileOperationsWorker._get_asset_files_paths - A
    C 338:0 FileOperationsModel - A
    M 354:4 FileOperationsModel.move_assets - A
    M 368:4 FileOperationsModel.delete_assets - A
    M 111:4 FileOperationsWorker._move_single_asset_with_conflict_resolution - A
    M 170:4 FileOperationsWorker._move_files - A
    M 184:4 FileOperationsWorker._compose_move_message - A
    M 396:4 FileOperationsModel._on_worker_finished - A
    M 18:4 FileOperationsWorker.__init__ - A
    M 349:4 FileOperationsModel.__init__ - A
    M 389:4 FileOperationsModel._connect_worker_signals - A
core\amv_models\folder_system_model.py
    M 128:4 FolderSystemModel._refresh_folder_recursive - B
    M 65:4 FolderSystemModel._load_subfolders - B
    M 43:4 FolderSystemModel._load_folder_structure - A
    C 11:0 FolderSystemModel - A
    M 88:4 FolderSystemModel.expand_folder - A
    M 146:4 FolderSystemModel._get_folder_icon - A
    M 31:4 FolderSystemModel.set_root_folder - A
    M 117:4 FolderSystemModel.refresh_folder - A
    M 20:4 FolderSystemModel.__init__ - A
    M 28:4 FolderSystemModel.get_tree_model - A
    M 40:4 FolderSystemModel.get_root_folder - A
    M 98:4 FolderSystemModel.collapse_folder - A
    M 103:4 FolderSystemModel._set_loading_state - A
    M 108:4 FolderSystemModel.is_loading - A
    M 112:4 FolderSystemModel.on_folder_clicked - A
core\amv_models\pairing_model.py
    M 25:4 PairingModel.load_unpair_files - A
    M 126:4 PairingModel.delete_unpaired_archives - A
    M 159:4 PairingModel.delete_unpaired_images - A
    M 192:4 PairingModel.create_asset_from_pair - A
    C 11:0 PairingModel - A
    M 69:4 PairingModel._create_default_unpair_files - A
    M 88:4 PairingModel.save_unpair_files - A
    M 109:4 PairingModel.remove_paired_files - A
    M 116:4 PairingModel.add_unpaired_archive - A
    M 121:4 PairingModel.add_unpaired_image - A
    M 12:4 PairingModel.__init__ - A
    M 19:4 PairingModel.set_work_folder - A
    M 103:4 PairingModel.get_unpaired_archives - A
    M 106:4 PairingModel.get_unpaired_images - A
core\amv_models\selection_model.py
    C 7:0 SelectionModel - A
    M 19:4 SelectionModel.add_selection - A
    M 24:4 SelectionModel.remove_selection - A
    M 29:4 SelectionModel.clear_selection - A
    M 12:4 SelectionModel.__init__ - A
    M 34:4 SelectionModel.get_selected_asset_ids - A
    M 37:4 SelectionModel.is_selected - A
    M 40:4 SelectionModel._emit_selection_changed - A
core\amv_models\workspace_folders_model.py
    M 32:4 WorkspaceFoldersModel._load_folders_from_config - B
    M 74:4 WorkspaceFoldersModel.add_folder - B
    M 140:4 WorkspaceFoldersModel.update_folder - B
    C 10:0 WorkspaceFoldersModel - A
    M 117:4 WorkspaceFoldersModel.remove_folder - A
    M 186:4 WorkspaceFoldersModel.get_folder_by_path - A
    M 193:4 WorkspaceFoldersModel.get_enabled_folders - A
    M 22:4 WorkspaceFoldersModel.load_folders - A
    M 176:4 WorkspaceFoldersModel._update_config - A
    M 15:4 WorkspaceFoldersModel.__init__ - A
    M 70:4 WorkspaceFoldersModel.get_folders - A
core\amv_views\amv_view.py
    M 155:4 AmvView.update_workspace_folder_buttons - B
    M 483:4 AmvView.update_toggle_button_text - B
    M 506:4 AmvView.remove_asset_tiles - A
    M 248:4 AmvView._position_control_panel - A
    M 372:4 AmvView._create_control_panel - A
    C 34:0 AmvView - A
    M 130:4 AmvView._create_folder_tree_view - A
    M 365:4 AmvView.update_gallery_placeholder - A
    M 526:4 AmvView.showEvent - A
    M 537:4 AmvView.resizeEvent - A
    M 44:4 AmvView.__init__ - A
    M 51:4 AmvView._load_icons - A
    M 56:4 AmvView._setup_ui - A
    M 78:4 AmvView._create_left_panel - A
    M 92:4 AmvView._create_left_panel_header - A
    M 144:4 AmvView._create_folder_buttons_panel - A
    M 223:4 AmvView._create_gallery_panel - A
    M 297:4 AmvView._create_edge_button - A
    M 308:4 AmvView._create_scroll_area - A
    M 335:4 AmvView._create_gallery_content_widget - A
    M 475:4 AmvView._on_splitter_moved - A
    M 479:4 AmvView.update_splitter_sizes - A
    M 498:4 AmvView._on_collapse_tree_clicked - A
    M 502:4 AmvView._on_expand_tree_clicked - A
core\amv_views\asset_tile_pool.py
    C 15:0 AssetTilePool - A
    M 27:4 AssetTilePool.acquire - A
    M 58:4 AssetTilePool.release - A
    M 73:4 AssetTilePool.clear - A
    M 21:4 AssetTilePool.__init__ - A
core\amv_views\asset_tile_view.py
    M 105:4 AssetTileView.reset_for_pool - C
    M 314:4 AssetTileView._setup_asset_tile_ui - B
    M 617:4 AssetTileView._on_checkbox_state_changed - B
    M 461:4 AssetTileView.mousePressEvent - B
    M 70:4 AssetTileView.update_asset_data - B
    M 424:4 AssetTileView._load_icon_with_fallback - A
    M 509:4 AssetTileView._start_drag - A
    M 580:4 AssetTileView._update_stars_visibility - A
    C 31:0 AssetTileView - A
    M 306:4 AssetTileView.update_ui - A
    M 587:4 AssetTileView.release_resources - A
    M 141:4 AssetTileView._setup_ui - A
    M 361:4 AssetTileView._on_thumbnail_loaded - A
    M 367:4 AssetTileView._on_thumbnail_error - A
    M 373:4 AssetTileView._set_thumbnail_pixmap - A
    M 396:4 AssetTileView._setup_folder_tile_ui - A
    M 494:4 AssetTileView.mouseMoveEvent - A
    M 645:4 AssetTileView.get_star_rating - A
    M 195:4 AssetTileView._setup_ui_without_styles - A
    M 351:4 AssetTileView._load_thumbnail_async - A
    M 551:4 AssetTileView._on_thumbnail_clicked - A
    M 561:4 AssetTileView._on_filename_clicked - A
    M 649:4 AssetTileView.set_star_rating - A
    M 654:4 AssetTileView._on_star_clicked - A
    M 666:4 AssetTileView.clear_stars - A
    M 693:4 AssetTileView._update_thumbnail_size - A
    M 42:4 AssetTileView.__init__ - A
    M 418:4 AssetTileView._create_placeholder_thumbnail - A
    M 449:4 AssetTileView._load_folder_icon - A
    M 456:4 AssetTileView._load_texture_icon - A
    M 571:4 AssetTileView.update_thumbnail_size - A
    M 598:4 AssetTileView.is_checked - A
    M 602:4 AssetTileView.set_checked - A
    M 670:4 AssetTileView.set_drag_and_drop_enabled - A
    M 674:4 AssetTileView._check_stars_fit - A
    M 685:4 AssetTileView.resizeEvent - A
core\amv_views\folder_tree_view.py
    M 210:4 CustomFolderTreeView.dragMoveEvent - B
    M 298:4 CustomFolderTreeView._get_drop_target_info - B
    M 353:4 CustomFolderTreeView._can_perform_drop - B
    M 80:4 CustomFolderTreeView.contextMenuEvent - B
    M 438:4 CustomFolderTreeView._on_current_folder_changed - B
    M 252:4 CustomFolderTreeView.dropEvent - A
    M 413:4 CustomFolderTreeView._clear_folder_highlight - A
    C 17:0 CustomFolderTreeView - A
    M 339:4 CustomFolderTreeView._get_assets_to_move - A
    M 395:4 CustomFolderTreeView._highlight_folder_at_position - A
    M 153:4 CustomFolderTreeView._open_folder_in_explorer - A
    M 171:4 CustomFolderTreeView._rebuild_assets_in_folder - A
    M 181:4 CustomFolderTreeView._refresh_folder - A
    M 191:4 CustomFolderTreeView.dragEnterEvent - A
    M 288:4 CustomFolderTreeView._validate_drop_event - A
    M 75:4 CustomFolderTreeView._connect_selection_model - A
    M 379:4 CustomFolderTreeView._perform_drop_operation - A
    M 428:4 CustomFolderTreeView._on_item_expanded - A
    M 433:4 CustomFolderTreeView._on_item_collapsed - A
    M 24:4 CustomFolderTreeView.__init__ - A
    M 45:4 CustomFolderTreeView.set_models - A
    M 58:4 CustomFolderTreeView.set_rebuild_callback - A
    M 62:4 CustomFolderTreeView.set_open_in_explorer_callback - A
    M 66:4 CustomFolderTreeView.set_refresh_folder_callback - A
    M 70:4 CustomFolderTreeView.setModel - A
    M 205:4 CustomFolderTreeView.dragLeaveEvent - A
core\amv_views\gallery_widgets.py
    C 31:0 DropHighlightDelegate - A
    M 37:4 DropHighlightDelegate.paint - A
    C 14:0 GalleryContainerWidget - A
    M 21:4 GalleryContainerWidget.__init__ - A
    M 25:4 GalleryContainerWidget.resizeEvent - A
core\amv_views\preview_gallery_view.py
    M 101:4 PreviewGalleryView._on_preview_checked - B
    M 135:4 PreviewGalleryView.remove_preview_by_path - B
    M 157:4 PreviewGalleryView._reorganize_tiles - A
    C 11:0 PreviewGalleryView - A
    M 53:4 PreviewGalleryView._clear_gallery - A
    M 64:4 PreviewGalleryView.set_previews - A
    M 94:4 PreviewGalleryView.update_tile_sizes - A
    M 122:4 PreviewGalleryView.get_columns_count - A
    M 17:4 PreviewGalleryView.__init__ - A
    M 25:4 PreviewGalleryView.init_ui - A
    M 90:4 PreviewGalleryView.on_slider_value_changed - A
    M 119:4 PreviewGalleryView._on_preview_clicked - A
    M 128:4 PreviewGalleryView.resizeEvent - A
    M 132:4 PreviewGalleryView.get_selected_preview - A
core\amv_views\preview_tile.py
    M 72:4 PreviewTile.load_thumbnail - A
    M 93:4 PreviewTile._scale_cached_pixmap - A
    C 15:0 PreviewTile - A
    M 123:4 PreviewTile._on_thumbnail_clicked - A
    M 127:4 PreviewTile._on_filename_clicked - A
    M 19:4 PreviewTile.__init__ - A
    M 29:4 PreviewTile.init_ui - A
    M 106:4 PreviewTile._create_placeholder_thumbnail - A
    M 131:4 PreviewTile._on_checkbox_state_changed - A
    M 134:4 PreviewTile.is_checked - A
    M 137:4 PreviewTile.set_checked - A
    M 140:4 PreviewTile.update_thumbnail_size - A
core\workers\asset_rebuilder_worker.py
    M 63:4 AssetRebuilderWorker._remove_asset_files - A
    C 16:0 AssetRebuilderWorker - A
    M 27:4 AssetRebuilderWorker.run - A
    M 78:4 AssetRebuilderWorker._remove_cache_folder - A
    M 96:4 AssetRebuilderWorker._run_scanner - A
    M 23:4 AssetRebuilderWorker.__init__ - A
core\workers\thumbnail_loader_worker.py
    C 20:0 ThumbnailLoaderWorker - A
    M 31:4 ThumbnailLoaderWorker.run - A
    C 14:0 ThumbnailLoaderSignals - A
    M 26:4 ThumbnailLoaderWorker.__init__ - A

586 blocks (classes, functions, methods) analyzed.
Average complexity: A (2.9948805460750854)
```

---

## Maintainability Index (MI)

> Brak danych o maintainability index.

## Błędy
```text
MI Errors:
usage: radon [-h] [-v] {cc,raw,mi,hal} ...
radon: error: unrecognized arguments: -a
```
