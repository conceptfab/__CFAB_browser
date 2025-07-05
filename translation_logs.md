
# Logi do tłumaczenia

## `core/amv_controllers/handlers/asset_rebuild_controller.py`
- `logger.info(f"ODŚWIEŻONO FOLDER po przebudowie: {current_folder}")`

## `core/amv_controllers/handlers/control_panel_controller.py`
- `logger.info("Deselected all stars - showing all assets")`
- `logger.info(f"Selected {star_rating} stars - filtering")`

## `core/amv_controllers/handlers/folder_tree_controller.py`
- `logger.info(f"ODŚWIEŻANIE FOLDERU: {folder_path}")`
- `logger.info(f"ODŚWIEŻONO FOLDER I ASSETY: {folder_path}")`

## `core/amv_models/asset_grid_model.py`
- `logger.info("WCZYTYWANIE OD NOWA assetów w folderze: %s", folder_path)`
- `logger.debug("Skanowanie zakończone, znaleziono %d assetów", len(scanned_assets))`
- `logger.debug("WCZYTANO OD NOWA %d assetów z plików .asset", len(all_assets))`
- `logger.debug(f"WCZYTYWANIE OD NOWA zakończone, łącznie {len(all_assets)} assetów")`
- `logger.debug("FolderSystemModel set_root_folder - otrzymana ścieżka: %s", folder_path)`
- `logger.debug("FolderSystemModel set_root_folder - znormalizowana ścieżka: %s", normalized_path)`
- `logger.warning(f"_load_subfolders - folder nie istnieje: {folder_path}")`
- `logger.debug(f"_load_subfolders - tworzę item dla: {folder_name} -> {f_path}")`
- `logger.debug(f"Odświeżanie folderu: {folder_path}")`
- `logger.warning("Brak elementu root w drzewie")`
- `logger.debug(f"Pomyślnie odświeżono folder: {folder_path}")`
- `logger.error(f"Błąd podczas odświeżania folderu {folder_path}: {e}")`
- `logger.warning(f"Folder roboczy nie istnieje: {folder_path}")`
- `logger.debug(f"Załadowano {len(self._folders)} folderów roboczych")`
- `logger.error(f"Błąd podczas ładowania folderów roboczych: {e}")`

## `core/amv_models/config_manager_model.py`
- `logger.debug("Ładowanie konfiguracji z pliku")`
- `logger.debug("Konfiguracja załadowana pomyślnie")`
- `logger.warning("Użyto domyślnej konfiguracji")`
- `logger.error(f"Błąd ładowania konfiguracji: {e}")`

## `core/amv_models/drag_drop_model.py`
- `logger.debug(f"Porównanie ścieżek: norm_target='{norm_target}', norm_current='{norm_current}'")`

## `core/amv_models/file_operations_model.py`
- `self.operation_error.emit(f"Błąd podczas operacji {self.operation_type}: {e}")`
- `logger.debug(f"Utworzono folder docelowy: {self.target_folder_path}")`
- `self.operation_error.emit(f"Nie można utworzyć folderu docelowego " f"{self.target_folder_path}: {e}")`
- `self.operation_progress.emit(i + 1, total_assets, f"Przenoszenie: {asset_name}")`
- `error_msg = f"Błąd przenoszenia assetu {asset_name}: {e}"`
- `logger.debug(f"Usunięto pusty folder .cache w źródle: {source_cache_dir}")`
- `logger.warning(f"Nie można usunąć pustego folderu .cache w źródle {source_cache_dir}: {e}")`
- `logger.warning(f"Osiągnięto maksymalną liczbę prób dla {original_name}")`
- `return {"success": False, "message": f"Błąd przenoszenia assetu {original_name}: {e}", "final_name": original_name}`
- `logger.debug(f"Przeniesiono: {source_path} -> {target_path}")`
- `message = f"Przeniesiono asset: {original_name} -> {unique_name} " f"(zmieniono nazwę z powodu konfliktu)"`
- `message = f"Pomyślnie przeniesiono asset: {original_name}"`
- `logger.debug(f"Zaktualizowano plik .asset po zmianie nazwy: " f"{original_basename} -> {new_basename}")`
- `logger.error(f"Błąd podczas aktualizacji pliku .asset: {e}")`
- `logger.debug(f"Oznaczono asset jako duplikat: {asset_path}")`
- `logger.error(f"Błąd podczas oznaczania assetu jako duplikat: {e}")`
- `self.operation_progress.emit(i + 1, total_assets, f"Usuwanie: {asset_name}")`
- `logger.debug(f"Usunięto plik: {file_path}")`
- `logger.debug(f"Pomyślnie usunięto asset: {asset_name}")`
- `error_msg = f"Błąd usuwania assetu {asset_name}: {e}"`
- `logger.debug(f"Usunięto pusty folder .cache: {cache_dir}")`
- `logger.warning(f"Nie można usunąć pustego folderu .cache {cache_dir}: {e}")`
- `logger.warning("Operacja już w toku. Zatrzymuję poprzednią operację.")`
- `logger.info("Zatrzymywanie bieżącej operacji...")`
- `logger.info("Operacja została zatrzymana.")`
- `logger.debug("Worker został usunięty.")`

