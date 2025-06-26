import json
import logging
import sys
from dataclasses import asdict, dataclass, field

from PyQt6.QtWidgets import (
    QAction,
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.gallery_tab import GalleryTab
from core.pairing_tab import PairingTab
from core.tools_tab import ToolsTab


@dataclass
class AppConfig:
    logger_level: str = "INFO"
    use_styles: bool = True
    thumbnail_size: int = 256
    work_folder1: dict = field(default_factory=dict)
    work_folder2: dict = field(default_factory=dict)
    work_folder3: dict = field(default_factory=dict)
    work_folder4: dict = field(default_factory=dict)
    work_folder5: dict = field(default_factory=dict)

    @classmethod
    def load(cls, config_path: str, logger: logging.Logger) -> "AppConfig":
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise TypeError("Config file must contain a dictionary.")

            config_args = {}
            for fld in cls.__dataclass_fields__.values():
                if fld.name in data:
                    try:
                        val = data[fld.name]
                        if not isinstance(val, fld.type):
                            val = fld.type(val)
                        config_args[fld.name] = val
                    except (ValueError, TypeError):
                        logger.warning(
                            "Config '%s' has wrong type. Expected %s, "
                            "got %s. Using default.",
                            fld.name,
                            fld.type,
                            type(data[fld.name]),
                        )
                else:
                    logger.warning(
                        "Config key '%s' not found. Using default.", fld.name
                    )

            return cls(**config_args)

        except (FileNotFoundError, json.JSONDecodeError, TypeError) as e:
            logger.warning(
                "Could not load config from %s: %s. Using default.", config_path, e
            )
            return cls()
        except Exception as e:
            logger.error(
                "An unexpected error occurred while loading config: %s. "
                "Using default.",
                e,
            )
            return cls()


class MainWindow(QMainWindow):

    def __init__(self, config_path="config.json"):
        super().__init__()

        self._setup_preliminary_logger()

        self.config = AppConfig.load(config_path, self.logger)

        if "thumbnail" in self.config.__dict__:
            self.config.thumbnail_size = self.config.thumbnail
            del self.config.thumbnail

        self._setup_logger()

        self.setWindowTitle("CFAB Browser")
        self.resize(800, 600)

        try:
            self._createMenuBar()
            self._createTabs()
            self.logger.info("MainWindow initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing MainWindow: {e}")
            raise

    def _setup_preliminary_logger(self):
        """Konfiguruje podstawowy logger przed załadowaniem konfiguracji."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def _setup_logger(self):
        """
        Konfiguruje logger na podstawie załadowanej konfiguracji.
        """
        try:
            logger_level = self.config.logger_level.upper()
            if not hasattr(logging, logger_level):
                self.logger.warning(
                    "Invalid logger level '%s' in config. Using INFO.", logger_level
                )
                logger_level = "INFO"

            logging.getLogger().setLevel(getattr(logging, logger_level))
            self.logger.info("Logger configured with level: %s", logger_level)

        except Exception as e:
            self.logger.error("Error setting up logger from config: %s", e)

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
                (GalleryTab, "Galeria", True),  # True = krytyczny tab
                (PairingTab, "Parowanie", False),
                (ToolsTab, "Narzędzia", False),
            ]

            successful_tabs = 0

            for tab_class, tab_name, is_critical in tabs_config:
                try:
                    tab_instance = tab_class()
                    self.tabs.addTab(tab_instance, tab_name)
                    successful_tabs += 1
                    self.logger.debug("Tab '%s' created successfully", tab_name)

                except Exception as e:
                    self.logger.error("Error creating tab '%s': %s", tab_name, e)
                    if is_critical:
                        # Jeśli krytyczny tab się nie załadował, dodaj placeholder
                        placeholder = QWidget()
                        layout = QVBoxLayout()
                        label_text = f"Błąd ładowania {tab_name}: {e}"
                        layout.addWidget(QLabel(label_text))
                        placeholder.setLayout(layout)
                        self.tabs.addTab(placeholder, f"{tab_name} (Błąd)")
                        successful_tabs += 1

            if successful_tabs == 0:
                raise RuntimeError("Failed to create any tabs")

            self.setCentralWidget(self.tabs)
            self.logger.info(
                "Tabs created successfully (%d/%d)", successful_tabs, len(tabs_config)
            )

        except Exception as e:
            self.logger.error("Critical error creating tabs: %s", e)
            # Taby są krytyczne - jeśli się nie załadują, aplikacja nie ma sensu
            raise RuntimeError(f"Failed to initialize application tabs: {e}") from e

    def get_config(self):
        """
        Zwraca konfigurację jako słownik dla kompatybilności wstecznej.
        """
        return asdict(self.config)

    def get_config_value(self, key, default=None):
        """
        Zwraca konkretną wartość z konfiguracji.
        """
        # Kompatybilność wsteczna dla 'thumbnail'
        if key == "thumbnail":
            key = "thumbnail_size"
        return getattr(self.config, key, default)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Critical error starting application: {e}")
        sys.exit(1)
