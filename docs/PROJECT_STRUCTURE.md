# Struktura projektu CFAB Browser

Drzewo folderów z opisem plików. Folder `do_usuniecia/` pomijany.

---

## Katalog główny

```
__CFAB_browser/
│
├── cfab_browser.py          # Punkt wejścia – main(), QApplication, splash, ładowanie stylów
├── run.py                   # Launcher – czyści __pycache__, uruchamia cfab_browser.py
├── config.json              # Konfiguracja – work_folder*, thumbnail, logger_level, use_styles
├── requirements.txt         # Zależności Python (PyQt6, Pillow, orjson, psutil, maturin)
├── rebuild_rust.py          # Skrypt budowania modułu Rust (wywołuje scanner_rust/build.py)
├── build_pyinstaller.py     # Skrypt budowania exe (PyInstaller)
├── CFAB_Browser.spec        # Specyfikacja PyInstaller
├── install_pyinstaller.bat  # Instalacja PyInstaller
├── readme.md                # Opis aplikacji, funkcjonalności, architektura
├── .gitignore
│
├── .cursor/                 # Reguły Cursor IDE
│   └── rules/
│       └── project.mdc     # Zasady projektu (PyQt6, brak over-engineering)
│
├── core/                    # Główny kod aplikacji
├── docs/                    # Dokumentacja
├── logs/                    # Logi (performance.log)
└── scanner_rust/            # Źródła modułu Rust
```

---

## core/

```
core/
│
├── __init__.py              # Pakiet core
├── main_window.py           # MainWindow – okno główne, menu, status bar, zakładki
├── amv_tab.py               # AmvTab – zakładka galerii zasobów (siatka + drzewo)
├── pairing_tab.py           # PairingTab – parowanie archiwów z podglądami
├── tools_tab.py             # ToolsTab – narzędzia (WebP, resize, duplikaty, itp.)
│
├── scanner.py               # AssetRepository – wrapper na moduł Rust (skanowanie)
├── thumbnail_cache.py       # ThumbnailCache – cache miniatur w pamięci (LRU)
├── json_utils.py            # load_from_file, save_to_file (orjson z fallback)
├── file_utils.py            # open_file_in_default_app, open_path_in_explorer, handle_file_action
├── preview_window.py       # PreviewWindow – okno podglądu zasobu
│
├── rules.py                 # Logika decyzji dla kliknięć w folderach
├── utilities.py             # Funkcje pomocnicze (update_main_window_status)
├── performance_monitor.py   # Monitor wydajności, mierzenie operacji, logi
├── thread_manager.py        # ThreadManager – zarządzanie wątkami
│
├── amv_models/              # Modele MVC – dane i logika
├── amv_views/               # Widoki MVC – komponenty UI
├── amv_controllers/        # Kontrolery MVC – obsługa zdarzeń
├── workers/                 # Wątki robocze (QThread, QRunnable)
├── tools/                   # Narzędzia batch (WebP, resize, rename, itp.)
├── managers/                # Menadżery UI (StatusBarManager)
├── resources/               # Zasoby – style QSS, ikony
└── __rust/                  # Skompilowane moduły Rust (.pyd)
```

---

## core/amv_models/

```
amv_models/
├── __init__.py
├── amv_model.py             # AmvModel – agregujący model zakładki AMV
├── asset_grid_model.py      # AssetGridModel – siatka zasobów, dane z AssetRepository
├── asset_tile_model.py      # AssetTileModel – pojedynczy kafelek zasobu
├── folder_system_model.py   # FolderSystemModel – drzewo folderów (QStandardItemModel)
├── workspace_folders_model.py # WorkspaceFoldersModel – foldery robocze
├── config_manager_model.py  # ConfigManagerModel – konfiguracja (cache)
├── control_panel_model.py  # ControlPanelModel – panel sterowania
├── selection_model.py      # SelectionModel – stan zaznaczenia
├── drag_drop_model.py     # DragDropModel – dane drag & drop
├── file_operations_model.py # FileOperationsModel – operacje na plikach (kopiuj, przenieś)
└── pairing_model.py        # PairingModel – parowanie archiwów z podglądami
```

---

## core/amv_views/

