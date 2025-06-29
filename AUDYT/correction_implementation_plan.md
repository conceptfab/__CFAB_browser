### **I. KRYTYCZNE POPRAWKI WYDAJNOŚCI I ARCHITEKTURY (Najwyższy Priorytet)**

Te poprawki są kluczowe dla stabilności, responsywności i skalowalności aplikacji. Należy je wdrożyć w pierwszej kolejności.

1.  **Asynchroniczne Generowanie Miniatur i Cache'owanie (core/thumbnail.py, core/scanner.py)**
    *   **Cel:** Znaczące przyspieszenie procesu skanowania i ładowania miniatur, zmniejszenie obciążenia CPU i I/O.
    *   **Instrukcje dla modelu:**
        1.  Zapoznaj się z analizami w plikach:
            *   `AUDYT/corrections/thumbnail_correction.md`
            *   `AUDYT/corrections/thumbnail_performance.md`
            *   `AUDYT/corrections/thumbnail_modernization.md`
            *   `AUDYT/corrections/thumbnail_cache_lazy_loading_correction.md`
            *   `AUDYT/corrections/scanner_correction.md`
            *   `AUDYT/corrections/scanner_performance.md`
            *   `AUDYT/corrections/scanner_modernization.md`
        2.  Wprowadź zmiany w plikach:
            *   `core/thumbnail.py` (przeniesienie logiki generowania miniatur z `ThumbnailProcessor` do puli wątków (`QThreadPool`) lub osobnego procesu. `process_thumbnail` powinien delegować to zadanie i zwracać wynik asynchronicznie. Upewnienie się, że `_thumbnail_cache` jest efektywnie wykorzystywany.)
            *   `core/scanner.py` (zmodyfikowanie `create_thumbnail_for_asset` tak, aby korzystała z asynchronicznego generowania miniatur.)
        3.  Po każdej logicznej zmianie, upewnij się, że kod działa poprawnie i nie wprowadza regresji. Odwołaj się do zasad w `poprawki.md`.
        4.  Zaktualizuj pliki patchujące:
            *   `AUDYT/patches/thumbnail_patch_code.md`
            *   `AUDYT/patches/thumbnail_optimization_patch.md`
            *   `AUDYT/patches/thumbnail_cache_lazy_loading_patch.md`
            *   `AUDYT/patches/scanner_patch_code.md`
            *   `AUDYT/patches/scanner_optimization_patch.md`
    *   **Powiązane pliki:** `core/thumbnail.py`, `core/scanner.py`

