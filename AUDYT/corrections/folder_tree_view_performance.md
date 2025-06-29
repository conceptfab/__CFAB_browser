### ⚡ folder_tree_view.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Krytyczne Problemy Wydajnościowe:

1.  **Brak Debouncingu dla Zdarzeń Rozwijania/Zwijania (WYSOKI PRIORYTET):**
    -   **Problem:** Dokument `stage_2.md` wyraźnie wskazuje na potrzebę "debounced expansion". Obecny kod nie implementuje żadnego opóźnienia. Sygnały `expanded` i `collapsed` są obsługiwane natychmiast. Jeśli użytkownik szybko klika lub skrypt rozwija wiele gałęzi naraz, może to prowadzić do lawiny operacji (np. lazy loading podfolderów), co obciąży aplikację.
    -   **Rekomendacja (WYSOKA):** Należy zaimplementować mechanizm **debounce** dla obsługi tych zdarzeń. Zamiast reagować na każde kliknięcie, należy użyć `QTimer`, aby poczekać na krótką przerwę (np. 100-200 ms) i dopiero wtedy przetworzyć wszystkie zmiany w jednej operacji. To szczególnie ważne w kontekście lazy loadingu, aby uniknąć wielokrotnego odpytywania systemu plików.

2.  **Nieefektywne Odświeżanie Widoku podczas Drag & Drop:**
    -   **Problem:** Metody `_highlight_folder_at_position` i `_clear_folder_highlight` wywołują `self.viewport().update()` przy każdym ruchu myszy podczas przeciągania. Wymusza to przemalowanie całego widocznego obszaru drzewa, co jest kosztowne i niepotrzebne.
    -   **Rekomendacja (ŚREDNIA):** Zamiast odświeżać cały viewport, należy odświeżać tylko te obszary, które faktycznie się zmieniły. Po przejściu na podświetlanie za pomocą `QStyledItemDelegate`, wystarczy wywołać `view.update(index)` tylko dla indeksu, który ma być podświetlony, oraz dla poprzednio podświetlonego indeksu. Qt jest wystarczająco inteligentne, aby zarządzać tymi małymi obszarami aktualizacji.

3.  **Potencjalnie Blokujące Operacje w Modelu:**
    -   **Problem:** Chociaż sam widok nie wykonuje operacji I/O, jest on połączony z `FolderSystemModel`, który w metodzie `_load_subfolders` używa blokującego `os.listdir()`. Jeśli drzewo folderów jest bardzo głębokie lub znajduje się na wolnym nośniku sieciowym, rozwijanie gałęzi może blokować interfejs użytkownika.
    -   **Rekomendacja (KRYTYCZNA - dotyczy modelu):** Logika ładowania podfolderów w `FolderSystemModel` musi zostać przeniesiona do osobnego wątku (`QThread` lub `asyncio`). Widok po kliknięciu w element do rozwinięcia powinien wyświetlać ikonę ładowania, a następnie asynchronicznie zlecać modelowi załadowanie danych. Po zakończeniu ładowania model powinien emitować sygnał, na który zareaguje widok, wypełniając gałąź danymi.
