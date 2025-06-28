# PATCH-CODE DLA: core/folder_scanner_worker.py

**Powiązany plik z analizą:** `../corrections/folder_scanner_worker_correction.md`
**Zasady ogólne:** `../refactoring_rules.md`

---

### PATCH 1: Delegowanie skanowania assetów i dostosowanie konstruktora

**Problem:** Metoda `_run_scanner` w `FolderStructureScanner` bezpośrednio wywołuje `find_and_create_assets` i zarządza postępem skanowania assetów, co narusza zasadę pojedynczej odpowiedzialności.
**Rozwiązanie:** Usunięcie metody `_run_scanner` z `FolderStructureScanner` i przekazanie instancji `AssetScannerModelMV` do konstruktora, aby delegować odpowiedzialność za skanowanie assetów.

```python
# ... istniejący kod ...

import logging
import os

from PyQt6.QtCore import QThread, pyqtSignal

from core.rules import FolderClickRules
# from core.scanner import find_and_create_assets # USUNIĘTO: Skanowanie assetów będzie delegowane

logger = logging.getLogger(__name__)


class FolderStructureScanner(QThread):
    """Worker do skanowania struktury folderów i wykrywania plików asset"""

    progress_updated = pyqtSignal(int)  # Sygnał postępu
    folder_found = pyqtSignal(str, int)  # Sygnał z folderem (ścieżka, poziom)
    assets_folder_found = pyqtSignal(str)  # Sygnał gdy folder zawiera pliki asset
    subfolders_only_found = pyqtSignal(str)  # Sygnał gdy folder ma tylko podfoldery
    scanner_started = pyqtSignal(str)  # Sygnał uruchomienia scannera
    scanner_finished = pyqtSignal(str)  # Sygnał zakończenia scannera
    finished_scanning = pyqtSignal()  # Sygnał zakończenia
    error_occurred = pyqtSignal(str)  # Sygnał błędu

    def __init__(self, folder_path: str, asset_scanner_model_mv):
        super().__init__()
        self.folder_path = folder_path
        self.asset_scanner_model_mv = asset_scanner_model_mv # DODANO: Instancja AssetScannerModelMV
        self.folders_found = []
        self.total_folders = 0
        self.processed_folders = 0

    def run(self):
        # ... istniejący kod ...

    # def _run_scanner(self, folder_path: str): # USUNIĘTO: Metoda przeniesiona do AssetScannerModelMV
    #     """
    #     Uruchamia scanner w określonym folderze
    #
    #     Args:
    #         folder_path (str): Ścieżka do folderu do przeskanowania
    #     """
    #     try:
    #         logger.info(f"Uruchamianie scannera w folderze: {folder_path}")
    #         self.scanner_started.emit(folder_path)
    #
    #         def progress_callback(current, total, message):
    #             if total > 0:
    #                 progress = int((current / total) * 100)
    #                 self.progress_updated.emit(min(progress, 100))
    #             logger.debug(f"Scanner progress: {message}")
    #
    #         created_assets = find_and_create_assets(folder_path, progress_callback)
    #
    #         if created_assets:
    #             logger.info(
    #                 f"Scanner zakończony, utworzono {len(created_assets)} "
    #                 f"plików asset w: {folder_path}"
    #             )
    #             self.scanner_finished.emit(folder_path)
    #             self.assets_folder_found.emit(folder_path)
    #         else:
    #             logger.warning(f"Scanner nie utworzył plików asset w: {folder_path}")
    #
    #     except Exception as e:
    #         error_msg = f"Błąd podczas uruchamiania scannera w {folder_path}: {e}"
    #         logger.error(error_msg)
    #         self.error_occurred.emit(error_msg)

    # ... reszta istniejącego kodu ...

    def handle_folder_click(self, folder_path: str):
        """
        Obsługuje kliknięcie użytkownika w folder używając logiki z rules.py

        # ... istniejący docstring ...
        """
        try:
            logger.info(f"Obsługa kliknięcia folderu: {folder_path}")

            # Użyj logiki z rules.py do podjęcia decyzji
            result = FolderClickRules.decide_action(folder_path)
            action = result.get("action")
            message = result.get("message", "")
            condition = result.get("condition", "")

            logger.info(f"Decyzja rules.py: {action} - {message} ({condition})")

            # Wykonaj akcję na podstawie decyzji z rules.py
            if action == "run_scanner":
                # Zamiast _run_scanner, wywołaj metodę z AssetScannerModelMV
                self.asset_scanner_model_mv.scan_folder(folder_path)
            elif action == "show_gallery":
                self.assets_folder_found.emit(folder_path)
            elif action == "error":
                self.error_occurred.emit(message)
            elif action == "no_action":
                logger.info(f"Brak akcji dla folderu: {message}")
            else:
                logger.warning(f"Nieznana akcja: {action}")

        except Exception as e:
            error_msg = f"Błąd obsługi kliknięcia folderu {folder_path}: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
```

