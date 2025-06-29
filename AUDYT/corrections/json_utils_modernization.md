### 🚀 json_utils.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Wprowadzenie `pathlib.Path` dla Ścieżek:**
    -   **Cel:** Zastąpienie stringów reprezentujących ścieżki nowoczesnym, obiektowym API `pathlib`.
    -   **Plan Działania:**
        1.  Zmienić sygnatury funkcji `load_from_file` i `save_to_file`, aby przyjmowały `file_path: Path`.
        2.  Wewnątrz funkcji używać metod obiektu `Path` do operacji na plikach (np. `file_path.open("rb")` zamiast `open(file_path, "rb")`).

2.  **Pełne Adnotacje Typów:**
    -   **Cel:** Poprawa czytelności i umożliwienie statycznej analizy kodu.
    -   **Plan Działania:**
        1.  Dodać pełne adnotacje typów do wszystkich funkcji i zmiennych, w tym `Union` dla `str` i `bytes`, `Any` dla `obj`.
        2.  Użyć `Optional[dict]` dla zwracanych wartości, jeśli `None` jest dopuszczalnym wynikiem.

3.  **Asynchroniczne Wersje Funkcji (Opcjonalnie, ale Rekomendowane):**
    -   **Cel:** Zapewnienie, że operacje I/O na plikach JSON nie blokują głównego wątku UI.
    -   **Plan Działania:**
        1.  Dodać asynchroniczne wersje funkcji `load_from_file` i `save_to_file`, np. `async def load_from_file_async(file_path: Path) -> Optional[dict]:`.
        2.  Wewnątrz tych funkcji używać `asyncio.to_thread` do wywoływania synchronicznych operacji plikowych.

4.  **Ujednolicenie Obsługi Błędów (Rzucanie Wyjątków):**
    -   **Cel:** Zapewnienie spójnego i przewidywalnego sposobu obsługi błędów.
    -   **Plan Działania:**
        1.  Zmienić funkcję `load_from_file`, aby rzucała wyjątki (np. `FileNotFoundError`, `json.JSONDecodeError`) zamiast zwracać `None`.
        2.  Komponenty wywołujące tę funkcję będą odpowiedzialne za obsługę tych wyjątków w swoich blokach `try...except`.

5.  **Konfigurowalność `ensure_ascii`:**
    -   **Cel:** Zwiększenie elastyczności funkcji `dumps` i `save_to_file`.
    -   **Plan Działania:**
        1.  Dodać parametr `ensure_ascii: bool = False` do funkcji `dumps` i `save_to_file`.
        2.  Przekazywać ten parametr do `json.dumps` w przypadku fallbacku.
