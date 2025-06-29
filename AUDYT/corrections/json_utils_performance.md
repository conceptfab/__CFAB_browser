### ⚡ json_utils.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Główne Problemy Wydajnościowe:

1.  **Synchroniczne Operacje Plikowe (NISKI PRIORYTET):**
    -   **Problem:** Funkcje `load_from_file` i `save_to_file` wykonują operacje odczytu/zapisu z dysku synchronicznie. Oznacza to, że wątek, który je wywołuje, jest blokowany na czas trwania operacji I/O.
    -   **Wpływ:** Chociaż dla małych plików JSON wpływ na wydajność jest minimalny, dla większych plików lub operacji na wolnych nośnikach (np. dysk sieciowy), może to prowadzić do krótkotrwałego zamrożenia interfejsu użytkownika, jeśli są wywoływane w głównym wątku UI. W kontekście całego systemu, gdzie te funkcje są używane przez inne komponenty (np. `ConfigManagerMV`, `scanner.py`), stają się one punktami, w których może dochodzić do blokowania.
    -   **Rekomendacja (NISKA):** Aby zapewnić pełną responsywność, zwłaszcza w aplikacjach GUI, operacje I/O powinny być wykonywane asynchronicznie. Można to osiągnąć poprzez:
        a)  **Asynchroniczne API:** Dodanie asynchronicznych wersji funkcji, np. `async def load_from_file_async(file_path: Path) -> dict:`. Wewnątrz tych funkcji można użyć `asyncio.to_thread` do uruchomienia synchronicznych operacji w puli wątków.
        b)  **Delegowanie do Wątków Roboczych:** Komponenty wywołujące te funkcje powinny uruchamiać je w osobnym wątku (np. `QThread`) lub w puli wątków (`QThreadPool`).

2.  **Fallback na Standardowy `json` (NISKI PRIORYTET):**
    -   **Problem:** Jeśli `orjson` nie jest zainstalowany, moduł używa standardowej biblioteki `json`. `orjson` jest znacznie szybszy w serializacji i deserializacji JSON, zwłaszcza dla dużych obiektów.
    -   **Wpływ:** W środowiskach, gdzie `orjson` nie jest dostępny, wydajność operacji JSON będzie niższa. Jest to jednak świadoma decyzja projektowa, aby zapewnić kompatybilność.
    -   **Rekomendacja (NISKA):** Zachęcać do instalacji `orjson` w środowisku produkcyjnym, aby uzyskać maksymalną wydajność.

#### Pozytywne Aspekty:

-   **Użycie `orjson`:** Priorytetowe użycie `orjson` (jeśli dostępny) jest bardzo dobrym rozwiązaniem z punktu widzenia wydajności, ponieważ jest to jedna z najszybszych bibliotek do obsługi JSON w Pythonie.
-   **Dobra Obsługa Błędów:** Funkcje poprawnie obsługują różne typy błędów (np. `FileNotFoundError`, `JSONDecodeError`, `PermissionError`), co zwiększa stabilność aplikacji.
