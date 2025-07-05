# Komunikaty i elementy UI do tłumaczenia

## core/amv_controllers/__init__.py

- `Katalog kontrolerów dla zakładki AMV
Zawiera kontrolery łączące modele z widokami.` (Docstring modułu)

## core/amv_controllers/amv_controller.py

- `Simplified constructor - używa tylko głównych komponentów.
Wszystkie sub-modele są dostępne przez model.` (Docstring `__init__`)
- `Wspólna logika dla obsługi kliknięć w pliki` (Docstring `_handle_file_action`)

## core/amv_controllers/handlers/control_panel_controller.py

- `Pomocnicza metoda do update checkboxów gwiazdek` (Docstring `_update_star_checkboxes`)
- `Pomocnicza metoda do filtrowania assetów` (Docstring `_get_filtered_assets`)

## core/amv_controllers/handlers/file_operation_controller.py

- `Wspólna walidacja zaznaczenia dla operacji` (Docstring `_validate_selection`)
- `Uproszczona metoda z wykorzystaniem centralnej walidacji` (Docstring `on_move_selected_clicked` i `on_delete_selected_clicked`)
- `Select target folder` (Tekst w `QFileDialog.getExistingDirectory`)
- `Moving assets...` (Tekst w `update_gallery_placeholder`)
- `Confirm Deletion`, `Are you sure you want to delete {len(assets_to_delete)} selected assets?
This operation is irreversible!` (Teksty w `QMessageBox.question`)
- `Deleting assets...` (Tekst w `update_gallery_placeholder`)

## core/amv_models/asset_grid_model.py

- `WCZYTUJE OD NOWA assety w folderze - odświeżenie = wczytanie od nowa!` (Docstring `scan_folder`)
- `Rozwija element i doładowuje jego dzieci (lazy loading).` (Docstring `FolderSystemModel.expand_folder`)
- `Odświeża strukturę określonego folderu.` (Docstring `FolderSystemModel.refresh_folder`)
- `Rekurencyjnie odświeża folder w drzewie.` (Docstring `FolderSystemModel._refresh_folder_recursive`)
- `Ładuje foldery robocze z konfiguracji.` (Docstring `WorkspaceFoldersModel.load_folders`)
- `Ładuje foldery z konfiguracji i emituje sygnał aktualizacji.` (Docstring `WorkspaceFoldersModel._load_folders_from_config`)
- `Folder {i}` (Nazwa domyślna folderu roboczego)
- `Zwraca listę folderów roboczych.` (Docstring `WorkspaceFoldersModel.get_folders`)

## core/amv_models/asset_tile_model.py

- `Saves asset data to the .asset file` (Docstring `_save_to_file`)

## core/amv_models/control_panel_model.py

- `Ustawia, czy jest zaznaczenie i emituje sygnał.` (Docstring `set_has_selection`)
- `Zwraca, czy jest zaznaczenie.` (Docstring `get_has_selection`)

## core/amv_models/drag_drop_model.py

- `Waliduje, czy upuszczenie jest możliwe w danym folderze.` (Docstring `validate_drop`)
- `Kończy operację drop i emituje sygnał.` (Docstring `complete_drop`)

## core/amv_models/file_operations_model.py

- `Przenosi zaznaczone assety do nowego folderu.` (Docstring `FileOperationsWorker._move_assets`)
- `Przenoszenie: {asset_name}` (Komunikat postępu `operation_progress`)
- `Generuje unikalną nazwę assetu dodając suffix _D_01, _D_02, itd.` (Docstring `_generate_unique_asset_name`)
- `Przenosi pojedynczy asset z obsługą konfliktów nazw...` (Docstring `_move_single_asset_with_conflict_resolution`)
- `Przeniesiono asset: {original_name} -> {unique_name} (zmieniono nazwę z powodu konfliktu)` (Komunikat `_compose_move_message`)
- `Pomyślnie przeniesiono asset: {original_name}` (Komunikat `_compose_move_message`)
- `Usuwa zaznaczone assety.` (Docstring `FileOperationsWorker._delete_assets`)
- `Usuwanie: {asset_name}` (Komunikat postępu `operation_progress`)
- `Zwraca listę ścieżek do wszystkich plików związanych z assetem.` (Docstring `_get_asset_files_paths`)
- `Model dla operacji na plikach (przenoszenie, usuwanie)...` (Docstring `FileOperationsModel`)
- `Inicjalizuje model operacji na plikach.` (Docstring `__init__`)
- `Przenosi assety z folderu źródłowego do docelowego.` (Docstring `move_assets`)
- `Usuwa zaznaczone assety.` (Docstring `delete_assets`)
- `Zatrzymuje bieżącą operację na plikach.` (Docstring `stop_operation`)
- `Łączy sygnały workera z sygnałami modelu.` (Docstring `_connect_worker_signals`)
- `Obsługa zakończenia pracy workera.` (Docstring `_on_worker_finished`)

## core/amv_tab.py

- `Główna klasa zakładki AMV...` (Docstring `AmvTab`)
- `Zwraca instancję kontrolera dla tej zakładki.` (Docstring `get_controller`)

