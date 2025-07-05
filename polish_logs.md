# Logi do tłumaczenia

## core/amv_controllers/handlers/asset_rebuild_controller.py

- `f"ODŚWIEŻONO FOLDER po przebudowie: {current_folder}"`

## core/amv_controllers/handlers/folder_tree_controller.py

- `f"ODŚWIEŻANIE FOLDERU: {folder_path}"`
- `f"ODŚWIEŻONO FOLDER I ASSETY: {folder_path}"`

## core/amv_views/amv_view.py

- `f"Panel kontrolny: pozycja=({x}, {y}), scroll_area=({scroll_x}, {scroll_y}, {scroll_width}x{scroll_height}), panel={panel_width}x{panel_height}"`
- `"Żądanie zwinięcia drzewa folderów"`
- `"Żądanie rozwinięcia drzewa folderów"`

## core/amv_views/asset_tile_pool.py

- `"AssetTilePool zainicjalizowany."`
- `"Pozyskano kafelek z puli."`
- `"Pula jest pusta, tworzenie nowego kafelka."`
- `f"Zwrócono kafelek {tile.asset_id} do puli. Rozmiar puli: {len(self._pool)}"`
- `"Pula kafelków została wyczyszczona."`

## core/amv_views/asset_tile_view.py

- `"Shift wciśnięty - blokada podglądu/archiwum, tylko drag and drop"`
- `f"Zaktualizowano pasek statusu po zmianie checkboxa dla {self.asset_id}"`
- `f"Nie można zaktualizować paska statusu: {e}"`

## core/amv_views/folder_tree_view.py

- `f"contextMenuEvent - pozycja myszy: {event.pos()}"`
- `"contextMenuEvent - item lub UserRole data jest None"`
- `"contextMenuEvent - index nie jest valid"`
- `f"Błąd obsługi menu kontekstowego: {e}"`
- `f"_open_folder_in_explorer - otrzymana ścieżka: {folder_path}"`
- `f"_open_folder_in_explorer - wywołuję callback z ścieżką: {folder_path}"`
- `f"_open_folder_in_explorer - brak callbacku, używam bezpośredniego otwarcia: {folder_path}"`
- `f"Błąd otwierania folderu w eksploratorze: {e}"`
- `"Brak callbacku do przebudowy assetów"`
- `f"Błąd wywołania callbacku przebudowy: {e}"`
- `"Brak callbacku do odświeżania folderu"`
- `f"Błąd wywołania callbacku odświeżania folderu: {e}"`

## core/amv_models/asset_grid_model.py

- `"WCZYTYWANIE OD NOWA assetów w folderze: %s"`
- `"Skanowanie zakończone, znaleziono %d assetów"`
- `"WCZYTANO OD NOWA %d assetów z plików .asset"`
- `f"WCZYTYWANIE OD NOWA zakończone, łącznie {len(all_assets)} assetów"`
- `"FolderSystemModel set_root_folder - otrzymana ścieżka: %s"`
- `"FolderSystemModel set_root_folder - znormalizowana ścieżka: %s"`
- `f"_load_subfolders - folder nie istnieje: {folder_path}"`
- `f"_load_subfolders - tworzę item dla: {folder_name} -> {f_path}"`
- `f"Odświeżanie folderu: {folder_path}"`
- `"Brak elementu root w drzewie"`
- `f"Znaleziono folder do odświeżenia: {target_path}"`
- `f"Pomyślnie odświeżono folder: {folder_path}"`
- `f"Błąd podczas odświeżania folderu {folder_path}: {e}"`
- `f"Błąd podczas rekurencyjnego odświeżania: {e}"`
- `f"Folder roboczy nie istnieje: {folder_path}"`
- `f"Załadowano {len(self._folders)} folderów roboczych"`
- `f"Błąd podczas ładowania folderów roboczych: {e}"`

## core/amv_models/config_manager_model.py

