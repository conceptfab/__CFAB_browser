### 📄 scanner.py - Analiza Poprawek

**Data analizy:** 29.06.2025

#### Główne Problemy Architektoniczne i Stylistyczne:

1.  **Antywzorzec "God Module" (Moduł Bóg):**
    -   **Problem:** Moduł `scanner.py` jest odpowiedzialny za zbyt wiele różnorodnych zadań: skanowanie plików, tworzenie assetów, generowanie miniatur, zarządzanie plikami JSON, obliczanie rozmiarów. To narusza Zasadę Pojedynczej Odpowiedzialności na poziomie modułu, czyniąc go trudnym do zrozumienia, testowania i rozwijania.
    -   **Rekomendacja:** Należy rozbić ten moduł na mniejsze, wyspecjalizowane moduły/klasy:
        -   `AssetScanner`: Odpowiedzialny za skanowanie folderów i identyfikację par archiwum/podgląd.
        -   `AssetCreator`: Odpowiedzialny za tworzenie plików `.asset` i zarządzanie ich metadanymi.
        -   `ThumbnailService`: Odpowiedzialny za generowanie miniatur.
        -   `UnpairedFilesManager`: Odpowiedzialny za zarządzanie plikiem `unpair_files.json`.
        -   `FileSizeCalculator`: Prosta funkcja do obliczania rozmiaru pliku.

2.  **Brak Struktur Danych (Użycie Surowych Słowników):**
    -   **Problem:** Dane assetów są reprezentowane jako surowe słowniki (`dict`). Jest to podatne na błędy (literówki w kluczach), brak walidacji typów i utrudnia czytelność kodu.
    -   **Rekomendacja:** Wprowadzić `dataclass` (np. `AssetData`, `FileInfo`) do reprezentowania danych. Zapewni to bezpieczeństwo typów, autouzupełnianie w IDE i znacznie czytelniejszy kod.

3.  **Ścisłe Powiązanie i Brak Wstrzykiwania Zależności:**
    -   **Problem:** Funkcje w module bezpośrednio wywołują inne funkcje z tego samego modułu lub importują konkretne implementacje (np. `core.json_utils`, `core.thumbnail`). To tworzy silne powiązania i utrudnia testowanie jednostkowe (mockowanie zależności).
    -   **Rekomendacja:** Tam, gdzie to możliwe, używać wstrzykiwania zależności. Np. `AssetCreator` mógłby przyjmować `ThumbnailService` w konstruktorze, zamiast bezpośrednio go importować.

4.  **Niejasne Granice Odpowiedzialności Funkcji:**
    -   **Problem:** Funkcje takie jak `_create_single_asset` wykonują wiele zadań: wczytują istniejące dane, obliczają rozmiar, sprawdzają foldery tekstur, zapisują dane i tworzą miniaturę. To sprawia, że są długie i trudne do zrozumienia.
    -   **Rekomendacja:** Rozbić te funkcje na mniejsze, bardziej spójne jednostki. Np. `_create_single_asset` mogłoby delegować zadania do `AssetCreator` i `ThumbnailService`.

5.  **Brak Pełnych Adnotacji Typów:**
    -   **Problem:** Wiele funkcji nie posiada pełnych adnotacji typów, co utrudnia statyczną analizę kodu i zrozumienie oczekiwanych typów danych.
    -   **Rekomendacja:** Dodać pełne adnotacje typów do wszystkich funkcji i zmiennych.
