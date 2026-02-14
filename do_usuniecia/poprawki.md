# Raport analizy kodu @core - CFAB Browser

## Podsumowanie
Przeanalizowano ~40 plików w katalogu `core/`. Architektura MVC jest dobrze zorganizowana.
Poniżej szczegółowe uwagi podzielone na kategorie.

---

## 1. WYDAJNOSC (Performance)

### 1.1 [KRYTYCZNE] `AssetTileView` - tworzenie QPixmap w wątku roboczym
**Plik:** `core/workers/thumbnail_loader_worker.py:37`
```python
pixmap = QPixmap(self.path)  # QPixmap NIE jest thread-safe!
```
`QPixmap` nie powinien być tworzony poza głównym wątkiem GUI. Qt dokumentacja jawnie ostrzega, że `QPixmap` nie jest thread-safe. Należy używać `QImage` w workerze, a konwertować na `QPixmap` dopiero w slocie w głównym wątku.

**Poprawka:** Zmienić worker na ładowanie `QImage`, konwersja `QPixmap.fromImage()` w slocie `_on_thumbnail_loaded`.

---

### 1.2 [KRYTYCZNE] `ThumbnailCache._evict_oldest()` - ponowne obliczanie rozmiaru pixmapy
**Plik:** `core/thumbnail_cache.py:114`
```python
pixmap_size = oldest_pixmap.toImage().sizeInBytes()
```
Przy każdym wyrzuceniu z cache konwertujemy QPixmap → QImage tylko po to, by odczytać rozmiar. To kosztowna operacja. Rozmiar powinien być przechowywany razem z pixmapą w cache (jako tuple `(pixmap, size)`).

Analogicznie w `put()` linia 80: `pixmap.toImage().sizeInBytes()` jest wywoływane przy każdym dodaniu.

**Poprawka:** Przechowywać `self.cache[path] = (pixmap, pixmap_size)` zamiast samego pixmapa.

---

### 1.3 [SREDNIE] `AssetGridController._reorganize_layout()` - pętla czyszczenia layoutu
**Plik:** `core/amv_controllers/handlers/asset_grid_controller.py:236-239`
```python
while self.view.gallery_layout.count():
    item = self.view.gallery_layout.takeAt(0)
    if item.widget():
        item.widget().hide()
```
`takeAt(0)` w pętli ma złożoność O(n²) ponieważ Qt przesuwa elementy po każdym usunięciu. Lepiej usuwać od końca lub użyć `QWidget.setUpdatesEnabled(False)` przed operacją.

**Poprawka:** Wyłączyć updates przed czyszczeniem, czyścić od końca:
```python
self.view.gallery_content_widget.setUpdatesEnabled(False)
# ... operacje na layoucie
self.view.gallery_content_widget.setUpdatesEnabled(True)
```

---

### 1.4 [SREDNIE] `FolderClickRules._categorize_file()` - nieoptymalne sprawdzanie rozszerzeń
**Plik:** `core/rules.py:421-438`
```python
for ext in FolderClickRules.ASSET_EXTENSIONS:
    if item_lower.endswith(ext):
        return "asset"
```
Zamiast iterować po setach z `endswith()`, lepiej użyć `os.path.splitext()` + lookup w secie (O(1)):
```python
_, ext = os.path.splitext(item_lower)
if ext in ASSET_EXTENSIONS: return "asset"
if ext in ARCHIVE_EXTENSIONS: return "archive"
if ext in PREVIEW_EXTENSIONS: return "preview"
```

---

### 1.5 [SREDNIE] `AssetGridModel.scan_folder()` - tworzenie nowej instancji `AssetRepository` przy każdym skanie
**Plik:** `core/amv_models/asset_grid_model.py:87`
```python
asset_repository = AssetRepository()
```
Przy każdym kliknięciu folderu tworzona jest nowa instancja Rust backend. Lepiej trzymać jedną instancję jako pole klasy.

---

### 1.6 [NISKIE] `SelectionModel._emit_selection_changed()` - konwersja set→list przy każdej zmianie
**Plik:** `core/amv_models/selection_model.py:41`
```python
self.selection_changed.emit(list(self._selected_asset_ids))
```
Przy dużej liczbie zaznaczonych elementów i częstych zmianach (np. Select All) to tworzy wiele tymczasowych list. Rozważyć debouncing sygnału.

---

### 1.7 [NISKIE] `PerformanceMonitor.metrics_history` - brak limitu wzrostu
**Plik:** `core/performance_monitor.py:141-142`
```python
if len(self.metrics_history) > 1000:
    self.metrics_history = self.metrics_history[-1000:]
```
Tworzenie nowej listy przy każdym przekroczeniu. Lepiej użyć `collections.deque(maxlen=1000)`.

