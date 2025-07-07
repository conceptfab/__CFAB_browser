# Lista fraz do tłumaczenia

Pliki posortowane pod względem ilości fraz do tłumaczenia (malejąco).

---

## 7. `core/tools/prefix_suffix_remover_worker.py` (17)

### UI Messages (3)
- `Brak plików do przetworzenia`
- `Przetwarzanie: {filename_with_ext}`
- `Usuwanie {self.mode} zakończone: {renamed_count} plików zmieniono`

### Logi (4)
- `Rozpoczęcie usuwania {self.mode} w folderze: {self.folder_path}`
- `Zmieniono: '{filename_with_ext}' -> '{new_full_filename}'`
- `Błąd podczas przetwarzania {os.path.basename(file_path)}: {e}`
- `Błąd podczas usuwania {self.mode}: {e}`

### Komentarze (10)
- `"""Worker do usuwania prefixu/suffixu z nazw plików"""`
- `# Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker`
- `# "prefix" lub "suffix"`
- `"""Główna metoda usuwania prefixu/suffixu"""`
- `# Znajdź wszystkie pliki w folderze`
- `# Przetwórz pliki`
- `# Sprawdź czy plik pasuje do kryteriów`
- `# Usuń spacje z końca po usunięciu prefix`
- `# Usuń spacje z końca po usunięciu suffix`
- `# Zmień nazwę`
- `# Przygotuj komunikat końcowy`

---

## 8. `core/tools/duplicate_finder_worker.py` (16)

### UI Messages (3)
- `No archive files to check`
- `No duplicates found`
- `Found {len(duplicates)} duplicate groups. Moved {moved_count} files to __duplicates__ folder`

### Logi (1)
- `Rozpoczęcie szukania duplikatów w folderze: {self.folder_path}`

### Komentarze (12)
- `# Log informacyjny o załadowaniu modułu Rust`
- `# Pobierz informacje o kompilacji`
- `"""Worker do znajdowania duplikatów plików na podstawie SHA-256"""`
- `# lista duplikatów do wyświetlenia`
- `"""Główna metoda znajdowania duplikatów"""`
- `# Znajdź pliki archiwum`
- `# Oblicz SHA-256 dla każdego pliku`
- `# Znajdź duplikaty`
- `# Przygotuj listę do przeniesienia (nowsze pliki)`
- `# Przenieś pliki do folderu __duplicates__`

---

## 9. `core/pairing_tab.py` (16)

### UI Messages (11)
- `Create asset`
- `Delete unpaired previews`
- `Delete unpaired archives`
- `Rebuild assets`
- `Open in default program`
- `Confirmation`
- `Are you sure you want to delete ALL unpaired previews from the list and disk?
This operation cannot be undone.`
- `Success`
- `Successfully deleted unpaired previews.`
- `Error`
- `An error occurred while deleting previews. Check logs.`
- `Are you sure you want to delete ALL unpaired archives from the list and disk?
This operation cannot be undone.`
- `Successfully deleted unpaired archives.`
- `An error occurred while deleting archives. Check logs.`
- `Are you sure you want to rebuild all assets in the folder:
{work_folder}?`
- `Process started`
- `Asset rebuild started in folder:
{work_folder}`
- `Rebuild Error`

### Logi (1)
- `Zabezpieczenie przed wieloma oknami`

### Komentarze (4)
- `# Użyj folderu roboczego z modelu zamiast folderu z pliku unpair_files.json`
- `# KATEGORYCZNE CZYSZCZENIE CACHE PAMIĘCI RAM PO PRZEBUDOWIE ASSETÓW!!!`
- `# CATEGORICAL CLEARING OF RAM CACHE EVEN AFTER REBUILD ERROR!!!`

---

## 10. `core/amv_models/asset_grid_model.py` (15)

### Logi (8)
- `WCZYTYWANIE OD NOWA assetów w folderze: %s`
- `Inicjalizacja skanowania...`
- `Skanowanie: {message}`
- `Rozpoczynanie skanowania plików...`
- `Skanowanie zakończone, znaleziono %d assetów`
- `Ładowanie assetów z plików...`
- `WCZYTANO OD NOWA %d assetów z plików .asset`
- `Finalizowanie...`
- `WCZYTYWANIE OD NOWA zakończone, łącznie {len(all_assets)} assetów`
- `Zakończono!`

### Komentarze (7)
- `# Początek - inicjalizacja (0-10%)`
- `# WCZYTAJ OD NOWA - najpierw skanuj i utwórz assety`
- `# Skanuj folder i utwórz nowe assety (10-80%)`
- `# Map scan progress to the 10-80% range`
- `# Ładowanie assetów (80-95%)`
- `# WCZYTAJ OD NOWA - teraz załaduj wszystkie assety z plików .asset`
- `# Finalizacja (95-100%)`

---

## 11. `core/amv_models/workspace_folders_model.py` (14)

### Logi (4)
- `Folder roboczy nie istnieje: {folder_path}`
- `Załadowano {len(self._folders)} folderów roboczych (sortowanie alfabetyczne)`
- `Błąd podczas ładowania folderów roboczych: {e}`

### Komentarze (10)
- `# Przeiteruj przez work_folder1 do work_folder9`
- `# Sprawdź, czy folder istnieje (tylko jeśli ma ścieżkę)`
- `# Ustaw domyślną ikonę jeśli nie ma określonej`
- `# Dodaj wszystkie foldery, nawet puste`
- `# Aktywny tylko jeśli ma ścieżkę i istnieje`
- `# SORTOWANIE ALFABETYCZNE - najpierw aktywne, potem nieaktywne`
- `# Sortuj aktywne foldery alfabetycznie`
- `# Sortuj nieaktywne foldery alfabetycznie`
- `# Puste foldery na końcu`
- `# Złóż wszystko w kolejności: aktywne, nieaktywne, puste`