- `"Ładowanie konfiguracji z pliku"`
- `"Konfiguracja załadowana pomyślnie"`
- `"Użyto domyślnej konfiguracji"`
- `f"Błąd ładowania konfiguracji: {e}"`

## core/amv_models/drag_drop_model.py

- `f"Porównanie ścieżek: norm_target='{norm_target}', norm_current='{norm_current}'"`

## core/amv_models/file_operations_model.py

- `f"Błąd podczas operacji {self.operation_type}: {e}"`
- `f"Utworzono folder docelowy: {self.target_folder_path}"`
- `f"Nie można utworzyć folderu docelowego {self.target_folder_path}: {e}"`
- `f"Błąd przenoszenia assetu {asset_name}: {e}"`
- `f"Usunięto pusty folder .cache w źródle: {source_cache_dir}"`
- `f"Nie można usunąć pustego folderu .cache w źródle {source_cache_dir}: {e}"`
- `f"Osiągnięto maksymalną liczbę prób dla {original_name}"`
- `f"Przeniesiono: {source_path} -> {target_path}"`
- `f"Zaktualizowano plik .asset po zmianie nazwy: {original_basename} -> {new_basename}"`
- `f"Błąd podczas aktualizacji pliku .asset: {e}"`
- `f"Oznaczono asset jako duplikat: {asset_path}"`
- `f"Błąd podczas oznaczania assetu jako duplikat: {e}"`
- `f"Usunięto plik: {file_path}"`
- `f"Pomyślnie usunięto asset: {asset_name}"`
- `f"Błąd usuwania assetu {asset_name}: {e}"`
- `f"Usunięto pusty folder .cache: {cache_dir}"`
- `f"Nie można usunąć pustego folderu .cache {cache_dir}: {e}"`
- `"Operacja już w toku. Zatrzymuję poprzednią operację."`
- `"Zatrzymywanie bieżącej operacji..."`
- `"Operacja została zatrzymana."`
- `"Worker został usunięty."`

## core/file_utils.py

- `f"open_path_in_explorer - otrzymana ścieżka: {path}"`
- `"Nieprawidłowa ścieżka: pusta lub nie string"`
- `f"open_path_in_explorer - znormalizowana ścieżka: {normalized_path}"`
- `f"Ścieżka nie istnieje: {normalized_path}"`
- `f"open_path_in_explorer - uruchamiam explorer z ścieżką: {normalized_path}"`
- `"Komenda 'explorer' nie jest dostępna"`
- `"Komenda 'open' nie jest dostępna"`
- `"Komenda 'xdg-open' nie jest dostępna"`
- `f"Otworzono ścieżkę w eksploratorze: {normalized_path}"`
- `f"Timeout podczas otwierania ścieżki: {path}"`
- `f"Błąd procesu podczas otwierania ścieżki {path}: {e}"`
- `f"Błąd podczas otwierania ścieżki {path}: {e}"`
- `f"Plik nie istnieje: {path}"`
- `f"Otworzono plik w domyślnej aplikacji: {path}"`
- `f"Timeout podczas otwierania pliku: {path}"`
- `f"Błąd procesu podczas otwierania pliku {path}: {e}"`
- `f"Błąd podczas otwierania pliku {path}: {e}"`

## core/json_utils.py

- `f"Plik {file_path} jest za duży ({file_size} bytes), limit: {max_size} bytes"`
- `f"Brak uprawnień do odczytu pliku {file_path}: {e}"`
- `f"Plik nie istnieje {file_path}: {e}"`
- `f"Nieprawidłowy format JSON w pliku {file_path}: {e}"`
- `f"Błąd kodowania pliku {file_path}: {e}"`
- `f"Nieoczekiwany błąd podczas ładowania pliku {file_path}: {e}"`

## core/main_window.py

