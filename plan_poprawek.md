# Plan Poprawek — CFAB Browser

**Data:** 2026-04-18
**Zakres audytu:** `core/` (~10 800 LOC Python/PyQt6), `scanner_rust/` (~1 800 LOC Rust, 3 crate'y PyO3), pliki legacy (`do_usuniecia/`, artefakty budowania).
**Status aplikacji:** działa prawidłowo — plan dotyczy wyłącznie poprawek, optymalizacji, usunięcia martwego kodu i redundancji. Żadna zmiana nie została wykonana; dokument jest propozycją do zatwierdzenia.

Legenda priorytetów:
- **P0 — Krytyczny:** błąd poprawnościowy, wyciek zasobów, ryzyko utraty danych lub UB.
- **P1 — Ważny:** dead code, istotny zysk wydajności, redundancja architektoniczna.
- **P2 — Drobny:** kosmetyka, małe optymalizacje, spójność stylistyczna.

---

## 1. Krytyczne (P0) — Python

### 1.1. `core/json_utils.py:102` — `NameError` gdy orjson jest zainstalowany
Klauzula `except json.JSONDecodeError` odwołuje się do modułu `json`, który jest importowany wyłącznie w gałęzi `except ImportError` w fallbacku orjson. Przy `HAS_ORJSON=True` pierwszy uszkodzony plik `.asset` wywołuje `NameError` zamiast przejść przez normalny handler.
**Impact:** pojedynczy uszkodzony plik przerywa cały skan biblioteki.
**Fix:** przenieść `import json` na poziom modułu (orjson i stdlib `json` mogą współistnieć) lub przechwytywać `(ValueError, Exception)` z rozgałęzieniem po backendzie.

### 1.2. [core/amv_models/workspace_folders_model.py:215](core/amv_models/workspace_folders_model.py#L215) — wywołanie nieistniejącej metody `ConfigManagerMV.save_config`
`add_folder`, `remove_folder`, `update_folder` wywołują `self._config_manager.save_config(config)`. Metoda nie istnieje (zweryfikowane grep'em); wywołanie rzuca `AttributeError`, który jest połykany przez szerokie `except`.
**Impact:** CRUD folderów workspace wygląda na działający w pamięci, ale nie persystuje na dysk. Restart wymazuje zmiany, a `bare except` tłumi wszelkie sygnały.
**Fix:** zaimplementować `ConfigManagerMV.save_config` delegujący do właściwego writer'a lub użyć istniejącego API (`set()` / `save()`). Zwęzić `except` do konkretnych wyjątków z `log.error(..., exc_info=True)`.

### 1.3. [core/amv_models/file_operations_model.py:199](core/amv_models/file_operations_model.py#L199) — nieosiągalna gałąź detekcji duplikatów
`_handle_post_move` sprawdza `os.path.exists(source_asset)` **po** `shutil.move`. Źródło już nie istnieje — warunek zawsze `False`, ścieżka "mark as duplicate" to dead code.
**Impact:** semantyka "oznacz zamiast nadpisać" jest utracona; `shutil.move` rzuca surowy wyjątek przy kolizji zamiast wejść w ścieżkę duplikatu.
**Fix:** sprawdzać `os.path.exists(destination_asset)` **przed** `shutil.move`. Rozgałęziać: jeśli destynacja istnieje → duplikat, jeśli nie → przenieść.

### 1.4. `core/amv_models/file_operations_model.py::_move_files` — brak rollback'u przy częściowej porażce
Pętla `shutil.move` jeden po drugim; porażka N-tego ruchu pozostawia 0..N-1 w destynacji a N..K w źródle. Brak kompensacji.
**Impact:** przerwanie w połowie (uprawnienia, brak miejsca, kill) dzieli asset na dwa foldery. Kolejny skan traktuje każdą połówkę jako osobny asset.
**Fix:** zbierać `moved` listę, w `except` odwrócić operacje. Pre-walidacja (wolne miejsce, istniejące destynacje). Emitować `partial_failure` z podziałem na success/fail dla UI.

### 1.5. `core/amv_controllers/handlers/folder_tree_controller.py::_scan_folder_safely` — throttling no-op, rescan aktywnego folderu zablokowany
`_scanning_in_progress` ustawiany synchroniczne True→False w tym samym wywołaniu — gate nigdy nie blokuje concurrent callerów. Osobno `if not force_rescan and self._last_scanned_folder == folder_path: return` blokuje refresh aktywnego folderu, co większość ścieżek sygnałowych nie omija.
**Impact:** użytkownik nie może re-skanować aktywnego folderu normalnymi eventami; zewnętrzne zmiany FS są niewidoczne do momentu przełączenia folderu i powrotu.
**Fix:** usunąć same-folder short-circuit lub ograniczyć do okna czasowego (np. `< 500 ms`). Dla prawdziwego in-flight guard przenieść skan na worker thread i dopiero tam używać `_scanning_in_progress`.

### 1.6. [core/workers/worker_manager.py:89](core/workers/worker_manager.py#L89) — sygnały `finished`/`error_occurred` bez `Qt.QueuedConnection`
Tylko `progress_updated` używa explicit `QueuedConnection`. Pozostałe połączenia to default (auto). Dla `QRunnable` z `QObject` na wątku workera lambda wywołująca `QMessageBox` może wykonać się off-thread.
**Impact:** UB w Qt; crashe trudne do reprodukcji, zwłaszcza na Windows.
**Fix:** wszystkie trzy connecty z `Qt.ConnectionType.QueuedConnection`. Lepiej: `handle_finished`/`handle_error` emitują czyste sygnały, a UI-slot'y są podłączone raz, w konstruktorze kontrolera, z Queued.

---

## 2. Krytyczne (P0) — Rust

### 2.1. `scanner_rust/crates/scanner/src/scanner.rs:107-358` — scanner trzyma GIL przez całe rayon parallel work
`find_and_create_assets`, `load_existing_assets`, `scan_folder_for_files`, `create_single_asset` przyjmują `py: Python`, ale **nie wołają** `py.detach(...)` / `py.allow_threads(...)`. Cała praca (`scan_and_group_files`, `par_iter().filter_map(...)` z dekodowaniem+kodowaniem WebP, całe I/O) wykonuje się z GIL'em. Wątki Pythona są zablokowane na czas skanu. `image_tools` i `hash_utils` robią to poprawnie.
**Impact:** największy powód zawieszenia GUI podczas skanu dużych bibliotek.
**Fix:** owinąć ciała funkcji `#[pymethods]` w `py.detach(|| { ... })` (wzór z `image_tools::resize_image`). Konwersję `asset_to_pydict` i progress callback zostawić w GIL — reszta pracuje na wątkach.

### 2.2. `scanner_rust/crates/scanner/src/scanner.rs:394-398` — destruktywny write-probe przy każdym skanie
```rust
let test_path = folder_path.join(".write_test");
if let Err(e) = std::fs::write(&test_path, "") { ... }
let _ = std::fs::remove_file(test_path);
```
**Impact:** TOCTOU przy współbieżnych skanach tego samego folderu, stray `.write_test` jeśli proces zabity, zużycie write-budgetu SSD.
**Fix:** usunąć probe. `std::fs::write(&json_path, ...)` na linii 467 zwróci realny błąd — propagować przez `?`. Ewentualnie `std::fs::metadata(folder_path)?.permissions().readonly()` bez side-effectów.

### 2.3. `scanner_rust/crates/scanner/src/scanner.rs:381-454` — `create_unpaired_files_json` podwójnie skanuje katalog i ignoruje przekazane mapy
Funkcja przyjmuje `_archive_by_name` i `_image_by_name` (już zeskanowane) i natychmiast je wyrzuca (`_`-prefix). Potem dwukrotnie `std::fs::read_dir(folder_path)` (linie 409 i 424), filtruje po rozszerzeniach, lowercase'uje każdy stem.
**Impact:** dla biblioteki ~10 000 plików → dwa pełne przejścia dirent + ~20 000 lowercasingów na skan. Dodatkowo hardcoded lista rozszerzeń (`["zip","rar","7z","sbsar","spsm"]`, `["png","jpg","jpeg","webp"]`) desynchronizuje się z `FileExtensions::default()`.
**Fix:** użyć przekazanych map:
```rust
for (name, path) in _archive_by_name {
    if !common_names.contains(name) {
        unpaired_files.archives.push(path.file_name().unwrap().to_string_lossy().into_owned());
    }
}
```
Usunąć `_` prefix. Jeden syscall batch zamiast dwóch.

### 2.4. `scanner_rust/crates/scanner/src/scanner.rs:441,451` — `println!` w release library code
Niewyłączalne `println!("[UNPAIRED ARCHIVE] ...")` na każdy unpaired entry. Tysiące linii na stdout podczas skanu.
**Fix:** `log::debug!` lub usunąć.

### 2.5. `scanner_rust/crates/scanner/src/scanner.rs:49-104` — `ScannerCache` jest kłamstwem API
`SCANNER_CACHE: Lazy<Mutex<ScannerCache>>` + `reset_scanner_cache` — ale **nigdzie** nie zapisuje/odczytuje `cache.archive_files`/`cache.image_files`/`cache.last_scan_path`. `use_cache` jest `#[allow(dead_code)]`. Globalna alokacja HashMap'ów, których nikt nie używa; `reset_cache` z Pythona to no-op.
**Fix:** decyzja binarna —
- **(A) Wire in:** populować cache w `scan_and_group_files` po kluczu `last_scan_path` + mtime folderu, short-circuit przy powtórnym wywołaniu.
- **(B) Delete:** usunąć `ScannerCache`, `SCANNER_CACHE`, `reset_scanner_cache`, `new_without_cache`, `use_cache`. Prostsze i zgodne z rzeczywistością.

---

## 3. Ważne (P1) — Wydajność i architektura

### 3.1. Python — `_force_rebuild_requested` czyszczony przed throttled rebuild
`asset_grid_controller.on_assets_changed` ustawia `_force_rebuild_requested=False` zaraz po planowaniu `_rebuild_asset_grid_immediate` przez throttle timer. Gdy timer odpala, flaga już wyczyszczona → force-rebuild degraduje się do normalnego.
**Fix:** przesunąć reset na koniec `_rebuild_asset_grid_immediate` po skonsumowaniu, albo zamknąć flagę w local-scope przy planowaniu i przekazać do slotu.

### 3.2. Python — `clear_asset_tiles` zwalnia do puli tylko widoczne kafelki
Gate `if tile.isVisible()`. Kafelki nigdy niewidoczne (off-viewport, świeżo utworzone) są porzucane zamiast zwracane do `AssetTilePool`.
**Impact:** przecieki QObject akumulowane przez sesję.
**Fix:** usunąć `isVisible()` — zwalniać wszystkie posiadane kafelki.

### 3.3. Python — `folder_system_model._load_subfolders` rekurencyjny na main thread
Cały tree deskansiony synchronicznie podczas populacji modelu. Dla głębokich workspace'ów → zawieszenie GUI, "Not Responding" na Windows.
**Fix:** lazy expansion (`hasChildren`/`fetchMore` wzorem `QFileSystemModel`) lub worker thread streamujący przez sygnały.

### 3.4. Python — `AssetTilePool` bez limitu wielkości
Każde przełączenie folderu może doepchnąć kafelki; nic nie trim'uje.
**Fix:** parametr `max_size` (np. 2× typowa pojemność viewport'u). Przy over-limit `deleteLater()` nadmiarowych w `release`.

### 3.5. Python — thumbnail worker aplikuje wynik po ścieżce zamiast po `request_id`
`asset_tile_view._load_thumbnail_async` filtruje wyniki przez `if path == self.model.get_thumbnail_path()`. Kafelek może być re-pooled do innego assetu z tą samą ścieżką (placeholder.png), a spóźnione wyniki nadpisują świeższe.
**Fix:** monotoniczny `request_id` per kafelek, store'owany jako "current"; ignore wyników o niepasującym id; rozłącz sygnał w `release()`.

### 3.6. Python — `performance_monitor._log_metrics` otwiera plik przy każdym wywołaniu
W hot paths (rebuild grid, thumbnail loads, scans) — wiele razy na sekundę. O(N) file-system ops.
**Fix:** single append-mode handle na cały lifetime monitora (close przy exicie) lub in-memory bufor flushowany `QTimer`.

### 3.7. Python — `thread_manager._validate_and_cleanup_registries` czyści rejestry bez sprawdzania `isRunning()`
Żywe referencje są zrzucane; Qt trzyma wątki przez parent/child graph, ale manager traci możliwość zatrzymania ich przy shutdown.
**Fix:** iterować rejestr, pomijać `isRunning()`, tylko finished usuwać. Przy shutdown: bounded `stop()` + `wait(timeout)` dla running.

### 3.8. Python — `resolution_loader_worker.stop()` woła `wait()` bez timeoutu
Przy wedged worker'ze GUI wisi w nieskończoność przy zamykaniu.
**Fix:** `self.wait(3000)` z logowaniem warning'u; flaga cancel polling'owana w pętli.

### 3.9. Rust — `opt-level = "z"` dla biblioteki przetwarzania obrazów
`scanner_rust/Cargo.toml:32`. `"z"` tłumi wektoryzację; `image`/`webp`/`sha2` mają tight pixel/byte loops.
**Impact:** 15-30% throughput loss na thumbnail generation.
**Fix:** `opt-level = 3` (zachować `lto=true`, `codegen-units=1`, `panic="abort"`, `strip=true`). Opcjonalny osobny profil `release-small` dla edge case'ów.

### 3.10. Rust — `walkdir` zadeklarowany, nigdzie nieużywany
`Cargo.toml:15`, `crates/scanner/Cargo.toml`. `grep` nie znajduje `walkdir::` — scanner używa `std::fs::read_dir` (płaskie, nie rekursywne). Ciąga `walkdir` + `same-file` do grafu zależności bez powodu.
**Fix:** usunąć z workspace deps i z `scanner/Cargo.toml`. Alternatywa (zmiana behawioru): realne rekursywne skanowanie przez `WalkDir + par_bridge + filter_entry`.

### 3.11. Rust — trzy zduplikowane `build_info.rs` (po jednym na crate)
`crates/scanner/src/build_info.rs`, `crates/image_tools/src/build_info.rs`, `crates/hash_utils/src/build_info.rs` — po 68 LOC, identyczne poza `module_number` (1/2/3) i nazwą. `vergen` dep setup trzykrotnie; zmiana formatu log-prefix'u → trzy miejsca.
**Fix:** nowy crate `crates/build_info_common` jako `rlib` eksportujący makro `build_info!(module_number, module_name)`. Każdy cdylib woła raz. Redukcja ~150 LOC.

### 3.12. Rust — `image_tools/src/config.rs` to dead code
44 LOC, nawet niezadeklarowane `mod config;` w `lib.rs`. `ImageToolsConfig`, `get_config`, `try_set_config` nieosiągalne. `generate_thumbnail` hardcode'uje `.cache`, `256`, quality `75`/`80`.
**Fix:** albo usunąć plik, albo wpiąć (`use crate::config::get_config;` w `lib.rs` + zastąpić hardcoded literals).

### 3.13. Rust — pipeline thumbnail zduplikowany w ~90%
`crates/scanner/src/thumbnail.rs:147-213` vs `crates/image_tools/src/lib.rs:156-283`: identyczny format allow-list, `resize_to_square`, `has_alpha`, dwuścieżkowy WebP encode, cache mtime check. Drift inevitable.
**Fix:** shared `crates/image_common` (rlib) konsumowany przez oba cdyliby. Łączy się z 3.11.

### 3.14. Rust — `resize_image` nadpisuje plik in-place bez ochrony atomowej
`image_tools/src/lib.rs:11-49`: `resized_img.save(&file_path)` — jeśli enkoder padnie w połowie, na dysku zostaje truncated file. Plus domyślne ustawienia kodera (JPEG quality 75 → generation loss na reruns, PNG uncompressed → ogromne pliki).
**Fix:** tmp-file w tym samym katalogu + fsync + `rename` (atomic replace). `JpegEncoder::new_with_quality` explicit. Rozważyć zwrot ścieżki webp do Pythona dla `unlink` oryginału.

### 3.15. Rust — kultowa paralelizacja w `validate_asset_inputs`
`crates/scanner/src/asset_builder.rs:142-148`: zagnieżdżone `rayon::join` dla **trzech** `Path::exists()` calli (~µs każdy). Koszt spawna rayon task'u o rzędy wielkości większy niż oszczędność.
**Fix:** sekwencyjnie. Oraz w `file_utils.rs::get_files_by_extensions` usunąć branch `> 1000` — dla pojedynczego katalogu `par_iter` to overhead.

### 3.16. Rust — `create_unpaired_files_json` + scan robią `read_dir` dwukrotnie na tym samym katalogu
`scanner.rs:365-368`: `rayon::join(|| read_dir_archives, || read_dir_images)` na tym samym folderze — thrashing na HDD, zbędne syscalls na SSD.
**Fix:** jeden `read_dir`, bucket po rozszerzeniu w jednym przebiegu.

---

## 4. Dead code / redundancje do usunięcia

### 4.1. `core/selection_counter.py` — zduplikowane z `SelectionModel`
`SelectionCounter.count_selected_assets` chodzi po widoku i liczy `tile.is_checked()`; `amv_models/selection_model.py` trzyma autorytatywny `selected_asset_ids`. Dwa źródła prawdy, możliwa desynchronizacja podczas animacji / throttled rebuild.
**Fix:** zastąpić `count_selected_assets` wywołaniem `len(selection_model.get_selected_asset_ids())` i usunąć [core/selection_counter.py](core/selection_counter.py).

### 4.2. `core/tools/file_renamer_worker.py` — nadpisane metody identyczne z `BaseNameWorker`
`_analyze_files`, `_rename_file` — byte-for-byte duplikaty base class. Plus reimport `secrets`/`string` wewnątrz `_generate_random_name` (już zaimportowane na górze).
**Fix:** usunąć override'y, polegać na dziedziczeniu; usunąć reimporty.

### 4.3. `core/scanner.py::create_thumbnail_for_asset` — placeholder zwracający `True`
Method zwraca `True` bez tworzenia miniatury. Callerzy branch'ujący po boolean'ie proceed jak po sukcesie.
**Fix:** albo zaimplementować przez `image_tools` backend, albo `raise NotImplementedError`. Nie wolno kłamać.

### 4.4. Rust — `ScannerError` enum × 2 (oba martwe)
`scanner.rs:10-30` (`#[allow(dead_code)]` na wariantach, z `thiserror`) i `types.rs:72-79` (druga kopia). Żaden call site nie konstruuje wariantów; crate używa `anyhow::Result` / `Box<dyn Error>` / `PyErr`.
**Fix:** usunąć oba enum'y, usunąć `thiserror` z deps scanner'a.

### 4.5. Rust — `ScannerConfig` w `types.rs:82-101`
Wszystkie pola `_`-prefixed i `#[allow(dead_code)]`. "Reserved for future use".
**Fix:** usunąć.

### 4.6. Rust — `with_extensions`, `create_empty_asset`, `ThumbnailGenerator::new` — `#[allow(dead_code)]`
`asset_builder.rs:28,108`, `thumbnail.rs:26`. Nieużywane konstruktory.
**Fix:** usunąć.

### 4.7. Rust — `once_cell::sync::Lazy` w `scanner.rs:47` vs `std::sync::OnceLock` używane w innych miejscach
Trzy z czterech statics używają `std::sync::OnceLock` (stable od 1.70). Tylko `SCANNER_CACHE` używa `once_cell::Lazy`.
**Fix:** zamienić na `static SCANNER_CACHE: OnceLock<Mutex<ScannerCache>> = OnceLock::new();` (lub usunąć w ramach punktu 2.5). Drop `once_cell` z workspace.

### 4.8. Rust — `log`/`env_logger` deklarowane ale użycie nierówne
Zadeklarowane w workspace; `hash_utils` nie używa wcale. Dwa `#[pymodule]` init'y wołają `env_logger::try_init()` — drugi silently fails (to-`try_` property). Tylko config pierwszego modułu wygrywa.
**Fix:** usunąć `log`+`env_logger` z `hash_utils`. Rozważyć routing do Pythonowego `logging` przez wspólny helper (GUI aplikacja — stderr i tak nie jest konsumowany).

---

## 5. Ważne (P1) — Architektura

### 5.1. `core/main_window.py` — god object (~756 LOC)
Vzierze signal wiring, menu construction, worker orchestration, status formatting. `working_directory_changed` podłączony dwukrotnie (w `_connect_amv_signals` i `_connect_tools_signals`). Mieszane komentarze PL/EN, emoji literals w `show_operation_status`.
**Impact:** trudny do review i unit testów, łatwe wprowadzenie double-handler bug'ów.
**Fix:** rozdzielić na `MainWindowView` (UI only) + `MainWindowController` (signal wiring). Skonsolidować połączenia w jednym miejscu. Ujednolicić język komentarzy. Stringi statusu do resource table.

### 5.2. [core/amv_views/folder_tree_view.py:73](core/amv_views/folder_tree_view.py#L73) — `currentChanged` podłączony dwukrotnie
`FolderTreeView.setModel` → `QTimer.singleShot(0, _connect_selection_model)` → connect. `FolderTreeController.setup` → drugi connect. Obie odpalają na każdy click.
**Fix:** kontroler jest właściwym ownerem sygnału; widok albo usuwa deferred connection, albo słot widoku jest pure-visual i gatowany sygnałem kontrolera.

### 5.3. Rust — progress callback wąski (~7 bucketów na tysiące assetów)
`scanner.rs:111-173`. Rayon workers nie mogą wziąć GIL, więc raportują tylko 0/20/25/80/95/97/100. UX: long stall 25% → 80%.
**Fix:** `AtomicUsize` inkrementowany przez rayon, osobny lekki wątek akwiruje GIL co ~500 ms i pushuje count do Pythona. Ewentualnie channel drain'owany z main-thread.

---

## 6. Drobne (P2) — Czytelność i mikro-optymalizacje

### 6.1. Rust — `crop_x = if new_width > size { 0 } else { 0 }` — tautologia
`thumbnail.rs:102-103` i `image_tools/lib.rs:240-241`. Obie gałęzie to `0`.
**Fix:** `let crop_x = 0u32; let crop_y = 0u32;` + komentarz "top-left crop". Alternatywnie center-crop: `(new_width.saturating_sub(size)) / 2`.

### 6.2. Rust — `get_file_size_mb` zaokrągla do 2 miejsc
`file_utils.rs:57-62`: `(size_mb * 100.0).round() / 100.0`. Lossy.
**Fix:** trzymać `size_bytes: u64` w `Asset`, formatować tylko na granicy Pythona.

### 6.3. Rust — `FileExtensions::default()` alokuje `HashSet<String>` per call
`types.rs:56-68`, używane w `asset_builder.rs:21`. Na każdą konstrukcję `AssetBuilder::new()` / `RustAssetRepository::new()`.
**Fix:** `&'static [&'static str]` albo `OnceLock<HashSet<String>>`.

### 6.4. Rust — hardcoded listy rozszerzeń w ≥3 miejscach
`types.rs:59-66` (źródło prawdy), `scanner.rs:407, 422`, `thumbnail.rs:160`. Drift przy dodaniu `.avif`.
**Fix:** jeden `FileExtensions::default()`, przekazywać w dół.

### 6.5. Rust — `asset_to_pydict` serializuje `asset.meta` jako string
`asset_builder.rs:194`: `py_dict.set_item("meta", asset.meta.to_string())?;` — `serde_json::Value` → string. Python musi robić `json.loads` zamiast dostawać dict.
**Fix:** `pythonize` crate lub manualny walk `Map<String, Value>` + `set_item`.

### 6.6. Rust — `hash_utils` używa 4 KB bufora
`hash_utils/src/lib.rs:17`. Dla GB-assetów zbyt mały; NVMe sweet spot to 64-256 KB.
**Fix:** `let mut buffer = [0u8; 64 * 1024];`.

### 6.7. Rust — `String` zamiast `PathBuf` na granicy PyO3
`scanner.rs:110,261,307,331-334`. Windows z legacy filenames może przekazać non-UTF-8.
**Fix:** zmienić sygnatury na `PathBuf`; PyO3 0.27 konwertuje `os.PathLike`/`str`/`bytes` z poprawnym encoding.

### 6.8. Rust — emoji w stderr (`🦀`)
`scanner.rs:192,199,283`, `lib.rs:25`, `image_tools/lib.rs:291`. Windows console w cp1250/cp852 → garbled output lub panic.
**Fix:** usunąć emoji albo `cfg(debug_assertions)`.

### 6.9. Rust — `has_transparency` niekompletny
`thumbnail.rs:34-43` vs `image_tools/lib.rs:65`. Dwie metody detekcji alpha w dwóch miejscach.
**Fix:** wszędzie `img.color().has_alpha()`.

### 6.10. Python — [core/rules.py](core/rules.py) `_folder_analysis_cache` O(N) eviction przez `min()`
Class-level cache (shared across instances). Na każdy insert past limit — liniowe przeszukanie.
**Fix:** `OrderedDict` w `__init__` + `popitem(last=False)` — O(1).

### 6.11. Python — [core/tools/webp_converter_worker.py:65](core/tools/webp_converter_worker.py#L65) skip-existing zostawia oryginał
Gdy `.webp` istnieje, worker pomija konwersję ale nie usuwa oryginału. Na reruns biblioteka rośnie duplikatami.
**Fix:** po weryfikacji non-empty+readable usunąć oryginał (lub do trash); konfigurowalne.

### 6.12. Python — [core/amv_models/asset_grid_model.py:127](core/amv_models/asset_grid_model.py#L127) `request_recalculate_columns` restartuje debounce przy identycznych wywołaniach
Podczas continuous resize kolumny nie ustalają się dopóki użytkownik nie zatrzyma myszy.
**Fix:** short-circuit przy identycznym width+thumbnail_size lub leading+trailing debounce.

---

## 7. Cleanup plików legacy

### 7.1. `do_usuniecia/` — do usunięcia w całości (~590 KB, 50+ plików)
Grep całego live codebase (`core/`, `scanner_rust/`, skrypty root) — **zero** żywych referencji. Jedyne wzmianki w `docs/DEVELOPER_GUIDE.md:3` i `docs/PROJECT_STRUCTURE.md:3` mówią "this folder is excluded, not production". Wszystkie wewnętrzne referencje są `do_usuniecia/*` → `do_usuniecia/*`.

Zawartość bezpieczna do usunięcia:
- `cleanup_final.py`, `cleanup_temp.py`, `cleanup_v2.py`, `force_cleanup.py`, `debug_import.py`, `quick_test.py`
- `__bandit_report.py`, `__radon_report.py`, `__vulture_report.py` (23-bajtowe stuby)
- `poprawki.md`, `raport.md`, `TODO.md`, `list.md`, `build_pyinstaller_upx_fix.md`, `README.txt`, `README_pyinstaller.txt`
- `__doc/` (templates, `_back/`, `_base/`, `mapa_kodu_dokumentacja/`, `szczegolowa_analiza_pliku/`)
- `__tools/` (standalone utilities: `add_texture.py`, `blend_move.py`, `compress_max.py`, `profile_analyzer.py` itd.)
- `__raports/vulture_report.md`

**Akcja:** `rm -rf do_usuniecia/`. Następnie usunąć dwie linie w `docs/DEVELOPER_GUIDE.md` i `docs/PROJECT_STRUCTURE.md`.

### 7.2. Artefakty budowania (~737 MB odzyskiwalnych)
- `_dist/` (118 MB) — PyInstaller output, regeneratable
- `build/` (11 MB) — PyInstaller scratch, regeneratable
- `scanner_rust/target/` (607 MB) — Cargo cache, regeneratable
- `logs/performance.log` (1.4 MB) — runtime artifact

**Akcja:** wyczyścić lokalnie; dodać do `.gitignore` jeśli brakuje (`logs/` nie jest w root `.gitignore`, tylko `*.log`).

### 7.3. `install_pyinstaller.bat` — auto-generowany
Tworzony przez `build_pyinstaller.py:551`. Bezpieczny do usunięcia — zostanie odtworzony.

### 7.4. `config.json` — runtime config zcommitowany z absolutnymi ścieżkami użytkownika
`Z:/3D_LIB`, `T:/_SBSAR_LIB`, `T:/___textures`. `.gitignore` wyklucza `local_config.json`, `user_settings.json` — ale nie `config.json`. Hardcoded w `CFAB_Browser.spec:8` jako PyInstaller data bundle.
**Fix:** rename zcommitowanej wersji do `config.example.json`, dodać `config.json` do `.gitignore`, `cfab_browser.py` robi copy-on-first-run jeśli lokalny nie istnieje.

### 7.5. Konsolidacja dokumentacji Rust
`scanner_rust/README.md`, `scanner_rust/QUICKSTART.md`, `scanner_rust/BUILD_INFO_README.md` — overlap.
**Fix:** merge w jeden `README.md`.

### 7.6. `.gitignore` — brakujące wpisy
- `logs/` (katalog, nie tylko `*.log`)
- `scanner_rust/target/` (potwierdzenie z root'a; `scanner_rust/.gitignore` istnieje)
- `config.json` (patrz 7.4)
- Legacy referencje do starej nazwy projektu `CFAB_3DHUB` — do usunięcia

---

## 8. Proponowana Cargo.toml po cleanup'ie

```toml
[profile.release]
lto = true
codegen-units = 1
panic = "abort"
opt-level = 3         # było "z" — zysk ~15-30% throughput, koszt ~1-2 MB .pyd
strip = true

[workspace.dependencies]
pyo3 = { version = "0.27", features = ["extension-module"] }
image = { version = "0.25", features = ["webp", "png", "jpeg"] }
sha2 = "0.10"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
rayon = "1.8"
anyhow = "1.0"
webp = "0.3"
# USUNIĘTE: walkdir (nieużywane, 3.10)
# USUNIĘTE: once_cell (zastąpione std::sync::OnceLock, 4.7)
# USUNIĘTE: thiserror (martwe enum'y, 4.4)
# log + env_logger: zostawić tylko jeśli logowanie realnie konsumowane; usunąć z hash_utils
```

Nowe crate'y:
- `crates/build_info_common` (rlib, makro — rozwiązuje 3.11)
- `crates/image_common` (rlib, ThumbnailGenerator — rozwiązuje 3.13)

---

## 9. Kolejność wdrażania (rekomendacja)

Podział na 4 iteracje, każda sensowna jako osobny PR.

### Iteracja 1 — Stabilność (P0, najwyższy ROI)
1. **1.1** `json_utils.py` — `import json` na module-level (trywialny, blokuje regresję produkcyjną).
2. **2.1** Rust scanner — `py.detach(...)` wokół ciał `#[pymethods]`. Największy UX win.
3. **2.2** Usunąć `.write_test` probe.
4. **2.4** Zamienić `println!` na `log::debug!`.
5. **1.2** `workspace_folders_model.py` — naprawić persistence `save_config`.
6. **1.3** `file_operations_model.py` — sprawdzanie destynacji przed `shutil.move`.
7. **1.6** Qt Queued connections w `worker_manager.py`.

**Efekt:** brak regresji krytycznych, skany nie blokują GUI, persistencja działa.

### Iteracja 2 — Wydajność (P1 perf)
1. **3.9** `opt-level = 3`.
2. **2.3** `create_unpaired_files_json` — użyć przekazanych map, jeden syscall.
3. **3.15**+**3.16** Usunąć cargo-cult `rayon::join`'y.
4. **3.6** `performance_monitor` — single file handle.
5. **3.3** `folder_system_model` — lazy expansion.
6. **3.14** `resize_image` — atomic write.
7. **6.6** `hash_utils` — buffer 64 KB.

**Efekt:** skan dużej biblioteki ~2× szybszy, lazy tree, brak truncated writes.

### Iteracja 3 — Dead code + architektura (P1 cleanup)
1. **7.1** Usunąć `do_usuniecia/`.
2. **4.1** Usunąć `selection_counter.py`.
3. **4.2** Deduplikacja `file_renamer_worker.py`.
4. **4.3** `create_thumbnail_for_asset` — implementować lub `NotImplementedError`.
5. **4.4-4.8** Rust dead code — `ScannerError` × 2, `ScannerConfig`, nieużywane konstruktory, `once_cell`, `log`+`env_logger` z `hash_utils`.
6. **2.5** Decyzja o `ScannerCache` — implementacja albo usunięcie (preferuje się usunięcie).
7. **3.11**+**3.13** Shared crate'y `build_info_common` i `image_common`.
8. **3.12** `image_tools/config.rs` — wpiąć albo usunąć.

**Efekt:** ~500+ LOC mniej w Ruście, spójne API z Pythonem, brak kłamstw w API.

### Iteracja 4 — Poprawki szczegółowe (P1 reszta + P2)
1. **1.4** `_move_files` — rollback.
2. **1.5** `folder_tree_controller` — rescan aktywnego folderu.
3. **3.1** `_force_rebuild_requested` — zachowanie przez throttle.
4. **3.2** `clear_asset_tiles` — release wszystkich kafelków.
5. **3.4** `AssetTilePool` — `max_size`.
6. **3.5** thumbnail worker — `request_id`.
7. **3.7**+**3.8** Thread lifecycle — bounded wait, guarded cleanup.
8. **5.1** Rozbić `main_window.py`.
9. **5.2** Pojedynczy connect `currentChanged`.
10. **5.3** Rust progress — `AtomicUsize` + lekki reporter.
11. Lista P2 (6.1-6.12) — batch.
12. **7.2-7.6** Cleanup legacy files, `.gitignore`, config.example.

---

## 10. Ryzyka i luki pokrycia testami

**Znane luki** (wskazane przez audyt Pythona):
- `json_utils` error paths z orjson zainstalowanym — brak testu złapałby 1.1 natychmiast.
- `WorkspaceFoldersModel.{add,remove,update}_folder` — brak persistence round-trip (złapałoby 1.2).
- `FileOperationsModel._handle_post_move` "destination exists" — brak testu (złapałoby 1.3).
- `FolderTreeController._scan_folder_safely` re-scan aktywnego folderu (1.5).
- Concurrency `ThreadManager._validate_and_cleanup_registries` + running workers (3.7).
- Thumbnail worker late-arrival / tile reuse (3.5).
- `AssetGridController` force-rebuild survives throttle (3.1).
- `SelectionCounter` vs `SelectionModel` — divergence regression (4.1 / 5.1).

**Rekomendacja:** każda iteracja dodaje testy dla łatanych defektów przed zmianą, nie po.

**Nieaudytowane obszary** (residual risk):
- Granica bezpieczeństwa PyO3 pod stresem (panic propagation, ownership zwracanych danych).
- Pełna analiza affinity `QObject`-derived `*Signals` holders (gdzie są konstruowane vs. gdzie emitują).
- File-system race conditions między scan/move/rebuild (prawdopodobne, niereprodukowane).
- Stress-test `thumbnail_cache` LRU przy heavy churn.

---

## 11. Podsumowanie ilościowe

- **Krytyczne defekty:** 11 (6 Python + 5 Rust).
- **Ważne P1:** 16 (perf + architektura).
- **P2 / drobne:** 12.
- **Dead code do usunięcia:** 8 jednostek (selection_counter.py, duplikaty w file_renamer, 2×ScannerError, ScannerConfig, 3 nieużywane konstruktory Rust, once_cell, env_logger w hash_utils, config.rs, ScannerCache jeśli decyzja B).
- **Legacy cleanup:** `do_usuniecia/` (590 KB, 50+ plików, 0 referencji), artefakty budowania (737 MB odzyskiwalnych), 3 zduplikowane `build_info.rs` (~150 LOC redukcji).
- **Oczekiwany zysk wydajności:** scan dużej biblioteki — szacunkowo 1.5-2× (kombinacja `py.detach`, single-scan unpaired, `opt-level=3`, buffer 64 KB, usunięcie cargo-cult parallelism).
- **Oczekiwana redukcja LOC:** ~500-700 LOC Rust + ~200-400 LOC Python.

---

**Status dokumentu:** propozycja do zatwierdzenia. Przed implementacją — przegląd z autorem, decyzja o zakresie każdej iteracji, oraz (opcjonalnie) utworzenie osobnego planu wdrożeniowego per iteracja zgodnie ze skill'em `writing-plans`.