## `core/amv_models/pairing_model.py`
- `logger.error(f"Error creating default {self.unpair_files_path}: {e}")`

## `core/amv_views/amv_view.py`
- `logger.info("Żądanie zwinięcia drzewa folderów")`
- `logger.info("Żądanie rozwinięcia drzewa folderów")`

## `core/amv_views/asset_tile_pool.py`
- `logger.info("AssetTilePool zainicjalizowany.")`
- `logger.debug("Pozyskano kafelek z puli.")`
- `logger.debug("Pula jest pusta, tworzenie nowego kafelka.")`
- `logger.debug(f"Zwrócono kafelek {tile.asset_id} do puli. " f"Rozmiar puli: {len(self._pool)}")`
- `logger.info("Pula kafelków została wyczyszczona.")`

## `core/amv_views/asset_tile_view.py`
- `logger.debug("Shift wciśnięty - blokada podglądu/archiwum, tylko drag and drop")`
- `logger.info("Drag and drop zablokowane podczas ładowania galerii.")`
- `logger.debug(f"Zaktualizowano pasek statusu po zmianie checkboxa dla {self.asset_id}")`
- `logger.debug(f"Nie można zaktualizować paska statusu: {e}")`

## `core/amv_views/folder_tree_view.py`
- `logger.warning("contextMenuEvent - item lub UserRole data jest None")`
- `logger.warning("contextMenuEvent - index nie jest valid")`
- `logger.error(f"Błąd obsługi menu kontekstowego: {e}")`
- `logger.debug(f"_open_folder_in_explorer - otrzymana ścieżka: {folder_path}")`
- `logger.debug(f"_open_folder_in_explorer - wywołuję callback z ścieżką: {folder_path}")`
- `logger.debug(f"_open_folder_in_explorer - brak callbacku, używam bezpośredniego otwarcia: {folder_path}")`
- `logger.error(f"Błąd otwierania folderu w eksploratorze: {e}")`
- `logger.warning("Brak callbacku do przebudowy assetów")`
- `logger.error(f"Błąd wywołania callbacku przebudowy: {e}")`
- `logger.warning("Brak callbacku do odświeżania folderu")`
- `logger.error(f"Błąd wywołania callbacku odświeżania folderu: {e}")`

## `core/file_utils.py`
- `logger.debug(f"open_path_in_explorer - otrzymana ścieżka: {path}")`
- `logger.error("Nieprawidłowa ścieżka: pusta lub nie string")`
- `logger.debug(f"open_path_in_explorer - znormalizowana ścieżka: " f"{normalized_path}")`
- `logger.error(f"Ścieżka nie istnieje: {normalized_path}")`
- `logger.debug(f"open_path_in_explorer - uruchamiam explorer z ścieżką: " f"{normalized_path}")`
- `logger.error("Komenda 'explorer' nie jest dostępna")`
- `logger.error("Komenda 'open' nie jest dostępna")`
- `logger.error("Komenda 'xdg-open' nie jest dostępna")`
- `logger.info(f"Otworzono ścieżkę w eksploratorze: {normalized_path}")`
- `logger.error(f"Timeout podczas otwierania ścieżki: {path}")`
- `logger.error(f"Błąd procesu podczas otwierania ścieżki {path}: {e}")`
- `logger.error(f"Błąd podczas otwierania ścieżki {path}: {e}")`
- `logger.error(f"Plik nie istnieje: {path}")`
- `logger.info(f"Otworzono plik w domyślnej aplikacji: {path}")`
- `logger.error(f"Timeout podczas otwierania pliku: {path}")`
- `logger.error(f"Błąd procesu podczas otwierania pliku {path}: {e}")`
- `logger.error(f"Błąd podczas otwierania pliku {path}: {e}")`

