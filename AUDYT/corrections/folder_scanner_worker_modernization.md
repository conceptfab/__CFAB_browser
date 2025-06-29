### 🚀 folder_scanner_worker.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Implementacja Wydajnego Skanowania z `os.scandir`:**
    -   **Cel:** Zastąpienie nieefektywnych i blokujących metod `os.walk`/`os.listdir` nowoczesnym i wydajnym `os.scandir` oraz wyeliminowanie podwójnego przechodzenia drzewa katalogów.
    -   **Plan Działania:**
        1.  Usunąć metodę `_count_total_folders`.
        2.  Przepisać metodę `_scan_folder_structure` tak, aby używała `os.scandir` do iterowania po zawartości katalogu.
        3.  W pętli `for entry in os.scandir(path):` sprawdzać `entry.is_dir()`.
        4.  W tej samej pętli implementować logikę rekurencyjnego wywołania oraz sprawdzać flagę anulowania.

2.  **Wprowadzenie Bezpiecznego Anulowania (Cooperative Cancellation):**
    -   **Cel:** Umożliwienie użytkownikowi bezpiecznego przerwania operacji skanowania w dowolnym momencie.
    -   **Plan Działania:**
        1.  Dodać do klasy atrybut `self._is_cancellation_requested = False` i metodę `request_cancellation()`, która go ustawia.
        2.  W głównej pętli skanującej (iterującej po `os.scandir`) na początku każdej iteracji dodawać warunek `if self._is_cancellation_requested: return`.
        3.  Zapewni to, że wątek zakończy pracę w sposób kontrolowany, nie pozostawiając po sobie nieposprzątanych zasobów.

3.  **Modernizacja do `pathlib`:**
    -   **Cel:** Zastąpienie operacji na stringach reprezentujących ścieżki nowoczesnym, obiektowym API `pathlib`.
    -   **Plan Działania:**
        1.  Przekazywać do konstruktora `folder_path` jako obiekt `pathlib.Path`.
        2.  Wewnątrz workera używać metod i właściwości obiektów `Path` do operacji na ścieżkach (np. `path.iterdir()` zamiast `os.scandir`, `sub_path.is_dir()`, `path.name`). `pathlib.Path.iterdir()` jest zbudowane na `os.scandir`, więc korzyści wydajnościowe zostaną zachowane.

4.  **Refaktoryzacja Logiki do Kontrolera:**
    -   **Cel:** Oczyszczenie workera z logiki, która nie jest bezpośrednio związana ze skanowaniem w tle.
    -   **Plan Działania:**
        1.  Całkowicie usunąć metodę `handle_folder_click` z tej klasy.
        2.  Przenieść jej logikę do `AmvController`, który będzie bezpośrednio korzystał z `FolderClickRules`.
        3.  Worker `FolderStructureScanner` powinien być odpowiedzialny tylko i wyłącznie za rekurencyjne skanowanie struktury katalogów i emitowanie sygnałów o znalezionych folderach.
