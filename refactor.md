Raport analizy kodu CFAB Browser
Pliki wymagające poprawek
1. core/main_window.py
Problemy:

Duplikaty funkcjonalności z SelectionCounter
Nieużywane metody DEPRECATED
Nadmierna złożoność klasy MainWindow

Zmiany:

Usuń duplikaty metod (linie 580-620):

python# USUŃ te metody - są duplikatami SelectionCounter:
def _count_visible_assets(self, grid_controller) -> int:
def _count_total_assets(self, grid_controller) -> int:  
def _count_filtered_assets(self, controller) -> tuple:
def _count_original_assets(self, controller) -> int:

Uprość metodę _calculate_asset_counts:

pythondef _calculate_asset_counts(self, controller_data: dict) -> AssetCounts:
    if not self.selection_counter:
        return AssetCounts(visible=0, total=0)
    
    return AssetCounts(
        visible=self.selection_counter.count_visible_assets(),
        total=self.selection_counter.count_total_assets()
    )

Usuń nieużywane importy:

python# USUŃ:
from collections import namedtuple  # jeśli AssetCounts nie jest używane gdzie indziej
2. core/amv_controllers/handlers/file_operation_controller.py
Problemy:

Skomplikowana logika optymalizacji w _remove_moved_assets_optimized
Duplikacja kodu walidacji

Zmiany:

Uprość metodę _remove_moved_assets_optimized (linie 150-250):

pythondef _remove_moved_assets_optimized(self, success_messages: list):
    """Szybkie usuwanie przeniesionych assetów"""
    if not success_messages or not self._validate_optimization_inputs(success_messages):
        return
    
    try:
        # Aktualizuj model
        current_assets = self.model.asset_grid_model.get_assets()
        updated_assets = [
            asset for asset in current_assets 
            if asset.get("name") not in success_messages
        ]
        self.model.asset_grid_model._assets = updated_assets
        
        # Usuń kafelki z widoku
        self._remove_tiles_from_view_fast(success_messages)
        
        # Odłożone odświeżanie
        QTimer.singleShot(100, self._refresh_folder_structure_delayed)
        
    except Exception as e:
        logger.error(f"Błąd optymalizacji: {e}")
        self._fallback_refresh_gallery()

Usuń duplikujące się metody walidacji - skonsoliduj do jednej metody w BaseWorker.

3. core/amv_views/asset_tile_view.py
Problemy:

Metoda _cleanup_connections_and_resources może powodować RuntimeError
Nadmierna złożoność sygnałów

Zmiany:

Popraw bezpieczne odłączanie sygnałów (linie 650-680):

pythondef _cleanup_connections_and_resources(self):
    """Bezpieczne odłączanie sygnałów"""
    try:
        # Sprawdź czy widget nie został już usunięty
        if not self or not hasattr(self, 'model'):
            return
            
        # Odłącz sygnały modelu
        if self.model and hasattr(self.model, 'data_changed'):
            try:
                self.model.data_changed.disconnect(self.update_ui)
            except (TypeError, RuntimeError):
                pass  # Sygnał już odłączony lub widget usunięty
        
        # Blokuj sygnały przed odłączaniem
        if hasattr(self, 'checkbox') and self.checkbox:
            self.checkbox.blockSignals(True)
            
    except RuntimeError:
        # Widget został już usunięty - to jest OK
        pass
4. core/rules.py
Problemy:

Cały plik wydaje się nieużywany
Nadmierna złożoność dla niewykorzystywanej funkcjonalności

Zmiany:

Sprawdź wykorzystanie FolderClickRules - jeśli nieużywane, usuń cały plik lub oznacz jako przyszłą funkcjonalność.

5. core/workers/asset_rebuilder_worker.py
Problemy:

Niespójność w obsłudze błędów w _remove_cache_folder

Zmiany:

Popraw obsługę błędów (linie 80-95):

pythondef _remove_cache_folder(self):
    """Usuwa folder .cache"""
    try:
        import shutil
        cache_folder = os.path.join(self.folder_path, ".cache")
        
        if os.path.exists(cache_folder):
            shutil.rmtree(cache_folder)
            logger.debug("Usunięto folder .cache: %s", cache_folder)
        else:
            logger.debug("Folder .cache nie istniał")
            
    except Exception as e:
        # Loguj błąd ale nie przerywaj operacji - cache można odtworzyć
        logger.warning(f"Nie można usunąć folderu .cache: {e}")
6. core/amv_controllers/handlers/asset_grid_controller.py
Problemy:

Potencjalne race conditions w throttling

Zmiany:

Popraw throttling w rebuild_asset_grid (linie 70-85):

pythondef rebuild_asset_grid(self, assets: list):
    """Throttled rebuild z lepszą synchronizacją"""
    # Anuluj poprzedni timer
    if self._rebuild_timer.isActive():
        self._rebuild_timer.stop()
    
    self._pending_assets = assets
    self._rebuild_timer.start(50)
7. Globalne usprawnienia
Zmiany:

Usuń nieużywane importy we wszystkich plikach:

python# Przykładowo w core/amv_tab.py:
# USUŃ: from typing import Optional (jeśli nie używane)

Skonsoliduj duplikujące się metody walidacji w core/tools/base_worker.py - inne workery powinny dziedziczyć te metody.
Sprawdź i usuń nieużywane pliki:


core/amv_views/preview_gallery_view.py - używane tylko w pairing_tab
core/amv_views/preview_tile.py - używane tylko w pairing_tab
core/amv_models/pairing_model.py - używane tylko w pairing_tab

Jeśli te pliki są używane tylko w jednym miejscu, rozważ przeniesienie logiki bezpośrednio do pairing_tab.
Podsumowanie
Kod wymaga refaktoryzacji w kierunku:

Usunięcia duplikatów funkcjonalności
Uproszczenia nadmiernie skomplikowanych metod
Poprawy obsługi błędów i race conditions
Usunięcia nieużywanych części kodu
Lepszego rozdziału odpowiedzialności między klasami