---

### 1.8 [NISKIE] `_position_control_panel()` - wielokrotne wywoływanie z timerów
**Plik:** `core/amv_views/amv_view.py:247, 326, 577, 588`
Ta metoda jest wywoływana z co najmniej 4 miejsc z QTimer.singleShot. Przy szybkim resizowaniu okna może to powodować wiele zbędnych obliczeń. Zastosować debouncing z jednym timerem.

---

## 2. BLEDY I POTENCJALNE PROBLEMY

### 2.1 [KRYTYCZNE] `pairing_tab._on_archive_clicked()` - brakujący import `subprocess`
**Plik:** `core/pairing_tab.py:271-279`
```python
elif sys.platform == "darwin":
    subprocess.run(["open", full_path], check=True, timeout=10)
```
Moduł `subprocess` nie jest importowany w `pairing_tab.py` (jest importowany w `file_utils.py` ale nie tutaj). Spowoduje `NameError` na macOS/Linux.

**Poprawka:** Dodać `import subprocess` na górze pliku LUB użyć istniejącej funkcji `open_file_in_default_app()` z `file_utils.py`.

---

### 2.2 [KRYTYCZNE] `ThreadManager.emergency_stop_all()` - brak blokady wątków
**Plik:** `core/thread_manager.py:238-255`
```python
def emergency_stop_all(self) -> None:
    for thread in self.active_threads:  # Brak self._lock!
```
Metoda `emergency_stop_all()` iteruje po `self.active_threads` i `self.thread_pools` bez `self._lock`, podczas gdy inne metody używają locka. Może prowadzić do race condition.

---

### 2.3 [SREDNIE] `ThumbnailCache.current_size_bytes` - potencjalnie ujemny rozmiar
**Plik:** `core/thumbnail_cache.py:115`
```python
self.current_size_bytes -= pixmap_size
```
Jeśli pixmap został zmodyfikowany lub zwolniony między `put()` a `_evict_oldest()`, rozmiar może nie odpowiadać. Brak zabezpieczenia przed ujemną wartością:
```python
self.current_size_bytes = max(0, self.current_size_bytes - pixmap_size)
```

---

### 2.4 [SREDNIE] `AssetTileView._on_checkbox_state_changed()` - traversal hierarchii widgetów
**Plik:** `core/amv_views/asset_tile_view.py:636-650`
```python
widget = self
while widget and widget.parent():
    widget = widget.parent()
    if hasattr(widget, "update_selection_status"):
        main_window = widget
        break
```
Ten kod chodzi po drzewie widgetów w górę przy KAŻDEJ zmianie checkboxa. Jest to zbyteczne, ponieważ sygnał `checkbox_state_changed` jest już podłączony do `control_panel_controller.update_button_states()`, a `SelectionModel.selection_changed` jest podłączony do `MainWindow._on_selection_changed()`. Ten traversal duplikuje logikę i może prowadzić do podwójnych aktualizacji.

**Poprawka:** Usunąć blok traversal - istniejące sygnały już obsługują aktualizację status bara.

---

### 2.5 [SREDNIE] `FolderClickRules._validate_folder_path()` - wadliwa walidacja path traversal
**Plik:** `core/rules.py:343`
```python
if ".." in folder_path or "\\.." in folder_path or "/.." in folder_path:
```
Sprawdzenie `".." in folder_path` da false positive dla ścieżek z `..` w nazwie pliku (np. `C:\folder\file..name`). Lepiej użyć `os.path.normpath()` i porównać wynik z oczekiwanym rootem.

---

### 2.6 [SREDNIE] `FolderClickRules._folder_analysis_cache` - class-level mutable dict
**Plik:** `core/rules.py:322-323`
```python
_folder_analysis_cache: Dict[str, Dict] = {}
_cache_timestamps: Dict[str, float] = {}
```
Słowniki class-level (nie instance-level) mogą rosnąć bez ograniczeń. Brak mechanizmu czyszczenia starych wpisów. Przy długotrwałym użytkowaniu aplikacji może to prowadzić do wycieku pamięci.

**Poprawka:** Dodać `max_cache_size` i czyścić najstarsze wpisy, lub wyczyścić cache przy zmianie workspace.

---

### 2.7 [SREDNIE] `PreviewWindow.thread_pool` - nieużywany ThreadManager
**Plik:** `core/preview_window.py:86`
```python
self.thread_pool = QThreadPool()
```
Każda instancja `PreviewWindow` tworzy własny `QThreadPool`. Te poole nie są rejestrowane w centralnym `ThreadManager`, więc nie zostaną poprawnie zatrzymane przy zamykaniu aplikacji.

