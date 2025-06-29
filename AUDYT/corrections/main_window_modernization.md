### 🚀 main_window.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Wydzielenie Logiki Konfiguracji do Dedykowanej Klasy:**
    -   **Cel:** Oddzielenie odpowiedzialności za zarządzanie konfiguracją od głównego okna aplikacji.
    -   **Plan Działania:**
        1.  Stworzyć klasę `ConfigManager` (lub `ConfigService`), która będzie odpowiedzialna za ładowanie, walidację, przechowywanie i udostępnianie konfiguracji.
        2.  `ConfigManager` powinien obsługiwać fallback do domyślnych wartości i logowanie błędów.
        3.  `MainWindow` będzie przyjmować instancję `ConfigManager` w konstruktorze (wstrzykiwanie zależności) lub tworzyć ją jako pierwszy krok w `__init__`.
        4.  Metody `get_config()` i `get_config_value()` zostaną przeniesione do `ConfigManager`.

2.  **Wprowadzenie Wzorca Mediatora/Event Bus dla Komunikacji Między Komponentami:**
    -   **Cel:** Zmniejszenie ścisłych powiązań między zakładkami i ułatwienie rozbudowy aplikacji.
    -   **Plan Działania:**
        1.  Stworzyć klasę `AppEventBus` (lub `AppMediator`), która będzie centralnym punktem do emitowania i subskrybowania zdarzeń.
        2.  Zamiast bezpośredniego łączenia sygnałów (`amv_controller.working_directory_changed.connect(self.pairing_tab.on_working_directory_changed)`), `AmvTab` (lub jego kontroler) będzie emitował zdarzenie do `AppEventBus` (np. `AppEventBus.emit("working_directory_changed", folder_path)`).
        3.  `PairingTab` (lub jego kontroler) będzie subskrybował to zdarzenie z `AppEventBus` (np. `AppEventBus.subscribe("working_directory_changed", self.on_working_directory_changed)`).
        4.  `MainWindow` będzie odpowiedzialne za utworzenie i udostępnienie instancji `AppEventBus` wszystkim komponentom.

3.  **Asynchroniczne Ładowanie Konfiguracji (Opcjonalnie):**
    -   **Cel:** Zapewnienie, że nawet w przypadku problemów z plikiem konfiguracyjnym, start aplikacji jest natychmiastowy.
    -   **Plan Działania:**
        1.  Jeśli `ConfigManager` zostanie zaimplementowany, jego metoda ładowania konfiguracji może być asynchroniczna (`async def load_config()`).
        2.  `MainWindow` może wyświetlić placeholder lub ekran ładowania, a następnie asynchronicznie załadować konfigurację. Po jej załadowaniu, główne komponenty UI zostaną zainicjalizowane.

4.  **Użycie `pathlib` dla Ścieżek:**
    -   **Cel:** Modernizacja kodu zgodnie z nowoczesnymi standardami Pythona.
    -   **Plan Działania:**
        1.  Zastąpić stringi reprezentujące ścieżki (np. `config_path`) obiektami `pathlib.Path`.
        2.  Wszelkie operacje na ścieżkach powinny być wykonywane przy użyciu metod `Path`.
