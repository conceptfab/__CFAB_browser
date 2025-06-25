# Poprawki do logiki obsługi kliknięć w foldery

## Wprowadzone zmiany

### Plik: `core/folder_scanner_worker.py`

**Metoda: `handle_folder_click`**

Zmieniono logikę decyzyjną zgodnie z wymaganiami użytkownika:

#### Poprzednia logika:

1. Sprawdzała czy są pliki asset
2. Jeśli tak - sprawdzała .cache
3. Jeśli nie - sprawdzała archiwa/podglądy

#### Nowa logika (zgodna z wymaganiami):

**WARUNEK 1**: Jeśli folder zawiera pliki archiwum i podglądy i NIE ma plików asset

- **Akcja**: Scanner zaczyna pracę i po sukcesie galeria wyświetla assety

**WARUNEK 2**: Jeśli folder zawiera pliki archiwum, podglądy i pliki asset

- **Podwarunek 2a**: Jeśli nie ma folderu .cache
  - **Akcja**: Scanner zaczyna pracę i po sukcesie galeria wyświetla assety
- **Podwarunek 2b**: Jeśli jest folder .cache ale zawiera inną liczbę plików thumb niż plików asset
  - **Akcja**: Scanner zaczyna pracę i po sukcesie galeria wyświetla assety
- **Podwarunek 2c**: Jeśli w .cache jest identyczna liczba plików thumb i asset
  - **Akcja**: Galeria wyświetla assety, scanner NIE uruchamia się automatycznie

**Dodatkowy przypadek**: Jeśli folder zawiera tylko pliki asset (bez archiwów/podglądów)

- Stosuje tę samą logikę co Warunek 2

## Szczegóły implementacji

### Zmienione warunki w kodzie:

```python
# LOGIKA DECYZYJNA ZGODNIE Z WYMAGANIAMI
if preview_archive_files and not asset_files:
    # WARUNEK 1: folder zawiera pliki archiwum i podglądy i NIE ma plików asset
    logger.info("Warunek 1: Uruchamiam scanner (brak plików asset)")
    self._run_scanner(folder_path)

elif preview_archive_files and asset_files:
    # WARUNEK 2: folder zawiera pliki archiwum, podglądy i pliki asset
    if not cache_exists:
        # Podwarunek 2a: nie ma folderu .cache - uruchom scanner
        logger.info("Warunek 2a: Uruchamiam scanner (brak .cache)")
        self._run_scanner(folder_path)

    elif cache_thumb_count != len(asset_files):
        # Podwarunek 2b: .cache istnieje ale liczba thumb != liczba asset
        logger.info(f"Warunek 2b: Uruchamiam scanner (thumb: {cache_thumb_count}, asset: {len(asset_files)})")
        self._run_scanner(folder_path)

    else:
        # Podwarunek 2c: .cache istnieje i liczba thumb == liczba asset
        # Galeria wyświetla assety, scanner NIE uruchamia się automatycznie
        logger.info(f"Warunek 2c: Wyświetlam galerię bez scannera (thumb: {cache_thumb_count}, asset: {len(asset_files)})")
        self.assets_folder_found.emit(folder_path)
```

## Zachowana funkcjonalność

- Galeria poprawnie obsługuje sygnał `assets_folder_found`
- `AssetScanner` może wyświetlać assety bez uruchamiania scannera
- `GridManager` poprawnie ustawia `current_folder_path` dla ładowania miniaturek
- Wszystkie pozostałe funkcjonalności pozostają niezmienione

## Testowanie

Aplikacja uruchamia się poprawnie. Logika decyzyjna jest teraz zgodna z wymaganiami użytkownika:

1. **Automatyczne uruchamianie scannera** gdy:

   - Brak plików asset (tylko archiwa/podglądy)
   - Brak folderu .cache
   - Niezgodna liczba miniaturek w .cache

2. **Wyświetlanie galerii bez scannera** gdy:

   - Folder .cache istnieje i ma identyczną liczbę miniaturek co plików asset

3. **Decyzja o uruchomieniu scannera** pozostaje do użytkownika gdy:
   - Wszystkie warunki są spełnione (identyczna liczba miniaturek i assetów)

---

# Nowa funkcjonalność: Drag and Drop

## Opis funkcjonalności

Dodano możliwość przeciągania kafelków asset-ów (thumbnail tiles) do folderów w drzewie folderów. Po upuszczeniu kafelka na folder, wszystkie 4 powiązane pliki zostają przeniesione do nowej lokalizacji.

## Pliki przenoszone razem

Dla każdego asset-a przenoszone są następujące 4 pliki:

1. **Plik archiwum** (`.zip`, `.rar`, `.sbsar`) - główny plik z zawartością
2. **Plik podglądu** (`.jpg`, `.png`, `.jpeg`, `.gif`) - obraz podglądu
3. **Plik asset** (`.asset`) - plik JSON z metadanymi
4. **Plik thumbnail** (`.thumb`) - miniaturka w folderze `.cache`

## Implementacja

### Plik: `core/thumbnail_tile.py`

**Dodane funkcjonalności:**

- **Sygnał `drag_started`** - emitowany przy rozpoczęciu przeciągania
- **Metoda `mousePressEvent`** - obsługa naciśnięcia myszy i rozpoczęcie drag
- **Metoda `_start_drag`** - tworzenie obiektu drag z MIME data
- **MIME data** - zawiera dane asset-a w formacie JSON