---

## ✅ CHECKLISTA WERYFIKACYJNA (DO WYPEŁNIENIA PRZED WDROŻENIEM)

#### **FUNKCJONALNOŚCI DO WERYFIKACJI:**

- [ ] **Funkcjonalność podstawowa** - czy plik nadal wykonuje swoją główną funkcję.
- [ ] **API kompatybilność** - czy wszystkie publiczne metody/klasy działają jak wcześniej.
- [ ] **Obsługa błędów** - czy mechanizmy obsługi błędów nadal działają.
- [ ] **Walidacja danych** - czy walidacja wejściowych danych działa poprawnie.
- [ ] **Logowanie** - czy system logowania działa bez spamowania.
- [ ] **Konfiguracja** - czy odczytywanie/zapisywanie konfiguracji działa.
- [ ] **Cache** - czy mechanizmy cache działają poprawnie.
- [ ] **Thread safety** - czy kod jest bezpieczny w środowisku wielowątkowym.
- [ ] **Memory management** - czy nie ma wycieków pamięci.
- [ ] **Performance** - czy wydajność nie została pogorszona.

#### **ZALEŻNOŚCI DO WERYFIKACJI:**

- [ ] **Importy** - czy wszystkie importy działają poprawnie.
- [ ] **Zależności zewnętrzne** - czy zewnętrzne biblioteki są używane prawidłowo.
- [ ] **Zależności wewnętrzne** - czy powiązania z innymi modułami działają.
- [ ] **Cykl zależności** - czy nie wprowadzono cyklicznych zależności.
- [ ] **Backward compatibility** - czy kod jest kompatybilny wstecz.
- [ ] **Interface contracts** - czy interfejsy są przestrzegane.
- [ ] **Event handling** - czy obsługa zdarzeń działa poprawnie.
- [ ] **Signal/slot connections** - czy połączenia Qt działają.
- [ ] **File I/O** - czy operacje na plikach działają.

#### **TESTY WERYFIKACYJNE:**

- [ ] **Test jednostkowy** - czy wszystkie funkcje działają w izolacji.
- [ ] **Test integracyjny** - czy integracja z innymi modułami działa.
- [ ] **Test regresyjny** - czy nie wprowadzono regresji.
- [ ] **Test wydajnościowy** - czy wydajność jest akceptowalna.

#### **KRYTERIA SUKCESU:**

- [ ] **WSZYSTKIE CHECKLISTY MUSZĄ BYĆ ZAZNACZONE** przed wdrożeniem.
- [ ] **BRAK FAILED TESTS** - wszystkie testy muszą przejść.
- [ ] **PERFORMANCE BUDGET** - wydajność nie pogorszona o więcej niż 5%.
- [ ] **CODE COVERAGE** - pokrycie kodu nie spadło poniżej 80%.