```
amv_views/
├── __init__.py
├── amv_view.py              # AmvView – główny widok (siatka + drzewo + panel)
├── asset_tile_view.py       # AssetTileView – pojedynczy kafelek zasobu (miniatura, drag)
├── asset_tile_pool.py       # AssetTilePool – pula kafelków (recykling widżetów)
├── folder_tree_view.py      # FolderTreeView – drzewo folderów z drag & drop
├── gallery_widgets.py        # GalleryContainerWidget, DropHighlightDelegate
├── preview_gallery_view.py  # PreviewGalleryView – galeria podglądów (PairingTab)
└── preview_tile.py          # PreviewTile – kafelek podglądu w PairingTab
```

---

## core/amv_controllers/

```
amv_controllers/
├── __init__.py
├── amv_controller.py        # AmvController – główny kontroler zakładki AMV
└── handlers/
    ├── __init__.py
    ├── asset_grid_controller.py    # AssetGridController – siatka zasobów, layout
    ├── asset_rebuild_controller.py # AssetRebuildController – odświeżanie zasobów
    ├── control_panel_controller.py # ControlPanelController – panel sterowania
    ├── file_operation_controller.py # FileOperationController – kopiuj, przenieś, usuń
    ├── folder_tree_controller.py   # FolderTreeController – drzewo folderów
    └── signal_connector.py         # SignalConnector – łączenie sygnałów MVC
```

---

## core/workers/

```
workers/
├── __init__.py
├── worker_manager.py        # WorkerManager, ManagedWorker – zarządzanie workerami
├── thumbnail_loader_worker.py   # ThumbnailLoaderWorker – asynchroniczne ładowanie miniatur
├── resolution_loader_worker.py  # ResolutionLoaderWorker – ładowanie rozdzielczości obrazów
└── asset_rebuilder_worker.py   # AssetRebuilderWorker – przebudowa zasobów w folderze
```

---

## core/tools/

```
tools/
├── __init__.py
├── base_worker.py           # BaseWorker, BaseToolWorker, BaseNameWorker
├── webp_converter_worker.py # Konwersja obrazów do WebP
├── image_resizer_worker.py  # Zmiana rozmiaru obrazów
├── file_renamer_worker.py   # Zmiana nazw plików
├── file_shortener_worker.py # Skracanie nazw plików
├── prefix_suffix_remover_worker.py # Usuwanie prefiksów/sufiksów
└── duplicate_finder_worker.py # Wyszukiwanie duplikatów
```

---

## core/managers/

```
managers/
└── status_bar_manager.py    # StatusBarManager – pasek statusu, progress bar
```

---

## core/resources/

```
resources/
├── styles.qss               # Style Qt (QSS)
└── img/
    ├── icon.png             # Ikona aplikacji
    ├── icon.ico
    ├── folder.png, folder_icon.png, open_folder_icon.png
    ├── workfolder_icon.png
    ├── texture.png
    ├── search.png
    ├── collapse_panel.png, open_panel.png
    └── ...
```

---

## core/__rust/

```
__rust/
├── __init__.py              # Eksport scanner_rust, image_tools, hash_utils
├── scanner_rust.pyd         # Moduł skanowania (Rust) – AssetRepository
├── image_tools.pyd          # Narzędzia obrazów (Rust)
└── hash_utils.pyd           # Funkcje hashowania (Rust)
```

---

## scanner_rust/

```
scanner_rust/
├── build.py                 # Skrypt budowania (maturin) – kopiuje .pyd do core/__rust/
├── setup.py                 # Setup dla pyo3/maturin
├── Cargo.toml               # Workspace Cargo (crates)
├── README.md, QUICKSTART.md, BUILD_INFO_README.md
├── benchmark.py             # Benchmark skanowania
├── test_build_info.py       # Test informacji o buildzie
├── install_rust.bat         # Instalacja Rust
│
└── crates/
    ├── scanner/             # Główny moduł – skanowanie, .asset, miniatury
    │   └── src/
    │       ├── lib.rs
    │       ├── scanner.rs
    │       ├── asset_builder.rs
    │       ├── thumbnail.rs
    │       ├── file_utils.rs
    │       ├── types.rs
    │       └── build_info.rs
    ├── image_tools/         # Przetwarzanie obrazów (resize, formaty)
    │   └── src/
    │       ├── lib.rs
    │       ├── config.rs
    │       └── build_info.rs
    └── hash_utils/          # Hashowanie plików
        └── src/
            ├── lib.rs
            └── build_info.rs
```

---

## docs/

```
docs/
├── DEVELOPER_GUIDE.md       # Przewodnik dla deweloperów – szybki start
└── PROJECT_STRUCTURE.md     # Ten plik – drzewo folderów z opisami
```

---

## logs/

```
logs/
└── performance.log          # Logi z performance_monitor
```