## `core/json_utils.py`
- `logger.error(f"Plik {file_path} jest za duży ({file_size} bytes), limit: {max_size} bytes")`
- `logger.error(f"Brak uprawnień do odczytu pliku {file_path}: {e}")`
- `logger.error(f"Plik nie istnieje {file_path}: {e}")`
- `logger.error(f"Nieprawidłowy format JSON w pliku {file_path}: {e}")`
- `logger.error(f"Błąd kodowania pliku {file_path}: {e}")`
- `logger.error(f"Nieoczekiwany błąd podczas ładowania pliku {file_path}: {e}")`

## `core/main_window.py`
- `print(f"Warning: Configuration file {config_path} not found. " "Using default configuration.")`
- `print(f"Warning: Invalid JSON in {config_path}: {e}. " "Using default configuration.")`
- `print(f"Warning: Permission denied reading {config_path}. " "Using default configuration.")`
- `print(f"Warning: Unexpected error loading config {config_path}: {e}. " "Using default configuration.")`
- `print("Warning: Invalid logger level in config. Using INFO.")`
- `self.logger.error(f"Błąd ładowania {tab_name}: {e}")`
- `self.logger.info(f"Łączę sygnał working_directory_changed z ToolsTab")`
- `self.logger.info("Sygnał working_directory_changed połączony z ToolsTab")`
- `self.logger.info("Zamykanie aplikacji - zatrzymywanie wątków...")`
- `self.logger.info(f"Zatrzymywanie wątku: {thread.__class__.__name__}")`
- `self.logger.warning(f"Wymuszenie zamknięcia wątku: {thread.__class__.__name__}")`
- `self.logger.info("Wszystkie wątki zostały zatrzymane")`
- `self.logger.error(f"Błąd podczas zatrzymywania wątków: {e}")`
- `print(f"Critical error starting application: {e}")`

## `core/pairing_tab.py`
- `print(f"PairingTab: Received new working directory: {path}")`
- `logger.warning(f"Nieprawidłowa ścieżka work_folder: {work_folder}")`
- `print("Error: Could not determine work folder to open archive.")`
- `print(f"Opening archive: {full_path}")`
- `logger.error(f"Plik nie istnieje: {full_path}")`
- `logger.error(f"Timeout podczas otwierania pliku: {full_path}")`
- `logger.error(f"Błąd procesu podczas otwierania pliku {full_path}: {e}")`
- `logger.error(f"Błąd podczas otwierania pliku {full_path}: {e}")`
- `print(f"Opening preview: {file_path}")`
- `print("Error: Could not determine work folder to create asset.")`
- `print(f"FATAL ERROR: Archive path does not exist: {archive_full_path}")`
- `print(f"FATAL ERROR: Preview path does not exist: {preview_full_path}")`
- `print("Asset created successfully. Removing items from lists...")`
- `print(f"Removed archive from UI: {archive_name}")`
- `print(f"Removed preview from UI: {preview_name}")`
- `print("Failed to create asset.")`

## `core/preview_window.py`
- `logger.error(f"Błąd ładowania obrazu: {e}")`
- `logger.error(f"Błąd skalowania obrazu: {e}")`