- `"Warning: Invalid logger level in config. Using INFO."`
- `f"Łączę sygnał working_directory_changed z ToolsTab"`
- `f"Sygnał working_directory_changed połączony z ToolsTab"`
- `f"Zamykanie aplikacji - zatrzymywanie wątków..."`
- `f"Zatrzymywanie wątku: {thread.__class__.__name__}"`
- `f"Wymuszenie zamknięcia wątku: {thread.__class__.__name__}"`
- `"Wszystkie wątki zostały zatrzymane"`
- `f"Błąd podczas zatrzymywania wątków: {e}"`

## core/pairing_tab.py

- `f"Nieprawidłowa ścieżka work_folder: {work_folder}"`
- `f"Plik nie istnieje: {full_path}"`
- `f"Timeout podczas otwierania pliku: {full_path}"`
- `f"Błąd procesu podczas otwierania pliku {full_path}: {e}"`
- `f"Błąd podczas otwierania pliku {full_path}: {e}"`

## core/preview_window.py

- `f"Nie można załadować obrazu: {self.image_path}"`
- `f"Błąd ładowania obrazu: {e}"`
- `f"Błąd skalowania obrazu: {e}"`

## core/rules.py

- `f"Cache hit dla folderu: {folder_path}"`
- `f"Zcache'owano analizę folderu: {folder_path}"`
- `f"Błąd sprawdzania .cache: {e}"`
- `f"Błąd analizy zawartości folderu {folder_path}: {e}"`
- `f"ANALIZA FOLDERU: ..."`
- `f"PRZYPADEK 1 WYKRYTY: ..."`
- `f"PRZYPADEK 2A WYKRYTY: ..."`
- `f"PRZYPADEK 2B WYKRYTY: ..."`
- `f"PRZYPADEK 2C WYKRYTY: ..."`
- `f"PRZYPADEK DODATKOWY (BRAK CACHE): ..."`
- `f"PRZYPADEK DODATKOWY (NIEZGODNA LICZBA): ..."`
- `f"PRZYPADEK DODATKOWY (GOTOWE): ..."`
- `f"PRZYPADEK DOMYŚLNY: ..."`
- `f"BŁĄD ANALIZY FOLDERU: {folder_path} - {content['error']}"`
- `f"BŁĄD DECYZJI: {folder_path} - {error_msg}"`

## core/scanner.py

- `f"Błąd podczas {operation}"`
- `f"Nieprawidłowa ścieżka folderu: {folder_path}"`
- `f"Znaleziono istniejący plik .asset: {name}.asset"`
- `f"Zachowano gwiazdki: {existing_asset_data['stars']} dla {name}"`
- `f"Zachowano kolor: {existing_asset_data['color']} dla {name}"`
- `f"Zachowano miniaturę: {existing_asset_data['thumbnail']} dla {name}"`
- `f"Utworzono plik .asset: {name}.asset"`
- `f"Błąd podczas tworzenia assetu {name}: {e}"`
- `f"Plik obrazu nie istnieje: {image_path}"`
- `f"Utworzono miniaturę: {thumbnail_path}"`
- `f"Zaktualizowano plik .asset z miniaturą: {asset_path}"`
- `f"Nie udało się utworzyć miniatury dla: {asset_name}"`
- `f"Utworzono plik unpair_files.json: ..."`
- `f"Rozpoczęto skanowanie folderu: {folder_path}"`
- `f"Zakończono skanowanie. Utworzono {len(all_assets)} assetów..."`
- `f"Błąd podczas skanowania folderu {folder_path}: {e}"`
- `f"Nie znaleziono sparowanych plików w: {folder_path}"`
- `f"Utworzono asset: {name}"`
- `f"Ładowanie istniejących assetów z: {folder_path}"`
- `f"Załadowano asset: {entry}"`
- `f"Nieprawidłowe dane w pliku: {entry}"`
- `f"Błąd podczas ładowania assetu {entry}: {e}"`
- `f"Dodano {len(special_folders)} specjalnych folderów na początku"`
- `f"Załadowano {len(assets)} assetów z {folder_path}"`
- `f"Błąd podczas ładowania assetów z {folder_path}: {e}"`

