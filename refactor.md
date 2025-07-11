🐛 Raport audytu kodu
📁 Pliki wymagające poprawek
1. core/amv_controllers/handlers/asset_rebuild_controller.py
python# PROBLEM: Duplikowanie klasy AssetRebuilderWorker 
from core.workers.asset_rebuilder_worker import AssetRebuilderWorker
# thumbnail_cache imported w utilities.clear_thumbnail_cache_after_rebuild()
Zmiany:

Usunąć nieużywany import thumbnail_cache (linia 11)
Sprawdzić czy klasa AssetRebuilderWorker nie jest duplikowana

2. core/amv_controllers/handlers/file_operation_controller.py
pythondef _remove_moved_assets_optimized(self, success_messages: list):
    """OPTIMIZATION: Fast removal of only moved assets without gallery rebuild"""
    try:
        if not self._validate_optimization_inputs(success_messages):
            return
        # ... bardzo długa metoda (150+ linii)
Zmiany:
3. Podzielić metodę _remove_moved_assets_optimized() na mniejsze funkcje
4. Usunąć duplikowaną logikę walidacji ścieżek
3. core/amv_models/file_operations_model.py
pythondef _update_asset_file_after_rename(self, original_asset_path, new_asset_path):
    # Upewnij się, że asset_file_path ma rozszerzenie .asset
    asset_file_path = new_asset_path
    if not asset_file_path.endswith('.asset'):
        asset_file_path = os.path.splitext(asset_file_path)[0] + '.asset'
Zmiany:
5. Naprawić polskie komentarze na angielskie
6. Ujednolicić obsługę błędów w metodach _move_single_asset_*
4. core/amv_views/asset_tile_view.py
pythondef reset_for_pool(self):
    """Resets the tile to a state ready for reuse in the pool."""
    # ... metoda nieużywana przez AssetTilePool
Zmiany:
7. Usunąć nieużywaną metodę reset_for_pool()
8. Uprościć logikę w update_asset_data() - za dużo sprawdzeń
5. core/main_window.py
pythondef _validate_grid_controller(self, controller_data: dict) -> bool:
def _filter_non_special_assets(self, assets) -> list:
def _calculate_asset_counts(self, controller_data: dict) -> AssetCounts:
# ... duplikowana logika z SelectionCounter
Zmiany:
9. Usunąć zduplikowane metody liczenia assetów - używać tylko SelectionCounter
10. Usunąć nieużywane struktury danych AssetCounts, AssetCountsDetailed
6. core/pairing_tab.py
python# PROBLEM: Polskie komentarze i niekonsequentne nazewnictwo
self._log_progress(i + 1, len(self.files_info["unpaired"]), f"Przetwarzanie: {filename}")
Zmiany:
11. Zmienić wszystkie polskie stringi na angielskie
12. Usunąć nieużywane importy json, subprocess, Path
7. core/tools_tab.py
pythondef _handle_worker_progress(self, button: QPushButton, current: int, total: int, message: str):
    WorkerManager.handle_progress(button, current, total, message)
# Metoda tylko przekazuje wywołanie - niepotrzebna
Zmiany:
13. Usunąć niepotrzebne metody proxy (_handle_worker_*)
14. Naprawić polskie stringi w UI (linia 394, 428)
8. core/utilities.py
pythondef clear_thumbnail_cache_after_rebuild(is_error: bool = False):
    """Simplified version - removed duplicate logic and excessive logging."""
    # Funkcja ma bardzo mało logiki
Zmiany:
15. Sprawdzić czy funkcja update_main_window_status() nie jest duplikatowana
16. Rozważyć połączenie z innymi modułami utility
9. core/workers/worker_manager.py
python# PROBLEM: Brak thread safety w metodach statycznych
@staticmethod
def start_worker_lifecycle(worker, button, original_text, parent_instance):
Zmiany:
17. Dodać thread safety do metod statycznych
18. Ujednolicić obsługę błędów we wszystkich metodach
10. core/tools/ (wszystkie pliki worker)*
python# PROBLEM: Duplikowana logika walidacji we wszystkich workerach
def _validate_working_directory(self) -> bool:
    # Ta sama logika w 6 plikach
Zmiany:
19. Przenieść wspólną logikę walidacji do BaseToolWorker
20. Usunąć duplikowaną logikę ładowania modułów Rust
🎯 Priorytety napraw
Wysokie (błędy krytyczne):

Punkty 1, 9, 17, 19

Średnie (optymalizacja):

Punkty 3, 7, 8, 13

Niskie (czyszczenie kodu):

Punkty 11, 14, 15, 18, 20

Szacowany czas: ~4-6 godzin pracy na wszystkie poprawki.