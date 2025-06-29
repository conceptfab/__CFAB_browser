### 🚀 folder_tree_view.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Implementacja Wzorca Delegata (`QStyledItemDelegate`):**
    -   **Cel:** Przejęcie pełnej kontroli nad wyglądem i zachowaniem elementów drzewa, co jest kluczowe dla wydajnego podświetlania i potencjalnie bardziej złożonego renderowania w przyszłości.
    -   **Plan Działania:**
        1.  Stworzyć klasę `FolderTreeDelegate`, która dziedziczy po `QStyledItemDelegate`.
        2.  Zaimplementować metodę `paint()`, aby niestandardowo rysować tło dla elementów podświetlonych podczas operacji drag & drop. Dane o tym, który element jest podświetlony, powinny być przechowywane w modelu drzewa (jako niestandardowa rola danych) lub w kontrolerze.
        3.  Ustawić instancję tego delegata dla `CustomFolderTreeView` za pomocą `setItemDelegate()`.

2.  **Refaktoryzacja do Architektury Sterowanej Sygnałami:**
    -   **Cel:** Całkowite oddzielenie widoku od logiki biznesowej i operacji na modelach.
    -   **Plan Działania:**
        1.  Usunąć z widoku wszystkie bezpośrednie odwołania do modeli (`drag_drop_model`, `file_operations_model` itp.).
        2.  Widok powinien emitować szczegółowe sygnały, np. `drop_occurred(target_path, mime_data)`, `context_menu_requested(path, position)`.
        3.  Dedykowany kontroler (`FolderTreeController`) będzie podłączony do tych sygnałów i będzie odpowiedzialny za całą logikę (walidację, wywoływanie operacji na plikach, aktualizowanie modeli).

3.  **Wprowadzenie `QTimer` dla Debouncingu:**
    -   **Cel:** Zrealizowanie wymagania "debounced expansion" z dokumentacji `stage_2.md`.
    -   **Plan Działania:**
        1.  W kontrolerze (`FolderTreeController`) utworzyć `QTimer` z `setSingleShot(True)`.
        2.  Gdy widok emituje sygnał `expanded` lub `collapsed`, kontroler nie reaguje od razu, lecz resetuje i uruchamia timer (np. na 150 ms).
        3.  Dopiero gdy timer zakończy odliczanie (co oznacza przerwę w akcjach użytkownika), kontroler wykonuje operację lazy-loadingu dla wszystkich zakolejkowanych zmian.

4.  **Modernizacja API i Sygnatur Metod:**
    -   **Cel:** Poprawa czytelności i bezpieczeństwa typów.
    -   **Plan Działania:**
        1.  Dodać pełne adnotacje typów (`type hints`) do wszystkich metod i atrybutów.
        2.  Zastąpić przekazywanie getterów (`current_folder_path_getter`) na rzecz bardziej jawnej komunikacji przez sygnały lub bezpośrednie zapytania do modelu w kontrolerze.
        3.  Używać `pathlib.Path` do reprezentowania ścieżek zamiast stringów.
