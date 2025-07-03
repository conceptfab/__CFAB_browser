# Plan Refaktoryzacji i Optymalizacji Galerii Assetów

Celem jest poprawa wydajności wyświetlania i interakcji z dużą liczbą assetów w galerii, przy zachowaniu 100% istniejącej funkcjonalności.

---

## Etap 1: Wprowadzenie Asynchronicznego Ładowania i Buforowania Miniatur (Thumbnail Caching)

**Cel:** Wyeliminowanie blokowania interfejsu użytkownika przez operacje I/O podczas ładowania miniatur.

**Kroki:**

1.  **Stworzenie `ThumbnailCache`:**
    *   Utworzenie nowej klasy `core.thumbnail_cache.ThumbnailCache`, która będzie działać jako singleton lub globalnie dostępna instancja.
    *   Cache będzie przechowywał załadowane `QPixmap` w pamięci, używając ścieżki do pliku miniatury jako klucza.
    *   Implementacja metody `get(path)` zwracającej `QPixmap` z cache lub `None`, jeśli go tam nie ma.
    *   Implementacja metody `put(path, pixmap)` dodającej miniaturę do cache.
    *   Dodanie logiki ograniczającej rozmiar cache (np. do 200-300 MB), aby uniknąć nadmiernego zużycia pamięci.

2.  **Stworzenie `ThumbnailLoader` (Worker):**
    *   Utworzenie klasy `core.workers.thumbnail_loader_worker.ThumbnailLoaderWorker` dziedziczącej po `QThread`.
    *   Worker będzie przyjmował w konstruktorze ścieżkę do miniatury.
    *   W metodzie `run()` będzie ładował obraz z dysku do `QPixmap`.
    *   Po załadowaniu, worker wyemituje sygnał `finished(path, pixmap)`.

3.  **Modyfikacja `AssetTileView`:**
    *   Zmiana logiki ładowania miniatury w `_setup_asset_tile_ui`.
    *   Najpierw kafelek spróbuje pobrać `QPixmap` z `ThumbnailCache`.
    *   Jeśli miniatura jest w cache, zostanie natychmiast wyświetlona.
    *   Jeśli nie, kafelek wyświetli tymczasowy placeholder (szary prostokąt) i uruchomi `ThumbnailLoaderWorker` dla danej miniatury.
    *   `AssetTileView` będzie miał slot połączony z sygnałem `finished` workera. Po otrzymaniu sygnału, zaktualizuje swoją ikonę i umieści `QPixmap` w `ThumbnailCache`.

**Testowanie po Etapie 1:**
*   **Sprawdzenie:** Aplikacja powinna uruchamiać się szybciej po wejściu do folderu z dużą liczbą assetów.
*   **Obserwacja:** Miniatury powinny pojawiać się stopniowo, bez "zamrażania" interfejsu. Przewijanie powinno być możliwe, gdy miniatury się ładują.
*   **Weryfikacja:** Wszystkie pozostałe funkcje (klikanie, zaznaczanie, D&D) muszą działać bez zmian.

---

## Etap 2: Optymalizacja Filtrowania i Aktualizacji Siatki

**Cel:** Zastąpienie pełnej przebudowy siatki dynamicznym pokazywaniem/ukrywaniem kafelków.

**Kroki:**

1.  **Modyfikacja `ControlPanelController`:**
    *   Zmiana metody `filter_assets_by_stars`.
    *   Zamiast wywoływać `rebuild_asset_grid`, metoda będzie pobierać listę *wszystkich* kafelków z `AssetGridController`.
    *   Następnie przeiteruje po tej liście. Dla każdego kafelka sprawdzi, czy jego model (`AssetTileModel`) spełnia kryteria filtra (np. ma odpowiednią liczbę gwiazdek).
    *   W zależności od wyniku, wywoła `tile.show()` lub `tile.hide()`.

2.  **Modyfikacja `AssetGridController`:**
    *   Metoda `rebuild_asset_grid` będzie nadal używana przy pierwszym ładowaniu folderu, ale nie przy filtrowaniu.
    *   Należy zapewnić, że `asset_tiles` w kontrolerze zawsze zawiera wszystkie kafelki dla danego folderu, a nie tylko te widoczne.

