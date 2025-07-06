Raport analizy kodu CFAB Browser
Pliki wymagające poprawek
1. core/scanner.py
Problemy:

Duplikacje metod walidacji ścieżek
Nieużywane metody pomocnicze
Niespójne wzorce obsługi błędów

Zmiany:

Usunąć duplikat walidacji: Skonsolidować _validate_folder_path_static i AssetRepository._validate_folder_path_static
Refaktoryzacja metod helper: Przenieść _handle_error do klasy bazowej
Uporządkować imports: Przenieść from core.json_utils import load_from_file, save_to_file na górę pliku

2. core/amv_controllers/amv_controller.py
Problemy:

Nieużywane metody callback
Duplikacja logiki obsługi plików

Zmiany:

Usunąć nieużywane metody: _on_config_loaded, _on_state_initialized - nie są połączone z sygnałami
Skonsolidować logikę: Połączyć _handle_file_action z podobnymi metodami w innych kontrolerach

3. core/amv_controllers/handlers/asset_grid_controller.py
Problemy:

Nieużywane metody filtrowania
Duplikacja logiki optymalizacji

Zmiany:

Usunąć nieużywane metody: set_star_filter, clear_star_filter jeśli nie są używane w sygnałach
Refaktoryzacja optymalizacji: Metody _remove_moved_assets_optimized są zbyt złożone - podzielić na mniejsze

4. core/amv_controllers/handlers/file_operation_controller.py
Problemy:

Duplikacja walidacji selekcji
Podobne wzorce w _validate_selection

Zmiany:

Skonsolidować walidację: Połączyć _validate_selection z innymi metodami walidacji
Uprościć logikę: Metoda _remove_moved_assets_optimized ma za dużo odpowiedzialności

5. core/amv_models/folder_system_model.py
Problemy:

Nieużywane metody cache
Duplikacja logiki liczenia assetów

Zmiany:

Sprawdzić użycie: Metoda clear_asset_count_cache może być nieużywana
Optymalizacja cache: _clear_cache_for_path zawiera duplikację logiki

6. core/thumbnail_cache.py
Problemy:

Nieużywana metoda

Zmiany:

Usunąć: Metoda get_current_size_mb() - nie jest używana w kodzie

7. core/amv_views/asset_tile_view.py
Problemy:

Potencjalne memory leaks w worker threads
Duplikacja metod disconnect

Zmiany:

Refaktoryzacja cleanup: Skonsolidować _disconnect_*_signals metody w jedną
Cleanup worker threads: Dodać lepsze zarządzanie ThumbnailLoaderWorker
Uprościć reset: Metody reset_for_pool i release_resources mają duplikacje

8. core/tools/webp_converter_worker.py i core/tools/image_resizer_worker.py
Problemy:

Duplikacja logiki walidacji ścieżek
Podobne wzorce obsługi błędów

Zmiany:

Wspólna klasa bazowa: Przenieść _validate_file_paths do BaseWorker
Skonsolidować error handling: Używać wspólnych metod z BaseWorker

9. core/main_window.py
Problemy:

Duplikacja logiki liczenia assetów
Zbyt długie metody

Zmiany:

Refaktoryzacja liczenia: Metody _calculate_*_assets mają duplikacje - przenieść do SelectionCounter
Podzielić długie metody: _createTabs jest za długa, podzielić na mniejsze metody

10. core/thread_manager.py
Problemy:

Potencjalne race conditions
Brak consistent cleanup

Zmiany:

Dodać thread safety: Więcej synchronizacji w stop_all_threads
Cleanup validation: Dodać sprawdzenie czy threads faktycznie się zakończyły

11. core/utilities.py
Problemy:

Funkcja używana tylko w jednym kontekście

Zmiany:

Przenieść funkcję: clear_thumbnail_cache_after_rebuild użyć tylko tam gdzie potrzebna
Uprościć: update_main_window_status może być uprośćzona

Podsumowanie najważniejszych problemów:

Duplikacje walidacji ścieżek w 4 różnych plikach
Nieużywane metody w kontrolerach (około 6 metod)
Inconsistent error handling w worker classes
Memory leaks potential w thumbnail loading
Threading cleanup issues w kilku miejscach
Performance issues w asset grid operations

Priorytet: Rozpocząć od punktów 1, 6, 7 jako najbardziej krytycznych dla stabilności aplikacji.