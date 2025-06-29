### ⚡ asset_tile_model.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Główne Problemy Wydajnościowe:

1.  **Synchroniczny Zapis do Pliku w Głównym Wątku (WYSOKI PRIORYTET):**
    -   **Problem:** Metoda `set_stars` bezpośrednio wywołuje `_save_to_file()`, która wykonuje blokującą operację zapisu na dysku (`save_to_file`). Każde kliknięcie w gwiazdkę powoduje natychmiastowy zapis do pliku `.asset`. Jeśli plik znajduje się na wolnym nośniku (dysk twardy, dysk sieciowy) lub antywirus skanuje operacje zapisu, może to powodować zauważalne, krótkie zacięcia interfejsu użytkownika.
    -   **Rekomendacja (WYSOKA):** Operacje zapisu na dysku muszą być wykonywane **asynchronicznie**. Należy zaimplementować system kolejkowania zapisów. Zmiany w modelu powinny być dodawane do kolejki, a dedykowany wątek roboczy (`QThread`) lub zadanie `asyncio` powinno w tle przetwarzać tę kolejkę i zapisywać dane na dysku. Można również zastosować strategię "debouce" dla zapisów – np. zapisywać zmiany dopiero po 1-2 sekundach od ostatniej modyfikacji, aby uniknąć wielokrotnych zapisów przy szybkim klikaniu.

2.  **Wielokrotne Wywołania `os.path.dirname`:**
    -   **Problem:** Metoda `_get_folder_path_from_file` jest wywoływana wielokrotnie w różnych getterach (`get_thumbnail_path`, `get_archive_path`, `get_preview_path`). Chociaż jest to bardzo szybka operacja, jej wielokrotne, niepotrzebne wywoływanie jest nieeleganckie i stanowi drobny, ale zbędny narzut.
    -   **Rekomendacja (NISKA):** Obliczyć ścieżkę do folderu raz w konstruktorze (`__init__`) i zapisać ją w atrybucie `self._folder_path`. Gettery powinny następnie korzystać z tego atrybutu. Jest to mikrooptymalizacja, ale poprawia czystość kodu.
