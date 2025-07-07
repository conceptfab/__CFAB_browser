Raport z analizy kodu CFAB Browser
Główne problemy wymagające poprawy
1. core/main_window.py - Duplikacje i przestarzałe metody
Problemy:

Deprecated metody nadal w kodzie (linie 461-497)
Duplikacja logiki liczenia assetów z SelectionCounter
Nadmiernie skomplikowane helper methods

Zmiany do wykonania:
python# DO USUNIĘCIA - deprecated metody:
def _count_visible_assets(self, grid_controller) -> int:
def _count_total_assets(self, grid_controller) -> int: 
def _count_filtered_assets(self, controller) -> tuple:
def _count_original_assets(self, controller) -> int:

# DO UPROSZCZENIA - zastąpić wywołaniami SelectionCounter:
def _get_asset_controller_data(self) -> dict:
def _calculate_asset_counts(self, controller_data: dict) -> AssetCounts:
2. core/amv_controllers/handlers/asset_grid_controller.py - Optymalizacje i duplikacje
Problemy:

Layout hash checking (linia 233) może nie działać poprawnie
Deprecated metody duplikujące SelectionCounter

Zmiany do wykonania:
python# DO USUNIĘCIA (linie 418-440):
def _count_visible_assets(self, grid_controller) -> int:
def _count_total_assets(self, grid_controller) -> int:

# DO POPRAWY (linia 233) - usunąć lub poprawić hash checking:
if hasattr(self, '_last_layout_hash') and self._last_layout_hash == new_layout_hash:
3. core/amv_controllers/handlers/file_operation_controller.py - Nadmierna złożoność
Problemy:

Bardzo złożona optymalizacja (linie 111-267)
Duplikacja obsługi błędów
Metody za długie i skomplikowane

Zmiany do wykonania:
python# DO UPROSZCZENIA - podzielić na mniejsze metody:
def _remove_moved_assets_optimized(self, success_messages: list):  # 35+ linii
def _remove_tiles_from_view_fast(self, asset_ids_to_remove: list):  # 40+ linii

# DO REFAKTORYZACJI - wydzielić wspólną obsługę błędów
# DO USUNIĘCIA - niepotrzebne mutex w _remove_tiles_from_view_fast
4. core/amv_views/asset_tile_view.py - Nadmiernie skomplikowany cleanup
Problemy:

Bardzo długa metoda _setup_ui_without_styles (110 linii)
Duplikacja cleanup methods
Nadmiernie skomplikowane zarządzanie zasobami

Zmiany do wykonania:
python# DO PODZIELENIA - _setup_ui_without_styles na mniejsze metody:
def _setup_ui_without_styles(self):  # 110 linii -> podzielić na 3-4 metody

# DO UPROSZCZENIA - cleanup methods (linie 792-869):
def _cleanup_connections_and_resources(self):
def _reset_state_variables(self):  
def _clear_ui_elements(self):
5. core/tools_tab.py - Duplikacja worker lifecycle
Problemy:

Duplikacja obsługi worker lifecycle
Podobne metody dla różnych workers
Brak wspólnego wzorca

Zmiany do wykonania:
python# DO REFAKTORYZACJI - utworzyć wspólną klasę WorkerManager
# DO USUNIĘCIA - duplikacje metod _start_*, _handle_*
# DO UNIFIKACJI - obsługa progress, finished, error dla wszystkich workers
6. core/workers/worker_manager.py - Nieużywane metody
Problemy:

Klasa WorkerManager nie jest w pełni wykorzystana
Niektóre metody handle_* są duplikowane w innych miejscach

Zmiany do wykonania:
python# DO ROZSZERZENIA - WorkerManager o dodatkowe funkcjonalności
# DO WYKORZYSTANIA - w tools_tab.py zamiast duplikacji kodu
7. core/utilities.py - Deprecated funkcjonalności
Problemy:

Funkcja update_main_window_status ma przestarzały komentarz o optymalizacji
Nieużywana funkcja get_file_size_mb

Zmiany do wykonania:
python# DO SPRAWDZENIA - czy get_file_size_mb jest rzeczywiście używana
# DO AKTUALIZACJI - dokumentacja w update_main_window_status
8. core/amv_models/pairing_model.py - Nieoptymalne operacje I/O
Problemy:

Synchroniczne operacje I/O w GUI thread
Brak proper error handling w niektórych metodach

Zmiany do wykonania:
python# DO POPRAWY - asynchroniczne operacje delete_unpaired_*
# DO DODANIA - lepszy error handling w load_unpair_files
Podsumowanie działań do wykonania

Usunąć deprecated metody z main_window.py i asset_grid_controller.py
Uprościć file_operation_controller.py przez podział na mniejsze metody
Refaktoryzować asset_tile_view.py - podzielić długie metody
Zunifikować obsługę workers w tools_tab.py używając WorkerManager
Poprawić error handling w pairing_model.py
Usunąć nieużywane importy i metody w całym kodzie
Zastąpić duplikacje logiki liczenia przez SelectionCounter
Uprościć cleanup methods w asset_tile_view.py

Priorytet: Wysokie problemy (1-4), Średnie (5-8)