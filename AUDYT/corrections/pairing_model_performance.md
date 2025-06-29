### ⚡ pairing_model.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Krytyczne Problemy Wydajnościowe:

1.  **Synchroniczne Operacje I/O w Głównym Wątku (KRYTYCZNY PRIORYTET):**
    -   **Problem:** Wszystkie metody wykonujące operacje na plikach (`load_unpair_files`, `save_unpair_files`, `delete_unpaired_archives`, `delete_unpaired_previews`, `create_asset_from_pair`) działają w sposób blokujący. Operacje takie jak usuwanie setek plików lub tworzenie nowego assetu (co wiąże się ze zmianą nazwy, zapisem pliku `.asset` i, co najważniejsze, **tworzeniem miniatury**) mogą zająć od kilkuset milisekund do kilku sekund, całkowicie zamrażając interfejs użytkownika.
    -   **Rekomendacja (KRYTYCZNA):** Wszystkie te operacje muszą być wykonane **asynchronicznie**. Należy je przenieść do dedykowanego wątku roboczego (`QThread`) lub, co jest bardziej nowoczesnym podejściem, zaimplementować jako zadania `asyncio` uruchamiane za pomocą `asyncio.to_thread`. Kontroler powinien inicjować operację, a następnie natychmiast zwrócić kontrolę do pętli zdarzeń, aktualizując UI (np. pokazując pasek postępu lub spinner) na podstawie sygnałów emitowanych przez wątek roboczy.

2.  **Nadmiarowe Zapisy na Dysk:**
    -   **Problem:** Metoda `save_unpair_files()` jest wywoływana po każdej pojedynczej zmianie na listach niesparowanych plików (np. po usunięciu jednej pary, po dodaniu jednego archiwum). Jeśli użytkownik wykonuje wiele takich operacji w krótkim czasie, prowadzi to do serii nieefektywnych, małych zapisów na dysku.
    -   **Rekomendacja (WYSOKA):** Należy zastosować strategię **debounce** lub **batching** dla zapisów. Zamiast zapisywać plik po każdej zmianie, należy:
        a) **Debounce:** Użyć `QTimer`, aby zapisać plik dopiero po upływie np. 2 sekund od ostatniej modyfikacji.
        b) **Batching:** Dodać jawną metodę `save()` lub przycisk "Zapisz zmiany" w interfejsie, aby użytkownik sam decydował, kiedy zapisać wszystkie wprowadzone zmiany naraz.

3.  **Iterowanie i Modyfikowanie Listy Jednocześnie:**
    -   **Problem:** Metody `delete_unpaired_archives` i `delete_unpaired_previews` poprawnie iterują po kopii listy (`for archive_name in self.unpaired_archives[:]`), co zapobiega błędom w czasie wykonania. Jest to jednak sygnał, że operacja jest nieefektywna. Tworzenie kopii dużej listy może zużywać niepotrzebnie pamięć.
    -   **Rekomendacja (NISKA):** Lepszym podejściem jest zbudowanie nowej listy plików, które nie zostały usunięte, lub iterowanie od końca. Jednak po przejściu na model z kolejką operacji i przetwarzaniem w tle, ten problem prawdopodobnie rozwiąże się sam, ponieważ logika będzie inna.
