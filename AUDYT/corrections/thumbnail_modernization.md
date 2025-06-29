### 🚀 thumbnail.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Pełna Asynchronizacja Generowania Miniatur:**
    -   **Cel:** Przeniesienie wszystkich operacji przetwarzania obrazu do puli wątków, aby zapewnić pełną responsywność UI.
    -   **Plan Działania:**
        1.  **`ThumbnailTask(QRunnable)`:** Stworzyć klasę dziedziczącą z `QRunnable`, która będzie zawierała logikę przetwarzania pojedynczego obrazu (otwieranie, skalowanie, zapis). Będzie ona przyjmować ścieżkę do obrazu, konfigurację i callback/sygnał do raportowania wyniku.
        2.  **`ThumbnailProcessor` (nowy):** Będzie odpowiedzialny za zarządzanie `QThreadPool`. Będzie przyjmował żądania generowania miniatur i dodawał `ThumbnailTask` do puli wątków. Będzie również nasłuchiwał na sygnały z `ThumbnailTask` i emitował własne sygnały (np. `thumbnail_ready(path, QPixmap)`).
        3.  **`ThumbnailLoaderWorker` (usunięcie/redefinicja):** Obecna klasa `ThumbnailLoaderWorker` jest zbędna lub powinna zostać przeprojektowana jako część `ThumbnailTask`.

2.  **Wydzielenie Logiki Konfiguracji i Cache:**
    -   **Cel:** Oddzielenie odpowiedzialności i ułatwienie testowania.
    -   **Plan Działania:**
        1.  **`ThumbnailConfigManager`:** Może pozostać jako singleton, ale powinien być wstrzykiwany do `ThumbnailProcessor`.
        2.  **`ThumbnailCacheManager`:** Powinien być wstrzykiwany do `ThumbnailProcessor` i `ThumbnailTask`. Będzie odpowiedzialny za zarządzanie ścieżkami do cache i sprawdzanie aktualności miniatur.
        3.  **`ThumbnailCache` (LRU):** Może pozostać jako globalna instancja lub być zarządzany przez `ThumbnailCacheManager`.

3.  **Użycie `dataclasses` dla Danych Konfiguracyjnych:**
    -   **Cel:** Zastąpienie słowników typowanymi, strukturalnymi obiektami dla konfiguracji.
    -   **Plan Działania:**
        1.  Zdefiniować `ThumbnailSettings` jako `dataclass` zawierającą pola takie jak `size`, `quality`, `format`, `cache_dir_name`.
        2.  `ThumbnailConfigManager` będzie zwracał instancję `ThumbnailSettings`.

4.  **Ujednolicenie Obsługi Błędów:**
    -   **Cel:** Zapewnienie spójnego sposobu raportowania błędów przetwarzania miniatur.
    -   **Plan Działania:**
        1.  `ThumbnailTask` powinien emitować sygnał `error_occurred(path, error_message)` w przypadku niepowodzenia.
        2.  `ThumbnailProcessor` będzie nasłuchiwał na te błędy i logował je, a także mógłby przekazywać je dalej do UI.

5.  **Pełne Adnotacje Typów:**
    -   **Cel:** Poprawa czytelności i umożliwienie statycznej analizy kodu.
    -   **Plan Działania:**
        1.  Upewnić się, że wszystkie metody i atrybuty mają precyzyjne adnotacje typów.
