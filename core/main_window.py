import logging
import sys

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.amv_tab import AmvTab
from core.json_utils import load_from_file
from core.pairing_tab import PairingTab
from core.tools_tab import ToolsTab


class MainWindow(QMainWindow):

    # Domyślna konfiguracja jako fallback
    DEFAULT_CONFIG = {
        "logger_level": "INFO",
        "use_styles": True,
        "thumbnail": 256,
        "work_folder1": {"path": "", "name": "", "icon": "", "color": ""},
        "work_folder2": {"path": "", "name": "", "icon": "", "color": ""},
        "work_folder3": {"path": "", "name": "", "icon": "", "color": ""},
        "work_folder4": {"path": "", "name": "", "icon": "", "color": ""},
        "work_folder5": {"path": "", "name": "", "icon": "", "color": ""},
    }

    def __init__(self, config_path="config.json"):
        super().__init__()

        # Ładowanie konfiguracji z proper error handling
        self.config = self._load_config_safe(config_path)

        # Konfiguracja loggera na podstawie załadowanej konfiguracji
        self._setup_logger()

        # Inicjalizacja okna
        self.setWindowTitle("CFAB Browser")
        self.resize(800, 600)

        try:
            self._createMenuBar()
            self._createTabs()
            self.logger.info("MainWindow initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing MainWindow: {e}")
            raise

    def _load_config_safe(self, config_path):
        """
        Bezpiecznie ładuje konfigurację z fallback do domyślnych wartości

        Args:
            config_path (str): Ścieżka do pliku konfiguracyjnego

        Returns:
            dict: Załadowana lub domyślna konfiguracja
        """
        try:
            config = load_from_file(config_path)

            # Walidacja podstawowych kluczy
            if not isinstance(config, dict):
                raise ValueError("Configuration must be a dictionary")

            # Uzupełnienie brakujących kluczy domyślnymi wartościami
            for key, default_value in self.DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = default_value

            return config

        except FileNotFoundError:
            print(
                f"Warning: Configuration file {config_path} not found. "
                f"Using default configuration."
            )
            return self.DEFAULT_CONFIG.copy()

        except (ValueError, UnicodeDecodeError) as e:
            print(
                f"Warning: Invalid JSON in {config_path}: {e}. "
                f"Using default configuration."
            )
            return self.DEFAULT_CONFIG.copy()

        except PermissionError:
            print(
                f"Warning: Permission denied reading {config_path}. "
                f"Using default configuration."
            )
            return self.DEFAULT_CONFIG.copy()

        except Exception as e:
            print(
                f"Warning: Unexpected error loading config {config_path}: {e}. "
                f"Using default configuration."
            )
            return self.DEFAULT_CONFIG.copy()

    def _setup_logger(self):
        """
        Konfiguruje logger na podstawie załadowanej konfiguracji
        """
        try:
            logger_level = self.config.get("logger_level", "INFO")

            # Sprawdź czy poziom logowania jest poprawny
            if not hasattr(logging, logger_level):
                logger_level = "INFO"
                print(f"Warning: Invalid logger level in config. Using INFO.")

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
        Tworzy pasek menu z proper error handling
        """
        try:
            menu_bar = QMenuBar(self)
            file_menu = QMenu("Plik", self)
            exit_action = QAction("Wyjście", self)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            menu_bar.addMenu(file_menu)
            self.setMenuBar(menu_bar)
            self.logger.debug("Menu bar created successfully")

        except Exception as e:
            self.logger.error(f"Error creating menu bar: {e}")
            # Menu bar nie jest krytyczny - aplikacja może działać bez niego
            # Ale logujemy błąd dla debugging

    def _createTabs(self):
        """
        Tworzy taby aplikacji z comprehensive error handling
        """
        try:
            self.tabs = QTabWidget()

            # Próbuj utworzyć każdy tab indywidualnie
            tabs_config = [
                (AmvTab, "Asset Browser", True),  # True = krytyczny tab (główna)
                (PairingTab, "Parowanie", False),
                (ToolsTab, "Narzędzia", False),
            ]

            successful_tabs = 0

            for tab_class, tab_name, is_critical in tabs_config:
                try:
                    tab_instance = tab_class()
                    self.tabs.addTab(tab_instance, tab_name)
                    successful_tabs += 1
                    self.logger.debug(f"Tab '{tab_name}' created successfully")

                except Exception as e:
                    self.logger.error(f"Error creating tab '{tab_name}': {e}")
                    if is_critical:
                        # Jeśli krytyczny tab się nie załadował, dodaj placeholder
                        placeholder = QWidget()
                        layout = QVBoxLayout()
                        layout.addWidget(QLabel(f"Błąd ładowania {tab_name}: {e}"))
                        placeholder.setLayout(layout)
                        self.tabs.addTab(placeholder, f"{tab_name} (Błąd)")
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

    def get_config(self):
        """
        Zwraca aktualną konfigurację aplikacji

        Returns:
            dict: Konfiguracja aplikacji
        """
        return self.config.copy()  # Zwracamy kopię żeby uniknąć modyfikacji

    def get_config_value(self, key, default=None):
        """
        Zwraca konkretną wartość z konfiguracji

        Args:
            key (str): Klucz konfiguracji
            default: Wartość domyślna jeśli klucz nie istnieje

        Returns:
            Wartość konfiguracji lub default
        """
        return self.config.get(key, default)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Critical error starting application: {e}")
        sys.exit(1)
