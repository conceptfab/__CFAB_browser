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

---

# Nowa funkcjonalność: Kafelki specjalnych folderów

## Opis funkcjonalności

Dodano możliwość wyświetlania specjalnych folderów (`tex`, `textures`, `maps`) na początku galerii jako dedykowane kafelki z ikoną folderu. Po kliknięciu w kafelek, folder otwiera się w eksploratorze systemu.

## Implementacja

### Plik: `core/thumbnail_tile.py`

**Dodana nowa klasa `FolderTile`:**

- **Specjalne stylowanie** - niebieska kolorystyka odróżniająca od zwykłych assetów
- **Ikona folderu** - ładuje ikonę z `core/resources/img/folder.png` lub używa emoji 📁 jako fallback
- **Sygnał `folder_clicked`** - emitowany przy kliknięciu, przekazuje ścieżkę do folderu
- **Metoda `update_thumbnail_size`** - obsługuje zmianę rozmiaru podobnie do zwykłych kafelków

**Kluczowe zmiany:**

```python
class FolderTile(QFrame):
    folder_clicked = pyqtSignal(str)  # Sygnał z ścieżką do folderu

    def __init__(self, thumbnail_size: int, folder_name: str, folder_path: str):
        # Stylowanie niebieskie odróżniające od assetów
        # Ładowanie ikony folderu
        # Setup layoutu z ikoną i nazwą

    def _load_folder_icon(self):
        # Ładuje folder.png z resources/img/
        # Fallback na emoji 📁

    def _on_folder_clicked(self, event):
        # Emituje sygnał folder_clicked z ścieżką
```

### Plik: `core/gallery_tab.py`

**Zmodyfikowana klasa `AssetScanner`:**

- **Metoda `_scan_special_folders`** - skanuje foldery `tex`, `textures`, `maps`
- **Struktura danych specjalnych folderów** - kompatybilna z istniejącym systemem assetów
- **Priorytet wyświetlania** - specjalne foldery dodawane na początek listy

**Zmodyfikowana klasa `GridManager`:**

- **Metoda `_create_folder_tile_safe`** - tworzy kafelki folderów z obsługą błędów
- **Metoda `_on_folder_tile_clicked`** - obsługuje kliknięcia w kafelki folderów
- **Wsparcie dla różnych systemów** - Windows (`os.startfile`), macOS (`open`), Linux (`xdg-open`)
- **Zmodyfikowana `_create_thumbnail_grid`** - rozpoznaje typ asset-a i tworzy odpowiedni kafelek

**Kluczowe zmiany:**

```python
# AssetScanner - skanowanie specjalnych folderów
def _scan_special_folders(self):
    special_folders = []
    special_folder_names = ["tex", "textures", "maps"]

    for folder_name in special_folder_names:
        folder_path = os.path.join(self.work_folder_path, folder_name)
        if os.path.isdir(folder_path):
            folder_data = {
                "type": "special_folder",
                "name": folder_name,
                "folder_path": folder_path,
                # ... inne pola kompatybilne z assetami
            }
            special_folders.append(folder_data)

# GridManager - tworzenie kafelków folderów
def _create_thumbnail_grid(self, assets, thumbnail_size):
    for i, asset in enumerate(assets):
        if asset.get("type") == "special_folder":
            tile = self._create_folder_tile_safe(asset, thumbnail_size)
        else:
            tile = self._create_asset_tile_safe(asset, i + 1, len(assets), thumbnail_size)

# Obsługa kliknięć w foldery
def _on_folder_tile_clicked(self, folder_path):
    if os.name == "nt":  # Windows
        os.startfile(folder_path)
    elif os.name == "posix":  # Linux/Mac
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", folder_path])
        else:  # Linux
            subprocess.run(["xdg-open", folder_path])
```

## Funkcjonalność wizualna

### Wyświetlanie specjalnych folderów

