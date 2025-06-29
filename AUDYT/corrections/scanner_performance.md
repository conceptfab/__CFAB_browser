### ⚡ scanner.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Krytyczne Problemy Wydajnościowe:

1.  **Synchroniczne Operacje I/O (KRYTYCZNY PRIORYTET):**
    -   **Problem:** Cały moduł `scanner.py` jest zbudowany na synchronicznych operacjach I/O. Każde wywołanie `os.listdir`, `os.path.exists`, `os.path.getsize`, `json.load`, `json.dump`, a zwłaszcza `process_thumbnail` (które samo w sobie jest operacją I/O i przetwarzania obrazu) blokuje wątek, w którym jest wykonywane. Jeśli `find_and_create_assets` jest wywoływane w wątku roboczym, ten wątek jest całkowicie zablokowany na czas skanowania i przetwarzania każdego assetu. Dla folderów zawierających setki lub tysiące plików, operacja ta może trwać bardzo długo, a wątek roboczy nie będzie mógł reagować na żadne sygnały (np. anulowanie).
    -   **Rekomendacja (KRYTYCZNA):** Wszystkie operacje I/O i przetwarzania obrazu muszą być **asynchroniczne**. Należy zaimplementować mechanizm, w którym skanowanie i tworzenie assetów odbywa się w tle, a poszczególne etapy (np. ładowanie pliku, generowanie miniatury) są wykonywane asynchronicznie. Można to osiągnąć poprzez:
        a)  Użycie `asyncio.to_thread` dla każdej blokującej operacji I/O w pętli.
        b)  Zaimplementowanie kolejki zadań, gdzie zadania są dodawane do puli wątków i przetwarzane równolegle.

2.  **Nieefektywne Skanowanie Plików (`os.listdir`):**
    -   **Problem:** Funkcje takie jak `_get_files_by_extensions` używają `os.listdir`, a następnie filtrują wyniki. `os.listdir` zwraca listę wszystkich nazw plików i katalogów, co dla dużych katalogów może być kosztowne. Następnie dla każdego elementu wykonywane są dodatkowe operacje (`os.path.join`, `os.path.splitext`).
    -   **Rekomendacja (WYSOKA):** Zastąpić `os.listdir` przez `os.scandir`. `os.scandir` zwraca iterator obiektów `DirEntry`, które zawierają już informacje o typie pliku (`is_file()`, `is_dir()`) i nazwie, co pozwala uniknąć wielu kosztownych wywołań `os.path.join` i `os.path.splitext`.

3.  **Wielokrotne Odczytywanie i Zapisywanie Plików `.asset`:**
    -   **Problem:** W `_create_single_asset`, plik `.asset` jest najpierw odczytywany (`load_from_file`), a następnie zapisywany (`save_to_file`). Dodatkowo, `create_thumbnail_for_asset` ponownie odczytuje i zapisuje ten sam plik. To prowadzi do nadmiarowych operacji I/O na tym samym pliku.
    -   **Rekomendacja (WYSOKA):** Zoptymalizować proces. Dane assetu powinny być wczytane raz, zmodyfikowane w pamięci, a następnie zapisane raz. Miniatura powinna być generowana na podstawie danych w pamięci, a jej status aktualizowany w obiekcie assetu przed finalnym zapisem.

4.  **Brak Mechanizmu Anulowania Operacji:**
    -   **Problem:** Moduł nie posiada żadnego mechanizmu, który pozwoliłby na bezpieczne przerwanie długotrwałej operacji skanowania i tworzenia assetów. Jeśli użytkownik zechce anulować, jedyną opcją jest gwałtowne zamknięcie wątku, co może prowadzić do uszkodzenia plików.
    -   **Rekomendacja (WYSOKA):** Zaimplementować mechanizm **cooperative cancellation** w funkcji `find_and_create_assets`. Funkcja powinna regularnie sprawdzać flagę anulowania i bezpiecznie kończyć pracę, jeśli zostanie ona ustawiona.
