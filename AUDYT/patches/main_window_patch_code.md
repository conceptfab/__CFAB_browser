# PATCH-CODE DLA: MAIN_WINDOW.PY

**Powiązany plik z analizą:** `../corrections/main_window_correction.md`
**Zasady ogólne:** `../refactoring_rules.md`

---

### PATCH 1: USUNIĘCIE GLOBAL CONFIG LOADING

**Problem:** Kod wykonuje się na module level bez try/catch, co może spowodować crash aplikacji
**Rozwiązanie:** Przeniesienie ładowania konfiguracji do konstruktora z proper error handling

```python
import json
import logging
import sys

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar, QTabWidget

from core.gallery_tab import GalleryTab
from core.pairing_tab import PairingTab
from core.tools_tab import ToolsTab

# Usunięcie global config loading - przenosimy do konstruktora
```

---

### PATCH 2: DODANIE FALLBACK CONFIGURATION

**Problem:** Brak mechanizmu fallback gdy konfiguracja jest nieprawidłowa
**Rozwiązanie:** Implementacja domyślnej konfiguracji

```python
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
        "work_folder5": {"path": "", "name": "", "icon": "", "color": ""}
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
```

---

### PATCH 3: IMPLEMENTACJA SAFE CONFIG LOADING

**Problem:** Brak graceful degradation przy błędach ładowania konfiguracji
**Rozwiązanie:** Implementacja bezpiecznego ładowania z fallback

```python
    def _load_config_safe(self, config_path):
        """
        Bezpiecznie ładuje konfigurację z fallback do domyślnych wartości
        
        Args:
            config_path (str): Ścieżka do pliku konfiguracyjnego
            
        Returns:
            dict: Załadowana lub domyślna konfiguracja
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # Walidacja podstawowych kluczy
            if not isinstance(config, dict):
                raise ValueError("Configuration must be a dictionary")
            
            # Uzupełnienie brakujących kluczy domyślnymi wartościami
            for key, default_value in self.DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = default_value
                    
            return config
            
        except FileNotFoundError:
            print(f"Warning: Configuration file {config_path} not found. Using default configuration.")
            return self.DEFAULT_CONFIG.copy()
            
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in {config_path}: {e}. Using default configuration.")
            return self.DEFAULT_CONFIG.copy()
            
        except PermissionError:
            print(f"Warning: Permission denied reading {config_path}. Using default configuration.")
            return self.DEFAULT_CONFIG.copy()
            
        except Exception as e:
            print(f"Warning: Unexpected error loading config {config_path}: {e}. Using default configuration.")
            return self.DEFAULT_CONFIG.copy()
```

---

### PATCH 4: CENTRALIZACJA LOGGER SETUP

**Problem:** Logger configuration w wrong place, potential conflicts
**Rozwiązanie:** Przeniesienie konfiguracji loggera do dedykowanej metody

```python
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
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            
            self.logger = logging.getLogger(__name__)
            self.logger.info(f"Logger initialized with level: {logger_level}")
            
        except Exception as e:
            # Fallback logger setup
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
            self.logger.error(f"Error setting up logger: {e}")
```

---

### PATCH 5: IMPROVED ERROR HANDLING W MENU CREATION

**Problem:** Brak error handling w _createMenuBar
**Rozwiązanie:** Dodanie try/catch z proper logging

```python
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
```

---

### PATCH 6: IMPROVED ERROR HANDLING W TABS CREATION

**Problem:** Brak error handling w _createTabs, które jest krytyczne dla funkcjonalności
**Rozwiązanie:** Dodanie comprehensive error handling

```python
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
                (ToolsTab, "Narzędzia", False)
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
                        from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
                        placeholder = QWidget()
                        layout = QVBoxLayout()
                        layout.addWidget(QLabel(f"Błąd ładowania {tab_name}: {e}"))
                        placeholder.setLayout(layout)
                        self.tabs.addTab(placeholder, f"{tab_name} (Błąd)")
                        successful_tabs += 1
            
            if successful_tabs == 0:
                raise RuntimeError("Failed to create any tabs")
                
            self.setCentralWidget(self.tabs)
            self.logger.info(f"Tabs created successfully ({successful_tabs}/{len(tabs_config)})")
            
        except Exception as e:
            self.logger.error(f"Critical error creating tabs: {e}")
            # Taby są krytyczne - jeśli się nie załadują, aplikacja nie ma sensu
            raise RuntimeError(f"Failed to initialize application tabs: {e}")
```

