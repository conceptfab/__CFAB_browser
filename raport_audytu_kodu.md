# Raport z Audytu Kodu - Katalog `core`

Na podstawie analizy kodu w katalogu `core` zidentyfikowano następujące obszary wymagające poprawy w celu zwiększenia czytelności, wydajności i utrzymywalności kodu. Poniżej znajduje się lista zadań do wykonania przez model AI.

## Lista Zadań do Wykonania:

1.  **Usunięcie zbędnych klas bazowych (`base_widgets.py`)**
    *   **Plik:** `core/base_widgets.py`
    *   **Problem:** Plik definiuje puste klasy bazowe (np. `BaseFrame`, `BaseLabel`), które miały służyć do stylizacji. Stylizacja jest realizowana w całości przez arkusze stylów (QSS) za pomocą selektorów ID i klas, co czyni te klasy Pythona zbędnymi.
    *   **Zadanie:**
        1.  Usunąć plik `core/base_widgets.py`.
        2.  Znaleźć wszystkie klasy w projekcie, które dziedziczą z tych bazowych klas (np. `AmvView(BaseWidget)`, `AssetTileView(TileBase)`).
        3.  Zmienić ich dziedziczenie na odpowiednie, wbudowane klasy PyQt6 (np. `QWidget`, `QFrame`).

2.  **Usunięcie nieużywanego workera skanera folderów**
    *   **Plik:** `core/folder_scanner_worker.py`
    *   **Problem:** Klasa `FolderStructureScanner` wydaje się być przestarzałą implementacją, której logika została zastąpiona przez nowsze komponenty, takie jak `AssetRepository` i modele w architekturze MVVM. Plik zawiera nieużywane importy i zakomentowany kod, co wskazuje na jego dezaktualizację.
    *   **Zadanie:** Usunąć plik `core/folder_scanner_worker.py` z projektu.

3.  **Refaktoryzacja i podział plików modeli (Zasada Pojedynczej Odpowiedzialności)**
    *   **Plik:** `core/amv_models/asset_grid_model.py`
    *   **Problem:** Plik ten łamie zasadę pojedynczej odpowiedzialności (SRP), definiując cztery oddzielne klasy modeli: `AssetGridModel`, `FolderTreeModel`, `FolderSystemModel` oraz `WorkspaceFoldersModel`. Dodatkowo, klasa `FolderTreeModel` jest prawdopodobnie nieużywana, ponieważ `FolderSystemModel` implementuje pełną logikę drzewa folderów.
    *   **Zadanie:**
        1.  Przenieść klasę `FolderSystemModel` do nowego pliku `core/amv_models/folder_system_model.py`.
        2.  Przenieść klasę `WorkspaceFoldersModel` do nowego pliku `core/amv_models/workspace_folders_model.py`.
        3.  Usunąć zbędną klasę `FolderTreeModel` z pliku `asset_grid_model.py`.
        4.  Zaktualizować wszystkie importy w projekcie, aby odzwierciedlały nową strukturę plików.

4.  **Przeniesienie workera operacji na plikach**
    *   **Plik:** `core/amv_models/file_operations_model.py`
    *   **Problem:** Klasa `FileOperationsWorker` jest zdefiniowana w tym samym pliku co `FileOperationsModel`. Dla zachowania spójności i separacji logiki, workery powinny znajdować się w dedykowanym katalogu `core/workers`.
    *   **Zadanie:** Przenieść klasę `FileOperationsWorker` do nowego pliku `core/workers/file_operations_worker.py` i zaktualizować import w `file_operations_model.py`.

5.  **Refaktoryzacja `AmvController` (zmniejszenie złożoności)**
    *   **Plik:** `core/amv_controllers/amv_controller.py`
    *   **Problem:** Klasa `AmvController` pełni rolę "God Object", obsługując zbyt wiele sygnałów i logiki, która powinna należeć do bardziej wyspecjalizowanych sub-kontrolerów (np. `AssetGridController`). Metody takie jak `_on_scan_started`, `_on_scan_completed` czy `_on_config_loaded` powinny być przeniesione.
    *   **Zadanie:** Zrefaktoryzować `AmvController`, przenosząc logikę obsługi sygnałów (metody `_on_*`) do odpowiednich sub-kontrolerów (`AssetGridController`, `ControlPanelController`, `FolderTreeController`), aby zmniejszyć jego złożoność i poprawić separację odpowiedzialności.

6.  **Optymalizacja aktualizacji paska statusu**
    *   **Plik:** `core/main_window.py`
    *   **Problem:** Metoda `update_selection_status` oblicza liczbę zaznaczonych elementów, iterując po widgetach `AssetTileView` w interfejsie użytkownika. Jest to nieefektywne i stanowi zły wzorzec (pobieranie stanu z widoku zamiast z modelu).
    *   **Zadanie:** Zmodyfikować metodę `update_selection_status`, aby pobierała informacje o liczbie zaznaczonych i wszystkich assetów bezpośrednio z odpowiednich modeli (`SelectionModel`, `AssetGridModel`), a nie poprzez inspekcję UI.

7.  **Uproszczenie i odseparowanie logiki w `AssetTileView`**
    *   **Plik:** `core/amv_views/asset_tile_view.py`
    *   **Problem:** Klasa zawiera logikę, która powinna być obsługiwana przez sygnały (np. ręczne szukanie `main_window` w pętli `while widget.parent()`). Jest to przykład zbyt ścisłego powiązania (tight coupling).
    *   **Zadanie:** Zastąpić ręczne wyszukiwanie `main_window` mechanizmem sygnałów i slotów. `AssetTileView` powinien emitować sygnał o zmianie zaznaczenia, a `MainWindow` powinien na niego reagować, aktualizując pasek statusu.

8.  **Finalne czyszczenie kodu**
    *   **Pliki:** Wszystkie pliki w `core/**`
    *   **Problem:** Po wykonaniu powyższych refaktoryzacji, w kodzie mogą pozostać nieużywane importy, zmienne lub prywatne metody.
    *   **Zadanie:** Przejrzeć wszystkie modyfikowane pliki i usunąć wszelkie nieużywane elementy, aby zapewnić czystość i porządek w kodzie.
