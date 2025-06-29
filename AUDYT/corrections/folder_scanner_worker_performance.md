### ⚡ folder_scanner_worker.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Krytyczne Problemy Wydajnościowe:

1.  **Blokujące Operacje I/O w Wątku Roboczym (WYSOKI PRIORYTET):**
    -   **Problem:** Mimo że kod działa w `QThread`, używa on w pełni synchronicznych i blokujących funkcji `os.walk()` i `os.listdir()`. Na czas działania tych funkcji cały wątek roboczy jest zablokowany i nie może zostać przerwany. Dla bardzo dużych struktur folderów (dziesiątki tysięcy katalogów) lub wolnych dysków sieciowych, operacja ta może trwać bardzo długo, a aplikacja nie będzie mogła jej anulować.
    -   **Rekomendacja (WYSOKA):** Należy przejść z `os.walk` i `os.listdir` na `os.scandir`. `os.scandir` jest znacznie bardziej wydajny, ponieważ zwraca iterator i nie pobiera od razu wszystkich informacji o plikach (jak np. rozmiar), jeśli nie są potrzebne. Pętla przetwarzająca wyniki z `os.scandir` powinna być główną pętlą wątku, w której regularnie sprawdzana będzie flaga anulowania.

2.  **Podwójne Przechodzenie Systemu Plików (WYSOKI PRIORYTET):**
    -   **Problem:** Kod najpierw rekurencyjnie przechodzi całe drzewo katalogów w `_count_total_folders()`, a następnie robi to ponownie w `_scan_folder_structure()`. To podwaja liczbę operacji I/O i jest skrajnie nieefektywne.
    -   **Rekomendacja (WYSOKA):** Należy całkowicie usunąć metodę `_count_total_folders`. Skanowanie powinno odbywać się w jednym przebiegu. Jeśli pasek postępu oparty na procentach jest konieczny, można najpierw szybko policzyć tylko liczbę katalogów na pierwszym poziomie, a następnie ekstrapolować postęp. Lepszym i prostszym rozwiązaniem jest jednak rezygnacja z postępu procentowego na rzecz prostego licznika przetworzonych folderów lub spinnera informującego o trwającej pracy.

#### Pozytywne Aspekty:

-   **Działanie w Tle:** Samo umieszczenie skanowania w osobnym wątku jest fundamentalnie poprawną decyzją architektoniczną, która chroni główny wątek UI przed zamrożeniem. Stanowi to solidną podstawę do dalszych optymalizacji.
-   **Delegowanie Skanowania Assetów:** Decyzja o usunięciu logiki `find_and_create_assets` z tego workera i delegowaniu jej do `AssetScannerModelMV` jest bardzo dobra. Dzięki temu ten komponent ma węższą i jaśniejszą odpowiedzialność, co ułatwia analizę i optymalizację.