## core/amv_views/__init__.py

- `Widoki dla zakładki AMV.
Zawiera komponenty UI odpowiedzialne za prezentację danych.` (Docstring modułu)

## core/amv_views/amv_view.py

- `Główny widok dla zakładki AMV...` (Docstring `AmvView`)
- `Ładuje ikony używane w widoku.` (Docstring `_load_icons`)
- `Zwiń` (Tekst przycisku `collapse_button`)
- `Rozwiń` (Tekst przycisku `expand_button`)
- `Zamknij panel` / `Otwórz panel` (Tooltip przycisku `toggle_button`)
- `Folder {i + 1}` (Domyślna nazwa przycisku folderu)
- `Pozycjonuje panel kontrolny na dole galerii` (Docstring `_position_control_panel`)
- `Tworzy przycisk przyklejony do lewej krawędzi do otwierania panelu` (Docstring `_create_edge_button`)
- `Otwórz panel` (Tooltip przycisku `edge_button`)
- `Panel galerii
(Oczekiwanie na wybór folderu)` (Tekst `placeholder_label`)
- `Zaznacz wszystkie` (Tekst przycisku `select_all_button`)
- `Przenieś zaznaczone` (Tekst przycisku `move_selected_button`)
- `Usuń zaznaczone` (Tekst przycisku `delete_selected_button`)
- `Odznacz wszystkie` (Tekst przycisku `deselect_all_button`)
- `Usuwa kafelki assetów z widoku galerii na podstawie ich ID.` (Docstring `remove_asset_tiles`)
- `Obsługuje pokazanie widoku` (Docstring `showEvent`)
- `Obsługuje zmianę rozmiaru okna` (Docstring `resizeEvent`)

## core/amv_views/asset_tile_pool.py

- `Zarządza pulą obiektów AssetTileView...` (Docstring `AssetTilePool`)
- `Pozyskuje kafelek z puli lub tworzy nowy, jeśli pula jest pusta.` (Docstring `acquire`)
- `Zwraca kafelek do puli, aby mógł być ponownie użyty.` (Docstring `release`)
- `Trwale usuwa wszystkie kafelki z puli...` (Docstring `clear`)

## core/amv_views/asset_tile_view.py

- `Aktualizuje dane kafelka dla Object Pooling...` (Docstring `update_asset_data`)
- `Resetuje kafelek do stanu gotowego do ponownego użycia w puli.` (Docstring `reset_for_pool`)
- `Ustawia QPixmap na etykiecie miniaturki, przycinając do kwadratu zgodnie z wymaganiami.` (Docstring `_set_thumbnail_pixmap`)
- `Tworzy placeholder miniaturkę gdy nie ma obrazka.` (Docstring `_create_placeholder_thumbnail`)
- `Uniwersalna metoda ładowania ikon z fallback` (Docstring `_load_icon_with_fallback`)
- `Obsługuje naciśnięcie myszy - kliknięcia i drag & drop.` (Docstring `mousePressEvent`)
- `Obsługuje ruch myszy - inicjuje drag & drop.` (Docstring `mouseMoveEvent`)
- `Aktualizuje rozmiar miniatury i przelicza layout.` (Docstring `update_thumbnail_size`)
- `Aktualizuje widoczność gwiazdek na podstawie dostępnej przestrzeni.` (Docstring `_update_stars_visibility`)
- `Zwalnia zasoby powiązane z kafelkiem, w tym cached_pixmap.` (Docstring `release_resources`)
- `Sprawdza czy kafelek jest zaznaczony.` (Docstring `is_checked`)
- `Ustawia stan zaznaczenia kafelka.` (Docstring `set_checked`)
- `Obsługuje zmianę stanu checkboxa.` (Docstring `_on_checkbox_state_changed`)
- `Pobiera ocenę gwiazdkową.` (Docstring `get_star_rating`)
- `Ustawia ocenę gwiazdkową.` (Docstring `set_star_rating`)
- `Obsługuje kliknięcie w gwiazdkę.` (Docstring `_on_star_clicked`)
- `Ustawia możliwość drag and drop dla kafelka.` (Docstring `set_drag_and_drop_enabled`)
- `Sprawdza czy gwiazdki mieszczą się na kafelku.` (Docstring `_check_stars_fit`)
- `Obsługuje zmianę rozmiaru kafelka.` (Docstring `resizeEvent`)
- `Aktualizuje rozmiar miniatury na podstawie dostępnej przestrzeni.` (Docstring `_update_thumbnail_size`)

## core/amv_views/folder_tree_view.py