**Testowanie po Etapie 2:**
*   **Sprawdzenie:** Filtrowanie po gwiazdkach powinno być natychmiastowe, bez widocznego opóźnienia i migotania.
*   **Weryfikacja:** Zaznaczanie, odznaczanie, przenoszenie i usuwanie przefiltrowanych assetów musi działać poprawnie.
*   **Weryfikacja:** Po zmianie filtra i powrocie do widoku wszystkich assetów, stan zaznaczenia poszczególnych kafelków musi być zachowany.

---

## Etap 3: Wprowadzenie "Object Pooling" dla `AssetTileView`

**Cel:** Drastyczne zmniejszenie kosztu tworzenia i niszczenia widgetów przy zmianie folderu lub dużej liczbie assetów.

**Kroki:**

1.  **Stworzenie `AssetTilePool`:**
    *   Utworzenie nowej klasy `core.amv_views.asset_tile_pool.AssetTilePool`.
    *   Pula będzie przechowywać nieużywane instancje `AssetTileView`.
    *   Implementacja metody `acquire()` zwracającej istniejący kafelek z puli lub tworzącej nowy, jeśli pula jest pusta.
    *   Implementacja metody `release(tile)` przyjmującej niepotrzebny kafelek, ukrywającej go i dodającej do puli.

2.  **Modyfikacja `AssetGridController`:**
    *   Kontroler będzie posiadał instancję `AssetTilePool`.
    *   Metoda `rebuild_asset_grid` zostanie fundamentalnie zmieniona:
        *   Na początku, wszystkie istniejące, widoczne kafelki zostaną "uwolnione" do puli za pomocą `pool.release(tile)`.
        *   Następnie, dla każdego assetu do wyświetlenia, kontroler "pozyska" kafelek z puli (`pool.acquire()`).
        *   Pozyskany kafelek zostanie zaktualizowany nowymi danymi (`tile.update_asset_data(...)`), dodany do layoutu i wyświetlony.
    *   Metoda `clear_asset_tiles` zostanie zmodyfikowana, aby uwalniała kafelki do puli zamiast je niszczyć.

3.  **Modyfikacja `AssetTileView`:**
    *   Dodanie metody `update_asset_data(model, ...)` do szybkiej aktualizacji danych kafelka bez potrzeby jego ponownego tworzenia. Metoda ta zaktualizuje etykiety, gwiazdki i załaduje nową miniaturę (korzystając z mechanizmu z Etapu 1).

**Testowanie po Etapie 3:**
*   **Sprawdzenie:** Przełączanie się między folderami (nawet tymi z dużą liczbą assetów) powinno być znacznie szybsze i płynniejsze.
*   **Obserwacja:** Analiza użycia pamięci i zasobów systemowych powinna wykazać mniejsze skoki podczas zmiany folderów.
*   **Weryfikacja:** Wszystkie funkcjonalności (filtrowanie, D&D, operacje na plikach) muszą działać bezbłędnie z nowym systemem zarządzania kafelkami.

---

## Etap 4: Weryfikacja końcowa i czyszczenie kodu

**Cel:** Upewnienie się, że wszystkie zmiany działają harmonijnie i usunięcie ewentualnego martwego kodu.

**Kroki:**

1.  **Pełne testy regresji:** Ponowne przetestowanie wszystkich funkcjonalności aplikacji:
    *   Ładowanie folderów.
    *   Przewijanie galerii.
    *   Filtrowanie.
    *   Zmiana rozmiaru okna i miniaturek.
    *   Zaznaczanie/odznaczanie (pojedyncze, wszystkie).
    *   Drag & Drop do folderów.
    *   Przenoszenie i usuwanie zaznaczonych assetów.
    *   Operacje z zakładki "Narzędzia".
2.  **Przegląd kodu:** Sprawdzenie, czy nie pozostały stare, nieużywane metody związane z poprzednim sposobem budowania siatki.
3.  **Monitoring wydajności:** Ostateczne pomiary wydajności w scenariuszach z dużą liczbą assetów, aby potwierdzić skuteczność optymalizacji.
