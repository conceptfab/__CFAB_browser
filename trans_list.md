File: core\amv_views\gallery_widgets.py

L46: # Rysuj tekst normalnie - niebieskie tło i tak będzie widoczne

core/amv_views/preview_gallery_view.py:21: self.\_current_preview_paths = [] # Aktualne ścieżki podglądów

core/main_window.py:262: "INFO": "ℹ️",

core/main_window.py:269: icon = level_mapping.get(log_level.upper(), "ℹ️")

core/main_window.py:361: "completed": "✅",

core/main_window.py:362: "started": "🔄",

core/main_window.py:364: "processing": "⏳",

core/main_window.py:367: icon = status_icons.get(status, "ℹ️")

core/pairing_tab.py:300: # Usuń archiwum z listy archiwów

core/pairing_tab.py:309: # Usuń podgląd z galerii podglądów

core/performance_monitor.py:233:# Globalna instancja monitora wydajności

core/rules.py:342: # Sprawdź czy ścieżka nie zawiera sekwencji path traversal

---

File: core\rules.py

L346: # Sprawdź czy ścieżka nie jest zbyt długa

L350: # Sprawdź czy ścieżka nie zawiera niedozwolonych znaków

L426: # Sprawdź rozszerzenia używając sets dla O(1) lookup

---

File: core\scanner.py

L28: logger.info(f"🦀 ✅ SUCCESS: Loaded LOCAL Rust scanner engine from: {scanner_location}")

L50: Wrapper na Rustowy backend skanera assetów.

---

File: core\tools\duplicate_finder_worker.py

L15: # Log informacyjny o załadowaniu modułu Rust

L24: print(f"🦀 RUST HASH_UTILS: Używam LOKALNEJ wersji z: {hash_utils_location} [build: {build_timestamp}, module: {module_number}]")

L26: print(f"🦀 RUST HASH_UTILS: Moduł załadowany (brak informacji o lokalizacji)")

L32: """Worker do znajdowania duplikatów plików na podstawie SHA-256"""

L35: duplicates_found = pyqtSignal(list) # lista duplikatów do wyświetlenia

L42: """Główna metoda znajdowania duplikatów"""

L44: logger.info(f"Rozpoczęcie szukania duplikatów w folderze: {self.folder_path}")

L46: # Znajdź pliki archiwum

L49: self.finished.emit("Brak plików archiwum do sprawdzenia")

L52: # Oblicz SHA-256 dla każdego pliku

L55: # Znajdź duplikaty

L59: self.finished.emit("Nie znaleziono duplikatów")

L62: # Przygotuj listę do przeniesienia (nowsze pliki)

L65: # Przenieś pliki do folderu **duplicates**

L68: message = f"Znaleziono {len(duplicates)} grup duplikatów. Przeniesiono {moved_count} plików do folderu **duplicates**"

---

File: core\tools\file_renamer_worker.py

L21: # Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker

L23: pairs_found = pyqtSignal(list) # lista par do wyświetlenia

L24: user_confirmation_needed = pyqtSignal(list) # czeka na potwierdzenie użytkownika

L45: self.finished.emit("Brak plików do przetworzenia")

L117: "Randomizowanie nazw nieparowanych plików...",

L145: message = f"Randomizacja nazw zakończona: {renamed_count} plików zrandomizowano"

L147: message += f", {error_count} błędów"

---

File: core\tools\file_shortener_worker.py

L19: # Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker

L21: pairs_found = pyqtSignal(list) # lista par do wyświetlenia

L22: user_confirmation_needed = pyqtSignal(list) # czeka na potwierdzenie użytkownika

L43: self.finished.emit("Brak plików do przetworzenia")

L101: f"Skrócona para: {archive_name[:20]}...",

L113: "Skracanie nazw nieparowanych plików...",

L143: message = f"Skracanie nazw zakończone: {shortened_count} plików skrócono"

L145: message += f", {error_count} błędów"

L252: """Zmienia nazwę pliku zachowując rozszerzenie"""

L258: # Utwórz nową nazwę z rozszerzeniem

L265: # Zmień nazwę

L268: f"Zmieniono nazwę: {os.path.basename(file_path)} -> {new_name + file_ext}"

L273: logger.error(f"Błąd podczas zmiany nazwy {file_path}: {e}")

---

File: core\tools\image_resizer_worker.py

L14: # Log informacyjny o załadowaniu modułu Rust

L23: print(f"🦀 RUST IMAGE_TOOLS: Używam LOKALNEJ wersji z: {image_tools_location} [build: {build_timestamp}, module: {module_number}]")

L25: print(f"🦀 RUST IMAGE_TOOLS: Moduł załadowany (brak informacji o lokalizacji)")

L33: # Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker

L49: self.finished.emit("Brak plików do zmiany rozmiaru")

---

File: core\tools\prefix_suffix_remover_worker.py

L16: """Worker do usuwania prefixu/suffixu z nazw plików"""

L18: # Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker

L27: """Główna metoda usuwania prefixu/suffixu"""

L30: f"Rozpoczęcie usuwania {self.mode} w folderze: {self.folder_path}"

L33: # Znajdź wszystkie pliki w folderze

L41: self.finished.emit("Brak plików do przetworzenia")

L44: # Przetwórz pliki

L54: # Sprawdź czy plik pasuje do kryteriów

L60: ).rstrip() # Usuń spacje z końca po usunięciu prefix

L66: ).rstrip() # Usuń spacje z końca po usunięciu suffix

L78: # Zmień nazwę

L94: f"Błąd podczas przetwarzania {os.path.basename(file_path)}: {e}"

L97: # Przygotuj komunikat końcowy

L99: f"Usuwanie {self.mode} zakończone: {renamed_count} plików zmieniono"

L102: message += f", {error_count} błędów"

L107: error_msg = f"Błąd podczas usuwania {self.mode}: {e}"

---

File: core\tools\webp_converter_worker.py

L14: # Log informacyjny o załadowaniu modułu Rust

L23: print(f"🦀 RUST IMAGE_TOOLS (WebP): Używam LOKALNEJ wersji z: {image_tools_location} [build: {build_timestamp}, module: {module_number}]")

L25: print(f"🦀 RUST IMAGE_TOOLS (WebP): Moduł załadowany (brak informacji o lokalizacji)")

L31: """Worker do konwersji plików graficznych do formatu WebP"""

L33: # Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker

L40: """Główna metoda konwersji do WebP"""

L47: self.finished.emit("Brak plików do konwersji na WebP")

L114: message = f"Konwersja zakończona: {converted_count} przekonwertowano"

L116: message += f", {skipped_count} pominięto (już istnieją)"

L118: message += f", {error_count} błędów"

L122: len(files_to_convert), len(files_to_convert), "Konwersja zakończona"

---

File: core\tools_tab.py

L759: # Połącz sygnały

L882: item_text = f"📦 {archive_name}\n 🖼️ {preview_name}"

L935: item_text = f"📦 {archive_name}\n 🖼️ {preview_name}"

---

File: core\workers\asset_rebuilder_worker.py

L53: self.progress_updated.emit(0, 100, "Usuwanie starych plików .asset...")

L68: 40, 100, "Skanowanie i tworzenie nowych assetów..."

L74: self.progress_updated.emit(100, 100, "Przebudowa zakończona!")

L76: f"Pomyślnie przebudowano assety w folderze: {self.folder_path}"
