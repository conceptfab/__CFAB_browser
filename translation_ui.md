
# UI i komunikaty do tłumaczenia

## `core/amv_controllers/amv_controller.py`
- `QMessageBox.warning(self.view, "Error", f"Cannot open: {path}")`
- `QMessageBox.warning(self.view, "Error", f"Path does not exist: {path}")`

## `core/amv_controllers/handlers/asset_grid_controller.py`
- `self.view.update_gallery_placeholder("No assets found in this folder.")`

## `core/amv_controllers/handlers/asset_rebuild_controller.py`
- `self.view.update_gallery_placeholder(f"Asset rebuild error: {error_message}")`

## `core/amv_controllers/handlers/file_operation_controller.py`
- `QMessageBox.information(self.view, operation_name, f"No assets selected for {operation_name.lower()}.")`
- `QMessageBox.warning(self.view, operation_name, "Could not find full data for the selected assets.")`
- `QFileDialog.getExistingDirectory(self.view, "Select target folder", ...)`
- `self.view.update_gallery_placeholder("Moving assets...")`
- `QMessageBox.question(self.view, "Confirm Deletion", (f"Are you sure you want to delete {len(assets_to_delete)} " "selected assets?\nThis operation is irreversible!"), ...)`
- `self.view.update_gallery_placeholder("Deleting assets...")`
- `self.view.update_gallery_placeholder("No assets found in this folder.")`
- `self.view.update_gallery_placeholder(f"File operation error: {error_msg}")`

## `core/amv_views/amv_view.py`
- `self.collapse_button = QPushButton("Zwiń")`
- `self.expand_button = QPushButton("Rozwiń")`
- `self.toggle_button.setToolTip("Zamknij panel")`
- `self.edge_button.setToolTip("Otwórz panel")`
- `self.placeholder_label = QLabel("Panel galerii\n(Oczekiwanie na wybór folderu)")`
- `self.select_all_button = QPushButton("Zaznacz wszystkie")`
- `self.move_selected_button = QPushButton("Przenieś zaznaczone")`
- `self.delete_selected_button = QPushButton("Usuń zaznaczone")`
- `self.deselect_all_button = QPushButton("Odznacz wszystkie")`
- `self.toggle_button.setToolTip("Zamknij panel" if is_panel_open else "Otwórz panel")`

## `core/file_utils.py`
- `QMessageBox.warning(parent_widget, "Błąd", f"Ścieżka nie istnieje: {path}")`
- `QMessageBox.warning(parent_widget, "Błąd", f"Timeout podczas otwierania ścieżki: {path}")`
- `QMessageBox.warning(parent_widget, "Błąd", f"Błąd procesu podczas otwierania: {path}")`
- `QMessageBox.warning(parent_widget, "Błąd", f"Nie można otworzyć ścieżki: {path}")`
- `QMessageBox.warning(parent_widget, "Błąd", f"Plik nie istnieje: {path}")`
- `QMessageBox.warning(parent_widget, "Błąd", f"Timeout podczas otwierania pliku: {path}")`
- `QMessageBox.warning(parent_widget, "Błąd", f"Błąd procesu podczas otwierania pliku: {path}")`
- `QMessageBox.warning(parent_widget, "Błąd", f"Nie można otworzyć pliku: {path}")`

## `core/main_window.py`
- `self.setWindowTitle("CFAB Browser")`
- `file_menu = QMenu("Plik", self)`
- `exit_action = QAction("Wyjście", self)`
- `self.tabs.addTab(tab_instance, "Asset Browser")`
- `self.tabs.addTab(tab_instance, "Parowanie")`
- `self.tabs.addTab(tab_instance, "Narzędzia")`
- `self.tabs.addTab(placeholder, f"{tab_name} (Błąd)")`
- `self.selected_label = QLabel("Zaznaczone: 0")`
- `status_text = f"Zaznaczone: {checked_count}"`
- `status_text += f" (widoczne: {filtered_count}/{total_count})"`