## core/thumbnail.py

- `f"Nieprawidłowa ścieżka obrazu: {image_path}"`
- `f"Plik nie istnieje: {image_path}"`
- `f"Nieobsługiwany format: {path.suffix}"`
- `f"Używam istniejącej miniaturki: {thumbnail_path}"`
- `f"Wygenerowano miniaturkę: {thumbnail_path}"`
- `f"Błąd generowania miniaturki dla {image_path}: {e}"`

## core/thumbnail_cache.py

- `f"ThumbnailCache zainicjalizowany z limitem {max_size_mb} MB."`
- `f"Dodano do cache: {path} ({pixmap_size / 1024:.1f} KB). Aktualny rozmiar cache: {self.current_size_bytes / (1024*1024):.1f} MB"`
- `f"Usunięto z cache (LRU): {oldest_path}. Aktualny rozmiar cache: {self.current_size_bytes / (1024*1024):.1f} MB"`
- `"ThumbnailCache został wyczyszczony."`

## core/tools_tab.py

- `f"Operacja zakończona: {message}"`
- `f"Błąd operacji: {error_message}"`
- `f"Nieprawidłowy folder: {self.folder_path}"`
- `f"Błąd podczas operacji: {e}"`
- `"Metoda _run_operation musi być zaimplementowana w klasie pochodnej."`
- `f"Rozpoczęcie konwersji na WebP w folderze: {self.folder_path}"`
- `f"Pomijam (już istnieje): {webp_path}"`
- `f"Konwersja udana, usuwam oryginalny plik: {original_path}"`
- `f"Plik {original_path} usunięty pomyślnie"`
- `f"Błąd przy usuwaniu pliku {original_path}: {e_rm}"`
- `f"Skutecznie skonwertowano: {original_path} -> {webp_path}"`
- `f"Błąd konwersji: {original_path}"`
- `f"Błąd podczas konwersji {original_path}: {e}"`
- `f"Błąd podczas konwersji na WebP: {e}"`
- `f"Znaleziono {len(files_to_convert)} plików do konwersji"`
- `f"Błąd podczas wyszukiwania plików: {e}"`
- `"Biblioteka Pillow nie jest zainstalowana"`
- `f"Błąd konwersji {input_path}: {e}"`
- `f"Rozpoczęcie zmniejszania obrazów w folderze: {self.folder_path}"`
- `f"Skutecznie zmniejszono: {filename}"`
- `f"Pominięto (nie wymaga zmniejszenia): {filename}"`
- `f"Błąd podczas zmniejszania {filename}: {e}"`
- `f"Błąd podczas zmniejszania obrazów: {e}"`
- `f"Znaleziono {len(files_to_resize)} plików do zmniejszenia"`
- `f"Zmniejszenie nie jest potrzebne"`
- `f"Błąd zmniejszania {file_path}: {e}"`
- `f"Rozpoczęcie skracania nazw w folderze: {self.folder_path}"`
- `f"Błąd podczas skracania nazw: {e}"`
- `f"Skrócono parę: {new_name}"`
- `f"Pominięto parę (nazwa w normie): {archive_name}"`
- `f"Błąd podczas skracania pary: {e}"`
- `f"Skrócono nazwę: {filename} -> {new_name}"`
- `f"Pominięto (nazwa w normie): {filename}"`
- `f"Błąd podczas skracania {filename}: {e}"`
- `f"Znaleziono {len(files_info['pairs'])} par i {len(files_info['unpaired'])} plików bez pary"`
- `f"Błąd podczas analizy plików: {e}"`
- `f"Plik o nazwie {new_name + file_ext} już istnieje"`
- `f"Zmieniono nazwę: {os.path.basename(file_path)} -> {new_name + file_ext}"`
- `f"Błąd zmiany nazwy {file_path}: {e}"`
- `f"Rozpoczęcie usuwania {self.mode} w folderze: {self.folder_path}"`
- `f"Plik o nazwie '{new_full_filename}' już istnieje. Pomijam."`
- `f"Zmieniono: '{filename_with_ext}' -> '{new_full_filename}'"`
- `f"Błąd podczas przetwarzania {os.path.basename(file_path)}: {e}"`
- `f"Błąd podczas usuwania {self.mode}: {e}"`
- `f"Walidacja folderu roboczego: {self.current_working_directory}"`
- `f"Folder istnieje: ..."`
- `f"Folder roboczy nie jest ustawiony lub nie istnieje: {self.current_working_directory}"`
- `f"Rozpoczęto operację w folderze: {self.current_working_directory}"`
- `f"Błąd podczas rozpoczynania operacji: {e}"`
- `f"Mapowanie operacji '{operation_name}' na przycisk '{button_name}' i pole '{worker_attr}'"`
- `f"Nieprawidłowy folder roboczy: {directory_path}"`
- `f"Ustawiono current_working_directory: {self.current_working_directory}"`
- `f"Ustawiono folder roboczy: {directory_path}"`
- `f"Folder nie istnieje: {directory_path}"`
- `f"Skanowanie zakończone: {len(archive_files)} archiwów, {len(preview_files)} podglądów"`
- `f"Błąd podczas skanowania folderu {directory_path}: {e}"`
- `"Biblioteka Pillow nie jest zainstalowana - nie można odczytać rozdzielczości"`
- `f"Nie można odczytać rozdzielczości {file_name}: {e}"`
- `"ToolsTab: Zatrzymywanie aktywnych wątków..."`
- `f"Zatrzymywanie workera: {worker.__class__.__name__}"`
- `"ToolsTab: Wszystkie wątki zostały zatrzymane"`
- `f"Błąd podczas zatrzymywania wątków w ToolsTab: {e}"`
- `f"Otworzono archiwum: {full_path}"`
- `f"Timeout podczas otwierania archiwum: {full_path}"`
- `f"Błąd procesu podczas otwierania archiwum {full_path}: {e}"`
- `f"Błąd podczas otwierania archiwum {full_path}: {e}"`
- `f"Plik nie istnieje: {full_path}"`
- `f"Otworzono podgląd: {full_path}"`
- `f"Błąd podczas otwierania podglądu {full_path}: {e}"`
- `f"Rozpoczęto usuwanie {mode} w folderze: {self.current_working_directory}"`
- `f"Błąd podczas rozpoczynania usuwania: {e}"`