- `Widok drzewa folderów z obsługą drag & drop...` (Docstring modułu)
- `Niestandardowy widok drzewa folderów z obsługą drag & drop i menu kontekstowego...` (Docstring `CustomFolderTreeView`)
- `Ustawia modele potrzebne do obsługi drag & drop.` (Docstring `set_models`)
- `Ustawia callback do przebudowy assetów.` (Docstring `set_rebuild_callback`)
- `Ustawia callback do otwierania folderu w eksploratorze.` (Docstring `set_open_in_explorer_callback`)
- `Ustawia callback do odświeżania folderu.` (Docstring `set_refresh_folder_callback`)
- `Obsługuje menu kontekstowe dla folderu.` (Docstring `contextMenuEvent`)
- `Odśwież folder` (Tekst akcji w menu)
- `Otwórz w Eksploratorze` (Tekst akcji w menu)
- `Przebuduj assety` (Tekst akcji w menu)
- `Otwiera folder w eksploratorze systemu.` (Docstring `_open_folder_in_explorer`)
- `Przebudowuje assety w wybranym folderze.` (Docstring `_rebuild_assets_in_folder`)
- `Odświeża folder.` (Docstring `_refresh_folder`)
- `Obsługuje zdarzenie wejścia przeciąganego elementu.` (Docstring `dragEnterEvent`)
- `Obsługuje zdarzenie opuszczenia obszaru przez przeciągany element.` (Docstring `dragLeaveEvent`)
- `Obsługuje zdarzenie ruchu przeciąganego elementu.` (Docstring `dragMoveEvent`)
- `Obsługuje zdarzenie upuszczenia elementu.` (Docstring `dropEvent`)
- `Sprawdza czy zdarzenie drop jest prawidłowe.` (Docstring `_validate_drop_event`)
- `Pobiera informacje o celu drop.` (Docstring `_get_drop_target_info`)
- `Pobiera pełne dane assetów do przeniesienia.` (Docstring `_get_assets_to_move`)
- `Sprawdza czy można wykonać operację drop.` (Docstring `_can_perform_drop`)
- `Wykonuje operację drop.` (Docstring `_perform_drop_operation`)
- `Podświetla folder pod podaną pozycją bez zmiany zaznaczenia roboczego.` (Docstring `_highlight_folder_at_position`)
- `Czyści podświetlenie folderu docelowego.` (Docstring `_clear_folder_highlight`)

## core/amv_views/gallery_widgets.py

- `Widoki galerii dla zakładki AMV...` (Docstring modułu)
- `Kontener galerii z siatką kafelków assetów...` (Docstring `GalleryContainerWidget`)
- `Delegat do podświetlania elementów podczas operacji drag & drop...` (Docstring `DropHighlightDelegate`)

## core/amv_views/preview_gallery_view.py

- `Usuwa wszystkie widgety z galerii w sposób zoptymalizowany.` (Docstring `_clear_gallery`)
- `Przeorganizuje kafelki w layoutcie po zmianie rozmiaru lub usunięciu elementu` (Docstring `_reorganize_tiles`)

## core/amv_views/preview_tile.py

- `Zwraca zwiększoną wysokość wiersza o 30%` (Docstring `ArchiveListItem.sizeHint`)
- `Otwórz w programie domyślnym` (Tekst akcji w menu)

## core/base_widgets.py

- `Klasy bazowe dla stylowania opartego na dziedziczeniu...` (Docstring modułu)
- `Bazowa klasa dla wszystkich ramek z podstawowym stylowaniem` (Docstring `BaseFrame`)
- `Aplikuje podstawowe style dla ramek` (Docstring `_apply_base_styles`)
- `Bazowa klasa dla wszystkich etykiet z podstawowym stylowaniem` (Docstring `BaseLabel`)
- `Aplikuje podstawowe style dla etykiet` (Docstring `_apply_base_styles`)
- `Bazowa klasa dla wszystkich przycisków z podstawowym stylowaniem` (Docstring `BaseButton`)
- `Aplikuje podstawowe style dla przycisków` (Docstring `_apply_base_styles`)
- `Bazowa klasa dla wszystkich checkboxów z podstawowym stylowaniem` (Docstring `BaseCheckBox`)
- `Aplikuje podstawowe style dla checkboxów` (Docstring `_apply_base_styles`)
- `Bazowa klasa dla wszystkich widgetów z podstawowym stylowaniem` (Docstring `BaseWidget`)
- `Aplikuje podstawowe style dla widgetów` (Docstring `_apply_base_styles`)
- `Bazowa klasa dla wszystkich kafelków (tiles)` (Docstring `TileBase`)
- `Aplikuje style specyficzne dla kafelków` (Docstring `_apply_tile_styles`)
- `Bazowa klasa dla checkboxów gwiazdek` (Docstring `StarCheckBoxBase`)
- `Aplikuje style specyficzne dla checkboxów gwiazdek` (Docstring `_apply_star_styles`)
- `Bazowa klasa dla przycisków kontrolnych` (Docstring `ControlButtonBase`)
- `Aplikuje style specyficzne dla przycisków kontrolnych` (Docstring `_apply_control_button_styles`)
- `Bazowa klasa dla przycisków panelowych` (Docstring `PanelButtonBase`)
- `Aplikuje style specyficzne dla przycisków panelowych` (Docstring `_apply_panel_button_styles`)

## core/file_utils.py