2.  **Implementacja Object Pooling / Virtual Scrolling dla Kafelków (core/amv_views/asset_tile_view.py, core/amv_views/preview_gallery_view.py, core/amv_controllers/amv_controller.py)**
    *   **Cel:** Eliminacja zacięć UI i nadmiernego zużycia pamięci podczas przewijania i odświeżania galerii.
    *   **Instrukcje dla modelu:**
        1.  Zapoznaj się z analizami w plikach:
            *   `AUDYT/corrections/asset_tile_view_correction.md`
            *   `AUDYT/corrections/asset_tile_view_performance.md`
            *   `AUDYT/corrections/asset_tile_view_modernization.md`
            *   `AUDYT/corrections/asset_tile_view_cache_lazy_loading_correction.md`
            *   `AUDYT/corrections/preview_gallery_view_correction.md`
            *   `AUDYT/corrections/preview_gallery_view_performance.md`
            *   `AUDYT/corrections/preview_gallery_view_modernization.md`
            *   `AUDYT/corrections/preview_gallery_view_cache_lazy_loading_correction.md`
            *   `AUDYT/corrections/amv_controller_correction.md`
            *   `AUDYT/corrections/amv_controller_performance.md`
            *   `AUDYT/corrections/amv_controller_modernization.md`
            *   `AUDYT/corrections/asset_grid_model_correction.md`
            *   `AUDYT/corrections/asset_grid_model_performance.md`
            *   `AUDYT/corrections/asset_grid_model_modernization.md`
            *   `AUDYT/corrections/asset_grid_model_cache_lazy_loading_correction.md`
        2.  Wprowadź zmiany w plikach:
            *   **`core/amv_views/asset_tile_view.py`:** Implementacja lazy loading dla miniatur (ładowanie tylko widocznych) i wykorzystanie globalnego cache miniatur.
            *   **`core/amv_views/preview_gallery_view.py`:** Implementacja object pooling/virtual scrolling dla `PreviewTile`. Optymalizacja `resizeEvent` tak, aby nie niszczyła i tworzyła kafelków od nowa.
            *   **`core/amv_controllers/amv_controller.py`:** Refaktoryzacja `_rebuild_asset_grid` w celu wykorzystania object pooling/virtual scrolling.
        3.  Po każdej logicznej zmianie, upewnij się, że kod działa poprawnie i nie wprowadza regresji. Odwołaj się do zasad w `poprawki.md`.
        4.  Zaktualizuj pliki patchujące:
            *   `AUDYT/patches/asset_tile_view_patch_code.md`
            *   `AUDYT/patches/asset_tile_view_optimization_patch.md`
            *   `AUDYT/patches/asset_tile_view_cache_lazy_loading_patch.md`
            *   `AUDYT/patches/preview_gallery_view_patch_code.md`
            *   `AUDYT/patches/preview_gallery_view_optimization_patch.md`
            *   `AUDYT/patches/preview_gallery_view_cache_lazy_loading_patch.md`
            *   `AUDYT/patches/amv_controller_patch_code.md`
            *   `AUDYT/patches/amv_controller_optimization_patch.md`
            *   `AUDYT/patches/asset_grid_model_patch_code.md`
            *   `AUDYT/patches/asset_grid_model_optimization_patch.md`
            *   `AUDYT/patches/asset_grid_model_cache_lazy_loading_patch.md`
    *   **Powiązane pliki:** `core/amv_views/asset_tile_view.py`, `core/amv_views/preview_gallery_view.py`, `core/amv_controllers/amv_controller.py`, `core/amv_models/asset_grid_model.py` (lazy loading/cache)

3.  **Modernizacja Architektury MVC i Wstrzykiwanie Zależności (DI) (core/amv_models/amv_model.py, core/amv_controllers/amv_controller.py, core/amv_views/amv_view.py, core/amv_tab.py)**
    *   **Cel:** Poprawa modularności, testowalności i elastyczności aplikacji.
    *   **Instrukcje dla modelu:**
        1.  Zapoznaj się z analizami w plikach:
            *   `AUDYT/corrections/amv_model_mvc_modernization_correction.md`
            *   `AUDYT/corrections/amv_model_dependency_injection_correction.md`
            *   `AUDYT/corrections/amv_controller_mvc_modernization_correction.md`
            *   `AUDYT/corrections/amv_controller_dependency_injection_correction.md`
            *   `AUDYT/corrections/amv_view_mvc_modernization_correction.md`
            *   `AUDYT/corrections/amv_tab_mvc_modernization_correction.md`
        2.  Wprowadź zmiany w plikach:
            *   **`core/amv_models/amv_model.py`:** Wstrzykiwanie zależności w konstruktorze dla wszystkich podległych modeli/repozytoriów. Definicja abstrakcyjnych interfejsów Repository.
            *   **`core/amv_controllers/amv_controller.py`:** Wstrzykiwanie bezpośrednich zależności do potrzebnych modeli (zamiast dostępu przez `self.model`).
            *   **`core/amv_views/amv_view.py`:** Wstrzykiwanie zależności dla widżetów (np. `CustomFolderTreeView`).
            *   **`core/amv_tab.py`:** Wstrzykiwanie zależności dla `AmvModel` i `AmvView`.
        3.  Po każdej logicznej zmianie, upewnij się, że kod działa poprawnie i nie wprowadza regresji. Odwołaj się do zasad w `poprawki.md`.
        4.  Zaktualizuj pliki patchujące:
            *   `AUDYT/patches/amv_model_mvc_modernization_patch.md`
            *   `AUDYT/patches/amv_model_dependency_injection_patch.md`
            *   `AUDYT/patches/amv_controller_mvc_modernization_patch.md`
            *   `AUDYT/patches/amv_controller_dependency_injection_patch.md`
            *   `AUDYT/patches/amv_view_mvc_modernization_patch.md`
            *   `AUDYT/patches/amv_tab_mvc_modernization_patch.md`
    *   **Powiązane pliki:** `core/amv_models/amv_model.py`, `core/amv_controllers/amv_controller.py`, `core/amv_views/amv_view.py`, `core/amv_tab.py`

