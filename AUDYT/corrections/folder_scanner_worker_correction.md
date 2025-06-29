### 📄 folder_scanner_worker.py - Analiza Poprawek

**Data analizy:** 29.06.2025

#### Główne Problemy Architektoniczne i Stylistyczne:

1.  **Nieefektywna Logika Skanowania (Podwójne Przechodzenie):**
    -   **Problem:** Obecna implementacja najpierw przechodzi całe drzewo katalogów za pomocą `os.walk` w `_count_total_folders`, a następnie robi to ponownie za pomocą rekurencyjnej funkcji `_scan_folder_structure`. Jest to nieefektywne i powoduje wykonanie podwójnej, niepotrzebnej pracy I/O.
    -   **Rekomendacja:** Należy połączyć te dwie operacje w jedną. Można użyć `os.scandir`, które jest bardziej wydajne niż `os.listdir`, i w jednej pętli rekurencyjnej zarówno zliczać foldery, jak i emitować sygnały o ich znalezieniu. Pasek postępu można zaktualizować, szacując całkowitą liczbę folderów lub po prostu pokazując liczbę przetworzonych folderów bez wartości procentowej.

2.  **Brak Bezpiecznego Mechanizmu Anulowania:**
    -   **Problem:** Wątek nie ma wbudowanego mechanizmu, który pozwalałby na jego bezpieczne zatrzymanie. Jeśli użytkownik zechce przerwać skanowanie, jedyną opcją jest `terminate()`, co jest niebezpieczne.
    -   **Rekomendacja:** Należy zaimplementować mechanizm **cooperative cancellation**. Dodać flagę `self._is_cancellation_requested`, którą można ustawić z zewnątrz. W pętlach wewnątrz metody `run()` (np. iterując po podfolderach) należy regularnie sprawdzać stan tej flagi i jeśli jest ustawiona na `True`, bezpiecznie zakończyć działanie wątku.

3.  **Mieszanie Odpowiedzialności:**
    -   **Problem:** Klasa `FolderStructureScanner` jest wątkiem roboczym, ale zawiera też metodę `handle_folder_click`, która jest logiką bardziej pasującą do kontrolera. Wątek powinien być odpowiedzialny tylko za wykonywanie długotrwałego zadania w tle.
    -   **Rekomendacja:** Przenieść metodę `handle_folder_click` do `AmvController`. Kontroler, po otrzymaniu sygnału o kliknięciu w folder z widoku, powinien sam wywołać `FolderClickRules.decide_action()` i na tej podstawie podjąć dalsze kroki (np. uruchomić skaner assetów).

4.  **Niejasne Nazewnictwo Sygnałów:**
    -   **Problem:** Nazwy sygnałów takie jak `scanner_finished` mogą być mylące, ponieważ ta klasa sama w sobie nie skanuje assetów, a jedynie strukturę folderów. `finished_scanning` jest bardziej ogólne.
    -   **Rekomendacja:** Ujednolicić i doprecyzować nazwy sygnałów, aby jasno odzwierciedlały, co się stało, np. `structure_scan_completed`, `folder_scan_request(path)`.
