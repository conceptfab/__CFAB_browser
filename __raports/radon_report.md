# 📊 Raport Radon (Złożoność)

**Data generowania:** 2025-07-06 22:49:42

---

## Złożoność Cyklomatyczna (CC)

```text
core\amv_tab.py
    C 19:0 AmvTab - A
    M 25:4 AmvTab.__init__ - A
    M 49:4 AmvTab.get_controller - A
core\file_utils.py
    F 398:0 handle_file_action - B
    F 316:0 _manage_preview_window - A
    F 35:0 _validate_path_input - A
    F 200:0 open_path_in_explorer - A
    F 246:0 open_file_in_default_app - A
    F 292:0 _validate_file_action_input - A
    F 56:0 _open_path_windows - A
    F 78:0 _open_path_macos - A
    F 100:0 _open_path_linux - A
    F 122:0 _open_file_windows - A
    F 143:0 _open_file_macos - A
    F 165:0 _open_file_linux - A
    F 16:0 _is_command_available - A
    F 187:0 _show_error_message - A
    F 347:0 _handle_folder_action - A
    F 364:0 _handle_file_thumbnail_action - A
    F 381:0 _handle_file_filename_action - A
core\json_utils.py
    F 67:0 load_from_file - B
    F 25:0 loads - A
    F 45:0 dumps - A
    F 113:0 save_to_file - A
core\main_window.py
    M 673:4 MainWindow._filter_non_special_assets - B
    M 96:4 MainWindow._load_config_safe - B
    M 281:4 MainWindow.update_working_directory_status - A
    M 433:4 MainWindow._connect_amv_signals - A
    M 467:4 MainWindow._connect_tools_signals - A
    M 492:4 MainWindow._on_folder_structure_changed - A
    M 627:4 MainWindow._handle_tab_indicator_error - A
    M 756:4 MainWindow._create_tabs_from_config - A
    C 38:0 MainWindow - A
    M 138:4 MainWindow._setup_logger - A
    M 248:4 MainWindow.update_status - A
    M 302:4 MainWindow.update_selection_status - A
    M 329:4 MainWindow._validate_components - A
    M 512:4 MainWindow._update_pairing_tab_indicator - A
    M 558:4 MainWindow.closeEvent - A
    M 589:4 MainWindow._find_pairing_tab_index - A
    M 602:4 MainWindow._count_unpaired_files - A
    M 789:4 MainWindow._setup_special_tab_features - A
    M 257:4 MainWindow.show_log_info - A
    M 341:4 MainWindow._has_provided_counts - A
    M 345:4 MainWindow._update_status_label - A
    M 351:4 MainWindow._handle_status_error - A
    M 418:4 MainWindow._connect_signals - A
    M 545:4 MainWindow._on_assets_changed - A
    M 644:4 MainWindow._get_asset_controller_data - A
    M 801:4 MainWindow._initialize_selection_counter - A
    M 40:4 MainWindow.__init__ - A
    M 166:4 MainWindow._createMenuBar - A
    M 184:4 MainWindow._createTabs - A
    M 199:4 MainWindow._createStatusBar - A
    M 357:4 MainWindow.show_operation_status - A
    M 374:4 MainWindow.setup_log_interceptor - A
    M 504:4 MainWindow._on_working_directory_changed_for_pairing - A
    M 532:4 MainWindow._on_selection_changed - A
    M 614:4 MainWindow._generate_tab_text - A
    M 621:4 MainWindow._set_tab_text_safely - A
    M 699:4 MainWindow._count_visible_assets - A
    M 709:4 MainWindow._count_total_assets - A
    M 719:4 MainWindow._calculate_asset_counts - A
    M 774:4 MainWindow._create_single_tab - A
    M 822:4 MainWindow._validate_tabs_creation - A
    M 838:4 MainWindow._calculate_current_asset_counts - A
    M 852:4 MainWindow._count_filtered_assets - A
    M 864:4 MainWindow._count_original_assets - A
    M 462:4 MainWindow._connect_status_signals - A
    M 661:4 MainWindow._validate_grid_controller - A
    M 731:4 MainWindow._handle_selection_change_error - A
    M 741:4 MainWindow._initialize_tab_references - A
    M 748:4 MainWindow._get_tabs_configuration - A
    M 814:4 MainWindow._create_error_placeholder - A
    M 834:4 MainWindow._get_amv_controller - A
core\pairing_tab.py
    M 253:4 PairingTab._on_archive_clicked - B
    M 326:4 PairingTab._on_create_asset_button_clicked - B
    M 188:4 PairingTab.load_data - B
    M 239:4 PairingTab._on_archive_checked - B
    M 418:4 PairingTab._on_rebuild_assets_clicked - A
    C 92:0 PairingTab - A
    M 298:4 PairingTab._remove_paired_items_from_ui - A
    M 488:4 PairingTab._update_basic_buttons - A
    M 497:4 PairingTab._update_create_asset_button - A
    M 507:4 PairingTab._notify_pairing_changed - A
    M 289:4 PairingTab._on_preview_clicked - A
    M 370:4 PairingTab._on_delete_unpaired_images_clicked - A
    M 394:4 PairingTab._on_delete_unpaired_archives_clicked - A
    M 469:4 PairingTab._validate_working_folder - A
    M 477:4 PairingTab._get_selection_state - A
    C 36:0 ArchiveListItem - A
    M 285:4 PairingTab._on_preview_selected - A
    M 42:4 ArchiveListItem.__init__ - A
    M 47:4 ArchiveListItem.init_ui - A
    M 63:4 ArchiveListItem.contextMenuEvent - A
    M 71:4 ArchiveListItem._on_checkbox_state_changed - A
    M 74:4 ArchiveListItem._handle_open - A
    M 78:4 ArchiveListItem.is_checked - A
    M 81:4 ArchiveListItem.set_checked - A
    M 84:4 ArchiveListItem.sizeHint - A
    M 98:4 PairingTab.__init__ - A
    M 105:4 PairingTab.on_working_directory_changed - A
    M 112:4 PairingTab.init_ui - A
    M 314:4 PairingTab._update_button_states - A
    M 322:4 PairingTab._update_create_asset_button_state - A
    M 450:4 PairingTab._on_rebuild_finished - A
    M 458:4 PairingTab._on_rebuild_error - A
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
    M 618:4 FolderClickRules.analyze_folder_content - B
    M 457:4 FolderClickRules._validate_folder_path - B
    M 542:4 FolderClickRules._categorize_file - B
    M 573:4 FolderClickRules._analyze_cache_folder - B
    C 419:0 FolderClickRules - A
    C 176:0 AdditionalCaseStrategy - A
    C 345:0 Condition2bRule - A
    M 351:4 Condition2bRule.matches - A
    C 358:0 Condition2cRule - A
    M 364:4 Condition2cRule.matches - A
    M 180:4 AdditionalCaseStrategy.execute - A
    C 258:0 DefaultCaseStrategy - A
    M 312:4 DecisionRule.handle - A
    C 322:0 Condition1Rule - A
    C 333:0 Condition2aRule - A
    M 339:4 Condition2aRule.matches - A
    C 371:0 AdditionalCaseRule - A
    M 509:4 FolderClickRules._get_cached_analysis - A
    M 744:4 FolderClickRules.decide_action - A
    C 31:0 DecisionStrategy - A
    C 48:0 Condition1Strategy - A
    C 75:0 Condition2aStrategy - A
    C 104:0 Condition2bStrategy - A
    C 140:0 Condition2cStrategy - A
    M 262:4 DefaultCaseStrategy.execute - A
    C 294:0 DecisionRule - A
    M 328:4 Condition1Rule.matches - A
    M 377:4 AdditionalCaseRule.matches - A
    C 382:0 DecisionEngine - A
    M 490:4 FolderClickRules._is_cache_valid - A
    M 720:4 FolderClickRules._log_folder_analysis - A
    M 737:4 FolderClickRules._get_decision_engine - A
    M 35:4 DecisionStrategy.execute - A
    M 52:4 Condition1Strategy.execute - A
    M 79:4 Condition2aStrategy.execute - A
    M 108:4 Condition2bStrategy.execute - A
    M 144:4 Condition2cStrategy.execute - A
    M 299:4 DecisionRule.__init__ - A
    M 303:4 DecisionRule.set_next - A
    M 308:4 DecisionRule.matches - A
    M 325:4 Condition1Rule.__init__ - A
    M 336:4 Condition2aRule.__init__ - A
    M 348:4 Condition2bRule.__init__ - A
    M 361:4 Condition2cRule.__init__ - A
    M 374:4 AdditionalCaseRule.__init__ - A
    M 387:4 DecisionEngine.__init__ - A
    M 391:4 DecisionEngine._build_decision_chain - A
    M 405:4 DecisionEngine.decide - A
    M 529:4 FolderClickRules._cache_analysis - A
    M 603:4 FolderClickRules._create_error_result - A
core\scanner.py
    M 235:4 AssetRepository._validate_asset_creation_inputs - B
    M 67:4 AssetRepository._get_files_by_extensions - B
    M 311:4 AssetRepository._preserve_user_data - B
    M 342:4 AssetRepository._save_asset_with_error_handling - B
    M 485:4 AssetRepository.create_thumbnail_for_asset - A
    M 638:4 AssetRepository.find_and_create_assets - A
    M 709:4 AssetRepository._create_assets_from_groups - A
    M 838:4 AssetRepository.load_existing_assets - A
    C 19:0 AssetRepository - A
    M 36:4 AssetRepository._handle_error - A
    M 141:4 AssetRepository._validate_texture_check_inputs - A
    M 182:4 AssetRepository._check_texture_folders_presence - A
    M 421:4 AssetRepository._validate_thumbnail_inputs - A
    M 599:4 AssetRepository._create_unpair_files_json - A
    M 798:4 AssetRepository._load_asset_files - A
    M 32:4 AssetRepository._validate_folder_path_static - A
    M 96:4 AssetRepository._scan_folder_for_files - A
    M 160:4 AssetRepository._scan_texture_folders - A
    M 212:4 AssetRepository._scan_for_named_folders - A
    M 262:4 AssetRepository._load_existing_asset_data - A
    M 374:4 AssetRepository._create_single_asset - A
    M 441:4 AssetRepository._parse_thumbnail_result - A
    M 460:4 AssetRepository._update_asset_with_thumbnail - A
    M 536:4 AssetRepository._find_unpaired_files - A
    M 758:4 AssetRepository._handle_asset_loading_errors - A
    M 772:4 AssetRepository._load_single_asset_file - A
    M 53:4 AssetRepository._has_valid_extension - A
    M 696:4 AssetRepository._scan_and_group_files - A
    M 747:4 AssetRepository._validate_asset_data - A
    M 27:4 AssetRepository.__init__ - A
    M 230:4 AssetRepository._scan_for_special_folders - A
    M 282:4 AssetRepository._create_base_asset_data - A
    M 417:4 AssetRepository._get_file_size_mb - A
    M 564:4 AssetRepository._create_unpaired_data_structure - A
    M 582:4 AssetRepository._save_unpaired_files_json - A
    M 819:4 AssetRepository._combine_with_special_folders - A
core\selection_counter.py
    M 53:4 SelectionCounter._get_asset_tiles - A
    M 75:4 SelectionCounter._count_tiles_by_condition - A
    M 126:4 SelectionCounter.count_total_assets - A
    M 239:4 SelectionCounter.get_status_text - A
    C 14:0 SelectionCounter - A
    M 158:4 SelectionCounter._validate_controller - A
    M 180:4 SelectionCounter._is_valid_asset_tile - A
    M 200:4 SelectionCounter._is_valid_selected_tile - A
    M 220:4 SelectionCounter._count_non_special_assets - A
    M 32:4 SelectionCounter.get_selection_summary - A
    M 22:4 SelectionCounter.__init__ - A
    M 102:4 SelectionCounter.count_selected_assets - A
    M 114:4 SelectionCounter.count_visible_assets - A
core\thread_manager.py
    M 163:4 ThreadManager._validate_and_cleanup_registries - A
    M 225:4 ThreadManager._stop_single_thread - A
    M 262:4 ThreadManager._emergency_stop_threads - A
    C 16:0 ThreadManager - A
    M 31:4 ThreadManager.register_thread - A
    M 48:4 ThreadManager.register_thread_pool - A
    M 130:4 ThreadManager._stop_all_thread_pools - A
    M 65:4 ThreadManager.unregister_thread - A
    M 80:4 ThreadManager.get_active_thread_count - A
    M 92:4 ThreadManager.stop_all_threads - A
    M 150:4 ThreadManager._stop_all_individual_threads - A
    M 274:4 ThreadManager._emergency_stop_thread_pools - A
    M 314:4 ThreadManager.get_status_report - A
    M 186:4 ThreadManager._try_graceful_thread_stop - A
    M 204:4 ThreadManager._try_force_thread_termination - A
    M 24:4 ThreadManager.__init__ - A
    M 285:4 ThreadManager._emergency_cleanup_registries - A
    M 292:4 ThreadManager.emergency_stop_all - A
core\thumbnail.py
    M 98:4 ThumbnailGenerator.generate_thumbnail - C
    C 41:0 ThumbnailGenerator - A
    F 227:0 get_config - A
    M 54:4 ThumbnailGenerator._has_transparency - A
    M 178:4 ThumbnailGenerator._is_thumbnail_current - A
    M 190:4 ThumbnailGenerator._resize_to_square - A
    F 254:0 get_generator - A
    M 74:4 ThumbnailGenerator._get_optimal_format_and_path - A
    F 263:0 generate_thumbnail - A
    M 44:4 ThumbnailGenerator.__init__ - A
core\thumbnail_cache.py
    M 63:4 ThumbnailCache.put - A
    C 15:0 ThumbnailCache - A
    M 23:4 ThumbnailCache.__new__ - A
    M 30:4 ThumbnailCache.__init__ - A
    M 45:4 ThumbnailCache.get - A
    M 93:4 ThumbnailCache._evict_oldest - A
    M 106:4 ThumbnailCache.clear - A
core\tools_tab.py
    M 481:4 ToolsTab.closeEvent - C
    M 363:4 ToolsTab._update_button_states - B
    M 552:4 ToolsTab._on_archive_double_clicked - B
    M 404:4 ToolsTab._handle_operation_finished - B
    M 257:4 ToolsTab.scan_working_directory - B
    M 588:4 ToolsTab._on_preview_double_clicked - B
    M 900:4 ToolsTab._show_pairs_dialog - B
    M 953:4 ToolsTab._show_pairs_dialog_shortener - B
    M 390:4 ToolsTab._handle_worker_finished - A
    M 466:4 ToolsTab._handle_worker_error - A
    M 701:4 ToolsTab._on_remove_clicked - A
    C 42:0 ToolsTab - A
    M 69:4 ToolsTab._validate_working_directory - A
    M 334:4 ToolsTab._get_image_resolution - A
    M 889:4 ToolsTab._handle_duplicates_finished - A
    M 118:4 ToolsTab._start_operation_with_confirmation - A
    M 238:4 ToolsTab.set_working_directory - A
    M 635:4 ToolsTab._on_file_renaming_clicked - A
    M 668:4 ToolsTab._on_file_shortening_clicked - A
    M 828:4 ToolsTab._on_find_duplicates_clicked - A
    M 88:4 ToolsTab._handle_worker_lifecycle - A
    M 314:4 ToolsTab._update_archive_list - A
    M 322:4 ToolsTab._update_preview_list - A
    M 787:4 ToolsTab._start_remove - A
    M 846:4 ToolsTab._start_find_duplicates - A
    M 52:4 ToolsTab.__init__ - A
    M 155:4 ToolsTab._setup_ui - A
    M 358:4 ToolsTab.clear_lists - A
    M 385:4 ToolsTab._handle_worker_progress - A
    M 478:4 ToolsTab._reset_button_state - A
    M 518:4 ToolsTab._on_webp_conversion_clicked - A
    M 538:4 ToolsTab._on_rebuild_assets_clicked - A
    M 614:4 ToolsTab._on_image_resizing_clicked - A
    M 653:4 ToolsTab._start_file_renaming - A
    M 686:4 ToolsTab._start_file_shortening - A
    M 1006:4 ToolsTab.clear_working_directory - A
core\utilities.py
    F 54:0 update_main_window_status - A
    F 11:0 clear_thumbnail_cache_after_rebuild - A
    F 31:0 get_file_size_mb - A
core\amv_controllers\amv_controller.py
    C 20:0 AmvController - A
    M 74:4 AmvController._on_splitter_state_changed - A
    M 96:4 AmvController._on_scan_progress - A
    M 26:4 AmvController.__init__ - A
    M 68:4 AmvController._connect_signals - A
    M 81:4 AmvController._on_config_loaded - A
    M 85:4 AmvController._on_state_initialized - A
    M 89:4 AmvController._on_scan_started - A
    M 104:4 AmvController._on_scan_completed - A
    M 125:4 AmvController._on_scan_error - A
    M 132:4 AmvController._handle_file_action - A
core\amv_controllers\handlers\asset_grid_controller.py
    M 167:4 AssetGridController._reorganize_layout - B
    M 91:4 AssetGridController._rebuild_asset_grid_immediate - B
    M 283:4 AssetGridController.clear_asset_tiles - B
    M 260:4 AssetGridController.on_recalculate_columns_requested - A
    M 55:4 AssetGridController.on_assets_changed - A
    C 21:0 AssetGridController - A
    M 122:4 AssetGridController._prepare_asset_maps - A
    M 146:4 AssetGridController._update_existing_tiles - A
    M 154:4 AssetGridController._add_new_tiles - A
    M 205:4 AssetGridController._get_asset_file_path - A
    M 235:4 AssetGridController.on_loading_state_changed - A
    M 83:4 AssetGridController._perform_delayed_rebuild - A
    M 140:4 AssetGridController._remove_unnecessary_tiles - A
    M 196:4 AssetGridController._finalize_grid_update - A
    M 212:4 AssetGridController._connect_tile_signals - A
    M 311:4 AssetGridController.set_original_assets - A
    M 24:4 AssetGridController.__init__ - A
    M 51:4 AssetGridController.setup - A
    M 75:4 AssetGridController.rebuild_asset_grid - A
    M 244:4 AssetGridController.on_gallery_resized - A
    M 252:4 AssetGridController.on_thumbnail_size_changed - A
    M 307:4 AssetGridController.get_asset_tiles - A
    M 318:4 AssetGridController.get_original_assets - A
    M 325:4 AssetGridController.set_star_filter - A
    M 330:4 AssetGridController.clear_star_filter - A
core\amv_controllers\handlers\asset_rebuild_controller.py
    M 24:4 AssetRebuildController.rebuild_assets_in_folder - A
    M 55:4 AssetRebuildController._stop_rebuild_safely - A
    M 130:4 AssetRebuildController.__del__ - A
    C 15:0 AssetRebuildController - A
    M 71:4 AssetRebuildController.on_rebuild_progress - A
    M 79:4 AssetRebuildController.on_rebuild_finished - A
    M 123:4 AssetRebuildController._cleanup_worker - A
    M 16:4 AssetRebuildController.__init__ - A
    M 51:4 AssetRebuildController.stop_rebuild - A
    M 101:4 AssetRebuildController.on_rebuild_error - A
core\amv_controllers\handlers\control_panel_controller.py
    M 131:4 ControlPanelController.on_star_filter_clicked - B
    M 168:4 ControlPanelController.filter_assets - B
    M 34:4 ControlPanelController.on_select_all_clicked - B
    C 16:0 ControlPanelController - A
    M 66:4 ControlPanelController.on_deselect_all_clicked - A
    M 96:4 ControlPanelController._perform_update_button_states - A
    M 19:4 ControlPanelController.__init__ - A
    M 30:4 ControlPanelController.setup - A
    M 84:4 ControlPanelController.on_selection_changed - A
    M 91:4 ControlPanelController.update_button_states - A
    M 127:4 ControlPanelController.on_control_panel_selection_state_changed - A
core\amv_controllers\handlers\file_operation_controller.py
    M 241:4 FileOperationController._remove_tiles_from_view_fast - C
    M 123:4 FileOperationController.on_file_operation_completed - B
    M 35:4 FileOperationController._validate_selection - A
    M 285:4 FileOperationController._refresh_folder_structure_delayed - A
    C 17:0 FileOperationController - A
    M 219:4 FileOperationController._update_controller_asset_list - A
    M 30:4 FileOperationController._get_assets_by_ids - A
    M 74:4 FileOperationController.on_move_selected_clicked - A
    M 93:4 FileOperationController.on_delete_selected_clicked - A
    M 174:4 FileOperationController._remove_moved_assets_optimized - A
    M 191:4 FileOperationController._validate_optimization_inputs - A
    M 204:4 FileOperationController._update_asset_model_fast - A
    M 303:4 FileOperationController._fallback_refresh_gallery - A
    M 115:4 FileOperationController.on_file_operation_progress - A
    M 233:4 FileOperationController._update_gallery_placeholder_state - A
    M 336:4 FileOperationController.on_drag_drop_completed - A
    M 20:4 FileOperationController.__init__ - A
    M 26:4 FileOperationController.setup - A
    M 313:4 FileOperationController.on_file_operation_error - A
    M 320:4 FileOperationController.on_drag_drop_started - A
    M 329:4 FileOperationController.on_drag_drop_possible - A
core\amv_controllers\handlers\folder_tree_controller.py
    M 19:4 FolderTreeController.setup - B
    M 89:4 FolderTreeController._scan_folder_safely - B
    C 8:0 FolderTreeController - A
    M 122:4 FolderTreeController.on_folder_clicked - A
    M 187:4 FolderTreeController.on_folder_refresh_requested - A
    M 65:4 FolderTreeController.set_show_asset_counts - A
    M 71:4 FolderTreeController.get_show_asset_counts - A
    M 77:4 FolderTreeController.set_recursive_asset_counts - A
    M 83:4 FolderTreeController.get_recursive_asset_counts - A
    M 115:4 FolderTreeController.on_folder_structure_changed - A
    M 139:4 FolderTreeController.on_workspace_folder_clicked - A
    M 149:4 FolderTreeController.on_tree_item_clicked - A
    M 156:4 FolderTreeController.on_tree_item_expanded - A
    M 162:4 FolderTreeController.on_tree_item_collapsed - A
    M 169:4 FolderTreeController.on_collapse_tree_requested - A
    M 178:4 FolderTreeController.on_expand_tree_requested - A
    M 9:4 FolderTreeController.__init__ - A
core\amv_controllers\handlers\signal_connector.py
    M 13:4 SignalConnector.connect_all - A
    C 6:0 SignalConnector - A
    M 7:4 SignalConnector.__init__ - A
core\amv_models\amv_model.py
    M 32:4 AmvModel.__init__ - B
    M 93:4 AmvModel.set_splitter_sizes - A
    C 23:0 AmvModel - A
    M 62:4 AmvModel.initialize_state - A
    M 87:4 AmvModel.toggle_left_panel - A
    M 98:4 AmvModel.get_splitter_sizes - A
    M 77:4 AmvModel.set_config - A
    M 80:4 AmvModel.set_thumbnail_size - A
    M 84:4 AmvModel.set_work_folder - A
    M 104:4 AmvModel.is_left_panel_collapsed - A
core\amv_models\asset_grid_model.py
    M 67:4 AssetGridModel.scan_folder - A
    C 15:0 AssetGridModel - A
    M 41:4 AssetGridModel.set_assets - A
    M 49:4 AssetGridModel.get_assets - A
    M 52:4 AssetGridModel.set_columns - A
    M 124:4 AssetGridModel._perform_recalculate_columns - A
    M 136:4 AssetGridModel._calculate_columns_cached - A
    M 27:4 AssetGridModel.__init__ - A
    M 57:4 AssetGridModel.get_columns - A
    M 60:4 AssetGridModel.set_current_folder - A
    M 64:4 AssetGridModel.get_current_folder - A
    M 114:4 AssetGridModel.request_recalculate_columns - A
core\amv_models\asset_tile_model.py
    M 30:4 AssetTileModel.get_thumbnail_path - A
    M 63:4 AssetTileModel._perform_save_to_file - A
    M 94:4 AssetTileModel.get_archive_path - A
    M 103:4 AssetTileModel.get_preview_path - A
    C 11:0 AssetTileModel - A
    M 44:4 AssetTileModel.get_stars - A
    M 48:4 AssetTileModel.set_stars - A
    M 84:4 AssetTileModel.get_folder_path - A
    M 112:4 AssetTileModel.get_special_folder_path - A
    M 16:4 AssetTileModel.__init__ - A
    M 27:4 AssetTileModel.get_name - A
    M 41:4 AssetTileModel.get_size_mb - A
    M 58:4 AssetTileModel._save_to_file - A
    M 81:4 AssetTileModel.has_textures_in_archive - A
    M 91:4 AssetTileModel.get_asset_type - A
    M 118:4 AssetTileModel.get_asset_data - A
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
    M 45:4 FileOperationsWorker._move_assets - C
    M 273:4 FileOperationsWorker._delete_assets - C
    M 157:4 FileOperationsWorker._prepare_files_to_move - B
    C 11:0 FileOperationsWorker - A
    M 33:4 FileOperationsWorker.run - A
    M 213:4 FileOperationsWorker._update_asset_file_after_rename - A
    M 110:4 FileOperationsWorker._generate_unique_asset_name - A
    M 248:4 FileOperationsWorker._mark_asset_as_duplicate - A
    M 419:4 FileOperationsModel._stop_worker_safely - A
    M 450:4 FileOperationsModel.__del__ - A
    M 199:4 FileOperationsWorker._handle_post_move - A
    M 330:4 FileOperationsWorker._get_asset_files_paths - A
    C 359:0 FileOperationsModel - A
    M 377:4 FileOperationsModel.move_assets - A
    M 399:4 FileOperationsModel.delete_assets - A
    M 132:4 FileOperationsWorker._move_single_asset_with_conflict_resolution - A
    M 191:4 FileOperationsWorker._move_files - A
    M 205:4 FileOperationsWorker._compose_move_message - A
    M 435:4 FileOperationsModel._connect_worker_signals - A
    M 443:4 FileOperationsModel._on_worker_finished - A
    M 18:4 FileOperationsWorker.__init__ - A
    M 28:4 FileOperationsWorker.request_stop - A
    M 370:4 FileOperationsModel.__init__ - A
    M 395:4 FileOperationsModel.get_last_target_folder - A
    M 415:4 FileOperationsModel.stop_operation - A
core\amv_models\folder_system_model.py
    M 102:4 FolderSystemModel._scan_folder_for_assets - C
    M 282:4 FolderSystemModel._refresh_folder_recursive - B
    M 199:4 FolderSystemModel._load_subfolders - B
    M 69:4 FolderSystemModel._get_cached_asset_count - B
    M 138:4 FolderSystemModel._clear_cache_for_path - A
    C 10:0 FolderSystemModel - A
    M 149:4 FolderSystemModel._format_folder_display_name - A
    M 174:4 FolderSystemModel._load_folder_structure - A
    M 263:4 FolderSystemModel.refresh_folder - A
    M 34:4 FolderSystemModel.set_show_asset_counts - A
    M 48:4 FolderSystemModel.set_recursive_asset_counts - A
    M 234:4 FolderSystemModel.expand_folder - A
    M 316:4 FolderSystemModel._get_folder_icon - A
    M 62:4 FolderSystemModel._count_assets_in_folder - A
    M 160:4 FolderSystemModel.set_root_folder - A
    M 19:4 FolderSystemModel.__init__ - A
    M 31:4 FolderSystemModel.get_tree_model - A
    M 44:4 FolderSystemModel.get_show_asset_counts - A
    M 58:4 FolderSystemModel.get_recursive_asset_counts - A
    M 94:4 FolderSystemModel._count_assets_direct - A
    M 98:4 FolderSystemModel._count_assets_recursive - A
    M 133:4 FolderSystemModel.clear_asset_count_cache - A
    M 171:4 FolderSystemModel.get_root_folder - A
    M 224:4 FolderSystemModel._is_system_folder - A
    M 244:4 FolderSystemModel.collapse_folder - A
    M 249:4 FolderSystemModel._set_loading_state - A
    M 254:4 FolderSystemModel.is_loading - A
    M 258:4 FolderSystemModel.on_folder_clicked - A
core\amv_models\pairing_model.py
    M 26:4 PairingModel.load_unpair_files - A
    M 127:4 PairingModel.delete_unpaired_archives - A
    M 160:4 PairingModel.delete_unpaired_images - A
    M 193:4 PairingModel.create_asset_from_pair - A
    C 12:0 PairingModel - A
    M 70:4 PairingModel._create_default_unpair_files - A
    M 89:4 PairingModel.save_unpair_files - A
    M 110:4 PairingModel.remove_paired_files - A
    M 117:4 PairingModel.add_unpaired_archive - A
    M 122:4 PairingModel.add_unpaired_image - A
    M 13:4 PairingModel.__init__ - A
    M 20:4 PairingModel.set_work_folder - A
    M 104:4 PairingModel.get_unpaired_archives - A
    M 107:4 PairingModel.get_unpaired_images - A
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
    M 32:4 WorkspaceFoldersModel._load_folders_from_config - C
    M 103:4 WorkspaceFoldersModel.add_folder - B
    M 169:4 WorkspaceFoldersModel.update_folder - B
    C 10:0 WorkspaceFoldersModel - A
    M 146:4 WorkspaceFoldersModel.remove_folder - A
    M 215:4 WorkspaceFoldersModel.get_folder_by_path - A
    M 222:4 WorkspaceFoldersModel.get_enabled_folders - A
    M 22:4 WorkspaceFoldersModel.load_folders - A
    M 205:4 WorkspaceFoldersModel._update_config - A
    M 15:4 WorkspaceFoldersModel.__init__ - A
    M 99:4 WorkspaceFoldersModel.get_folders - A
core\amv_views\amv_view.py
    M 523:4 AmvView.remove_asset_tiles - C
    M 156:4 AmvView.update_workspace_folder_buttons - B
    M 500:4 AmvView.update_toggle_button_text - B
    M 249:4 AmvView._position_control_panel - A
    C 35:0 AmvView - A
    M 373:4 AmvView._create_control_panel - A
    M 131:4 AmvView._create_folder_tree_view - A
    M 366:4 AmvView.update_gallery_placeholder - A
    M 569:4 AmvView.showEvent - A
    M 580:4 AmvView.resizeEvent - A
    M 45:4 AmvView.__init__ - A
    M 52:4 AmvView._load_icons - A
    M 57:4 AmvView._setup_ui - A
    M 79:4 AmvView._create_left_panel - A
    M 93:4 AmvView._create_left_panel_header - A
    M 145:4 AmvView._create_folder_buttons_panel - A
    M 224:4 AmvView._create_gallery_panel - A
    M 298:4 AmvView._create_edge_button - A
    M 309:4 AmvView._create_scroll_area - A
    M 336:4 AmvView._create_gallery_content_widget - A
    M 492:4 AmvView._on_splitter_moved - A
    M 496:4 AmvView.update_splitter_sizes - A
    M 515:4 AmvView._on_collapse_tree_clicked - A
    M 519:4 AmvView._on_expand_tree_clicked - A
core\amv_views\asset_tile_pool.py
    M 58:4 AssetTilePool.release - A
    C 15:0 AssetTilePool - A
    M 27:4 AssetTilePool.acquire - A
    M 74:4 AssetTilePool.clear - A
    M 21:4 AssetTilePool.__init__ - A
core\amv_views\asset_tile_view.py
    M 682:4 AssetTileView._cleanup_connections_and_resources - C
    M 289:4 AssetTileView._setup_asset_tile_ui - B
    M 602:4 AssetTileView._on_checkbox_state_changed - B
    M 728:4 AssetTileView._clear_ui_elements - B
    M 69:4 AssetTileView.update_asset_data - B
    M 452:4 AssetTileView.mousePressEvent - B
    M 408:4 AssetTileView._load_icon_with_fallback - A
    M 500:4 AssetTileView._start_drag - A
    M 571:4 AssetTileView._update_stars_visibility - A
    C 31:0 AssetTileView - A
    M 281:4 AssetTileView.update_ui - A
    M 116:4 AssetTileView._setup_ui - A
    M 343:4 AssetTileView._on_thumbnail_loaded - A
    M 349:4 AssetTileView._on_thumbnail_error - A
    M 355:4 AssetTileView._set_thumbnail_pixmap - A
    M 378:4 AssetTileView._setup_folder_tile_ui - A
    M 485:4 AssetTileView.mouseMoveEvent - A
    M 630:4 AssetTileView.get_star_rating - A
    M 170:4 AssetTileView._setup_ui_without_styles - A
    M 333:4 AssetTileView._load_thumbnail_async - A
    M 542:4 AssetTileView._on_thumbnail_clicked - A
    M 552:4 AssetTileView._on_filename_clicked - A
    M 634:4 AssetTileView.set_star_rating - A
    M 639:4 AssetTileView._on_star_clicked - A
    M 651:4 AssetTileView.clear_stars - A
    M 748:4 AssetTileView._remove_from_parent - A
    M 755:4 AssetTileView._update_thumbnail_size - A
    M 42:4 AssetTileView.__init__ - A
    M 107:4 AssetTileView.reset_for_pool - A
    M 402:4 AssetTileView._create_placeholder_thumbnail - A
    M 433:4 AssetTileView._load_folder_icon - A
    M 440:4 AssetTileView._load_texture_icon - A
    M 445:4 AssetTileView._load_empty_texture_spacer - A
    M 562:4 AssetTileView.update_thumbnail_size - A
    M 578:4 AssetTileView.release_resources - A
    M 583:4 AssetTileView.is_checked - A
    M 587:4 AssetTileView.set_checked - A
    M 655:4 AssetTileView.set_drag_and_drop_enabled - A
    M 659:4 AssetTileView._check_stars_fit - A
    M 670:4 AssetTileView.resizeEvent - A
    M 719:4 AssetTileView._reset_state_variables - A
core\amv_views\folder_tree_view.py
    M 80:4 CustomFolderTreeView.contextMenuEvent - B
    M 288:4 CustomFolderTreeView.dragMoveEvent - B
    M 376:4 CustomFolderTreeView._get_drop_target_info - B
    M 431:4 CustomFolderTreeView._can_perform_drop - B
    M 516:4 CustomFolderTreeView._on_current_folder_changed - B
    M 330:4 CustomFolderTreeView.dropEvent - A
    M 491:4 CustomFolderTreeView._clear_folder_highlight - A
    C 17:0 CustomFolderTreeView - A
    M 417:4 CustomFolderTreeView._get_assets_to_move - A
    M 473:4 CustomFolderTreeView._highlight_folder_at_position - A
    M 175:4 CustomFolderTreeView._toggle_asset_counts - A
    M 191:4 CustomFolderTreeView._toggle_recursive_counts - A
    M 207:4 CustomFolderTreeView._get_show_asset_counts - A
    M 217:4 CustomFolderTreeView._get_recursive_asset_counts - A
    M 231:4 CustomFolderTreeView._open_folder_in_explorer - A
    M 249:4 CustomFolderTreeView._rebuild_assets_in_folder - A
    M 259:4 CustomFolderTreeView._refresh_folder - A
    M 269:4 CustomFolderTreeView.dragEnterEvent - A
    M 366:4 CustomFolderTreeView._validate_drop_event - A
    M 75:4 CustomFolderTreeView._connect_selection_model - A
    M 457:4 CustomFolderTreeView._perform_drop_operation - A
    M 506:4 CustomFolderTreeView._on_item_expanded - A
    M 511:4 CustomFolderTreeView._on_item_collapsed - A
    M 24:4 CustomFolderTreeView.__init__ - A
    M 45:4 CustomFolderTreeView.set_models - A
    M 58:4 CustomFolderTreeView.set_rebuild_callback - A
    M 62:4 CustomFolderTreeView.set_open_in_explorer_callback - A
    M 66:4 CustomFolderTreeView.set_refresh_folder_callback - A
    M 70:4 CustomFolderTreeView.setModel - A
    M 227:4 CustomFolderTreeView.set_folder_tree_controller - A
    M 283:4 CustomFolderTreeView.dragLeaveEvent - A
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
    M 70:4 PreviewTile.load_thumbnail - A
    C 15:0 PreviewTile - A
    M 104:4 PreviewTile._on_thumbnail_clicked - A
    M 108:4 PreviewTile._on_filename_clicked - A
    M 19:4 PreviewTile.__init__ - A
    M 27:4 PreviewTile.init_ui - A
    M 91:4 PreviewTile._create_placeholder_thumbnail - A
    M 112:4 PreviewTile._on_checkbox_state_changed - A
    M 115:4 PreviewTile.is_checked - A
    M 118:4 PreviewTile.set_checked - A
    M 121:4 PreviewTile.update_thumbnail_size - A
core\tools\base_worker.py
    M 57:4 BaseWorker._validate_file_paths - A
    M 83:4 BaseWorker._validate_single_file_path - A
    M 130:4 BaseWorker._validate_output_path - A
    C 13:0 BaseWorker - A
    M 25:4 BaseWorker.run - A
    M 111:4 BaseWorker._validate_input_file - A
    M 45:4 BaseWorker.stop - A
    M 20:4 BaseWorker.__init__ - A
    M 39:4 BaseWorker._run_operation - A
    M 155:4 BaseWorker._handle_pillow_import_error - A
    M 160:4 BaseWorker._handle_operation_error - A
core\tools\duplicate_finder_worker.py
    M 172:4 DuplicateFinderWorker._move_related_files - C
    C 18:0 DuplicateFinderWorker - A
    M 108:4 DuplicateFinderWorker._find_duplicates - A
    M 140:4 DuplicateFinderWorker._move_duplicates_to_folder - A
    M 28:4 DuplicateFinderWorker._run_operation - A
    M 63:4 DuplicateFinderWorker._find_archive_files - A
    M 77:4 DuplicateFinderWorker._calculate_file_hashes - A
    M 126:4 DuplicateFinderWorker._prepare_files_to_move - A
    M 100:4 DuplicateFinderWorker._calculate_sha256 - A
    M 24:4 DuplicateFinderWorker.__init__ - A
core\tools\file_renamer_worker.py
    M 65:4 FileRenamerWorker._perform_renaming - C
    M 156:4 FileRenamerWorker._analyze_files - C
    C 18:0 FileRenamerWorker - B
    M 36:4 FileRenamerWorker._run_operation - A
    M 227:4 FileRenamerWorker._generate_random_name - A
    M 237:4 FileRenamerWorker._rename_file - A
    M 26:4 FileRenamerWorker.__init__ - A
    M 32:4 FileRenamerWorker.confirm_operation - A
core\tools\file_shortener_worker.py
    M 63:4 FileShortenerWorker._perform_shortening - C
    M 180:4 FileShortenerWorker._analyze_files - C
    C 16:0 FileShortenerWorker - B
    M 154:4 FileShortenerWorker._generate_unique_name - B
    M 34:4 FileShortenerWorker._run_operation - A
    M 251:4 FileShortenerWorker._rename_file - A
    M 24:4 FileShortenerWorker.__init__ - A
    M 30:4 FileShortenerWorker.confirm_operation - A
core\tools\image_resizer_worker.py
    M 25:4 ImageResizerWorker._run_operation - B
    C 16:0 ImageResizerWorker - B
    M 121:4 ImageResizerWorker._resize_image - B
    M 171:4 ImageResizerWorker._calculate_new_size - B
    M 93:4 ImageResizerWorker._find_files_to_resize - A
    M 22:4 ImageResizerWorker.__init__ - A
core\tools\prefix_suffix_remover_worker.py
    M 26:4 PrefixSuffixRemoverWorker._run_operation - C
    C 15:0 PrefixSuffixRemoverWorker - B
    M 21:4 PrefixSuffixRemoverWorker.__init__ - A
core\tools\webp_converter_worker.py
    M 25:4 WebPConverterWorker._run_operation - B
    M 142:4 WebPConverterWorker._convert_to_webp - B
    C 16:0 WebPConverterWorker - B
    M 118:4 WebPConverterWorker._find_files_to_convert - A
    M 22:4 WebPConverterWorker.__init__ - A
core\workers\asset_rebuilder_worker.py
    M 33:4 AssetRebuilderWorker.run - C
    M 81:4 AssetRebuilderWorker._remove_asset_files - B
    C 16:0 AssetRebuilderWorker - A
    M 101:4 AssetRebuilderWorker._remove_cache_folder - A
    M 119:4 AssetRebuilderWorker._run_scanner - A
    M 23:4 AssetRebuilderWorker.__init__ - A
    M 28:4 AssetRebuilderWorker.request_stop - A
core\workers\thumbnail_loader_worker.py
    C 20:0 ThumbnailLoaderWorker - A
    M 31:4 ThumbnailLoaderWorker.run - A
    C 14:0 ThumbnailLoaderSignals - A
    M 26:4 ThumbnailLoaderWorker.__init__ - A
core\workers\worker_manager.py
    C 10:0 WorkerManager - A
    M 14:4 WorkerManager.handle_progress - A
    M 21:4 WorkerManager.handle_finished - A
    M 42:4 WorkerManager.reset_button_state - A
    M 35:4 WorkerManager.handle_error - A

751 blocks (classes, functions, methods) analyzed.
Average complexity: A (3.0905459387483356)
```