4.  **Implementacja Wzorca Repository (core/scanner.py, core/amv_models/file_operations_model.py)**
    *   **Cel:** Abstrakcja warstwy dostępu do danych, ułatwienie testowania i przyszłych zmian w przechowywaniu danych.
    *   **Instrukcje dla modelu:**
        1.  Zapoznaj się z analizami w plikach:
            *   `AUDYT/corrections/scanner_repository_pattern_correction.md`
            *   `AUDYT/corrections/file_operations_model_repository_pattern_correction.md`
        2.  Wprowadź zmiany w plikach:
            *   **`core/scanner.py`:** Przekształcenie w klasę `AssetRepository` implementującą `IAssetRepository`, enkapsulującą logikę skanowania i ładowania assetów.
            *   **`core/amv_models/file_operations_model.py`:** Przekształcenie w klasę implementującą `IFileOperationsRepository`.
        3.  Po każdej logicznej zmianie, upewnij się, że kod działa poprawnie i nie wprowadza regresji. Odwołaj się do zasad w `poprawki.md`.
        4.  Zaktualizuj pliki patchujące:
            *   `AUDYT/patches/scanner_repository_pattern_patch.md`
            *   `AUDYT/patches/file_operations_model_repository_pattern_patch.md`
    *   **Powiązane pliki:** `core/scanner.py`, `core/amv_models/file_operations_model.py`

---

### **II. WYSOKIE PRIORYTETY (Wpływ na Wydajność i Jakość Kodu)**

Te poprawki mają znaczący wpływ na wydajność i jakość kodu, ale mogą być wdrożone po zakończeniu krytycznych poprawek.

1.  **Implementacja Monitoringu Wydajności (core/amv_controllers/amv_controller.py, core/scanner.py, core/thumbnail.py)**
    *   **Cel:** Zapewnienie narzędzi do ciągłej optymalizacji i identyfikacji bottlenecków.
    *   **Instrukcje dla modelu:**
        1.  Zapoznaj się z analizami w plikach:
            *   `AUDYT/corrections/amv_controller_performance_monitoring_correction.md`
            *   `AUDYT/corrections/scanner_performance_monitoring_correction.md`
            *   `AUDYT/corrections/thumbnail_performance_monitoring_correction.md`
        2.  Wprowadź zmiany w plikach:
            *   **`core/amv_controllers/amv_controller.py`:** Pomiar czasu trwania kluczowych operacji, monitorowanie zużycia pamięci.
            *   **`core/scanner.py`:** Pomiar czasu trwania funkcji skanujących i tworzących assety.
            *   **`core/thumbnail.py`:** Pomiar czasu trwania operacji przetwarzania obrazów.
        3.  Po każdej logicznej zmianie, upewnij się, że kod działa poprawnie i nie wprowadza regresji. Odwołaj się do zasad w `poprawki.md`.
        4.  Zaktualizuj pliki patchujące:
            *   `AUDYT/patches/amv_controller_performance_monitoring_patch.md`
            *   `AUDYT/patches/scanner_performance_monitoring_patch.md`
            *   `AUDYT/patches/thumbnail_performance_monitoring_patch.md`
    *   **Powiązane pliki:** `core/amv_controllers/amv_controller.py`, `core/scanner.py`, `core/thumbnail.py`

---

### **III. ŚREDNIE PRIORYTETY (Optymalizacja i Usprawnienia)**

Te poprawki poprawiają wydajność i jakość kodu, ale nie są tak krytyczne jak poprzednie.

