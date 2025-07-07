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
from core.json_utils import load_from_file
from core.pairing_tab import PairingTab
from core.tools_tab import ToolsTab
from core.thread_manager import ThreadManager
from core.selection_counter import SelectionCounter

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
        
        # Initialize SelectionCounter (will be properly set up after AMV tab creation)
        self.selection_counter = None

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
            self._createStatusBar()

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

    def _createStatusBar(self):
        """
        Creates application status bar
        """
        try:
            self.status_bar = QStatusBar(self)
            self.setStatusBar(self.status_bar)

            # Container with three columns
            status_container = QWidget()
            status_layout = QHBoxLayout()
            status_layout.setContentsMargins(0, 0, 0, 0)
            status_layout.setSpacing(0)

            # Left column: messages
            self.status_message_label = QLabel("")
            self.status_message_label.setMinimumWidth(200)
            self.status_message_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            status_layout.addWidget(self.status_message_label, 2)

            # Center: centered progress bar
            center_widget = QWidget()
            center_layout = QHBoxLayout()
            center_layout.setContentsMargins(0, 0, 0, 0)
            center_layout.setSpacing(0)
            center_layout.addStretch(1)
            self.status_progress_bar = QProgressBar()
            self.status_progress_bar.setFixedHeight(12)
            self.status_progress_bar.setMinimumWidth(300)
            self.status_progress_bar.setMaximumWidth(360)
            self.status_progress_bar.setValue(0)
            self.status_progress_bar.setVisible(True)
            center_layout.addWidget(self.status_progress_bar)
            center_layout.addStretch(1)
            center_widget.setLayout(center_layout)
            status_layout.addWidget(center_widget, 1)

            # Right column: number of selected tiles
            self.selected_label = QLabel("Selected: 0")
            self.selected_label.setMinimumWidth(100)
            self.selected_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            status_layout.addWidget(self.selected_label, 2)

            status_container.setLayout(status_layout)
            self.status_bar.addWidget(status_container, 1)
            self.logger.debug("Status bar created successfully")
        except Exception as e:
            self.logger.error(f"Error creating status bar: {e}")

    def update_status(self, message, timeout=5000):
        """Updates the status message label with a new message"""
        try:
            if hasattr(self, "status_message_label") and self.status_message_label:
                self.status_message_label.setText(message)
                self.logger.debug(f"Status updated: {message}")
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")

    def show_log_info(self, log_level, message):
        """Displays log info in the status message label in a user-friendly way"""
        try:
            # Mapping log levels to friendly messages
            level_mapping = {
                "INFO": "ℹ️",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "DEBUG": "🔍",
                "CRITICAL": "🚨",
            }

            icon = level_mapping.get(log_level.upper(), "ℹ️")

            # Truncate long messages
            if len(message) > 100:
                message = message[:97] + "..."

            status_message = f"{icon} {message}"
            self.update_status(status_message)

        except Exception as e:
            self.logger.error(f"Error showing log info: {e}")

    def update_working_directory_status(self, directory_path):
        """Updates the status bar with information about the current working directory"""
        try:
            if directory_path:
                # Truncate long path for better readability
                if len(directory_path) > 80:
                    # Show only last parts of path
                    parts = directory_path.split("\\")
                    if len(parts) > 3:
                        short_path = f"...\\{'\\'.join(parts[-3:])}"
                    else:
                        short_path = directory_path
                else:
                    short_path = directory_path

                status_message = f"📁 Working directory: {short_path}"
                self.update_status(status_message, timeout=0)  # No timeout
                self.logger.debug(f"Working directory status updated: {directory_path}")
        except Exception as e:
            self.logger.error(f"Error updating working directory status: {e}")

    def update_selection_status(
        self, selected_count=None, filtered_count=None, total_count=None
    ):
        """Updates the number of selected assets on the right side of the status bar"""
        try:
            if not self._validate_components():
                return
                
            # Use provided counts or calculate via SelectionCounter
            if self._has_provided_counts(selected_count, filtered_count, total_count):
                summary = {
                    'selected': selected_count,
                    'visible': filtered_count,
                    'total': total_count
                }
                self.logger.debug(f"Using provided counts: {summary}")
            else:
                summary = self.selection_counter.get_selection_summary()
                self.logger.debug(f"Calculated counts: {summary}")
            
            # Generate and set status text
            status_text = self.selection_counter.get_status_text(summary)
            self._update_status_label(status_text)
            
        except Exception as e:
            self._handle_status_error(e)
    
    def _validate_components(self) -> bool:
        """Validate that required components are available for status update"""
        if not hasattr(self, "amv_tab") or not self.amv_tab:
            self.logger.debug("AMV tab not available")
            return False
            
        if not self.selection_counter:
            self.logger.debug("SelectionCounter not available")
            return False
            
        return True
    
    def _has_provided_counts(self, selected_count, filtered_count, total_count) -> bool:
        """Check if external counts were provided"""
        return selected_count is not None and filtered_count is not None and total_count is not None
    
    def _update_status_label(self, status_text: str):
        """Update the status label with new text"""
        if hasattr(self, "selected_label") and self.selected_label:
            self.selected_label.setText(status_text)
            self.logger.debug(f"Updated status bar: {status_text}")
    
    def _handle_status_error(self, error: Exception):
        """Handle errors in status update with fallback"""
        self.logger.error(f"Error updating selection status: {error}")
        if hasattr(self, "selected_label") and self.selected_label:
            self.selected_label.setText("Selected: 0")

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
        """Calculate visible and total asset counts using SelectionCounter"""
        if not self.selection_counter:
            logger.warning("SelectionCounter not available for asset counting")
            return AssetCounts(visible=0, total=0)
        
        visible_count = self.selection_counter.count_visible_assets()
        total_count = self.selection_counter.count_total_assets()
        
        self.logger.debug(f"Visible assets: {visible_count}, Total assets: {total_count}")
        return AssetCounts(visible=visible_count, total=total_count)
    
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
    
    def _get_tabs_configuration(self) -> list:
        """Get configuration for tabs to create"""
        return [
            (AmvTab, "Asset Browser", True),  # True = critical tab (main)
            (PairingTab, "Pairing", False),
            (ToolsTab, "Tools", False),
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
            self._initialize_selection_counter()
        elif isinstance(tab_instance, PairingTab):
            self.pairing_tab = tab_instance
        elif isinstance(tab_instance, ToolsTab):
            self.tools_tab = tab_instance
            # Force deactivation of buttons on startup
            self.tools_tab.clear_working_directory()
    
    def _initialize_selection_counter(self):
        """Initialize SelectionCounter after AMV tab is ready"""
        try:
            amv_controller = self.amv_tab.get_controller()
            if amv_controller:
                self.selection_counter = SelectionCounter(amv_controller)
                self.logger.info("SelectionCounter initialized")
            else:
                self.logger.warning("Could not initialize SelectionCounter - no AMV controller")
        except Exception as e:
            self.logger.error(f"Error initializing SelectionCounter: {e}")
            self.selection_counter = None
    
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
        """Calculate all asset counts using SelectionCounter"""
        if not self.selection_counter:
            logger.warning("SelectionCounter not available for detailed asset counting")
            return AssetCountsDetailed(selected=0, filtered=0, total=0)
        
        summary = self.selection_counter.get_selection_summary()
        
        return AssetCountsDetailed(
            selected=summary['selected'],
            filtered=summary['visible'], 
            total=summary['total']
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
