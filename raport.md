Raport analizy kodu CFAB Browser
1. Duplikaty i nieużywane funkcje
core/amv_controllers/amv_controller.py

Usunąć duplikat metody _on_tile_thumbnail_clicked i _on_tile_filename_clicked - logika jest identyczna z _handle_file_action
Scali logikę obsługi kliknięć w kafelki do jednej metody

python# USUŃ te duplikaty:
def _on_tile_thumbnail_clicked(self, asset_id: str, asset_path: str, tile: QObject):
def _on_tile_filename_clicked(self, asset_id: str, asset_path: str, tile: QObject):

# ZOSTAW tylko:
def _handle_file_action(self, path: str, action_type: str):
core/amv_controllers/handlers/control_panel_controller.py

Usunąć duplikat metody _update_star_checkboxes_consistently - używana tylko w jednym miejscu
Scali filtrowanie gwiazdek - metoda filter_assets_by_stars ma zbędną duplicację logiki

python# USUŃ duplikowaną logikę w filter_assets_by_stars:
def filter_assets_by_stars(self, min_stars: int):
    # Usuń powtarzające się wywołania self._update_star_checkboxes_consistently
2. Nieużywane importy i zmienne
core/amv_views/amv_view.py

Usunąć nieużywane zmienne z __init__:

python# USUŃ te nieużywane zmienne:
self.asset_rebuilder = None  # Worker dla przebudowy assetów
core/main_window.py

Usunąć nieużywane metody helper:

python# Te metody są nieużywane:
def _show_info_message_box(self, title: str, message: str):
def _show_error_message_box(self, title: str, message: str):
3. Błędy logiczne i potencjalne problemy
core/amv_controllers/handlers/asset_grid_controller.py

Naprawić potencjalny błąd NoneType w on_assets_changed:

pythondef on_assets_changed(self, assets):
    if not assets:  # DODAJ sprawdzenie None
        self.set_original_assets([])
        return
    self.set_original_assets(assets)

Naprawić niekonsystentne używanie active_star_filter:

pythondef on_assets_changed(self, assets):
    # BŁĄD: używa controller.asset_grid_controller.active_star_filter
    # POWINNO BYĆ: self.active_star_filter
    current_star_filter = self.active_star_filter  # Nie self.controller.asset_grid_controller.active_star_filter
core/amv_views/asset_tile_view.py

Naprawić błąd w reset_for_pool - za dużo try/except blokuje prawdziwe błędy:

pythondef reset_for_pool(self):
    # ZAMIEŃ na bardziej precyzyjne sprawdzenia zamiast try/except dla wszystkiego
    if hasattr(self, "model") and self.model is not None:
        try:
            self.model.data_changed.disconnect(self.update_ui)
        except (TypeError, RuntimeError):
            pass
core/amv_controllers/handlers/file_operation_controller.py

Usunąć nadmiarowe debugowanie w on_drag_drop_completed:

python# USUŃ te nadmiarowe logi debug:
logger.debug(f"assets_to_move: {[a.get('name') for a in assets_to_move]}")
logger.debug(f"[DROP DEBUG] asset_ids: {asset_ids}")
# Pozostaw tylko istotne błędy
4. Problemy z architekturą
core/amv_controllers/handlers/signal_connector.py

Usunąć komentowane/nieużywane połączenia sygnałów:

python# USUŃ te zakomentowane linie:
# self.model.asset_grid_model.rebuild_requested.connect(
#     self.controller.asset_rebuild_controller.rebuild_assets_in_folder
# )

Naprawić komentarz o błędnym połączeniu:

python# USUŃ ten komentarz i sprawdź czy rzeczywiście nie jest potrzebne:
# USUNIĘTO BŁĘDNE POŁĄCZENIE, KTÓRE POWODOWAŁO RESETOWANIE FILTRÓW
5. Nieoptymalne rozwiązania
core/tools_tab.py

Uprości mapowanie operacji w _start_operation_with_confirmation:

python# ZAMIEŃ ten słownik na enum lub stałe klasy:
button_mapping = {
    "konwersji na webp": ("webp_button", "webp_converter"),
    "konwersji na WebP": ("webp_button", "webp_converter"), # DUPLIKAT!
}
core/amv_views/folder_tree_view.py

Uprości obsługę przeciągania - za dużo zagnieżdżonych sprawdzeń w dropEvent:

pythondef dropEvent(self, event):
    # REFAKTORYZUJ: wynieś walidację do osobnych metod
    if not self._validate_drop_event(event):
        return
    
    target_info = self._get_drop_target_info(event)
    if not target_info:
        return
6. Inconsistent error handling
core/scanner.py

Zunifikuj obsługę błędów w AssetRepository:

python# DODAJ bazową metodę dla obsługi błędów:
def _handle_error(self, operation: str, error: Exception, file_path: str = None):
    error_msg = f"Błąd podczas {operation}"
    if file_path:
        error_msg += f" dla {file_path}"
    error_msg += f": {error}"
    logger.error(error_msg)
    return None
7. Podsumowanie zmian do wprowadzenia
Najwyższy priorytet:

Punkty 1, 2: Usunięcie duplikatów w AmvController
Punkty 7, 8: Naprawienie błędów NoneType w AssetGridController
Punkt 13: Naprawienie duplikatu mapowania w ToolsTab

Średni priorytet:

Punkty 5, 6: Usunięcie nieużywanych zmiennych i metod
Punkty 10, 11: Wyczyszczenie nadmiarowego debugowania

Niski priorytet:

Punkty 14, 15: Refaktoryzacja dla lepszej czytelności

Łącznie 15 konkretnych punktów do poprawy w 8 plikach.