---

### 2.8 [NISKIE] `AssetTileView.thread_pool` - globalny class-level QThreadPool
**Plik:** `core/amv_views/asset_tile_view.py:40`
```python
thread_pool = QThreadPool()
```
Globalny `QThreadPool` na poziomie klasy nie jest zarządzany przez `ThreadManager`. Przy zamykaniu aplikacji workery w tym poolu mogą nie zostać zatrzymane.

---

### 2.9 [NISKIE] `ToolsTab.closeEvent()` - `file_shortener` nie jest w liście workerów
**Plik:** `core/tools_tab.py:462`
W `__init__` brak `self.file_shortener = None`, ale w `_start_file_shortening()` jest `self.file_shortener = FileShortenerWorker(...)`. W `closeEvent()` jest sprawdzenie `hasattr(self, "file_shortener")` ale nie ma go w inicjalizacji pola.

---

### 2.10 [NISKIE] `json_utils.dumps()` - niespójny typ zwracany
**Plik:** `core/json_utils.py:56-64`
Gdy `HAS_ORJSON=True`, `dumps()` zwraca `bytes`. Gdy `False`, zwraca `str`. Wywołujący muszą obsługiwać oba typy, co jest podatne na błędy.

---

## 3. LOGIKA I ARCHITEKTURA

### 3.1 [SREDNIE] Duplikacja kodu otwierania plików
**Pliki:** `core/pairing_tab.py:267-279`, `core/tools_tab.py:527-533`
Kod otwierania plików w domyślnej aplikacji (`os.startfile` / `subprocess.run`) jest zduplikowany w:
- `pairing_tab._on_archive_clicked()`
- `tools_tab._on_archive_double_clicked()`
- `tools_tab._on_preview_double_clicked()`

Istnieje gotowa funkcja `open_file_in_default_app()` w `file_utils.py`.

**Poprawka:** Zamienić zduplikowany kod na wywołania `open_file_in_default_app()`.

---

### 3.2 [SREDNIE] `_show_pairs_dialog` i `_show_pairs_dialog_shortener` - niemal identyczne
**Plik:** `core/tools_tab.py:781-885`
Te dwa dialogi różnią się tylko tytułem i workerem (`file_renamer` vs `file_shortener`). Powinny być zunifikowane w jedną parametryzowaną metodę.

---

### 3.3 [SREDNIE] `ToolsTab._on_find_duplicates_clicked()` - podwójne potwierdzenie
**Plik:** `core/tools_tab.py:758-779`
Metoda najpierw wyświetla `QMessageBox.question`, a potem wywołuje `_start_operation_with_confirmation`, który wyświetla KOLEJNY `QMessageBox.question`. Użytkownik musi potwierdzić dwa razy.

**Poprawka:** Usunąć pierwszy dialog lub zmienić na bezpośrednie tworzenie workera bez `_start_operation_with_confirmation`.

---

### 3.4 [SREDNIE] `MainWindow._createStatusBar()` - martwy kod
**Plik:** `core/main_window.py:201-248`
Metoda `_createStatusBar()` jest zdefiniowana ale nigdy nie wywoływana - StatusBarManager obsługuje tworzenie status bara w `__init__`. Metoda tworzy duplikatowe pola (`self.status_progress_bar`, `self.selected_label`) które mogą kolidować z polami z `StatusBarManager`.

**Poprawka:** Usunąć `_createStatusBar()`.

---

### 3.5 [NISKIE] `scanner.py:97-108` - placeholder metoda `create_thumbnail_for_asset`
```python
def create_thumbnail_for_asset(self, asset_file_path, preview_path):
    # This would need to be implemented in Rust backend
    # For now, return True as placeholder
    return True
```
Metoda zawsze zwraca `True` niezależnie od tego czy thumbnail został faktycznie utworzony.

---

### 3.6 [NISKIE] `AmvView._create_scroll_area()` - monkey-patching resizeEvent
**Plik:** `core/amv_views/amv_view.py:328-333`
```python
original_resize = self.scroll_area.resizeEvent
def new_resize_event(event):
    original_resize(event)
    on_scroll_area_resize()
self.scroll_area.resizeEvent = new_resize_event
```
Monkey-patching `resizeEvent` jest kruche. Lepiej stworzyć podklasę `QScrollArea` z nadpisanym `resizeEvent` lub użyć event filtra.

---