- `Moduł utility dla operacji na plikach i ścieżkach...` (Docstring modułu)
- `Sprawdza czy komenda jest dostępna w systemie.` (Docstring `_is_command_available`)
- `Otwiera ścieżkę w eksploratorze plików systemu.` (Docstring `open_path_in_explorer`)
- `Błąd`, `Ścieżka nie istnieje: {path}` (Teksty w `QMessageBox.warning`)
- `Błąd`, `Timeout podczas otwierania ścieżki: {path}` (Teksty w `QMessageBox.warning`)
- `Błąd`, `Błąd procesu podczas otwierania: {path}` (Teksty w `QMessageBox.warning`)
- `Błąd`, `Nie można otworzyć ścieżki: {path}` (Teksty w `QMessageBox.warning`)
- `Otwiera plik w domyślnej aplikacji systemu.` (Docstring `open_file_in_default_app`)
- `Błąd`, `Plik nie istnieje: {path}` (Teksty w `QMessageBox.warning`)
- `Błąd`, `Timeout podczas otwierania pliku: {path}` (Teksty w `QMessageBox.warning`)
- `Błąd`, `Błąd procesu podczas otwierania pliku: {path}` (Teksty w `QMessageBox.warning`)
- `Błąd`, `Nie można otworzyć pliku: {path}` (Teksty w `QMessageBox.warning`)

## core/json_utils.py

- `JSON utilities z fallback na standardowy json...` (Docstring modułu)
- `Uniwersalna funkcja do deserializacji JSON` (Docstring `loads`)
- `Uniwersalna funkcja do serializacji JSON` (Docstring `dumps`)
- `Ładuje JSON z pliku` (Docstring `load_from_file`)
- `Zapisuje JSON do pliku` (Docstring `save_to_file`)

## core/main_window.py

- `Bezpiecznie ładuje konfigurację z fallback do domyślnych wartości` (Docstring `_load_config_safe`)
- `Konfiguruje logger na podstawie załadowanej konfiguracji` (Docstring `_setup_logger`)
- `Tworzy pasek menu z proper error handling` (Docstring `_createMenuBar`)
- `Plik` (Tekst menu)
- `Wyjście` (Tekst akcji)
- `Tworzy taby aplikacji z comprehensive error handling` (Docstring `_createTabs`)
- `Asset Browser`, `Parowanie`, `Narzędzia` (Nazwy zakładek)
- `Błąd ładowania {tab_name}: {e}` (Tekst w `QLabel`)
- `{tab_name} (Błąd)` (Nazwa zakładki z błędem)
- `Tworzy pasek statusu aplikacji` (Docstring `_createStatusBar`)
- `Zaznaczone: 0` (Tekst `selected_label`)
- `Aktualizuje pasek statusu z nową wiadomością` (Docstring `update_status`)
- `Wyświetla informacje z logów w pasku statusu w przyjaznej formie` (Docstring `show_log_info`)
- `Aktualizuje pasek statusu z informacją o aktualnym katalogu roboczym` (Docstring `update_working_directory_status`)
- `📁 Katalog roboczy: {short_path}` (Komunikat statusu)
- `Aktualizuje liczbę zaznaczonych assetów po prawej stronie paska statusu` (Docstring `update_selection_status`)
- `Zaznaczone: {checked_count}` (Komunikat statusu)
- ` (widoczne: {filtered_count}/{total_count})` (Komunikat statusu)
- `Wyświetla status operacji w pasku statusu` (Docstring `show_operation_status`)
- `Konfiguruje przechwytywanie logów do wyświetlania w pasku statusu` (Docstring `setup_log_interceptor`)
- `Sprawdza czy komunikat powinien być wyświetlony w pasku statusu` (Docstring `_should_show_in_status`)
- `Uproszczona metoda łączenia sygnałów` (Docstring `_connect_signals`)
- `Łączy sygnały AMV Tab` (Docstring `_connect_amv_signals`)
- `Łączy sygnały Status Bar` (Docstring `_connect_status_signals`)
- `Łączy sygnały Tools Tab` (Docstring `_connect_tools_signals`)
- `Obsługuje zmianę zaznaczenia i aktualizuje pasek statusu` (Docstring `_on_selection_changed`)
- `Obsługuje zmianę assetów i aktualizuje pasek statusu` (Docstring `_on_assets_changed`)
- `Obsługuje zamykanie aplikacji - zatrzymuje wszystkie wątki` (Docstring `closeEvent`)

## core/pairing_tab.py