1.  **Optymalizacja Ładowania i Skalowania Obrazów w `PreviewWindow` (core/preview_window.py)**
    *   **Cel:** Zmniejszenie zacięć UI podczas otwierania i skalowania dużych obrazów podglądu.
    *   **Instrukcje dla modelu:**
        1.  Zapoznaj się z analizami w plikach:
            *   `AUDYT/corrections/preview_window_correction.md`
            *   `AUDYT/corrections/preview_window_performance.md`
            *   `AUDYT/corrections/preview_window_modernization.md`
            *   `AUDYT/corrections/preview_window_thread_safety_correction.md`
        2.  Wprowadź zmiany w plikach:
            *   **`core/preview_window.py`:** Asynchroniczne ładowanie obrazów, optymalizacja skalowania `QPixmap`, efektywne zarządzanie pamięcią `QPixmap`.
        3.  Po każdej logicznej zmianie, upewnij się, że kod działa poprawnie i nie wprowadza regresji. Odwołaj się do zasad w `poprawki.md`.
        4.  Zaktualizuj pliki patchujące:
            *   `AUDYT/patches/preview_window_patch_code.md`
            *   `AUDYT/patches/preview_window_optimization_patch.md`
            *   `AUDYT/patches/preview_window_thread_safety_patch.md`
    *   **Powiązane pliki:** `core/preview_window.py`

---

### **IV. NISKIE PRIORYTETY (Usprawnienia Jakości Kodu i Drobne Optymalizacje)**

Te poprawki dotyczą głównie jakości kodu, czytelności i drobnych optymalizacji.

