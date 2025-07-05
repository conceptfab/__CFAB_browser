Raport analizy kodu CFAB Browser
1. Duplikaty kodu
1.1 Duplikacja modelu FolderSystemModel
Pliki:

core/amv_models/asset_grid_model.py (linie 192-353)
core/amv_models/folder_system_model.py (cały plik)

Problem: Klasa FolderSystemModel jest zdefiniowana w dwóch miejscach
Rozwiązanie: Usuń duplikat z asset_grid_model.py i importuj z folder_system_model.py
1.2 Duplikacja modelu WorkspaceFoldersModel
Pliki:

core/amv_models/asset_grid_model.py (linie 356-481)
core/amv_models/workspace_folders_model.py (cały plik)

Problem: Klasa WorkspaceFoldersModel jest zdefiniowana w dwóch miejscach
Rozwiązanie: Usuń duplikat z asset_grid_model.py i importuj z workspace_folders_model.py
2. Nieużywane funkcje
2.1 W pliku core/amv_controllers/handlers/control_panel_controller.py
python# Linia 170: Nieużywana funkcja
def filter_assets_by_stars(self, min_stars: int):
    # Ta funkcja jest wywoływana tylko w asset_grid_controller.py linia 42
    # ale można użyć filter_assets() zamiast tego
Rozwiązanie: Usuń filter_assets_by_stars() i używaj filter_assets() wszędzie
3. Błędy logiczne
3.1 Problem z obsługą tekstu w filtrze
Plik: core/amv_controllers/handlers/control_panel_controller.py
python# Linia 169 - brak obsługi self.view.text_input
def filter_assets(self):
    """Filtruje assety po gwiazdkach i tekście naraz."""
    min_stars = self.controller.asset_grid_controller.active_star_filter
    text = self.view.text_input.text().strip().lower() if hasattr(self.view, 'text_input') else ''
    # Reszta kodu...
Problem: Filtr tekstowy nie jest podłączony do sygnału
Rozwiązanie: W signal_connector.py dodaj połączenie sygnału textChanged
4. Niepotrzebne importy
4.1 W pliku core/amv_models/amv_model.py
python# Linia 7: Niepotrzebny import Optional - używany tylko w type hints
from typing import Optional
4.2 W pliku core/thumbnail.py
python# Linia 10: Komentarz o usuniętych importach PyQt6 - usuń go
# Usunięte nieużywane importy PyQt6
5. Nieużywane pliki
5.1 Plik core/base_widgets.py
Problem: Ten plik definiuje bazowe klasy dla stylowania, ale nigdzie nie jest używany
Rozwiązanie: Usuń plik lub zaimplementuj dziedziczenie w widgetach
6. Problemy z wydajnością
6.1 Wielokrotne skanowanie folderów
Plik: core/amv_controllers/handlers/asset_rebuild_controller.py
python# Linia 65-71: Po przebudowie assetów następuje pełne odświeżenie
def on_rebuild_finished(self, message: str):
    # ...
    self.controller.folder_tree_controller.on_folder_refresh_requested(current_folder)
    # To powoduje pełne przeskanowanie folderu
Rozwiązanie: Zamiast pełnego skanowania, odśwież tylko widok z istniejących danych
7. Błędy w logowaniu
7.1 Niespójne poziomy logowania
Pliki: Wiele plików używa logger.info() dla debugowania
Rozwiązanie: Zmień na logger.debug() dla informacji debugowych
8. Kod do refaktoryzacji
8.1 W pliku core/amv_models/asset_grid_model.py
python# Zmiana w linii 10
from core.amv_models.folder_system_model import FolderSystemModel
from core.amv_models.workspace_folders_model import WorkspaceFoldersModel

# Usuń linie 192-481 (duplikaty klas)
8.2 W pliku core/amv_controllers/handlers/signal_connector.py
python# Dodaj po linii 76
# Połącz sygnał filtra tekstowego
self.view.text_input.textChanged.connect(
    lambda: control_panel_controller.filter_assets()
)
8.3 W pliku core/amv_controllers/handlers/control_panel_controller.py
python# Usuń funkcję filter_assets_by_stars (linie 196-210)
# Użyj filter_assets() wszędzie
9. Podsumowanie
Pliki wymagające poprawek:

core/amv_models/asset_grid_model.py - usuń duplikaty klas
core/amv_controllers/handlers/control_panel_controller.py - usuń nieużywaną funkcję
core/amv_controllers/handlers/signal_connector.py - dodaj brakujące połączenie sygnału
core/base_widgets.py - rozważ usunięcie
core/amv_controllers/handlers/asset_rebuild_controller.py - optymalizacja odświeżania

Priorytet: Wysokie dla punktów 1-3, średnie dla pozostałych.