import logging
import sys

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
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtCore import Qt

from core.amv_tab import AmvTab
from core.json_utils import load_from_file
from core.pairing_tab import PairingTab
from core.tools_tab import ToolsTab


class MainWindow(QMainWindow):

    def __init__(self, config_path="config.json"):
        super().__init__()

        # Domyślna konfiguracja jako pole klasy
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

            # Sprawdź czy poziom logowania jest poprawny
            if not hasattr(logging, logger_level):
                logger_level = "INFO"
                print("Warning: Invalid logger level in config. Using INFO.")

            # Konfiguracja loggera tylko jeśli nie został już skonfigurowany
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
            # Menu bar nie jest krytyczny - aplikacja może działać bez niego

    def _createTabs(self):
        """
        Creates application tabs with comprehensive error handling
        """
        try:
            self.tabs = QTabWidget()
            self.amv_tab = None
            self.pairing_tab = None
            self.tools_tab = None

            # Try to create each tab individually
            tabs_config = [
                (AmvTab, "Asset Browser", True),  # True = critical tab (main)
                (PairingTab, "Pairing", False),
                (ToolsTab, "Tools", False),
            ]

            successful_tabs = 0

            for tab_class, tab_name, is_critical in tabs_config:
                try:
                    if tab_class is AmvTab:
                        tab_instance = AmvTab(main_window=self)
                    else:
                        tab_instance = tab_class()

                    if isinstance(tab_instance, AmvTab):
                        self.amv_tab = tab_instance
                    elif isinstance(tab_instance, PairingTab):
                        self.pairing_tab = tab_instance
                    elif isinstance(tab_instance, ToolsTab):
                        self.tools_tab = tab_instance
                        # Wymuszenie dezaktywacji przycisków na starcie
                        self.tools_tab.clear_working_directory()

                    self.tabs.addTab(tab_instance, tab_name)
                    successful_tabs += 1
                    self.logger.debug(f"Tab '{tab_name}' created successfully")

                except Exception as e:
                    self.logger.error(f"Error creating tab '{tab_name}': {e}")
                    if is_critical:
                        # Jeśli krytyczny tab się nie załadował, dodaj placeholder
                        placeholder = QWidget()
                        layout = QVBoxLayout()
                        layout.addWidget(QLabel(f"Error loading {tab_name}: {e}"))
                        placeholder.setLayout(layout)
                        self.tabs.addTab(placeholder, f"{tab_name} (Error)")
                        successful_tabs += 1

            if successful_tabs == 0:
                raise RuntimeError("Failed to create any tabs")

            self.setCentralWidget(self.tabs)
            self.logger.info(
                f"Tabs created successfully " f"({successful_tabs}/{len(tabs_config)})"
            )

        except Exception as e:
            self.logger.error(f"Critical error creating tabs: {e}")
            # Taby są krytyczne - jeśli się nie załadują, aplikacja nie ma sensu
            raise RuntimeError(f"Failed to initialize application tabs: {e}")

    def _createStatusBar(self):
        """
        Creates application status bar
        """
        try:
            self.status_bar = QStatusBar(self)
            self.setStatusBar(self.status_bar)

            # Kontener z trzema kolumnami
            status_container = QWidget()
            status_layout = QHBoxLayout()
            status_layout.setContentsMargins(0, 0, 0, 0)
            status_layout.setSpacing(0)

            # Lewa kolumna: komunikaty
            self.status_message_label = QLabel("")
            self.status_message_label.setMinimumWidth(200)
            self.status_message_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            status_layout.addWidget(self.status_message_label, 2)

            # Środek: progress bar wyśrodkowany
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

            # Prawa kolumna: liczba zaznaczonych kafli
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
            # Mapowanie poziomów logowania na przyjazne komunikaty
            level_mapping = {
                "INFO": "ℹ️",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "DEBUG": "🔍",
                "CRITICAL": "🚨",
            }

            icon = level_mapping.get(log_level.upper(), "ℹ️")

            # Skróć długie wiadomości
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
                # Skróć długą ścieżkę dla lepszej czytelności
                if len(directory_path) > 80:
                    # Pokazuj tylko ostatnie części ścieżki
                    parts = directory_path.split("\\")
                    if len(parts) > 3:
                        short_path = f"...\\{'\\'.join(parts[-3:])}"
                    else:
                        short_path = directory_path
                else:
                    short_path = directory_path

                status_message = f"📁 Working directory: {short_path}"
                self.update_status(status_message, timeout=0)  # Bez limitu czasu
                self.logger.debug(f"Working directory status updated: {directory_path}")
        except Exception as e:
            self.logger.error(f"Error updating working directory status: {e}")

    def update_selection_status(
        self, selected_count=None, filtered_count=None, total_count=None
    ):
        """Updates the number of selected assets on the right side of the status bar"""
        try:
            if not hasattr(self, "amv_tab") or not self.amv_tab:
                return
            # Jeśli selected_count jest przekazany, użyj go
            if selected_count is not None:
                checked_count = selected_count
                self.logger.debug(f"Using provided selected_count: {checked_count}")
            else:
                # Oblicz liczbę zaznaczonych na podstawie stanu checkboxów w kafelkach
                amv_controller = self.amv_tab.get_controller()
                if not amv_controller or not hasattr(
                    amv_controller, "asset_grid_controller"
                ):
                    return
                asset_grid_controller = amv_controller.asset_grid_controller
                if not hasattr(asset_grid_controller, "asset_tiles"):
                    return
                checked_count = 0
                for tile in asset_grid_controller.asset_tiles:
                    if (
                        hasattr(tile, "model")
                        and tile.model
                        and not tile.model.is_special_folder
                        and hasattr(tile, "is_checked")
                        and tile.is_checked()
                    ):
                        checked_count += 1
                self.logger.debug(f"Calculated checked_count: {checked_count}")
            if hasattr(self, "selected_label") and self.selected_label:
                # Ustaw tekst z dodatkową informacją o widocznych/wszystkich assetach
                if filtered_count is not None and total_count is not None:
                    status_text = f"Selected: {checked_count}"
                    if filtered_count != total_count:
                        status_text += f" (visible: {filtered_count}/{total_count})"
                else:
                    status_text = f"Selected: {checked_count}"
                self.selected_label.setText(status_text)
                self.logger.debug(f"Updated status bar: {status_text}")
        except Exception as e:
            self.logger.error(f"Error updating selection status: {e}")
            # Fallback - ustaw domyślny tekst
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
            # Dodaj handler do przechwytywania ważnych komunikatów
            class StatusBarHandler(logging.Handler):
                def __init__(self, main_window):
                    super().__init__()
                    self.main_window = main_window

                def emit(self, record):
                    try:
                        # Sprawdź czy to ważny komunikat do wyświetlenia
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
                        "katalog roboczy",
                        "folder clicked",
                        "asset grid rebuilt",
                        "scanning",
                        "skanowanie",
                        "completed",
                        "zakończono",
                        "error",
                        "błąd",
                        "failed",
                        "nie udało się",
                    ]

                    message = record.getMessage().lower()
                    return any(keyword in message for keyword in important_messages)

            # Dodaj handler do głównego loggera
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
            self.logger.info("Łączę sygnał working_directory_changed z ToolsTab")
            amv_controller.working_directory_changed.connect(
                self.tools_tab.set_working_directory
            )
            self.logger.info("Sygnał working_directory_changed połączony z ToolsTab")
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
        # Przykładowe miejsce na sygnały statusu, do rozbudowy jeśli potrzeba
        pass

    def _connect_tools_signals(self):
        """Connects Tools Tab signals"""
        if self.tools_tab:
            # Połącz sygnał odświeżania struktury folderów z AMV tab
            self.tools_tab.folder_structure_changed.connect(
                self._on_folder_structure_changed
            )
            logger.info("Połączono sygnał folder_structure_changed z AMV tab")

    def _on_folder_structure_changed(self, folder_path: str):
        """Obsługuje zmianę struktury folderów - odświeża drzewo folderów"""
        try:
            if self.amv_tab:
                amv_controller = self.amv_tab.get_controller()
                if amv_controller and hasattr(amv_controller, 'folder_tree_controller'):
                    # Wywołaj odświeżenie folderu
                    amv_controller.folder_tree_controller.on_folder_refresh_requested(folder_path)
                    logger.info(f"Odświeżono drzewo folderów dla: {folder_path}")
        except Exception as e:
            logger.error(f"Błąd podczas odświeżania drzewa folderów: {e}")

    def _on_selection_changed(self, selected_asset_ids):
        """Handles selection change and updates the status bar"""
        try:
            selected_count = len(selected_asset_ids)
            self.logger.debug(f"Selection changed: {selected_count} items selected")
            # Pobierz całkowitą ilość assetów z modelu (bez specjalnych folderów)
            amv_controller = self.amv_tab.get_controller()
            if amv_controller and hasattr(amv_controller, "asset_grid_controller"):
                asset_grid_controller = amv_controller.asset_grid_controller
                # Licz aktualnie widoczne assety (bez specjalnych folderów)
                visible_count = 0
                if hasattr(asset_grid_controller, "asset_tiles"):
                    for tile in asset_grid_controller.asset_tiles:
                        if (
                            hasattr(tile, "model")
                            and tile.model
                            and not tile.model.is_special_folder
                        ):
                            visible_count += 1
                # Pobierz oryginalną listę assetów (bez filtrowania)
                total_count = 0
                if hasattr(asset_grid_controller, "get_original_assets"):
                    original_assets = asset_grid_controller.get_original_assets()
                    total_count = (
                        len(
                            [
                                asset
                                for asset in original_assets
                                if asset.get("type") != "special_folder"
                            ]
                        )
                        if original_assets
                        else 0
                    )
                self.logger.debug(
                    f"Visible assets: {visible_count}, Total assets: {total_count}"
                )
            else:
                visible_count = 0
                total_count = 0
            self.update_selection_status(selected_count, visible_count, total_count)
        except Exception as e:
            self.logger.error(f"Error handling selection change: {e}")
            # Fallback - aktualizuj tylko z selected_count
            self.update_selection_status(selected_count, 0, 0)

    def _on_assets_changed(self, assets):
        """Handles asset change and updates the status bar"""
        try:
            amv_controller = self.amv_tab.get_controller()
            # Liczba widocznych assetów = liczba kafelków w galerii (bez specjalnych folderów)
            if amv_controller and hasattr(amv_controller, "asset_tiles"):
                filtered_count = len(
                    [
                        tile
                        for tile in amv_controller.asset_tiles
                        if not tile.model.is_special_folder
                    ]
                )
                selected_count = len(
                    [
                        tile
                        for tile in amv_controller.asset_tiles
                        if hasattr(tile, "is_checked")
                        and tile.is_checked()
                        and not tile.model.is_special_folder
                    ]
                )
            else:
                filtered_count = 0
                selected_count = 0

            # Pobierz oryginalną listę assetów (bez filtrowania)
            original_assets = getattr(amv_controller, "original_assets", [])
            total_count = len(
                [
                    asset
                    for asset in original_assets
                    if asset.get("type") != "special_folder"
                ]
            )

            self.update_selection_status(selected_count, filtered_count, total_count)

        except Exception as e:
            self.logger.error(f"Error handling assets change: {e}")

    # Usunięte nieużywane metody get_config() i get_config_value()

    def closeEvent(self, event):
        """Handles application closing - stops all threads"""
        try:
            self.logger.info("Closing application - stopping threads...")

            # Lista wszystkich wątków do zatrzymania
            threads_to_stop = []

            # Zatrzymaj wątki z Tools Tab
            if hasattr(self, "tools_tab") and self.tools_tab:
                if (
                    hasattr(self.tools_tab, "webp_converter")
                    and self.tools_tab.webp_converter
                ):
                    threads_to_stop.append(self.tools_tab.webp_converter)
                if (
                    hasattr(self.tools_tab, "asset_rebuilder")
                    and self.tools_tab.asset_rebuilder
                ):
                    threads_to_stop.append(self.tools_tab.asset_rebuilder)
                if (
                    hasattr(self.tools_tab, "remove_worker")
                    and self.tools_tab.remove_worker
                ):
                    threads_to_stop.append(self.tools_tab.remove_worker)

            # Zatrzymaj wątki z AMV Tab
            if hasattr(self, "amv_tab") and self.amv_tab:
                if hasattr(self.amv_tab, "controller") and self.amv_tab.controller:
                    controller = self.amv_tab.controller
                    # Stary worker (jeśli jeszcze gdzieś jest)
                    if (
                        hasattr(controller, "asset_rebuilder")
                        and controller.asset_rebuilder
                    ):
                        threads_to_stop.append(controller.asset_rebuilder)
                    # Nowy worker po refaktoryzacji
                    if (
                        hasattr(controller, "asset_rebuild_controller")
                        and controller.asset_rebuild_controller
                        and hasattr(
                            controller.asset_rebuild_controller, "asset_rebuilder"
                        )
                        and controller.asset_rebuild_controller.asset_rebuilder
                    ):
                        threads_to_stop.append(
                            controller.asset_rebuild_controller.asset_rebuilder
                        )

            # Zatrzymaj wątki z Pairing Tab
            if hasattr(self, "pairing_tab") and self.pairing_tab:
                if (
                    hasattr(self.pairing_tab, "rebuild_thread")
                    and self.pairing_tab.rebuild_thread
                ):
                    threads_to_stop.append(self.pairing_tab.rebuild_thread)

            # Zatrzymaj wszystkie wątki
            for thread in threads_to_stop:
                if thread and thread.isRunning():
                    self.logger.info(
                        f"Stopping thread: {thread.__class__.__name__}"
                    )
                    # Użyj nowej metody stop() jeśli jest dostępna
                    if hasattr(thread, "stop"):
                        thread.stop()
                    else:
                        # Fallback do starej metody
                        thread.quit()
                        if not thread.wait(5000):
                            self.logger.warning(
                                f"Forcing thread termination: {thread.__class__.__name__}"
                            )
                            thread.terminate()
                            thread.wait(2000)

            self.logger.info("All threads have been stopped")

        except Exception as e:
            self.logger.error(f"Error while stopping threads: {e}")

        # Zaakceptuj zdarzenie zamknięcia
        event.accept()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Critical error starting application: {e}")
        sys.exit(1)