1.  **Wprowadzenie Type Hints (wszystkie analizowane pliki)**
    *   **Cel:** Zwiększenie czytelności kodu, ułatwienie debugowania i wczesne wykrywanie błędów.
    1.  **Wprowadzenie Type Hints (wszystkie analizowane pliki)**
    *   **Cel:** Zwiększenie czytelności kodu, ułatwienie debugowania i wczesne wykrywanie błędów.
    *   **Instrukcje dla modelu:**
        1.  Zapoznaj się z analizami w plikach:
            *   `AUDYT/corrections/amv_controller_correction.md`
            *   `AUDYT/corrections/amv_controller_dependency_injection_correction.md`
            *   `AUDYT/corrections/amv_controller_mvc_modernization_correction.md`
            *   `AUDYT/corrections/amv_controller_performance_monitoring_correction.md`
            *   `AUDYT/corrections/amv_model_dependency_injection_correction.md`
            *   `AUDYT/corrections/amv_model_mvc_modernization_correction.md`
            *   `AUDYT/corrections/amv_model_repository_pattern_correction.md`
            *   `AUDYT/corrections/asset_grid_model_cache_lazy_loading_correction.md`
            *   `AUDYT/corrections/asset_grid_model_correction.md`
            *   `AUDYT/corrections/asset_grid_model_thread_safety_correction.md`
            *   `AUDYT/corrections/asset_tile_view_cache_lazy_loading_correction.md`
            *   `AUDYT/corrections/asset_tile_view_correction.md`
            *   `AUDYT/corrections/asset_tile_view_thread_safety_correction.md`
            *   `AUDYT/corrections/file_operations_model_correction.md`
            *   `AUDYT/corrections/file_operations_model_repository_pattern_correction.md`
            *   `AUDYT/corrections/folder_scanner_worker_correction.md`
            *   `AUDYT/corrections/preview_gallery_view_cache_lazy_loading_correction.md`
            *   `AUDYT/corrections/preview_gallery_view_correction.md`
            *   `AUDYT/corrections/preview_gallery_view_thread_safety_correction.md`
            *   `AUDYT/corrections/preview_window_correction.md`
            *   `AUDYT/corrections/preview_window_thread_safety_correction.md`
            *   `AUDYT/corrections/scanner_correction.md`
            *   `AUDYT/corrections/scanner_performance_monitoring_correction.md`
            *   `AUDYT/corrections/scanner_repository_pattern_correction.md`
            *   `AUDYT/corrections/thumbnail_cache_lazy_loading_correction.md`
            *   `AUDYT/corrections/thumbnail_correction.md`
            *   `AUDYT/corrections/thumbnail_performance_monitoring_correction.md`
        2.  Wprowadź zmiany w plikach:
            *   Dodaj pełne adnotacje typów do wszystkich funkcji, metod i zmiennych we wszystkich analizowanych plikach.
        3.  Po każdej logicznej zmianie, upewnij się, że kod działa poprawnie i nie wprowadza regresji. Odwołaj się do zasad w `poprawki.md`.
        4.  Zaktualizuj pliki patchujące:
            *   `AUDYT/patches/amv_controller_patch_code.md`
            *   `AUDYT/patches/amv_controller_optimization_patch.md`
            *   `AUDYT/patches/amv_controller_mvc_modernization_patch.md`
            *   `AUDYT/patches/amv_controller_dependency_injection_patch.md`
            *   `AUDYT/patches/amv_controller_performance_monitoring_patch.md`
            *   `AUDYT/patches/amv_model_dependency_injection_patch.md`
            *   `AUDYT/patches/amv_model_mvc_modernization_patch.md`
            *   `AUDYT/patches/amv_model_repository_pattern_patch.md`
            *   `AUDYT/patches/asset_grid_model_cache_lazy_loading_patch.md`
            *   `AUDYT/patches/asset_grid_model_patch_code.md`
            *   `AUDYT/patches/asset_grid_model_optimization_patch.md`
            *   `AUDYT/patches/asset_grid_model_thread_safety_patch.md`
            *   `AUDYT/patches/asset_tile_view_cache_lazy_loading_patch.md`
            *   `AUDYT/patches/asset_tile_view_patch_code.md`
            *   `AUDYT/patches/asset_tile_view_optimization_patch.md`
            *   `AUDYT/patches/asset_tile_view_thread_safety_patch.md`
            *   `AUDYT/patches/file_operations_model_patch_code.md`
            *   `AUDYT/patches/file_operations_model_optimization_patch.md`
            *   `AUDYT/patches/file_operations_model_repository_pattern_patch.md`
            *   `AUDYT/patches/folder_scanner_worker_patch_code.md`
            *   `AUDYT/patches/folder_scanner_worker_optimization_patch.md`
            *   `AUDYT/patches/preview_gallery_view_cache_lazy_loading_patch.md`
            *   `AUDYT/patches/preview_gallery_view_patch_code.md`
            *   `AUDYT/patches/preview_gallery_view_optimization_patch.md`
            *   `AUDYT/patches/preview_gallery_view_thread_safety_patch.md`
            *   `AUDYT/patches/preview_window_patch_code.md`
            *   `AUDYT/patches/preview_window_optimization_patch.md`
            *   `AUDYT/patches/preview_window_thread_safety_patch.md`
            *   `AUDYT/patches/scanner_patch_code.md`
            *   `AUDYT/patches/scanner_optimization_patch.md`
            *   `AUDYT/patches/scanner_performance_monitoring_patch.md`
            *   `AUDYT/patches/scanner_repository_pattern_patch.md`
            *   `AUDYT/patches/thumbnail_cache_lazy_loading_patch.md`
            *   `AUDYT/patches/thumbnail_patch_code.md`
            *   `AUDYT/patches/thumbnail_optimization_patch.md`
            *   `AUDYT/patches/thumbnail_performance_monitoring_patch.md`
    *   **Powiązane pliki:** Wszystkie analizowane pliki.

2.  **Ulepszone Zarządzanie Zasobami (Context Managers) (core/amv_models/file_operations_model.py, core/scanner.py, core/thumbnail.py)**
    *   **Cel:** Zapewnienie prawidłowego zwalniania zasobów i unikanie wycieków.
    *   **Instrukcje dla modelu:**
        1.  Zapoznaj się z analizami w plikach:
            *   `AUDYT/corrections/file_operations_model_correction.md`
            *   `AUDYT/corrections/file_operations_model_modernization.md`
            *   `AUDYT/corrections/scanner_correction.md`
            *   `AUDYT/corrections/scanner_modernization.md`
            *   `AUDYT/corrections/thumbnail_correction.md`
            *   `AUDYT/corrections/thumbnail_modernization.md`
        2.  Wprowadź zmiany w plikach:
            *   **`core/amv_models/file_operations_model.py`:** Upewnienie się, że wszystkie operacje na plikach używają `with open(...)` lub innych odpowiednich menedżerów kontekstu.
            *   **`core/scanner.py`:** Upewnienie się, że wszystkie operacje na plikach używają `with open(...)` lub innych odpowiednich menedżerów kontekstu.
            *   **`core/thumbnail.py`:** Upewnienie się, że wszystkie operacje na plikach (np. `Image.open()`) używają `with` statement.
        3.  Po każdej logicznej zmianie, upewnij się, że kod działa poprawnie i nie wprowadza regresji. Odwołaj się do zasad w `poprawki.md`.
        4.  Zaktualizuj pliki patchujące:
            *   `AUDYT/patches/file_operations_model_patch_code.md`
            *   `AUDYT/patches/scanner_patch_code.md`
            *   `AUDYT/patches/thumbnail_patch_code.md`
    *   **Powiązane pliki:** `core/amv_models/file_operations_model.py`, `core/scanner.py`, `core/thumbnail.py`