- `Utwórz asset` (Tekst przycisku)
- `Usuń podglądy bez pary` (Tekst przycisku)
- `Usuń archiwa bez pary` (Tekst przycisku)
- `Przebuduj assety` (Tekst przycisku)
- `Potwierdzenie`, `Czy na pewno chcesz usunąć WSZYSTKIE niesparowane podglądy z listy i z dysku?
Tej operacji nie można cofnąć.` (Teksty w `QMessageBox.question`)
- `Sukces`, `Pomyślnie usunięto niesparowane podglądy.` (Teksty w `QMessageBox.information`)
- `Błąd`, `Wystąpił błąd podczas usuwania podglądów. Sprawdź logi.` (Teksty w `QMessageBox.warning`)
- `Potwierdzenie`, `Czy na pewno chcesz usunąć WSZYSTKIE niesparowane archiwa z listy i z dysku?
Tej operacji nie można cofnąć.` (Teksty w `QMessageBox.question`)
- `Sukces`, `Pomyślnie usunięto niesparowane archiwa.` (Teksty w `QMessageBox.information`)
- `Błąd`, `Wystąpił błąd podczas usuwania archiwów. Sprawdź logi.` (Teksty w `QMessageBox.warning`)
- `Błąd`, `Folder roboczy nie jest ustawiony lub nie istnieje.` (Teksty w `QMessageBox.warning`)
- `Potwierdzenie`, `Czy na pewno chcesz przebudować wszystkie assety w folderze:
{work_folder}?` (Teksty w `QMessageBox.question`)
- `Proces rozpoczęty`, `Rozpoczęto przebudowę assetów w folderze:
{work_folder}` (Teksty w `QMessageBox.information`)
- `Sukces`, `message` (Teksty w `QMessageBox.information`)
- `Błąd przebudowy`, `error_message` (Teksty w `QMessageBox.critical`)

## core/performance_monitor.py

- `Moduł monitoringu wydajności dla aplikacji CFAB Browser...` (Docstring modułu)
- `Klasa do przechowywania metryk wydajności` (Docstring `PerformanceMetrics`)
- `Finalizuje pomiar metryk` (Docstring `finish`)
- `Konwertuje metryki do słownika` (Docstring `to_dict`)
- `Główna klasa monitoringu wydajności` (Docstring `PerformanceMonitor`)
- `Inicjalizuje monitor wydajności` (Docstring `__init__`)
- `Konfiguruje system logowania` (Docstring `_setup_logging`)
- `Loguje metryki do pliku i/lub konsoli` (Docstring `_log_metrics`)
- `Pobiera aktualne zużycie pamięci w MB` (Docstring `_get_memory_usage`)
- `Context manager do mierzenia wydajności operacji` (Docstring `measure_operation`)
- `Dekorator do mierzenia wydajności funkcji` (Docstring `measure_function`)
- `Pobiera globalną instancję monitora wydajności` (Docstring `get_performance_monitor`)
- `Krótka funkcja do mierzenia operacji` (Docstring `measure_operation`)
- `Krótka funkcja do dekorowania funkcji` (Docstring `measure_function`)

## core/preview_window.py

- `Podgląd - {os.path.basename(self.image_path)}` (Tytuł okna)
- `Ładowanie obrazu...` (Tekst `image_label`)
- `Pokazuje okno podglądu.` (Docstring `show_window`)
- `Błąd ładowania obrazu: {e}` (Tekst `image_label`)

## core/rules.py

- `Rules - Logika decyzyjna dla obsługi kliknięć w foldery...` (Docstring modułu)
- `Klasa zawierająca logikę decyzyjną dla kliknięć w foldery...` (Docstring `FolderClickRules`)
- `Waliduje ścieżkę folderu pod kątem bezpieczeństwa` (Docstring `_validate_folder_path`)
- `Ścieżka folderu nie może być pusta`, `Ścieżka folderu musi być stringiem`, `Ścieżka zawiera niedozwolone sekwencje path traversal`, `Ścieżka folderu jest zbyt długa`, `Ścieżka zawiera niedozwolone znaki...` (Komunikaty błędów)
- `Sprawdza czy cache dla folderu jest aktualny` (Docstring `_is_cache_valid`)
- `Pobiera zcache'owaną analizę folderu` (Docstring `_get_cached_analysis`)
- `Zapisuje analizę folderu do cache` (Docstring `_cache_analysis`)
- `Kategoryzuje plik na podstawie rozszerzenia` (Docstring `_categorize_file`)
- `Analizuje zawartość folderu cache i zwraca liczbę miniaturek` (Docstring `_analyze_cache_folder`)
- `Pomocnicza metoda do generowania słownika błędu...` (Docstring `_create_error_result`)
- `Analizuje zawartość folderu i zwraca szczegółowe informacje o plikach...` (Docstring `analyze_folder_content`)
- `Folder nie istnieje: {folder_path}` (Komunikat błędu)
- `Brak uprawnień do odczytu folderu: {e}` (Komunikat błędu)
- `Błąd analizy folderu: {e}` (Komunikat błędu)
- `Obsługuje warunek 1...` (Docstring `_handle_condition_1`)
- `Brak plików asset - uruchamiam scanner` (Komunikat decyzji)
- `Obsługuje warunek 2a...` (Docstring `_handle_condition_2a`)
- `Brak folderu .cache - uruchamiam scanner` (Komunikat decyzji)
- `Obsługuje warunek 2b...` (Docstring `_handle_condition_2b`)
- `Niezgodna liczba miniaturek... - uruchamiam scanner` (Komunikat decyzji)
- `Obsługuje warunek 2c...` (Docstring `_handle_condition_2c`)
- `Wszystko gotowe - wyświetlam galerię...` (Komunikat decyzji)
- `Obsługuje dodatkowy przypadek: Tylko pliki asset, brak .cache` (Docstring `_handle_additional_case_no_cache`)
- `Tylko pliki asset, brak .cache - uruchamiam scanner` (Komunikat decyzji)
- `Obsługuje dodatkowy przypadek: Tylko pliki asset, niezgodna liczba miniaturek` (Docstring `_handle_additional_case_mismatch`)
- `Tylko pliki asset, niezgodna liczba miniaturek... - uruchamiam scanner` (Komunikat decyzji)
- `Obsługuje dodatkowy przypadek: Tylko pliki asset, wszystko gotowe` (Docstring `_handle_additional_case_ready`)
- `Tylko pliki asset, wszystko gotowe - wyświetlam galerię...` (Komunikat decyzji)
- `Obsługuje przypadek domyślny: Folder nie zawiera odpowiednich plików` (Docstring `_handle_default_case`)
- `Folder nie zawiera odpowiednich plików` (Komunikat decyzji)
- `Podejmuje decyzję o akcji na podstawie zawartości folderu...` (Docstring `decide_action`)