---

## 12. `core/tools/file_shortener_worker.py` (13)

### UI Messages (5)
- `No files to process`
- `Shortening pair names...`
- `Shortened pair: {archive_name[:20]}...`
- `Shortening unpaired file names...`
- `Processing: {filename[:20]}...`
- `Name shortening completed: {shortened_count} files shortened`

### Logi (3)
- `Zmieniono nazwę: {os.path.basename(file_path)} -> {new_name + file_ext}`
- `Błąd podczas zmiany nazwy {file_path}: {e}`

### Komentarze (5)
- `# Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker`
- `# lista par do wyświetlenia`
- `# czeka na potwierdzenie użytkownika`
- `"""Zmienia nazwę pliku zachowując rozszerzenie"""`
- `# Pobierz rozszerzenie`
- `# Utwórz nową nazwę z rozszerzeniem`
- `# Zmień nazwę`

---

## 13. `core/amv_models/drag_drop_model.py` (12)

### Logi (1)
- `Porównanie ścieżek: norm_target='{norm_target}', norm_current='{norm_current}'`

### Komentarze (11)
- `# Lista ID assetów przeciąganych`
- `# Czy upuszczenie jest możliwe`
- `# Ścieżka docelowa, lista ID przeniesionych assetów`
- `# NOWE: zabezpieczenie przed rekurencją`
- `# ZABEZPIECZENIE: Sprawdź czy operacja już nie jest w toku`
- `# Normalizuj ścieżki do porównania`
- `# Przykład: Nie zezwalaj na upuszczanie do folderów tekstur`
- `# ZABEZPIECZENIE: Sprawdź czy asset_ids są prawidłowe`
- `# ZABEZPIECZENIE: Sprawdź czy target_path jest prawidłowy`
- `# Wyczyść po zakończeniu operacji`
- `# W przypadku błędu, wyczyść stan`

---

## 14. `core/scanner.py` (11)

### Logi (4)
- `🦀 ✅ SUKCES: Załadowano LOKALNY silnik Rust scanner z: {scanner_location}`
- `🦀 RUST SCANNER: Używam LOKALNEJ wersji z: {scanner_location} [build: {build_timestamp}, module: {module_number}]`
- `🦀 ⚠️ FALLBACK: Używam GLOBALNEGO silnika Rust scanner z: {scanner_location}`
- `🦀 RUST SCANNER: FALLBACK - używam globalnej wersji z: {scanner_location} [build: {build_timestamp}, module: {module_number}]`
- `🦀 ❌ BŁĄD: Nie można załadować żadnej wersji scanner_rust: {e}`

### Komentarze (7)
- `# ZAWSZE preferuj lokalną wersję Rust scannera z core/__rust`
- `# Usuń site-packages z path tymczasowo aby wymusić lokalną wersję`
- `# Usuń wszystkie ścieżki zawierające site-packages dla scanner_rust`
- `# Dodaj lokalny folder na początek`
- `# Pobierz informacje o kompilacji`
- `# Przywróć oryginalną ścieżkę w przypadku błędu`
- `# Nie można załadować Rustowego backendu (scanner_rust): {}`
- `"""Wrapper na Rustowy backend skanera assetów."""`

---

## 15. `core/amv_models/file_operations_model.py` (9)

### Logi (1)
- `Błąd przenoszenia assetu {original_name}: {e}`

### Komentarze (8)
- `# 1. Plik .asset`
- `# 2. Plik archiwum`
- `# 3. Plik podglądu`
- `# 4. Plik miniatury w folderze .cache`
- `# Przechowuj folder docelowy`
- `# Zapisz folder docelowy`
- `# Zwraca folder docelowy ostatniej operacji move`
- `# Wyczyść folder docelowy przy delete`

---

## Pozostałe pliki

- **`core/tools/file_renamer_worker.py` (8)**: 5 UI, 3 komentarze
- **`core/workers/asset_rebuilder_worker.py` (8)**: 5 UI, 1 log, 2 komentarze
- **`core/amv_controllers/handlers/folder_tree_controller.py` (8)**: 2 logi, 6 komentarzy
- **`core/tools/image_resizer_worker.py` (7)**: 4 UI, 3 komentarze
- **`core/tools/webp_converter_worker.py` (7)**: 4 UI, 3 komentarze
- **`core/json_utils.py` (6)**: 5 logów, 1 komentarz
- **`core/amv_views/preview_tile.py` (6)**: 6 komentarzy
- **`core/amv_controllers/amv_controller.py` (5)**: 5 komentarzy
- **`core/amv_controllers/handlers/asset_grid_controller.py` (5)**: 5 komentarzy
- **`core/amv_models/pairing_model.py` (5)**: 5 komentarzy
- **`core/amv_tab.py` (5)**: 5 komentarzy
- **`core/performance_monitor.py` (5)**: 5 komentarzy
- **`core/utilities.py` (5)**: 2 logi, 3 komentarze
- **`core/amv_models/config_manager_model.py` (4)**: 4 logi
- **`core/rules.py` (4)**: 4 komentarze
- **`core/main_window.py` (4)**: 4 UI
- **`core/preview_window.py` (3)**: 1 UI, 1 log, 1 komentarz
- **`core/amv_controllers/handlers/asset_rebuild_controller.py` (2)**: 2 komentarze
- **`core/amv_models/selection_model.py` (2)**: 2 komentarze
- **`core/selection_counter.py` (2)**: 2 UI
- **`core/workers/worker_manager.py` (2)**: 2 UI
- **`core/amv_controllers/handlers/signal_connector.py` (1)**: 1 komentarz
- **`core/amv_views/preview_gallery_view.py` (1)**: 1 komentarz