3.  **Weryfikacja Thread Safety (core/amv_models/asset_grid_model.py, core/amv_views/asset_tile_view.py, core/amv_views/preview_gallery_view.py, core/preview_window.py)**
    *   **Cel:** Potwierdzenie i ewentualne drobne usprawnienia w zakresie bezpieczeństwa wątkowego.
    *   **Instrukcje dla modelu:**
        1.  Zapoznaj się z analizami w plikach:
            *   `AUDYT/corrections/asset_grid_model_thread_safety_correction.md`
            *   `AUDYT/corrections/asset_tile_view_thread_safety_correction.md`
            *   `AUDYT/corrections/preview_gallery_view_thread_safety_correction.md`
            *   `AUDYT/corrections/preview_window_thread_safety_correction.md`
        2.  Wprowadź zmiany w plikach:
            *   **`core/amv_models/asset_grid_model.py`:** Weryfikacja dostępu do danych, cyklu życia połączeń sygnał-slot.
            *   **`core/amv_views/asset_tile_view.py`:** Weryfikacja dostępu do danych, cyklu życia połączeń sygnał-slot.
            *   **`core/amv_views/preview_gallery_view.py`:** Weryfikacja dostępu do danych, cyklu życia połączeń sygnał-slot.
            *   **`core/preview_window.py`:** Weryfikacja dostępu do danych, cyklu życia połączeń sygnał-slot.
        3.  Po każdej logicznej zmianie, upewnij się, że kod działa poprawnie i nie wprowadza regresji. Odwołaj się do zasad w `poprawki.md`.
        4.  Zaktualizuj pliki patchujące:
            *   `AUDYT/patches/asset_grid_model_thread_safety_patch.md`
            *   `AUDYT/patches/asset_tile_view_thread_safety_patch.md`
            *   `AUDYT/patches/preview_gallery_view_thread_safety_patch.md`
            *   `AUDYT/patches/preview_window_thread_safety_patch.md`
    *   **Powiązane pliki:** `core/amv_models/asset_grid_model.py`, `core/amv_views/asset_tile_view.py`, `core/amv_views/preview_gallery_view.py`, `core/preview_window.py`

4.  **Optymalizacja Skanowania Folderów (core/folder_scanner_worker.py)**
    *   **Cel:** Drobne usprawnienia w wydajności skanowania folderów.
    *   **Instrukcje dla modelu:**
        1.  Zapoznaj się z analizami w plikach:
            *   `AUDYT/corrections/folder_scanner_worker_correction.md`
            *   `AUDYT/corrections/folder_scanner_worker_performance.md`
            *   `AUDYT/corrections/folder_scanner_worker_modernization.md`
        2.  Wprowadź zmiany w plikach:
            *   **`core/folder_scanner_worker.py`:** Optymalizacja zliczania folderów i rekurencyjnego skanowania, jeśli okażą się problematyczne.
        3.  Po każdej logicznej zmianie, upewnij się, że kod działa poprawnie i nie wprowadza regresji. Odwołaj się do zasad w `poprawki.md`.
        4.  Zaktualizuj pliki patchujące:
            *   `AUDYT/patches/folder_scanner_worker_patch_code.md`
            *   `AUDYT/patches/folder_scanner_worker_optimization_patch.md`
    *   **Powiązane pliki:** `core/folder_scanner_worker.py`