## `core/rules.py`
- `logger.debug(f"Cache hit dla folderu: {folder_path}")`
- `logger.debug(f"Zcache'owano analizę folderu: {folder_path}")`
- `logger.warning(f"Błąd sprawdzania .cache: {e}")`
- `logger.error(f"Błąd analizy zawartości folderu {folder_path}: {e}")`
- `logger.error(f"Błąd analizy folderu: {e}")`
- `logger.debug(f"ANALIZA FOLDERU: {folder_path} | " f"Asset: {content.get('asset_count', 0)} | " f"Podglądy/Archiwa: {content.get('preview_archive_count', 0)} | " f"Cache: {'TAK' if content.get('cache_exists', False) else 'NIE'} | " f"Miniatury: {content.get('cache_thumb_count', 0)}")`
- `logger.debug(f"PRZYPADEK 1 WYKRYTY: {folder_path} | " f"Pliki archiwalne/podglądy: {preview_archive_count} | " f"Pliki asset: {asset_count} | " f"DECYZJA: Uruchamiam scanner (brak plików asset)")`
- `logger.debug(f"PRZYPADEK 2A WYKRYTY: {folder_path} | " f"Pliki archiwalne/podglądy: {preview_archive_count} | " f"Pliki asset: {asset_count} | " f"Cache: NIE | " f"DECYZJA: Uruchamiam scanner (brak folderu .cache)")`
- `logger.debug(f"PRZYPADEK 2B WYKRYTY: {folder_path} | " f"Pliki archiwalne/podglądy: {preview_archive_count} | " f"Pliki asset: {asset_count} | " f"Cache: TAK | " f"Miniatury: {cache_thumb_count} | " f"DECYZJA: Uruchamiam scanner (niezgodna liczba miniaturek)")`
- `logger.debug(f"PRZYPADEK 2C WYKRYTY: {folder_path} | " f"Pliki archiwalne/podglądy: {preview_archive_count} | " f"Pliki asset: {asset_count} | " f"Cache: TAK | " f"Miniatury: {cache_thumb_count} | " f"DECYZJA: Wyświetlam galerię (wszystko gotowe)")`
- `logger.debug(f"PRZYPADEK DODATKOWY (BRAK CACHE): {folder_path} | " f"Pliki asset: {asset_count} | " f"Pliki archiwalne/podglądy: {preview_archive_count} | " f"Cache: NIE | " f"DECYZJA: Uruchamiam scanner (tylko asset, brak .cache)")`
- `logger.debug(f"PRZYPADEK DODATKOWY (NIEZGODNA LICZBA): {folder_path} | " f"Pliki asset: {asset_count} | " f"Pliki archiwalne/podglądy: {preview_archive_count} | " f"Cache: TAK | " f"Miniatury: {cache_thumb_count} | " f"DECYZJA: Uruchamiam scanner (niezgodna liczba miniaturek)")`
- `logger.debug(f"PRZYPADEK DODATKOWY (GOTOWE): {folder_path} | " f"Pliki asset: {asset_count} | " f"Pliki archiwalne/podglądy: {preview_archive_count} | " f"Cache: TAK | " f"Miniatury: {cache_thumb_count} | " f"DECYZJA: Wyświetlam galerię (wszystko gotowe)")`
- `logger.debug(f"PRZYPADEK DOMYŚLNY: {folder_path} | " f"Pliki asset: {asset_count} | " f"Pliki archiwalne/podglądy: {preview_archive_count} | " f"Cache: {'TAK' if cache_exists else 'NIE'} | " f"Miniatury: {cache_thumb_count} | " f"DECYZJA: Brak akcji (folder nie zawiera odpowiednich plików)")`
- `logger.error(f"BŁĄD ANALIZY FOLDERU: {folder_path} - {content['error']}")`
- `logger.error(f"BŁĄD DECYZJI: {folder_path} - {error_msg}")`

## `core/scanner.py`
- `logger.error(f"Błąd podczas {operation}")`
- `logger.warning(f"Nie znaleziono sparowanych plików w: {folder_path}")`
- `logger.info(f"Utworzono plik unpair_files.json: " f"{len(unpaired_archives)} nieparowanych archiwów, " f"{len(unpaired_images)} nieparowanych obrazów")`
- `logger.error("tworzenia pliku unpair_files.json", e)`
- `logger.info(f"Rozpoczęto skanowanie folderu: {folder_path}")`
- `logger.info(f"Zakończono skanowanie. Utworzono {len(all_assets)} assetów " f"(w tym {len(special_folders)} specjalnych folderów).")`
- `logger.error(f"Błąd podczas skanowania folderu {folder_path}: {e}")`
- `logger.info(f"Ładowanie istniejących assetów z: {folder_path}")`
- `logger.warning(f"Nieprawidłowe dane w pliku: {entry}")`
- `logger.error(f"Błąd podczas ładowania assetu {entry}: {e}")`
- `logger.debug(f"Dodano {len(special_folders)} specjalnych folderów na początku")`
- `logger.info(f"Załadowano {len(assets)} assetów z {folder_path}")`
- `logger.error(f"Błąd podczas ładowania assetów z {folder_path}: {e}")`