---

## Maintainability Index (MI)

```text
core\amv_tab.py - A
core\file_utils.py - A
core\json_utils.py - A
core\main_window.py - A
core\pairing_tab.py - A
core\performance_monitor.py - A
core\preview_window.py - A
core\rules.py - A
core\scanner.py - A
core\selection_counter.py - A
core\thread_manager.py - A
core\thumbnail.py - A
core\thumbnail_cache.py - A
core\tools_tab.py - A
core\utilities.py - A
core\__init__.py - A
core\amv_controllers\amv_controller.py - A
core\amv_controllers\__init__.py - A
core\amv_controllers\handlers\asset_grid_controller.py - A
core\amv_controllers\handlers\asset_rebuild_controller.py - A
core\amv_controllers\handlers\control_panel_controller.py - A
core\amv_controllers\handlers\file_operation_controller.py - A
core\amv_controllers\handlers\folder_tree_controller.py - A
core\amv_controllers\handlers\signal_connector.py - A
core\amv_controllers\handlers\__init__.py - A
core\amv_models\amv_model.py - A
core\amv_models\asset_grid_model.py - A
core\amv_models\asset_tile_model.py - A
core\amv_models\config_manager_model.py - A
core\amv_models\control_panel_model.py - A
core\amv_models\drag_drop_model.py - A
core\amv_models\file_operations_model.py - A
core\amv_models\folder_system_model.py - A
core\amv_models\pairing_model.py - A
core\amv_models\selection_model.py - A
core\amv_models\workspace_folders_model.py - A
core\amv_models\__init__.py - A
core\amv_views\amv_view.py - A
core\amv_views\asset_tile_pool.py - A
core\amv_views\asset_tile_view.py - A
core\amv_views\folder_tree_view.py - A
core\amv_views\gallery_widgets.py - A
core\amv_views\preview_gallery_view.py - A
core\amv_views\preview_tile.py - A
core\amv_views\__init__.py - A
core\tools\base_worker.py - A
core\tools\duplicate_finder_worker.py - A
core\tools\file_renamer_worker.py - A
core\tools\file_shortener_worker.py - A
core\tools\image_resizer_worker.py - A
core\tools\prefix_suffix_remover_worker.py - A
core\tools\webp_converter_worker.py - A
core\tools\__init__.py - A
core\workers\asset_rebuilder_worker.py - A
core\workers\thumbnail_loader_worker.py - A
core\workers\worker_manager.py - A
core\workers\__init__.py - A
```
