# 💻 PATCH KODU: main_window.py

**Data:** 2024-05-22

**Link do zasad refaktoryzacji:** [`refactoring_rules.md`](../../doc/refactoring_rules.md)

---

## 📝 OPIS ZMIAN

Ten patch wprowadza następujące ulepszenia do pliku `main_window.py`:

1.  **Klasa Konfiguracyjna `AppConfig`:** Wprowadzono `dataclass` `AppConfig` do zarządzania konfiguracją. Zapewnia to bezpieczeństwo typów, wartości domyślne i centralizuje logikę walidacji, eliminując potrzebę ręcznego sprawdzania kluczy w słowniku.
2.  **Refaktoryzacja Ładowania Konfiguracji:** Metoda `_load_config_safe` została uproszczona i przeniesiona do `AppConfig` jako metoda klasowa `load`. Logika ładowania i walidacji jest teraz w jednym miejscu.
3.  **Spójne Logowanie:** Wszystkie komunikaty o błędach podczas ładowania konfiguracji są teraz obsługiwane przez standardowy logger, a nie przez `print()`. Wymagało to wczesnej, podstawowej konfiguracji loggera przed załadowaniem głównej konfiguracji.
4.  **Redukcja Powiązań:** Zmiany przygotowują grunt pod wstrzykiwanie zależności (Dependency Injection) dla zakładek, chociaż pełna implementacja DI zostanie wykonana w osobnym kroku, aby zachować atomowość zmian.

Zmiany te poprawiają solidność, testowalność i czytelność kodu, zgodnie z rekomendacjami z pliku `main_window_correction.md`.

---

## ✂️ FRAGMENTY KODU DO ZASTOSOWANIA

### 1. Importy i definicja `AppConfig`

```python
import json
import logging
import sys
from dataclasses import asdict, dataclass, field

from PyQt6.QtGui import QAction
# ... (reszta importów bez zmian)
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

            # Walidacja typów i uzupełnianie brakujących kluczy
            config_args = {}
            for fld in cls.__dataclass_fields__.values():
                if fld.name in data:
                    if isinstance(data[fld.name], fld.type):
                        config_args[fld.name] = data[fld.name]
                    else:
                        logger.warning(
                            f"Config '{fld.name}' has wrong type. "
                            f"Expected {fld.type}, got {type(data[fld.name])}. "
                            f"Using default."
                        )
                else:
                    logger.warning(f"Config key '{fld.name}' not found. Using default.")

            return cls(**config_args)

        except (FileNotFoundError, json.JSONDecodeError, TypeError) as e:
            logger.warning(
                f"Could not load config from {config_path}: {e}. "
                f"Using default configuration."
            )
            return cls()
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while loading config: {e}. "
                f"Using default configuration."
            )
            return cls()

```

### 2. Zmodyfikowana klasa `MainWindow`

```python
class MainWindow(QMainWindow):

    def __init__(self, config_path="config.json"):
        super().__init__()

        # Wczesna konfiguracja loggera, aby był dostępny wszędzie
        self._setup_preliminary_logger()

        # Ładowanie konfiguracji przy użyciu nowej klasy
        self.config = AppConfig.load(config_path, self.logger)

        # Pełna konfiguracja loggera na podstawie załadowanej konfiguracji
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
                self.logger.warning(f"Invalid logger level '{logger_level}' in config. Using INFO.")
                logger_level = "INFO"

            # Ustawienie poziomu dla głównego loggera
            logging.getLogger().setLevel(getattr(logging, logger_level))
            self.logger.info(f"Logger configured with level: {logger_level}")

        except Exception as e:
            self.logger.error(f"Error setting up logger from config: {e}")

    # Usunięto _load_config_safe - logika przeniesiona do AppConfig.load

    # Metody _createMenuBar, _createTabs, get_config, get_config_value
    # pozostają bez zmian, ale mogą teraz korzystać z self.config jako obiektu
    # np. self.config.thumbnail_size zamiast self.config.get("thumbnail")

    def get_config(self):
        """
        Zwraca konfigurację jako słownik dla kompatybilności wstecznej.
        """
        return asdict(self.config)

    def get_config_value(self, key, default=None):
        """
        Zwraca konkretną wartość z konfiguracji.
        """
        return getattr(self.config, key, default)

# ... (reszta pliku bez zmian)
```