## core/scanner.py

- `Implementacja repozytorium assetów...` (Docstring `AssetRepository`)
- `Inicjalizuje repozytorium assetów.` (Docstring `__init__`)
- `DODAJ bazową metodę dla obsługi błędów` (Docstring `_handle_error`)
- `Pomocnicza funkcja do wyszukiwania plików o określonych rozszerzeniach` (Docstring `_get_files_by_extensions`)
- `Skanuje folder w poszukiwaniu plików archiwów i obrazów` (Docstring `_scan_folder_for_files`)
- `Sprawdza obecność folderów tekstur w folderze roboczym` (Docstring `_check_texture_folders_presence`)
- `Statyczna walidacja ścieżki folderu` (Docstring `_validate_folder_path_static`)
- `Skanuje folder w poszukiwaniu podfolderów o zadanych nazwach.` (Docstring `_scan_for_named_folders`)
- `Skanuje folder w poszukiwaniu specjalnych folderów (tex, textures, maps).` (Docstring `_scan_for_special_folders`)
- `Tworzy pojedynczy plik .asset` (Docstring `_create_single_asset`)
- `Pobiera rozmiar pliku w megabajtach` (Docstring `_get_file_size_mb`)
- `Tworzy miniaturę dla assetu` (Docstring `create_thumbnail_for_asset`)
- `Tworzy plik JSON z nieparowanymi plikami` (Docstring `_create_unpair_files_json`)
- `Wyszukuje i tworzy assety w określonym folderze` (Docstring `find_and_create_assets`)
- `Tworzenie assetu: {name}` (Komunikat postępu)
- `Skanuje folder i grupuje pliki według nazw` (Docstring `_scan_and_group_files`)
- `Tworzy assety z pogrupowanych plików` (Docstring `_create_assets_from_groups`)
- `Ładuje istniejące assety z określonego folderu` (Docstring `load_existing_assets`)

## core/thumbnail.py

- `Prosty generator miniaturek obrazów` (Docstring `ThumbnailGenerator`)
- `Inicjalizuje generator miniaturek` (Docstring `__init__`)
- `Generuje miniaturkę dla obrazu` (Docstring `generate_thumbnail`)
- `Sprawdza czy miniaturka jest aktualna` (Docstring `_is_thumbnail_current`)
- `Przeskalowuje obraz do kwadratu z przycinaniem...` (Docstring `_resize_to_square`)
- `Pobiera konfigurację miniaturek` (Docstring `get_config`)
- `Pobiera globalną instancję generatora` (Docstring `get_generator`)
- `Główna funkcja do generowania miniaturek` (Docstring `generate_thumbnail`)

## core/thumbnail_cache.py

- `ThumbnailCache - Zarządzanie buforowaniem miniatur w pamięci.` (Docstring modułu)
- `Klasa do buforowania miniatur (QPixmap) w pamięci z ograniczeniem rozmiaru (LRU).` (Docstring `ThumbnailCache`)
- `Inicjalizuje cache.` (Docstring `__init__`)
- `Pobiera QPixmap z cache.` (Docstring `get`)
- `Dodaje QPixmap do cache.` (Docstring `put`)
- `Usuwa najstarszy element z cache (LRU).` (Docstring `_evict_oldest`)
- `Czyści cały cache.` (Docstring `clear`)
- `Zwraca aktualny rozmiar cache w MB.` (Docstring `get_current_size_mb`)

## core/tools_tab.py

