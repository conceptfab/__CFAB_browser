### 🚀 config_manager_model.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Wprowadzenie `dataclass` dla Konfiguracji:**
    -   **Cel:** Zastąpienie surowych słowników typowanymi, strukturalnymi obiektami konfiguracji.
    -   **Plan Działania:**
        1.  Zdefiniować `ConfigData` jako `dataclass` z odpowiednimi polami i typami (np. `logger_level: str`, `thumbnail_size: int`, `work_folders: list[WorkFolderData]`).
        2.  W metodzie `load_config`, po wczytaniu słownika z JSON, przekonwertować go na instancję `ConfigData`.
        3.  Wprowadzić walidację danych podczas konwersji, aby zapewnić, że konfiguracja jest poprawna.

2.  **Asynchroniczne Ładowanie i Zapisywanie Konfiguracji:**
    -   **Cel:** Zapewnienie, że operacje I/O na pliku konfiguracyjnym nie blokują głównego wątku UI.
    -   **Plan Działania:**
        1.  Przepisać metody `load_config` i (jeśli zostanie dodana) `save_config` na funkcje asynchroniczne (`async def`).
        2.  Wewnątrz tych funkcji używać `asyncio.to_thread` do wywoływania blokujących operacji plikowych (`load_from_file`, `save_to_file`).
        3.  Model będzie emitował sygnały `config_loaded` i `config_error` po zakończeniu asynchronicznej operacji.

3.  **Użycie `pathlib` dla Ścieżek:**
    -   **Cel:** Modernizacja kodu zgodnie z nowoczesnymi standardami Pythona.
    -   **Plan Działania:**
        1.  Zastąpić stringi reprezentujące ścieżki (`_config_path`) obiektami `pathlib.Path`.
        2.  Wszelkie operacje na ścieżkach powinny być wykonywane przy użyciu metod `Path` (np. `path.exists()`, `path.stat().st_mtime`).

4.  **Wydzielenie Logiki Domyślnej Konfiguracji:**
    -   **Cel:** Uczynienie klasy bardziej spójną i łatwiejszą do testowania.
    -   **Plan Działania:**
        1.  Przenieść domyślną konfigurację (`_get_default_config`) do osobnego modułu lub statycznej metody w `ConfigData`.
        2.  `ConfigManagerMV` powinien jedynie ładować i zarządzać konfiguracją, a nie definiować jej domyślne wartości.

5.  **Udoskonalenie Sygnałów:**
    -   **Cel:** Dostarczanie bardziej szczegółowych informacji o załadowanej konfiguracji.
    -   **Plan Działania:**
        1.  Zmienić sygnaturę `config_loaded` na `config_loaded = pyqtSignal(ConfigData)`, aby emitować obiekt `ConfigData` zamiast surowego słownika.
