# PATCH-CODE DLA: core/rules.py

**Powiązany plik z analizą:** `../corrections/rules_correction.md`
**Zasady ogólne:** `../refactoring_rules.md`

---

### PATCH 1: Przeniesienie importu `time`

**Problem:** Moduł `time` jest importowany wewnątrz metod statycznych `_is_cache_valid` i `_cache_analysis`, co jest niezgodne z konwencjami i może prowadzić do subtelnych problemów.
**Rozwiązanie:** Przeniesienie importu `time` na początek pliku, obok innych importów.

```python
import logging
import os
import re
import time  # Przeniesiono import na początek pliku
from typing import Dict, Optional, Set

logger = logging.getLogger(__name__)


class FolderClickRules:
    # ... istniejący kod ...

    @staticmethod
    def _is_cache_valid(folder_path: str) -> bool:
        """
        Sprawdza czy cache dla folderu jest aktualny

        Args:
            folder_path (str): Ścieżka do folderu

        Returns:
            bool: True jeśli cache jest aktualny
        """
        # import time  # USUNIĘTO: Przeniesiono na początek pliku

        if folder_path not in FolderClickRules._cache_timestamps:
            return False

        current_time = time.time()
        cache_time = FolderClickRules._cache_timestamps[folder_path]

        return (current_time - cache_time) < FolderClickRules.CACHE_TTL

    # ... istniejący kod ...

    @staticmethod
    def _cache_analysis(folder_path: str, analysis: Dict) -> None:
        """
        Zapisuje analizę folderu do cache

        Args:
            folder_path (str): Ścieżka do folderu
            analysis (Dict): Wynik analizy do zcache'owania
        """
        # import time  # USUNIĘTO: Przeniesiono na początek pliku

        FolderClickRules._folder_analysis_cache[folder_path] = analysis
        FolderClickRules._cache_timestamps[folder_path] = time.time()
        logger.debug(f"Zcache'owano analizę folderu: {folder_path}")

    # ... reszta istniejącego kodu ...
```

---

### PATCH 2: Uproszczenie tworzenia słowników błędów

**Problem:** Powtarzające się tworzenie słowników błędów (`error_result`) w metodzie `analyze_folder_content`.
**Rozwiązanie:** Wprowadzenie funkcji pomocniczej `_create_error_result` do generowania tych słowników.

```python
# ... istniejący kod ...

class FolderClickRules:
    # ... istniejący kod ...

    @staticmethod
    def _create_error_result(message: str) -> Dict:
        """
        Tworzy standardowy słownik wynikowy dla błędów analizy folderu.

        Args:
            message (str): Komunikat błędu.

        Returns:
            Dict: Słownik z informacjami o błędzie i pustymi danymi.
        """
        return {
            "error": message,
            "asset_files": [],
            "preview_archive_files": [],
            "cache_exists": False,
            "cache_thumb_count": 0,
            "asset_count": 0,
            "preview_archive_count": 0,
        }

    @staticmethod
    def analyze_folder_content(folder_path: str) -> dict:
        """
        Analizuje zawartość folderu i zwraca szczegółowe informacje o plikach

        # ... istniejący docstring ...
        """
        # Sprawdź cache
        cached_result = FolderClickRules._get_cached_analysis(folder_path)
        if cached_result:
            return cached_result

        # Walidacja input
        validation_error = FolderClickRules._validate_folder_path(folder_path)
        if validation_error:
            return FolderClickRules._create_error_result(validation_error)

        try:
            # Sprawdź czy folder istnieje
            if not os.path.exists(folder_path):
                return FolderClickRules._create_error_result(
                    f"Folder nie istnieje: {folder_path}"
                )

            # Pobierz listę wszystkich elementów w folderze
            try:
                items = os.listdir(folder_path)
            except (OSError, PermissionError) as e:
                return FolderClickRules._create_error_result(
                    f"Brak uprawnień do odczytu folderu: {e}"
                )

            # ... reszta istniejącego kodu ...

        except Exception as e:
            logger.error(f"Błąd analizy zawartości folderu {folder_path}: {e}")
            return FolderClickRules._create_error_result(
                f"Błąd analizy folderu: {e}"
            )

    # ... reszta istniejącego kodu ...
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