- **Pozycja** - specjalne foldery wyświetlane na początku galerii (przed assetami)
- **Stylowanie** - niebieska kolorystyka (#2D3E50, #34495E, #3498DB) odróżniająca od assetów
- **Ikona** - ikona folderu z pliku `folder.png` lub emoji 📁 jako fallback
- **Hover efekt** - podświetlenie na niebiesko przy najechaniu myszą

### Zachowanie kafelków

- **Rozmiar** - dopasowuje się do ustawionego rozmiaru thumbnail z dodatkowym miejscem na tekst
- **Layout** - ikona na górze, nazwa folderu poniżej, wycentrowane
- **Kliknięcie** - otwiera folder w eksploratorze systemu

## Logika skanowania

### Priorytet folderów

1. **Specjalne foldery** - skanowane jako pierwsze i dodawane na początek listy
2. **Zwykłe assety** - dodawane po specjalnych folderach
3. **Pusty folder** - jeśli brak assetów i specjalnych folderów, wyświetla komunikat

### Wykrywane foldery

- `tex` - folder z teksturami
- `textures` - alternatywna nazwa dla tekstur
- `maps` - folder z mapami/teksturami

### Struktura danych

```json
{
  "type": "special_folder",
  "name": "tex",
  "folder_path": "/path/to/tex",
  "size_mb": 0.0,
  "thumbnail": false,
  "archive": "",
  "preview": "",
  "stars": null
}
```

## Kompatybilność

- **Istniejące funkcjonalności** - nie wpływa na obsługę zwykłych assetów
- **Slider rozmiaru** - kafelki folderów reagują na zmianę rozmiaru thumbnail
- **Drag and drop** - foldery nie obsługują drag (nie są assetami)
- **System operacyjny** - działa na Windows, macOS i Linux

## Bezpieczeństwo

- **Walidacja ścieżek** - sprawdzanie czy folder istnieje przed otwarciem
- **Obsługa błędów** - logowanie błędów przy problemach z otwieraniem folderów
- **Fallback ikony** - graceful degradation przy problemach z ładowaniem ikony

## Użycie

1. **Wykrywanie** - aplikacja automatycznie wykrywa specjalne foldery w folderze roboczym
2. **Wyświetlanie** - kafelki folderów pojawiają się na początku galerii
3. **Kliknięcie** - kliknij kafelek aby otworzyć folder w eksploratorze
4. **Zmiana rozmiaru** - użyj suwaka rozmiaru thumbnail aby dostosować rozmiar kafelków

---

# Poprawki wyglądu UI

## Opis zmian

Poprawiono wygląd interfejsu użytkownika, usuwając jasne ramki wokół galerii oraz poprawiając widoczność progress bara i suwaka rozmiaru.

## Zmiany w `core/gallery_tab.py`

### Usunięcie ramek galerii

**Panel galerii:**

- Zmiana z `QFrame.Shape.Box` na `QFrame.Shape.NoFrame`
- Dodano ciemne tło `#1E1E1E` bez ramek
- Zredukowano spacing do 0

**Scroll area:**

- Usunięto ramkę (`QScrollArea.Shape.NoFrame`)
- Dodano stylowanie scrollbarów:
  - Ciemne tło `#2D2D30`
  - Zaokrąglone uchwyty `#424242`
  - Hover efekt `#535353`
  - Pressed efekt `#007ACC`

### Poprawa dolnego panelu kontrolnego

**Panel kontrolny:**

- Zwiększenie wysokości z 18px do 32px
- Większe marginesy (12px, 6px) i spacing (16px)
- Dodano etykiety "Postęp:" i "Rozmiar:" dla lepszej czytelności

### Poprawa progress bara

**Stylowanie:**

```css
QProgressBar {
  border: 1px solid #555555;
  background-color: #2d2d30;
  color: #ffffff;
  border-radius: 10px;
  font-size: 11px;
  font-weight: bold;
}
QProgressBar::chunk {
  background-color: qlineargradient(
    x1: 0,
    y1: 0,
    x2: 1,
    y2: 0,
    stop: 0 #007acc,
    stop: 1 #1c97ea
  );
  border-radius: 9px;
}
```

**Poprawki:**

- Większy kontrast (ciemniejsze tło, jaśniejszy tekst)
- Gradient na pasku postępu
- Zaokrąglone narożniki
- Pogrubiona czcionka

### Poprawa suwaka rozmiaru

**Stylowanie:**

```css
QSlider::groove:horizontal {
  border: 1px solid #555555;
  height: 10px;
  background: #2d2d30;
  border-radius: 5px;
}
QSlider::handle:horizontal {
  background: qlineargradient(...);
  border: 2px solid #ffffff;
  width: 18px;
  border-radius: 9px;
}
```

**Poprawki:**

- Większy i bardziej widoczny uchwyt (18px)
- Gradient na uchwycie
- Biała ramka dla kontrastu
- Różne kolory dla hover (#FFD700) i pressed (#FF6B6B)
- Grubszy track (10px)

### Scrollbary

**Stylowanie pionowych i poziomych:**

- Ciemne tło `#2D2D30`
- Zaokrąglone uchwyty `border-radius: 6px`
- Smooth hover efekty
- Usunięte strzałki (height/width: 0px)
- Marginesy 2px dla lepszego wyglądu

## Efekt wizualny

### Przed zmianami:

- Jasne ramki wokół galerii
- Słabo widoczny progress bar
- Mały, trudno chwytany suwak
- Brak etykiet kontrolek

### Po zmianach:

- Czysta galeria bez ramek
- Wyraźny progress bar z gradientem
- Duży, łatwy w użyciu suwak z gradientem
- Czytelne etykiety "Postęp:" i "Rozmiar:"
- Profesjonalne scrollbary

## Kompatybilność

- Wszystkie zmiany są tylko kosmetyczne
- Nie wpływają na funkcjonalność aplikacji
- Zachowana responsywność i interaktywność
- Poprawiony kontrast dla lepszej dostępności