## `core/pairing_tab.py`
- `open_action = QAction("Otwórz w programie domyślnym", self)`
- `self.create_asset_button = QPushButton("Utwórz asset")`
- `self.delete_previews_button = QPushButton("Usuń podglądy bez pary")`
- `self.delete_archives_button = QPushButton("Usuń archiwa bez pary")`
- `self.rebuild_assets_button = QPushButton("Przebuduj assety")`
- `reply = QMessageBox.question(self, "Potwierdzenie", "Czy na pewno chcesz usunąć WSZYSTKIE niesparowane podglądy z listy i z dysku?\nTej operacji nie można cofnąć.", ...)`
- `QMessageBox.information(self, "Sukces", "Pomyślnie usunięto niesparowane podglądy.")`
- `QMessageBox.warning(self, "Błąd", "Wystąpił błąd podczas usuwania podglądów. Sprawdź logi.")`
- `reply = QMessageBox.question(self, "Potwierdzenie", "Czy na pewno chcesz usunąć WSZYSTKIE niesparowane archiwa z listy i z dysku?\nTej operacji nie można cofnąć.", ...)`
- `QMessageBox.information(self, "Sukces", "Pomyślnie usunięto niesparowane archiwa.")`
- `QMessageBox.warning(self, "Błąd", "Wystąpił błąd podczas usuwania archiwów. Sprawdź logi.")`
- `QMessageBox.warning(self, "Błąd", "Folder roboczy nie jest ustawiony lub nie istnieje.")`
- `reply = QMessageBox.question(self, "Potwierdzenie", f"Czy na pewno chcesz przebudować wszystkie assety w folderze:\n{work_folder}?", ...)`
- `QMessageBox.information(self, "Proces rozpoczęty", f"Rozpoczęto przebudowę assetów w folderze:\n{work_folder}")`
- `QMessageBox.information(self, "Sukces", message)`
- `QMessageBox.critical(self, "Błąd przebudowy", error_message)`

## `core/preview_window.py`
- `self.setWindowTitle(f"Podgląd - {os.path.basename(self.image_path)}")`
- `self.image_label.setText("Ładowanie obrazu...")`

## `core/tools_tab.py`
- `QMessageBox.warning(self, "Błąd", "Folder roboczy nie jest ustawiony lub nie istnieje.")`
- `left_layout.addWidget(QLabel("Pliki"))`
- `right_layout.addWidget(QLabel("Narzędzia"))`
- `self.webp_button = QPushButton("Konwertuj na WebP")`
- `self.image_resizer_button = QPushButton("Zmniejsz obrazy")`
- `self.file_renamer_button = QPushButton("Skróć nazwy plików")`
- `self.remove_button = QPushButton("Usuń prefix/suffix")`
- `self.rebuild_button = QPushButton("Przebuduj assety")`
- `QMessageBox.warning(self, "Błąd", f"Nie można skanować folderu: {e}")`
- `max_name_length, ok = QInputDialog.getInt(self, "Limit znaków", "Podaj maksymalną długość nazw plików (bez rozszerzenia):", ...)`
- `dialog.setWindowTitle("Usuwanie prefiksów/sufiksów")`
- `mode_label = QLabel("Wybierz tryb operacji:")`
- `prefix_radio = QRadioButton("Usuń PREFIX (początek nazwy)")`
- `suffix_radio = QRadioButton("Usuń SUFFIX (koniec nazwy)")`
- `text_label = QLabel("Tekst do usunięcia (wielkość liter ma znaczenie):")`
- `text_edit.setPlaceholderText("Wpisz tekst który ma być usunięty z nazw plików...")`
- `example_label = QLabel("Przykłady: _8K, _FINAL, temp_, backup_, ' 0' (spacja+zero)")`
- `ok_button = QPushButton("USUŃ")`
- `cancel_button = QPushButton("Anuluj")`
- `QMessageBox.warning(self, "Błąd", "Proszę wprowadzić tekst do usunięcia.")`
- `self.remove_button.setText("Usuwanie...")`
- `dialog.setWindowTitle("Pary plików do zmiany nazw")`
- `header_label = QLabel(f"Znaleziono {len(pairs)} par plików do przetworzenia:")`
- `ok_button = QPushButton("Kontynuuj")`
- `cancel_button = QPushButton("Anuluj")`

