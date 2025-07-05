Raport z problemów w kodzie CFAB Browser
Duplikaty i nieużywane elementy
1. Duplikacja klasy FolderSystemModel
Pliki: core/amv_models/asset_grid_model.py i core/amv_models/folder_system_model.py
python# W asset_grid_model.py (linie 113-310) - usuń tę duplikowaną klasę
class FolderSystemModel(QObject):
    # ... cała implementacja jest zduplikowana
Rozwiązanie: Usuń klasę FolderSystemModel z pliku asset_grid_model.py i dodaj import:
pythonfrom .folder_system_model import FolderSystemModel
2. Nieużywane importy w folder_tree_view.py
Plik: core/amv_views/folder_tree_view.py
python# Linia 13 - nieużywany import
from core.file_utils import open_path_in_explorer
Rozwiązanie: Usuń import, funkcja jest już dostępna przez callback.
3. Nieużywane pola klasy w asset_tile_view.py
Plik: core/amv_views/asset_tile_view.py
python# Linia 72 - nieużywane pole
self._cached_pixmap = None
Rozwiązanie: Usuń pole i wszystkie odwołania do niego.
Błędy logiczne
4. Niespójność w metodzie filter_assets
Plik: core/amv_controllers/handlers/control_panel_controller.py
python# Linie 124-135 - problem z dostępem do text_input
text = self.view.text_input.text().strip().lower() if hasattr(self.view, 'text_input') else ''
Rozwiązanie: Sprawdź czy pole text_input istnieje w view lub dodaj obsługę błędu.
5. Potencjalny problem z None w asset_grid_controller.py
Plik: core/amv_controllers/handlers/asset_grid_controller.py
python# Linia 85 - sprawdzenie None powinno być na początku
def on_assets_changed(self, assets):
    if not assets:  # ADD check for None
        self.set_original_assets([])
        return
Rozwiązanie: Dodaj bardziej szczegółowe sprawdzenie:
pythonif assets is None or len(assets) == 0:
Problemy z wydajnością
6. Brak ograniczenia cache w ThumbnailCache
Plik: core/thumbnail_cache.py
python# Linie 63-78 - metoda put może doprowadzić do OOM
def put(self, path: str, pixmap: QPixmap):
    # Brak sprawdzenia czy pixmap nie jest zbyt duży
Rozwiązanie: Dodaj sprawdzenie maksymalnego rozmiaru pojedynczego obiektu:
pythonMAX_SINGLE_ITEM_SIZE = 50 * 1024 * 1024  # 50MB
if pixmap_size > MAX_SINGLE_ITEM_SIZE:
    logger.warning(f"Pixmap too large: {pixmap_size}")
    return
7. Niepotrzebne wielokrotne wywołania update_button_states
Plik: core/amv_controllers/handlers/control_panel_controller.py
python# Metody wywołują update_button_states() wielokrotnie
# Linie: 182, 204, w filter_assets_by_stars()
Rozwiązanie: Połącz wywołania lub użyj debouncing pattern.
Problemy z zarządzaniem pamięcią
8. Brak wywołania deleteLater() w asset_tile_pool.py
Plik: core/amv_views/asset_tile_pool.py
python# Linia 82 - metoda clear nie wywołuje deleteLater()
def clear(self):
    for tile in self._pool:
        tile.deleteLater()  # Może być problem z timing
Rozwiązanie: Dodaj sprawdzenie stanu obiektu przed deleteLater().
Problemy bezpieczeństwa
9. Brak walidacji ścieżek w file_utils.py
Plik: core/file_utils.py
python# Linie 145-150 - słaba walidacja path traversal
if ".." in folder_path or "\\.." in folder_path or "/.." in folder_path:
Rozwiązanie: Użyj os.path.abspath() i os.path.commonpath() dla lepszej walidacji.
Nieefektywne operacje
10. Powolne operacje I/O w głównym wątku
Plik: core/amv_models/asset_tile_model.py
python# Linia 73 - operacja zapisu w głównym wątku
def _save_to_file(self):
    save_to_file(self.data, self.asset_file_path, indent=True)
Rozwiązanie: Przenieś do worker thread lub użyj queue do asynchronicznego zapisu.
Problemy z obsługą błędów
11. Brak obsługi wyjątków w scanner.py
Plik: core/scanner.py
python# Linie 150-160 - metody mogą rzucać nieobsłużone wyjątki
def _check_texture_folders_presence(folder_path: str) -> bool:
    # Brak try-catch dla os.listdir()
Rozwiązanie: Dodaj obsługę PermissionError i FileNotFoundError.
Łączna liczba problemów: 11
Priorytety napraw:

Krytyczne: Punkty 1, 4, 5, 9 (duplikacje, błędy logiczne, bezpieczeństwo)
Wysokie: Punkty 6, 10, 11 (wydajność, pamięć, błędy)
Średnie: Punkty 2, 3, 7, 8 (czyszczenie kodu, optymalizacje)