**Kluczowe zmiany:**

```python
# Sygnał dla rozpoczęcia drag
drag_started = pyqtSignal(object)

# Obsługa naciśnięcia myszy
def mousePressEvent(self, event):
    if event.button() == Qt.MouseButton.LeftButton:
        if self.asset_data:
            self._start_drag(event)

# Tworzenie MIME data
def _start_drag(self, event):
    drag = QDrag(self)
    mime_data = QMimeData()
    asset_json = json.dumps(self.asset_data)
    mime_data.setData("application/x-cfab-asset", asset_json.encode('utf-8'))
    drag.setMimeData(mime_data)
    drag.exec(Qt.DropAction.MoveAction)
```

### Plik: `core/gallery_tab.py`

**Dodane funkcjonalności:**

- **Obsługa drag and drop** dla przycisków folderów w drzewie
- **Obsługa drag and drop** dla przycisków w panelu szybkiego dostępu
- **Metody obsługi drag events:**
  - `_on_folder_drag_enter` - podświetlanie folderu przy najechaniu
  - `_on_folder_drag_leave` - przywracanie normalnego stylu
  - `_on_folder_drop` - obsługa upuszczenia asset-a
- **Metoda `_move_asset_to_folder`** - przenoszenie wszystkich 4 plików
- **Metoda `_refresh_gallery_after_move`** - odświeżanie galerii po przeniesieniu

**Kluczowe zmiany:**

```python
# Włącz obsługę drag and drop dla przycisków folderów
folder_button.setAcceptDrops(True)
folder_button.dragEnterEvent = lambda event, path=folder_path: self._on_folder_drag_enter(event, path)
folder_button.dragLeaveEvent = lambda event, path=folder_path: self._on_folder_drag_leave(event, path)
folder_button.dropEvent = lambda event, path=folder_path: self._on_folder_drop(event, path)

# Przenoszenie wszystkich 4 plików
def _move_asset_to_folder(self, asset_data, target_folder_path):
    files_to_move = []

    # 1. Plik archiwum
    archive_filename = asset_data.get('archive')
    if archive_filename:
        archive_path = os.path.join(source_folder_path, archive_filename)
        if os.path.exists(archive_path):
            files_to_move.append(('archive', archive_path, archive_filename))

    # 2. Plik podglądu
    preview_filename = asset_data.get('preview')
    if preview_filename:
        preview_path = os.path.join(source_folder_path, preview_filename)
        if os.path.exists(preview_path):
            files_to_move.append(('preview', preview_path, preview_filename))

    # 3. Plik asset
    asset_filename = f"{asset_name}.asset"
    asset_path = os.path.join(source_folder_path, asset_filename)
    if os.path.exists(asset_path):
        files_to_move.append(('asset', asset_path, asset_filename))

    # 4. Plik thumbnail
    cache_folder = os.path.join(source_folder_path, ".cache")
    thumb_filename = f"{asset_name}.thumb"
    thumb_path = os.path.join(cache_folder, thumb_filename)
    if os.path.exists(thumb_path):
        files_to_move.append(('thumbnail', thumb_path, thumb_filename))

    # Przenieś wszystkie pliki
    for file_type, source_path, filename in files_to_move:
        shutil.move(source_path, target_path)
```

## Funkcjonalność wizualna

### Podświetlanie folderów

- **Normalny stan**: Przyciski folderów mają standardowy wygląd
- **Podczas drag**: Folder nad którym jest przeciągany asset zostaje podświetlony niebieskim kolorem
- **Po upuszczeniu**: Folder wraca do normalnego wyglądu

### Ikona drag

- Podczas przeciągania wyświetlana jest miniaturka asset-a jako ikona drag
- Ikona jest wyśrodkowana względem kursora myszy

## Bezpieczeństwo i walidacja

### Sprawdzanie plików

- Sprawdzanie czy wszystkie 4 pliki asset-a istnieją przed przeniesieniem
- Walidacja czy folder docelowy istnieje
- Sprawdzanie czy folder docelowy nie jest tym samym co źródłowy

### Obsługa błędów

- Logowanie wszystkich operacji przenoszenia
- Obsługa błędów przy przenoszeniu poszczególnych plików
- Kontynuacja przenoszenia nawet jeśli niektóre pliki się nie powiodły

### Odświeżanie galerii

- Automatyczne odświeżanie galerii po przeniesieniu asset-a
- Wywołanie `handle_folder_click` dla aktualnego folderu
- Aktualizacja wyświetlania miniaturek

## Użycie

1. **Rozpoczęcie drag**: Kliknij i przeciągnij kafelek asset-a w galerii
2. **Podświetlanie**: Przeciągaj nad folderami w drzewie - folder zostanie podświetlony
3. **Upuszczenie**: Upuść kafelek na wybrany folder
4. **Przeniesienie**: Wszystkie 4 pliki zostaną przeniesione do nowej lokalizacji
5. **Odświeżenie**: Galeria zostanie automatycznie odświeżona

## Kompatybilność

- Funkcjonalność działa z istniejącą logiką aplikacji
- Nie wpływa na inne funkcjonalności (kliknięcia, podgląd, otwieranie archiwów)
- Zachowuje wszystkie istniejące sygnały i sloty