---

### PATCH 7: DODANIE GET_CONFIG METHOD

**Problem:** Brak dostępu do konfiguracji z zewnątrz dla innych komponentów
**Rozwiązanie:** Dodanie publicznej metody do dostępu do konfiguracji

```python
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
```

---

### PATCH 8: UPDATED MODULE-LEVEL EXECUTION

**Problem:** Stary kod module-level może nadal być wykonywany
**Rozwiązanie:** Aktualizacja if __name__ == "__main__" z error handling

```python
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Critical error starting application: {e}")
        sys.exit(1)
```

---

## ✅ CHECKLISTA WERYFIKACYJNA (DO WYPEŁNIENIA PRZED WDROŻENIEM)

#### **FUNKCJONALNOŚCI DO WERYFIKACJI:**

- [ ] **Funkcjonalność podstawowa** - czy MainWindow nadal tworzy okno z trzema tabami
- [ ] **API kompatybilność** - czy MainWindow() konstruktor działa identycznie dla cfab_browser.py
- [ ] **Obsługa błędów** - czy aplikacja nie crashuje przy uszkodzonym config.json
- [ ] **Walidacja danych** - czy nieprawidłowa konfiguracja jest zastępowana domyślną
- [ ] **Logowanie** - czy logger jest prawidłowo konfigurowany bez konfliktów
- [ ] **Konfiguracja** - czy fallback configuration działa poprawnie
- [ ] **Cache** - nie dotyczy tego modułu
- [ ] **Thread safety** - czy kod jest thread-safe (używa tylko Qt main thread)
- [ ] **Memory management** - czy nie ma wycieków pamięci przy tworzeniu UI komponentów
- [ ] **Performance** - czy czas uruchomienia aplikacji nie został znacząco pogorszony

#### **ZALEŻNOŚCI DO WERYFIKACJI:**

- [ ] **Importy** - czy wszystkie importy Qt i core modules działają poprawnie
- [ ] **Zależności zewnętrzne** - czy PyQt6 jest używane prawidłowo
- [ ] **Zależności wewnętrzne** - czy cfab_browser.py nadal może zaimportować i używać MainWindow
- [ ] **Cykl zależności** - czy nie wprowadzono cyklicznych importów
- [ ] **Backward compatibility** - czy API MainWindow jest 100% kompatybilne wstecz
- [ ] **Interface contracts** - czy signature konstruktora nie uległ zmianie (dodany optional config_path)
- [ ] **Event handling** - czy Qt events (close, menu actions) działają poprawnie
- [ ] **Signal/slot connections** - czy exit_action.triggered.connect(self.close) działa
- [ ] **File I/O** - czy ładowanie config.json działa z proper error handling

#### **TESTY WERYFIKACYJNE:**

- [ ] **Test jednostkowy** - czy MainWindow można utworzyć bez błędów
- [ ] **Test integracyjny** - czy integration z cfab_browser.py działa
- [ ] **Test regresyjny** - czy nie wprowadzono regresji w podstawowej funkcjonalności UI
- [ ] **Test wydajnościowy** - czy uruchomienie aplikacji jest co najmniej tak samo szybkie

#### **SPECJALNE TESTY ERROR HANDLING:**

- [ ] **Test z brakującym config.json** - aplikacja uruchamia się z domyślną konfiguracją
- [ ] **Test z uszkodzonym JSON** - aplikacja uruchamia się z domyślną konfiguracją  
- [ ] **Test z niepełnym config.json** - brakujące klucze są uzupełniane
- [ ] **Test z permission denied** - aplikacja używa domyślnej konfiguracji
- [ ] **Test graceful degradation** - aplikacja działa nawet gdy niektóre taby się nie załadują

#### **KRYTERIA SUKCESU:**

- [ ] **WSZYSTKIE CHECKLISTY MUSZĄ BYĆ ZAZNACZONE** przed wdrożeniem
- [ ] **BRAK FAILED TESTS** - wszystkie testy muszą przejść
- [ ] **PERFORMANCE BUDGET** - czas uruchomienia nie pogorszony o więcej niż 10%
- [ ] **ERROR RESILIENCE** - aplikacja nie crashuje przy żadnym scenariuszu błędu konfiguracji