- `Wspólna klasa do zarządzania workerami` (Docstring `WorkerManager`)
- `Wspólna logika obsługi postępu` (Docstring `handle_progress`)
- `Wspólna logika obsługi zakończenia` (Docstring `handle_finished`)
- `Sukces` (Tytuł `show_info_message`)
- `Wspólna logika obsługi błędów` (Docstring `handle_error`)
- `Błąd` (Tytuł `show_error_message`)
- `Wspólna logika resetowania stanu przycisku` (Docstring `reset_button_state`)
- `Bazowa klasa dla workerów operacji na plikach.` (Docstring `BaseWorker`)
- `Metoda do nadpisania w klasach pochodnych.` (Docstring `_run_operation`)
- `Bezpiecznie zatrzymuje wątek` (Docstring `stop`)
- `Worker do konwersji plików obrazów na format WebP` (Docstring `WebPConverterWorker`)
- `Główna metoda konwersji na WebP` (Docstring `_run_operation`)
- `Brak plików do konwersji na WebP` (Komunikat `finished`)
- `Konwertowanie: {os.path.basename(original_path)}` (Komunikat postępu)
- `Konwersja zakończona: {converted_count} skonwertowano...` (Komunikat `finished`)
- `Konwersja zakończona` (Komunikat postępu)
- `Znajduje pliki do konwersji na WebP` (Docstring `_find_files_to_convert`)
- `Konwertuje pojedynczy plik na WebP` (Docstring `_convert_to_webp`)
- `Worker do zmniejszania plików obrazów` (Docstring `ImageResizerWorker`)
- `Główna metoda zmniejszania obrazów` (Docstring `_run_operation`)
- `Brak plików do zmniejszenia` (Komunikat `finished`)
- `Zmniejszanie: {filename}` (Komunikat postępu)
- `Zmniejszanie zakończone: {resized_count} zmniejszono...` (Komunikat `finished`)
- `Zmniejszanie zakończone` (Komunikat postępu)
- `Znajduje pliki do zmniejszenia` (Docstring `_find_files_to_resize`)
- `Zmniejsza pojedynczy obraz` (Docstring `_resize_image`)
- `Oblicza nowe wymiary według zasad skalowania` (Docstring `_calculate_new_size`)
- `Worker do skracania nazw plików` (Docstring `FileRenamerWorker`)
- `Metoda wywoływana po potwierdzeniu przez użytkownika` (Docstring `confirm_operation`)
- `Główna metoda skracania nazw plików` (Docstring `_run_operation`)
- `Brak plików do przetworzenia` (Komunikat `finished`)
- `Wykonuje właściwe skracanie nazw` (Docstring `_perform_renaming`)
- `Skracanie nazw par...` (Komunikat postępu)
- `Skrócono parę: ...` (Komunikat postępu)
- `Skracanie nazw plików bez pary...` (Komunikat postępu)
- `Przetwarzanie: {filename}` (Komunikat postępu)
- `Skracanie nazw zakończone: {renamed_count} plików skrócono...` (Komunikat `finished`)
- `Analizuje pliki w folderze i znajduje pary` (Docstring `_analyze_files`)
- `Generuje losową nazwę z zestawu 8 cyfr + 8 liter` (Docstring `_generate_random_name`)
- `Zmienia nazwę pliku zachowując rozszerzenie` (Docstring `_rename_file`)
- `Worker do usuwania prefixu/suffixu z nazw plików` (Docstring `PrefixSuffixRemoverWorker`)
- `Główna metoda usuwania prefixu/suffixu` (Docstring `_run_operation`)
- `Przetwarzanie: {filename_with_ext}` (Komunikat postępu)
- `Usuwanie {self.mode} zakończone: {renamed_count} plików zmieniono...` (Komunikat `finished`)
- `Wspólna walidacja folderu roboczego` (Docstring `_validate_working_directory`)
- `Błąd`, `Folder roboczy nie jest ustawiony lub nie istnieje.` (Teksty w `QMessageBox.warning`)
- `Jednolita obsługa cyklu życia worker` (Docstring `_handle_worker_lifecycle`)
- `Błąd`, `Nie można rozpocząć operacji: {e}` (Teksty w `QMessageBox.critical`)
- `Uniwersalna metoda do rozpoczynania operacji z potwierdzeniem` (Docstring `_start_operation_with_confirmation`)
- `Potwierdzenie {operation_name.lower()}`, `Czy na pewno chcesz {operation_name.lower()} w folderze...` (Teksty w `QMessageBox.question`)
- `konwersji na webp`, `przebudowy assetów`, `zmniejszania obrazów`, `skracania nazw plików`, `usuwania prefixu/suffixu` (Nazwy operacji)
- `Pliki` (Etykieta)
- `Narzędzia` (Etykieta)
- `Konwertuj na WebP` (Tekst przycisku)
- `Zmniejsz obrazy` (Tekst przycisku)
- `Skróć nazwy plików` (Tekst przycisku)
- `Usuń prefix/suffix` (Tekst przycisku)
- `Przebuduj assety` (Tekst przycisku)
- `Ustawia folder roboczy i skanuje pliki` (Docstring `set_working_directory`)
- `Skanuje folder roboczy w poszukiwaniu plików archiwum i podglądów` (Docstring `scan_working_directory`)
- `Błąd`, `Nie można skanować folderu: {e}` (Teksty w `QMessageBox.warning`)
- `Aktualizuje listę plików archiwum` (Docstring `_update_archive_list`)
- `Aktualizuje listę plików podglądów` (Docstring `_update_preview_list`)
- `Pobiera rozdzielczość obrazu w formacie 'szerokość x wysokość'` (Docstring `_get_image_resolution`)
- `brak danych`, `brak Pillow`, `błąd odczytu` (Komunikaty o rozdzielczości)
- `Czyści obie listy` (Docstring `clear_lists`)
- `Aktualizuje stan wszystkich przycisków` (Docstring `_update_button_states`)
- `Zatrzymuje wszystkie aktywne wątki przed zniszczeniem` (Docstring `closeEvent`)
- `Ta operacja:
• Skonwertuje pliki...` (Opis w `_on_webp_conversion_clicked`)
- `Ta operacja:
• Usunie wszystkie pliki .asset...` (Opis w `_on_rebuild_assets_clicked`)
- `Obsługuje podwójne kliknięcie na plik archiwum` (Docstring `_on_archive_double_clicked`)
- `Błąd`, `Timeout podczas otwierania archiwum` (Teksty w `QMessageBox.warning`)
- `Błąd`, `Błąd procesu podczas otwierania archiwum` (Teksty w `QMessageBox.warning`)
- `Błąd`, `Nie można otworzyć archiwum: {e}` (Teksty w `QMessageBox.warning`)
- `Błąd`, `Plik nie istnieje: {file_name}` (Teksty w `QMessageBox.warning`)
- `Obsługuje podwójne kliknięcie na plik podglądu` (Docstring `_on_preview_double_clicked`)
- `Błąd`, `Nie można otworzyć podglądu: {e}` (Teksty w `QMessageBox.warning`)
- `Obsługuje kliknięcie przycisku zmniejszania obrazów` (Docstring `_on_image_resizing_clicked`)
- `Ta operacja:
• Zmniejszy obrazy...` (Opis w `_on_image_resizing_clicked`)
- `Obsługuje kliknięcie przycisku skracania nazw plików` (Docstring `_on_file_renaming_clicked`)
- `Limit znaków`, `Podaj maksymalną długość nazw plików (bez rozszerzenia):` (Teksty w `QInputDialog.getInt`)
- `Rozpoczyna skracanie nazw plików` (Docstring `_start_file_renaming`)
- `Obsługuje kliknięcie przycisku usuwania prefixu/suffixu` (Docstring `_on_remove_clicked`)
- `Usuwanie prefiksów/sufiksów` (Tytuł okna dialogowego)
- `Wybierz tryb operacji:` (Etykieta)
- `Usuń PREFIX (początek nazwy)` (Tekst `QRadioButton`)
- `Usuń SUFFIX (koniec nazwy)` (Tekst `QRadioButton`)
- `Tekst do usunięcia (wielkość liter ma znaczenie):` (Etykieta)
- `Wpisz tekst który ma być usunięty z nazw plików...` (Placeholder)
- `Przykłady: _8K, _FINAL, temp_, backup_, ' 0' (spacja+zero)` (Etykieta)
- `USUŃ` (Tekst przycisku)
- `Anuluj` (Tekst przycisku)
- `Błąd`, `Proszę wprowadzić tekst do usunięcia.` (Teksty w `QMessageBox.warning`)
- `Rozpoczyna usuwanie prefixu/suffixu z nazw plików` (Docstring `_start_remove`)
- `Usuwanie...` (Tekst przycisku)
- `Wyświetla okno z listą par, które będą zmieniane` (Docstring `_show_pairs_dialog`)
- `Pary plików do zmiany nazw` (Tytuł okna dialogowego)
- `Znaleziono {len(pairs)} par plików do przetworzenia:` (Etykieta)
- `Kontynuuj` (Tekst przycisku)
- `Czyści folder roboczy, dezaktywuje przyciski i czyści listy` (Docstring `clear_working_directory`)

