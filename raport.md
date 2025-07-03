CFAB Browser - Raport Analizy Kodu
📝 Wykryte Problemy i Zadania do Poprawek
1. core/amv_controllers/amv_controller.py
Duplikaty i redundancja:

Linia 181-184: Usunięty kod AssetRebuilderThread z komentarzem, ale wciąż obecny w pliku
Linia 1100-1200: Funkcja _update_button_states() wywoływana w nadmiarze (12 miejsc) - optymalizacja potrzebna
Linia 800-900: Podobna logika w _on_file_operation_completed i _on_drag_drop_completed

Nieużywane zmienne:

Linia 179: self.asset_rebuilder = None - inicjalizacja nigdy nie używana bezpośrednio
Linia 180: self.original_assets = [] - używana ale można zastąpić wywołaniem modelu

2. core/amv_models/asset_grid_model.py
Duplikaty funkcjonalności:

Linia 85-95 vs 120-130: _scan_for_special_folders powtarza logikę w _analyze_cache_folder
Linia 200-250: get_asset_data_lazy może być zoptymalizowana - podobna logika w set_assets

3. core/amv_models/pairing_model.py
Błędy w kodzie:

Linia 42-50: load_unpair_files() - nieświadoma niespójność nazw kluczy (unpaired_images vs unpaired_previews)
Linia 120-130: save_unpair_files() - duplikacja kodu w zapisie meta danych

4. core/scanner.py
Nieużywane funkcje:

Linia 350-450: Globalne funkcje wrapper (_create_single_asset, create_thumbnail_for_asset) - duplikują metody klasy
Linia 200-250: _check_texture_folders_presence może być statyczna

5. core/thumbnail.py
Nieużywane importy i funkcje:

Linia 1-10: Importy Path z pathlib używane tylko raz, można zastąpić os.path
Linia 250-300: process_thumbnails_batch - nieużywana funkcja legacy

6. core/tools_tab.py
Duplikaty kodu:

Linia 200-300: Podobne wzorce w worker'ach - można wyciągnąć klasę bazową
Linia 850-950: Powtarzające się wzorce w _on_*_progress, _on_*_finished, _on_*_error

7. core/amv_views/amv_view.py
Nieużywane metody:

Linia 450-470: clear_stars() i clear_star_filter() - duplikują funkcjonalność
Linia 500-520: get_current_star_filter() - metoda zdefiniowana ale nigdy nie używana

8. core/base_widgets.py
Optymalizacja stylów:

Linia 50-200: Podobne style CSS można wyciągnąć do zmiennych lub mixinów

9. core/json_utils.py
Nieużywane funkcje:

Linia 80-120: Skomplikowana logika fallback'u orjson/json może być uproszczona

10. core/performance_monitor.py
Nieużywane funkcjonalności:

Linia 150-200: get_statistics() - zdefiniowana ale nie używana w aplikacji
Linia 300-350: clear_history() - metoda nigdy nie wywoływana