### 3.7 [NISKIE] `AssetTileView.update_thumbnail_size()` - niespójne wymiary kafelka
**Plik:** `core/amv_views/asset_tile_view.py:574-581`
```python
tile_width = new_size + (2 * self.MARGINS_SIZE)  # new_size + 16
tile_height = new_size + 70
```
Ale w `_calculate_tile_dimensions()` (linia 178-181):
```python
filename_width = 60 + 136 + 60  # 256px
tile_width = max(self.thumbnail_size, filename_width)
tile_height = self.thumbnail_size + 60 + (2 * tile_padding) + (2 * tile_border)
```
Logika obliczania wymiarów jest niespójna między tymi dwiema metodami. `update_thumbnail_size()` nie uwzględnia `filename_width`, `tile_padding` i `tile_border`.

**Poprawka:** Zunifikować logikę obliczeń wymiarów w jednej metodzie.

---

## 4. THREAD SAFETY

### 4.1 [KRYTYCZNE] `WorkerManager.handle_progress()` - warunek wątku
**Plik:** `core/workers/worker_manager.py:30-40`
Metoda próbuje wykryć czy jest w GUI wątku, ale `QMetaObject.invokeMethod` z lambdą nie jest poprawnym wzorcem w PyQt6. Może prowadzić do crash'y.

**Poprawka:** Użyć `QMetaObject.invokeMethod` z `Q_ARG` lub lepiej - podłączyć sygnał `progress_updated` z `Qt.ConnectionType.QueuedConnection`.

---

### 4.2 [SREDNIE] `ToolsTab._update_preview_list()` - `terminate()` na workerze
**Plik:** `core/tools_tab.py:293`
```python
self.resolution_loader.terminate()
```
`QThread.terminate()` jest niebezpieczne i może prowadzić do uszkodzenia pamięci. Lepiej użyć flagi stopu.

---

### 4.3 [SREDNIE] `ToolsTab._on_resolution_loaded()` - liniowe wyszukiwanie w liście
**Plik:** `core/tools_tab.py:326-333`
```python
for i in range(self.preview_list.count()):
    item = self.preview_list.item(i)
    ...
```
Przy wielu plikach preview, każde załadowanie rozdzielczości wymaga przejścia całej listy. Lepiej użyć słownika `file_name → QListWidgetItem`.

---

## 5. POPRAWKI KOSMETYCZNE I CZYSZCZENIE

### 5.1 `utilities.py` - nadmiarowe puste linie
**Plik:** `core/utilities.py:30-33` - 4 puste linie między funkcjami (konwencja PEP8: 2).

### 5.2 `main_window.py` - komentarze w różnych językach
Mieszanka komentarzy po polsku i angielsku (np. linia 618: "NOWE METODY POMOCNICZE - REFAKTORYZACJA"). Ustandaryzować do angielskiego.

### 5.3 `pairing_tab.py:104-105` - `print()` zamiast `logger`
```python
print(f"PairingTab: Received new working directory: {path}")
```
Używany `print()` zamiast loggera w wielu miejscach w `pairing_tab.py` (linie 104, 258, 288, 304, 346, 355, 366).

### 5.4 `tools_tab.py:3` - podwójny import `sys`
```python
import sys  # linia 4
# ... i później:
if __name__ == "__main__":
    import sys  # linia 896
```

### 5.5 `file_utils.py` - identyczne metody open_path/open_file
`_open_path_macos()` i `_open_file_macos()` mają identyczną implementację. Podobnie Linux. Można zunifikować.

### 5.6 `main_window.py:795-797` - puste linie na końcu pliku
Trzy puste linie przed `if __name__`.

---

## 6. PRIORYTET NAPRAW

| Priorytet | Opis | Plik |
|-----------|------|------|
| P0 | QPixmap w wątku roboczym | thumbnail_loader_worker.py |
| P0 | Brakujący import subprocess | pairing_tab.py |
| P0 | WorkerManager.handle_progress thread safety | worker_manager.py |
| P1 | ThumbnailCache - przechowywanie rozmiaru | thumbnail_cache.py |
| P1 | Duplikacja kodu otwierania plików | pairing_tab.py, tools_tab.py |
| P1 | Podwójne potwierdzenie w find duplicates | tools_tab.py |
| P1 | Traversal hierarchii w checkbox handler | asset_tile_view.py |
| P1 | Niespójne wymiary kafelka | asset_tile_view.py |
| P1 | Martwy kod _createStatusBar | main_window.py |
| P2 | O(n²) czyszczenie layoutu | asset_grid_controller.py |
| P2 | Optymalizacja _categorize_file | rules.py |
| P2 | Zunifikowanie dialogów par | tools_tab.py |
| P2 | ThreadManager.emergency_stop_all lock | thread_manager.py |
| P2 | ThumbnailCache ujemny rozmiar | thumbnail_cache.py |
| P2 | Niezarządzane QThreadPool | preview_window.py, asset_tile_view.py |
| P3 | FolderClickRules cache bez limitu | rules.py |
| P3 | PerformanceMonitor deque | performance_monitor.py |
| P3 | print() zamiast logger | pairing_tab.py |
| P3 | Monkey-patching resizeEvent | amv_view.py |
| P3 | json_utils niespójny typ zwracany | json_utils.py |