## `core/thumbnail.py`
- `logger.debug(msg)`
- `logger.debug(f"Wygenerowano miniaturkę: {thumbnail_path}")`
- `logger.error(msg)`

## `core/thumbnail_cache.py`
- `logger.info(f"ThumbnailCache zainicjalizowany z limitem {max_size_mb} MB.")`
- `logger.debug(f"Cache HIT dla: {path}")`
- `logger.debug(f"Cache MISS dla: {path}")`
- `logger.debug(f"Dodano do cache: {path} ({pixmap_size / 1024:.1f} KB)." f" Aktualny rozmiar cache: {self.current_size_bytes / (1024*1024):.1f} MB")`
- `logger.debug(f"Usunięto z cache (LRU): {oldest_path}." f" Aktualny rozmiar cache: {self.current_size_bytes / (1024*1024):.1f} MB")`
- `logger.info("ThumbnailCache został wyczyszczony.")`

## `core/tools_tab.py`
- `logger.debug(f"Worker progress: {progress}% - {message}")`
- `logger.info(f"Operacja zakończona: {message}")`
- `logger.error(f"Błąd operacji: {error_message}")`
- `logger.error(f"Błąd podczas operacji: {e}")`
- `logger.info(f"Rozpoczęcie konwersji na WebP w folderze: {self.folder_path}")`
- `logger.info(f"[WebP] START iteracja {i+1}/{len(files_to_convert)}: {original_path}")`
- `logger.info(f"[WebP] Emituję progress_updated dla {original_path}")`
- `logger.info(f"[WebP] Sprawdzam czy {webp_path} już istnieje")`
- `logger.info(f"[WebP] Pomijam (już istnieje): {webp_path}")`
- `logger.info(f"[WebP] Rozpoczynam konwersję {original_path} -> {webp_path}")`
- `logger.info(f"[WebP] Konwersja udana, usuwam oryginalny plik: {original_path}")`
- `logger.info(f"[WebP] Plik {original_path} usunięty pomyślnie")`
- `logger.error(f"[WebP] Błąd przy usuwaniu pliku {original_path}: {e_rm}")`
- `logger.info(f"[WebP] Skutecznie skonwertowano: {original_path} -> {webp_path}")`
- `logger.error(f"[WebP] Błąd konwersji: {original_path}")`
- `logger.info(f"[WebP] END iteracja {i+1}/{len(files_to_convert)}: {original_path}")`
- `logger.error(f"[WebP] Błąd podczas konwersji {original_path}: {e}")`
- `logger.info(f"[WebP] Przygotowuję komunikat końcowy")`
- `logger.info(f"[WebP] Emituję progress_updated końcowy")`
- `logger.info(f"[WebP] Emituję finished: {message}")`
- `logger.error(f"[WebP] {error_msg}")`
- `logger.info(f"Znaleziono {len(files_to_convert)} plików do konwersji")`
- `logger.error(f"Błąd podczas wyszukiwania plików: {e}")`
- `logger.info(f"[WebP] _convert_to_webp START: {input_path} -> {output_path}")`
- `logger.info(f"[WebP] Importuję PIL.Image")`
- `logger.info(f"[WebP] Otwieram obraz: {input_path}")`
- `logger.info(f"[WebP] Obraz otwarty, rozmiar: {img.size}, tryb: {img.mode}")`
- `logger.info(f"[WebP] Konwertuję tryb {img.mode} na RGB")`
- `logger.info(f"[WebP] Konwersja trybu zakończona")`
- `logger.info(f"[WebP] Zapisuję jako WebP: {output_path}")`
- `logger.info(f"[WebP] Zapis zakończony pomyślnie")`
- `logger.error("[WebP] Biblioteka Pillow nie jest zainstalowana")`
- `logger.error(f"[WebP] Błąd konwersji {input_path}: {e}")`
- `logger.info(f"[WebP] _convert_to_webp END: {input_path}")`
- `logger.info(f"Rozpoczęcie zmniejszania obrazów w folderze: {self.folder_path}")`
- `logger.info(f"[Resize] START iteracja {i+1}/{len(files_to_resize)}: {filename}")`
- `logger.info(f"[Resize] Emituję progress_updated dla {filename}")`
- `logger.info(f"[Resize] Rozpoczynam zmniejszanie: {filename}")`
- `logger.info(f"[Resize] Skutecznie zmniejszono: {filename}")`
- `logger.info(f"[Resize] Pominięto (nie wymaga zmniejszenia): {filename}")`
- `logger.info(f"[Resize] END iteracja {i+1}/{len(files_to_resize)}: {filename}")`
- `logger.error(f"[Resize] Błąd podczas zmniejszania {filename}: {e}")`
- `logger.info(f"[Resize] Przygotowuję komunikat końcowy")`
- `logger.info(f"[Resize] Emituję progress_updated końcowy")`
- `logger.info(f"[Resize] Emituję finished: {message}")`
- `logger.error(f"[Resize] {error_msg}")`
- `logger.info(f"Znaleziono {len(files_to_resize)} plików do zmniejszenia")`
- `logger.info(f"[Resize] _resize_image START: {file_path}")`
- `logger.info(f"[Resize] Importuję PIL.Image")`
- `logger.info(f"[Resize] Otwieram obraz: {file_path}")`
- `logger.info(f"[Resize] Obraz otwarty, rozmiar: {img.size}")`
- `logger.info(f"[Resize] Nowy rozmiar: {new_width}x{new_height}")`
- `logger.info(f"[Resize] Zmniejszenie nie jest potrzebne")`
- `logger.info(f"[Resize] Zmniejszam obraz")`
- `logger.info(f"[Resize] Zapisuję zmniejszony obraz: {file_path}")`
- `logger.info(f"[Resize] Zapis zakończony pomyślnie")`
- `logger.error("[Resize] Biblioteka Pillow nie jest zainstalowana")`
- `logger.error(f"[Resize] Błąd zmniejszania {file_path}: {e}")`
- `logger.info(f"[Resize] _resize_image END: {file_path}")`
- `logger.info(f"Rozpoczęcie skracania nazw w folderze: {self.folder_path}")`
- `logger.error(f"Błąd podczas skracania nazw: {e}")`
- `logger.info(f"Skrócono parę: {new_name}")`
- `logger.debug(f"Pominięto parę (nazwa w normie): {archive_name}")`
- `logger.error(f"Błąd podczas skracania pary: {e}")`
- `logger.info(f"Skrócono nazwę: {filename} -> {new_name}")`
- `logger.debug(f"Pominięto (nazwa w normie): {filename}")`
- `logger.error(f"Błąd podczas skracania {filename}: {e}")`
- `logger.info(f"Znaleziono {len(files_info['pairs'])} par i {len(files_info['unpaired'])} plików bez pary")`
- `logger.error(f"Błąd podczas analizy plików: {e}")`
- `logger.warning(f"Plik o nazwie {new_name + file_ext} już istnieje")`
- `logger.debug(f"Zmieniono nazwę: {os.path.basename(file_path)} -> {new_name + file_ext}")`
- `logger.error(f"Błąd zmiany nazwy {file_path}: {e}")`
- `logger.info(f"Rozpoczęcie usuwania {self.mode} w folderze: {self.folder_path}")`
- `logger.warning(f"Plik o nazwie '{new_full_filename}' już istnieje. Pomijam.")`
- `logger.info(f"Zmieniono: '{filename_with_ext}' -> '{new_full_filename}'")`
- `logger.error(f"Błąd podczas przetwarzania {os.path.basename(file_path)}: {e}")`
- `logger.error(f"Błąd podczas usuwania {self.mode}: {e}")`
- `logger.debug(f"Walidacja folderu roboczego: {self.current_working_directory}")`
- `logger.debug(f"Folder istnieje: {os.path.exists(self.current_working_directory) if self.current_working_directory else False}")`
- `logger.warning(f"Folder roboczy nie jest ustawiony lub nie istnieje: {self.current_working_directory}")`
- `logger.info(f"Rozpoczęto operację w folderze: {self.current_working_directory}")`
- `logger.error(f"Błąd podczas rozpoczynania operacji: {e}")`
- `logger.debug(f"Mapowanie operacji '{operation_name}' na przycisk '{button_name}' i pole '{worker_attr}'")`
- `logger.debug("ToolsTab UI setup completed with 2-column layout")`
- `logger.debug(f"ToolsTab.set_working_directory() wywołane z: {directory_path}")`
- `logger.warning(f"Nieprawidłowy folder roboczy: {directory_path}")`
- `logger.debug(f"Ustawiono current_working_directory: {self.current_working_directory}")`
- `logger.info(f"Ustawiono folder roboczy: {directory_path}")`
- `logger.error(f"Folder nie istnieje: {directory_path}")`
- `logger.info(f"Skanowanie zakończone: {len(archive_files)} archiwów, " f"{len(preview_files)} podglądów")`
- `logger.error(f"Błąd podczas skanowania folderu {directory_path}: {e}")`
- `logger.warning("Biblioteka Pillow nie jest zainstalowana - nie można odczytać rozdzielczości")`
- `logger.debug(f"Nie można odczytać rozdzielczości {file_name}: {e}")`
- `logger.info("ToolsTab: Zatrzymywanie aktywnych wątków...")`
- `logger.info(f"Zatrzymywanie workera: {worker.__class__.__name__}")`
- `logger.info("ToolsTab: Wszystkie wątki zostały zatrzymane")`
- `logger.error(f"Błąd podczas zatrzymywania wątków w ToolsTab: {e}")`
- `logger.debug(f"Kliknięto przycisk WebP. Folder roboczy: {self.current_working_directory}")`
- `logger.debug(f"Przycisk WebP enabled: {self.webp_button.isEnabled()}")`
- `logger.info(f"Otworzono archiwum: {full_path}")`
- `logger.error(f"Timeout podczas otwierania archiwum: {full_path}")`
- `logger.error(f"Błąd procesu podczas otwierania archiwum {full_path}: {e}")`
- `logger.error(f"Błąd podczas otwierania archiwum {full_path}: {e}")`
- `logger.warning(f"Plik nie istnieje: {full_path}")`
- `logger.info(f"Otworzono podgląd: {full_path}")`
- `logger.error(f"Błąd podczas otwierania podglądu {full_path}: {e}")`
- `logger.debug(f"Kliknięto przycisk Image Resizer. Folder roboczy: {self.current_working_directory}")`
- `logger.debug(f"Przycisk Image Resizer enabled: {self.image_resizer_button.isEnabled()}")`
- `logger.info(f"Rozpoczęto usuwanie {mode} w folderze: {self.current_working_directory}")`
- `logger.error(f"Błąd podczas rozpoczynania usuwania: {e}")`

## `core/workers/asset_rebuilder_worker.py`
- `logger.info("Rozpoczęcie przebudowy assetów w folderze: %s", self.folder_path)`
- `logger.debug("Usunięto plik asset: %s", asset_file)`
- `logger.info("Usunięto %d plików .asset", len(asset_files))`
- `logger.error(f"Błąd usuwania plików .asset: {e}")`
- `logger.info("BEZWZGLĘDNIE usunięto folder .cache: %s", cache_folder)`
- `logger.info("Folder .cache nie istniał - i tak go usunęliśmy")`
- `logger.error(f"Błąd usuwania folderu .cache: {e}")`
- `logger.info("Scanner utworzył %d nowych assetów", len(created_assets))`
- `logger.error(f"Błąd uruchamiania scanner-a: {e}")`

## `core/workers/thumbnail_loader_worker.py`
- `logger.debug(f"Pomyślnie załadowano miniaturę: {self.path}")`
- `logger.error(error_msg)`