## core/utilities.py

- `Moduł utilities - wspólne funkcje narzędziowe` (Docstring modułu)
- `Pobiera rozmiar pliku w megabajtach` (Docstring `get_file_size_mb`)

## core/workers/asset_rebuilder_worker.py

- `AssetRebuilderWorker - Worker dla przebudowy assetów w folderze...` (Docstring modułu)
- `Worker dla przebudowy assetów w folderze` (Docstring `AssetRebuilderWorker`)
- `Główna metoda przebudowy assetów` (Docstring `run`)
- `Usuwanie starych plików .asset...` (Komunikat postępu)
- `Usuwanie folderu .cache...` (Komunikat postępu)
- `Skanowanie i tworzenie nowych assetów...` (Komunikat postępu)
- `Przebudowa zakończona!` (Komunikat postępu)
- `Pomyślnie przebudowano assety w folderze: {self.folder_path}` (Komunikat `finished`)
- `Usuwa wszystkie pliki .asset z folderu` (Docstring `_remove_asset_files`)
- `BEZWZGLĘDNIE usuwa folder .cache - folder cache do kurwy, nie ważne co zawiera` (Docstring `_remove_cache_folder`)
- `Uruchamia scanner.py w folderze` (Docstring `_run_scanner`)

## core/workers/thumbnail_loader_worker.py

- `ThumbnailLoaderWorker - Asynchroniczne ładowanie miniatur.` (Docstring modułu)
- `Sygnały dla workera ładowania miniatur.` (Docstring `ThumbnailLoaderSignals`)
- `Worker (QRunnable) do asynchronicznego ładowania pojedynczej miniatury...` (Docstring `ThumbnailLoaderWorker`)
- `Ładuje miniaturę z dysku.` (Docstring `run`)