---

## 7. PODSUMOWANIE OGÓLNE

**Mocne strony:**
- Dobrze zorganizowana architektura MVC z dependency injection
- Object Pooling dla AssetTileView (optymalizacja tworzenia widgetów)
- Centralizowany ThreadManager do zarządzania wątkami
- Debouncing na obliczeniach kolumn i rebuild'ach gridu
- Rust backend dla operacji I/O intensywnych (skanowanie, hashowanie)
- LRU cache dla miniaturek z limitem pamięci

**Główne ryzyka:**
- Thread safety przy operacjach na QPixmap (potencjalne crash'e)
- Brakujące importy mogące powodować NameError na nie-Windows platformach
- Wycieki pamięci z nieograniczonymi cache'ami class-level
- Duplikacja kodu zwiększająca koszt utrzymania

---

## 8. WPROWADZONE POPRAWKI (2025-02-14)

### P0 – Krytyczne
| # | Poprawka | Plik | Status |
|---|----------|------|--------|
| 1.1 | QPixmap → QImage w workerze, konwersja w slocie GUI | thumbnail_loader_worker.py, asset_tile_view.py | ✅ |
| 2.1 | Użycie `open_file_in_default_app()` zamiast subprocess | pairing_tab.py | ✅ |
| 4.1 | QueuedConnection dla `progress_updated` | worker_manager.py | ✅ |

### P1 – Wysokie
| # | Poprawka | Plik | Status |
|---|----------|------|--------|
| 1.2 | Cache przechowuje `(pixmap, size)`, zabezpieczenie ujemnego rozmiaru | thumbnail_cache.py | ✅ |
| 3.1 | Zastąpienie duplikatu kodu `open_file_in_default_app()` | pairing_tab.py, tools_tab.py | ✅ |
| 3.3 | Usunięcie podwójnego potwierdzenia w Find Duplicates | tools_tab.py | ✅ |
| 2.4 | Usunięcie traversal hierarchii w checkbox handler | asset_tile_view.py | ✅ |
| 3.7 | Zunifikowanie wymiarów kafelka w `_calculate_tile_dimensions()` | asset_tile_view.py | ✅ |
| 3.4 | Usunięcie martwego kodu `_createStatusBar()` | main_window.py | ✅ |

### P2 – Średnie
| # | Poprawka | Plik | Status |
|---|----------|------|--------|
| 1.3 | `setUpdatesEnabled(False/True)` przy czyszczeniu layoutu | asset_grid_controller.py | ✅ |
| 1.4 | Optymalizacja `_categorize_file` – splitext + lookup O(1) | rules.py | ✅ |
| 2.2 | Lock w `emergency_stop_all()` | thread_manager.py | ✅ |
| 2.3 | Zabezpieczenie przed ujemnym `current_size_bytes` | thumbnail_cache.py | ✅ |
| 2.5 | Poprawiona walidacja path traversal (segment `..`) | rules.py | ✅ |

### P3 – Niskie
| # | Poprawka | Plik | Status |
|---|----------|------|--------|
| 1.7 | `deque(maxlen=1000)` zamiast listy | performance_monitor.py | ✅ |
| 2.6 | `MAX_CACHE_SIZE` i eviction w FolderClickRules | rules.py | ✅ |
| 5.3 | `print()` → `logger` | pairing_tab.py | ✅ |
| 5.1 | Nadmiarowe puste linie | utilities.py | ✅ |
| 5.4 | Usunięcie podwójnego importu `sys` | tools_tab.py | ✅ |
| - | Usunięcie nieużywanego importu `subprocess` | tools_tab.py | ✅ |
| - | Usunięcie nieużywanego importu `sys` | pairing_tab.py | ✅ |

### Nie wdrożone (wymagają szerszej refaktoryzacji)
- 3.2: Zunifikowanie `_show_pairs_dialog` i `_show_pairs_dialog_shortener`
- 2.7, 2.8: Rejestracja QThreadPool w ThreadManager
- 3.6: Monkey-patching resizeEvent w amv_view
- 2.10: Niespójny typ zwracany w json_utils.dumps()