## core/utilities.py

- `f"Plik nie istnieje: {file_path}"`
- `f"Błąd podczas pobierania rozmiaru pliku {file_path}: {e}"`

## core/workers/asset_rebuilder_worker.py

- `f"Nieprawidłowy folder: {self.folder_path}"`
- `f"Rozpoczęcie przebudowy assetów w folderze: {self.folder_path}"`
- `f"Pomyślnie przebudowano assety w folderze: {self.folder_path}"`
- `f"Błąd podczas przebudowy assetów: {e}"`
- `f"Usunięto plik asset: {asset_file}"`
- `f"Usunięto {len(asset_files)} plików .asset"`
- `f"Błąd usuwania plików .asset: {e}"`
- `f"BEZWZGLĘDNIE usunięto folder .cache: {cache_folder}"`
- `"Folder .cache nie istniał - i tak go usunęliśmy"`
- `f"Błąd usuwania folderu .cache: {e}"`
- `f"Scanner utworzył {len(created_assets)} nowych assetów"`
- `f"Błąd uruchamiania scanner-a: {e}"`

## core/workers/thumbnail_loader_worker.py

- `f"Plik miniatury nie istnieje: {self.path}"`
- `f"Nie można załadować QPixmap z pliku: {self.path}"`
- `f"Pomyślnie załadowano miniaturę: {self.path}"`
- `f"Błąd ładowania miniatury {self.path}: {e}"`
