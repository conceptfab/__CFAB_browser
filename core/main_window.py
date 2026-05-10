import logging
import sys
from collections import namedtuple

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QProgressBar,
    QHBoxLayout,
    QSizePolicy,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from core.amv_tab import AmvTab
from core.console_tab import ConsoleTab
from core.json_utils import load_from_file
from core.pairing_tab import PairingTab
from core.tools_tab import ToolsTab
from core.thread_manager import ThreadManager
from core.managers.status_bar_manager import StatusBarManager

# Global logger instance for functions outside the class
logger = logging.getLogger(__name__)

# Data structures for asset counts (used in refactored functions)
AssetCounts = namedtuple('AssetCounts', ['visible', 'total'])
AssetCountsDetailed = namedtuple('AssetCountsDetailed', ['selected', 'filtered', 'total'])


class MainWindow(QMainWindow):

    def __init__(self, config_path="config.json"):
        super().__init__()

        # Initialize ThreadManager early
        self.thread_manager = ThreadManager()
        logger.info("ThreadManager initialized")

        self.status_bar_manager = None

        # Default configuration as class field
        self.default_config = {
            "logger_level": "INFO",
            "use_styles": True,
            "thumbnail": 256,
            "work_folder1": {"path": "", "name": "", "icon": "", "color": ""},
            "work_folder2": {"path": "", "name": "", "icon": "", "color": ""},
            "work_folder3": {"path": "", "name": "", "icon": "", "color": ""},
            "work_folder4": {"path": "", "name": "", "icon": "", "color": ""},
            "work_folder5": {"path": "", "name": "", "icon": "", "color": ""},
        }

        self.config = self._load_config_safe(config_path)
        self._setup_logger()

        self.setWindowTitle("CFAB Browser")
        self.resize(1400, 600)
        self.setWindowIcon(QIcon("core/resources/img/icon.png"))

        try:
            self.logger.info("Creating menu bar...")
            self._createMenuBar()

            self.logger.info("Creating status bar...")
            self.status_bar_manager = StatusBarManager(self, self.logger)

            self.logger.info("Creating tabs...")
            self._createTabs()

            self.logger.info("Setting up log interceptor...")
            self.setup_log_interceptor()

            self.logger.info("Connecting signals...")
            self._connect_signals()

            self.logger.info("MainWindow initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing MainWindow: {e}")
            import traceback

            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise

        # Update initial selection status
        self.update_selection_status(0, 0, 0)

    def _load_config_safe(self, config_path):
        """Safely loads configuration with fallback to default values"""
        try:
            config = load_from_file(config_path)

            if not isinstance(config, dict):
                raise ValueError("Configuration must be a dictionary")

            for key, default_value in self.default_config.items():
                if key not in config:
                    config[key] = default_value

            return config

        except FileNotFoundError:
            print(
                f"Warning: Configuration file {config_path} not found. "
                "Using default configuration."
            )
            return self.default_config.copy()

        except (ValueError, UnicodeDecodeError) as e:
            print(
                f"Warning: Invalid JSON in {config_path}: {e}. "
                "Using default configuration."
            )
            return self.default_config.copy()

        except PermissionError:
            print(
                f"Warning: Permission denied reading {config_path}. "
                "Using default configuration."
            )
            return self.default_config.copy()

        except Exception as e:
            print(
                f"Warning: Unexpected error loading config {config_path}: {e}. "
                "Using default configuration."
            )
            return self.default_config.copy()

    def _setup_logger(self):
        """
        Configures logger based on loaded configuration
        """
        try:
            logger_level = self.config.get("logger_level", "INFO")

            # Check if logging level is correct
            if not hasattr(logging, logger_level):
                logger_level = "INFO"
                print("Warning: Invalid logger level in config. Using INFO.")

            # Configure logger only if not already configured
            if not logging.getLogger().handlers:
                logging.basicConfig(
                    level=getattr(logging, logger_level),
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                )

            self.logger = logging.getLogger(__name__)
            self.logger.info(f"Logger initialized with level: {logger_level}")

        except Exception as e:
            # Fallback logger setup
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
            self.logger.error(f"Error setting up logger: {e}")

    def _createMenuBar(self):
        """
        Creates menu bar with proper error handling
        """
        try:
            menu_bar = QMenuBar(self)
            file_menu = QMenu("File", self)
            exit_action = QAction("Exit", self)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            menu_bar.addMenu(file_menu)
            self.setMenuBar(menu_bar)
            self.logger.debug("Menu bar created successfully")

        except Exception as e:
            self.logger.error(f"Error creating menu bar: {e}")
            # Menu bar is not critical - application can work without it

    def _createTabs(self):
        """Creates application tabs with comprehensive error handling"""
        try:
            self._initialize_tab_references()
            
            tabs_config = self._get_tabs_configuration()
            successful_tabs = self._create_tabs_from_config(tabs_config)
            
            self._validate_tabs_creation(successful_tabs, len(tabs_config))
            
        except Exception as e:
            self.logger.error(f"Critical error creating tabs: {e}")
            # Tabs are critical - if they don't load, application is meaningless
            raise RuntimeError(f"Failed to initialize application tabs: {e}")

    def update_status(self, message, timeout=5000):
        if self.status_bar_manager:
            self.status_bar_manager.update_status(message, timeout)

    def show_log_info(self, log_level, message):
        if self.status_bar_manager:
            self.status_bar_manager.show_log_info(log_level, message)

    def update_working_directory_status(self, directory_path):
        if self.status_bar_manager:
            self.status_bar_manager.update_working_directory_status(directory_path)

    def update_selection_status(
        self, selected_count=None, filtered_count=None, total_count=None
    ):
        try:
            if not hasattr(self, "amv_tab") or not self.amv_tab:
                return

            if self._has_provided_counts(selected_count, filtered_count, total_count):
                summary = {
                    "selected": selected_count,
                    "visible": filtered_count,
                    "total": total_count,
                }
            else:
                summary = self._compute_selection_summary()

            status_text = self._format_status_text(summary)
            if self.status_bar_manager:
                self.status_bar_manager.update_selection_status(status_text)

        except Exception as e:
            self._handle_status_error(e)

    def _has_provided_counts(self, selected_count, filtered_count, total_count) -> bool:
        """Check if external counts were provided"""
        return selected_count is not None and filtered_count is not None and total_count is not None

    def _compute_selection_summary(self) -> dict:
        """Pulls selected/visible/total directly from the authoritative models.
        SelectionModel owns the selected set; tiles/original_assets own visible/total."""
        controller = self.amv_tab.get_controller() if self.amv_tab else None
        if controller is None:
            return {"selected": 0, "visible": 0, "total": 0}

        selected = 0
        selection_model = getattr(getattr(controller, "model", None), "selection_model", None)
        if selection_model is not None:
            selected = len(selection_model.get_selected_asset_ids())

        grid = getattr(controller, "asset_grid_controller", None)
        visible = self._count_visible_tiles(grid)
        total = self._count_total_assets(grid)

        return {"selected": selected, "visible": visible, "total": total}

    def _count_visible_tiles(self, grid_controller) -> int:
        if grid_controller is None:
            return 0
        tiles = getattr(grid_controller, "asset_tiles", None) or []
        return sum(
            1 for tile in tiles
            if getattr(tile, "model", None)
            and not getattr(tile.model, "is_special_folder", False)
        )

    def _count_total_assets(self, grid_controller) -> int:
        if grid_controller is None or not hasattr(grid_controller, "get_original_assets"):
            return 0
        originals = grid_controller.get_original_assets() or []
        return sum(1 for asset in originals if asset.get("type") != "special_folder")

    @staticmethod
    def _format_status_text(summary: dict) -> str:
        selected = summary.get("selected", 0)
        visible = summary.get("visible", 0)
        total = summary.get("total", 0)
        text = f"Selected: {selected}"
        if visible != total and total > 0:
            text += f" (visible: {visible}/{total})"
        return text
    
    def _update_status_label(self, status_text: str):
        if self.status_bar_manager:
            self.status_bar_manager.update_selection_status(status_text)
    
    def _handle_status_error(self, error: Exception):
        self.logger.error(f"Error updating selection status: {error}")
        if self.status_bar_manager:
            self.status_bar_manager.update_selection_status("Selected: 0")

    def show_operation_status(self, operation_name, status="completed"):
        """Displays operation status in the status bar"""
        try:
            status_icons = {
                "completed": "✅",
                "started": "🔄",
                "failed": "❌",
                "processing": "⏳",
            }

            icon = status_icons.get(status, "ℹ️")
            status_message = f"{icon} {operation_name}"
            self.update_status(status_message)

        except Exception as e:
            self.logger.error(f"Error showing operation status: {e}")

    def setup_log_interceptor(self):
        """Configures log capturing for display in the status bar"""
        try:
            # Add handler for capturing important messages
            class StatusBarHandler(logging.Handler):
                def __init__(self, main_window):
                    super().__init__()
                    self.main_window = main_window

                def emit(self, record):
                    try:
                        # Check if this is an important message to display
                        if self._should_show_in_status(record):
                            self.main_window.show_log_info(
                                record.levelname, record.getMessage()
                            )
                    except Exception as e:
                        logger.debug(f"Exception in status handler: {e}")

                def _should_show_in_status(self, record):
                    """Checks if the message should be shown in the status bar"""
                    important_messages = [
                        "working directory",
                        "folder clicked",
                        "asset grid rebuilt",
                        "scanning",
                        "completed",
                        "error",
                        "failed",
                    ]

                    message = record.getMessage().lower()
                    return any(keyword in message for keyword in important_messages)

            # Add handler to main logger
            status_handler = StatusBarHandler(self)
            status_handler.setLevel(logging.INFO)
            logging.getLogger().addHandler(status_handler)

            self.logger.info("Log interceptor set up for status bar")

        except Exception as e:
            self.logger.error(f"Error setting up log interceptor: {e}")

    def _connect_signals(self):
        """Simplified method for connecting signals"""
        signal_connections = [
            (self._connect_amv_signals, "AMV"),
            (self._connect_status_signals, "Status"),
            (self._connect_tools_signals, "Tools"),
        ]

        for connect_method, component_name in signal_connections:
            try:
                connect_method()
                self.logger.info(f"Successfully connected {component_name} signals.")
            except Exception as e:
                self.logger.error(f"Error connecting {component_name} signals: {e}")

    def _connect_amv_signals(self):
        """Connects AMV Tab signals"""
        if not self.amv_tab:
            self.logger.error("AMV tab is not initialized; cannot connect signals.")
            return
        amv_controller = self.amv_tab.get_controller()
        if not amv_controller:
            self.logger.error("Could not get AMV controller to connect signals.")
            return

        amv_controller.working_directory_changed.connect(
            self.pairing_tab.on_working_directory_changed
        )
        amv_controller.working_directory_changed.connect(
            self.update_working_directory_status
        )
        if self.tools_tab:
            self.logger.info("Connecting working_directory_changed signal with ToolsTab")
            amv_controller.working_directory_changed.connect(
                self.tools_tab.set_working_directory
            )
            self.logger.info("working_directory_changed signal connected with ToolsTab")
        if hasattr(amv_controller.model, "selection_model"):
            amv_controller.model.selection_model.selection_changed.connect(
                self._on_selection_changed
            )
        if hasattr(amv_controller.model, "asset_grid_model"):
            amv_controller.model.asset_grid_model.assets_changed.connect(
                self._on_assets_changed
            )
        self.update_selection_status(0, 0, 0)

    def _connect_status_signals(self):
        """Connects Status Bar signals"""
        # Connect status signals, to be expanded if needed
        pass

    def _connect_tools_signals(self):
        """Connects Tools Tab signals"""
        if self.tools_tab:
            # Connect folder structure refresh signal with AMV tab
            self.tools_tab.folder_structure_changed.connect(
                self._on_folder_structure_changed
            )
            logger.info("Connected folder_structure_changed signal with AMV tab")
        
        # Connect working directory changes to update pairing tab indicator
        if self.amv_tab:
            amv_controller = self.amv_tab.get_controller()
            if amv_controller:
                amv_controller.working_directory_changed.connect(
                    self._on_working_directory_changed_for_pairing
                )
                logger.info("Connected working_directory_changed signal for pairing tab indicator")
        
        # Connect pairing changes to update pairing tab indicator  
        if self.pairing_tab:
            self.pairing_tab.pairing_changed.connect(
                self._update_pairing_tab_indicator
            )
            logger.info("Connected pairing_changed signal for pairing tab indicator")

    def _on_folder_structure_changed(self, folder_path: str):
        """Handles folder structure change - refreshes the folder tree"""
        try:
            if self.amv_tab:
                amv_controller = self.amv_tab.get_controller()
                if amv_controller and hasattr(amv_controller, 'folder_tree_controller'):
                    # Call folder refresh
                    amv_controller.folder_tree_controller.on_folder_refresh_requested(folder_path)
                    logger.info(f"Refreshed folder tree for: {folder_path}")
        except Exception as e:
            logger.error(f"Error while refreshing folder tree: {e}")

    def _on_working_directory_changed_for_pairing(self, folder_path: str):
        """Update pairing tab indicator when working directory changes"""
        try:
            logger.info(f"Updating pairing tab indicator for: {folder_path}")
            self._update_pairing_tab_indicator(folder_path)
        except Exception as e:
            logger.error(f"Error updating pairing tab indicator: {e}")

    def _update_pairing_tab_indicator(self, folder_path: str = None):
        """Update pairing tab title with indicator if unpaired files exist"""
        try:
            tab_index = self._find_pairing_tab_index()
            if tab_index == -1:
                return
                
            unpaired_count = self._count_unpaired_files(folder_path)
            tab_text = self._generate_tab_text(unpaired_count)
            self._set_tab_text_safely(tab_index, tab_text)
            
            # Log results
            if unpaired_count > 0:
                logger.info(f"Pairing tab indicator: Found {unpaired_count} unpaired files in {folder_path}")
            else:
                logger.debug("No unpaired files found - using normal tab text")
                
        except Exception as e:
            self._handle_tab_indicator_error(e)

    def _on_selection_changed(self, selected_asset_ids):
        """Handles selection change and updates the status bar"""
        try:
            selected_count = len(selected_asset_ids)
            self.logger.debug(f"Selection changed: {selected_count} items selected")
            
            controller_data = self._get_asset_controller_data()
            counts = self._calculate_asset_counts(controller_data)
            self.update_selection_status(selected_count, counts.visible, counts.total)
            
        except Exception as e:
            self._handle_selection_change_error(e, selected_count)

    def _on_assets_changed(self, assets):
        """Handles asset change and updates the status bar"""
        try:
            controller = self._get_amv_controller()
            if not controller:
                return
                
            counts = self._calculate_current_asset_counts(controller)
            self.update_selection_status(counts.selected, counts.filtered, counts.total)
            
        except Exception as e:
            self.logger.error(f"Error handling assets change: {e}")

    def closeEvent(self, event):
        """Handles application closing - stops all threads using ThreadManager"""
        try:
            self.logger.info("Closing application...")
            
            # Use ThreadManager for centralized thread management
            success = self.thread_manager.stop_all_threads(timeout_ms=5000)
            
            if not success:
                self.logger.warning("Some threads did not stop gracefully")
                # Optional: Ask user if they want to force close or wait
                # For now, we accept the close event anyway
            
            self.logger.info("Application closing completed")
            
        except Exception as e:
            self.logger.error(f"Error during application shutdown: {e}")
            # Even if there's an error, we should still allow the application to close
            # Use emergency stop as last resort
            try:
                self.thread_manager.emergency_stop_all()
            except Exception as emergency_error:
                self.logger.error(f"Emergency stop failed: {emergency_error}")

        # Detach the in-app console so logging/stdio don't reference dead Qt objects.
        if self.console_tab is not None:
            try:
                self.console_tab.shutdown()
            except Exception as console_error:
                self.logger.error(f"Error shutting down console tab: {console_error}")

        # Always accept the close event
        event.accept()

    # ===============================================
    # HELPER FUNCTIONS FOR _update_pairing_tab_indicator 
    # ===============================================
    
    def _find_pairing_tab_index(self) -> int:
        """Find index of pairing tab in tabs widget"""
        if not self.pairing_tab:
            logger.debug("No pairing tab available")
            return -1
            
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) == self.pairing_tab:
                return i
                
        logger.warning("Could not find pairing tab index")
        return -1
    
    def _count_unpaired_files(self, folder_path: str) -> int:
        """Count unpaired files in given folder"""
        if not folder_path or not hasattr(self.pairing_tab, 'model') or not self.pairing_tab.model:
            return 0
            
        unpaired_archives = self.pairing_tab.model.get_unpaired_archives()
        unpaired_images = self.pairing_tab.model.get_unpaired_images()
        total_count = len(unpaired_archives) + len(unpaired_images)
        
        logger.debug(f"Found {len(unpaired_archives)} unpaired archives and {len(unpaired_images)} unpaired images")
        return total_count
    
    def _generate_tab_text(self, unpaired_count: int) -> str:
        """Generate appropriate tab text based on unpaired files count"""
        if unpaired_count > 0:
            return f"⚠️ Pairing ({unpaired_count})"
        else:
            return "Pairing"
    
    def _set_tab_text_safely(self, tab_index: int, text: str):
        """Safely set tab text with validation"""
        if tab_index >= 0:
            self.tabs.setTabText(tab_index, text)
            logger.debug(f"Updated pairing tab text to: '{text}'")
    
    def _handle_tab_indicator_error(self, error: Exception):
        """Handle errors in tab indicator update with fallback"""
        logger.error(f"Error updating pairing tab indicator: {error}")
        
        # Fallback - set normal text
        try:
            if hasattr(self, 'pairing_tab') and self.pairing_tab:
                fallback_index = self._find_pairing_tab_index()
                if fallback_index >= 0:
                    self.tabs.setTabText(fallback_index, "Pairing")
        except Exception as fallback_error:
            logger.error(f"Critical error in pairing tab fallback: {fallback_error}")

    # ===============================================
    # HELPER FUNCTIONS FOR _on_selection_changed 
    # ===============================================
    
    def _get_asset_controller_data(self) -> dict:
        """Get asset controller and its data"""
        amv_controller = self.amv_tab.get_controller()
        
        if not amv_controller or not hasattr(amv_controller, "asset_grid_controller"):
            return {"controller": None, "grid_controller": None}
            
        asset_grid_controller = amv_controller.asset_grid_controller
        return {
            "controller": amv_controller, 
            "grid_controller": asset_grid_controller
        }
    
    # ===============================================
    # NOWE METODY POMOCNICZE - REFAKTORYZACJA _calculate_asset_counts
    # ===============================================
    
    def _validate_grid_controller(self, controller_data: dict) -> bool:
        """Validate grid controller from controller data
        
        Args:
            controller_data: Dictionary containing controller information
            
        Returns:
            bool: True if grid_controller is valid, False otherwise
        """
        grid_controller = controller_data.get("grid_controller")
        return grid_controller is not None
    
    def _filter_non_special_assets(self, assets) -> list:
        """Filter out special folder assets from asset list
        
        Args:
            assets: List of asset objects or tiles
            
        Returns:
            list: Filtered list without special folder assets
        """
        if not assets:
            return []
            
        # Handle tile objects (from asset_tiles)
        if hasattr(assets[0], 'model') if assets else False:
            return [
                tile for tile in assets
                if (hasattr(tile, "model") and tile.model 
                    and not tile.model.is_special_folder)
            ]
        
        # Handle asset data dictionaries (from original_assets)
        return [
            asset for asset in assets 
            if asset.get("type") != "special_folder"
        ]
    


    def _calculate_asset_counts(self, controller_data: dict) -> AssetCounts:
        """Calculate visible and total asset counts straight from the grid."""
        grid = controller_data.get("grid_controller") if controller_data else None
        return AssetCounts(
            visible=self._count_visible_tiles(grid),
            total=self._count_total_assets(grid),
        )
    
    def _handle_selection_change_error(self, error: Exception, selected_count: int):
        """Handle errors during selection change"""
        self.logger.error(f"Error handling selection change: {error}")
        # Fallback - update only with selected_count
        self.update_selection_status(selected_count, 0, 0)

    # ===============================================
    # HELPER FUNCTIONS FOR _createTabs 
    # ===============================================
    
    def _initialize_tab_references(self):
        """Initialize tab instance references"""
        self.tabs = QTabWidget()
        self.amv_tab = None
        self.pairing_tab = None
        self.tools_tab = None
        self.console_tab = None

    def _get_tabs_configuration(self) -> list:
        """Get configuration for tabs to create"""
        return [
            (AmvTab, "Asset Browser", True),  # True = critical tab (main)
            (PairingTab, "Pairing", False),
            (ToolsTab, "Tools", False),
            (ConsoleTab, "Console", False),
        ]
    
    def _create_tabs_from_config(self, config: list) -> int:
        """Create tabs from configuration, return success count"""
        successful_tabs = 0
        
        for tab_class, tab_name, is_critical in config:
            try:
                success = self._create_single_tab(tab_class, tab_name, is_critical)
                if success:
                    successful_tabs += 1
                    self.logger.debug(f"Tab '{tab_name}' created successfully")
            except Exception as e:
                self.logger.error(f"Error creating tab '{tab_name}': {e}")
                if is_critical:
                    self._create_error_placeholder(tab_name, e)
                    successful_tabs += 1
        
        return successful_tabs
    
    def _create_single_tab(self, tab_class, tab_name: str, is_critical: bool) -> bool:
        """Create single tab instance with error handling"""
        # Create tab instance with special handling for AmvTab
        if tab_class is AmvTab:
            tab_instance = AmvTab(main_window=self)
        else:
            tab_instance = tab_class()
        
        # Set appropriate instance reference and setup special features
        self._setup_special_tab_features(tab_instance, tab_class)
        
        # Add tab to widget
        self.tabs.addTab(tab_instance, tab_name)
        return True
    
    def _setup_special_tab_features(self, tab_instance, tab_class):
        """Setup special features for specific tab types"""
        if isinstance(tab_instance, AmvTab):
            self.amv_tab = tab_instance
        elif isinstance(tab_instance, PairingTab):
            self.pairing_tab = tab_instance
        elif isinstance(tab_instance, ToolsTab):
            self.tools_tab = tab_instance
            # Force deactivation of buttons on startup
            self.tools_tab.clear_working_directory()
        elif isinstance(tab_instance, ConsoleTab):
            self.console_tab = tab_instance
    
    def _create_error_placeholder(self, tab_name: str, error: Exception):
        """Create error placeholder for critical tabs that failed to load"""
        placeholder = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Error loading {tab_name}: {error}"))
        placeholder.setLayout(layout)
        self.tabs.addTab(placeholder, f"{tab_name} (Error)")
    
    def _validate_tabs_creation(self, successful_tabs: int, total_tabs: int):
        """Validate that tabs were created successfully"""
        if successful_tabs == 0:
            raise RuntimeError("Failed to create any tabs")
        
        self.setCentralWidget(self.tabs)
        self.logger.info(f"Tabs created successfully ({successful_tabs}/{total_tabs})")

    # ===============================================
    # HELPER FUNCTIONS FOR _on_assets_changed 
    # ===============================================
    
    def _get_amv_controller(self):
        """Get AMV controller with validation"""
        return self.amv_tab.get_controller()
    
    def _calculate_current_asset_counts(self, controller) -> AssetCountsDetailed:
        """Pull selected/visible/total from the authoritative models directly."""
        summary = self._compute_selection_summary()
        return AssetCountsDetailed(
            selected=summary["selected"],
            filtered=summary["visible"],
            total=summary["total"],
        )
    



if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Critical error starting application: {e}")
        sys.exit(1)
