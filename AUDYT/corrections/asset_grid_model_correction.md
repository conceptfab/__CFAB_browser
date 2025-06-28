**⚠️ KRYTYCZNE: Przed rozpoczęciem pracy zapoznaj się z ogólnymi zasadami refaktoryzacji, poprawek i testowania opisanymi w pliku [refactoring_rules.md](refactoring_rules.md).**

---

# 🐞 ANALIZA PLIKU: asset_grid_model.py - KOREKTA

**Wersja: 1.0**

**Data: 2025-06-28**

**Autor: Gemini**

---

## 🎯 CEL KOREKTY

Refaktoryzacja pliku `asset_grid_model.py` w celu poprawy zgodności z zasadą pojedynczej odpowiedzialności (SRP), zwiększenia czytelności i ułatwienia utrzymania kodu.

## 📊 WYNIKI ANALIZY

- **Stan:** ✅ Plik przeanalizowany.
- **Wynik:** Zidentyfikowano poważne naruszenie zasady SRP i hardkodowane wartości.

### 📝 Podsumowanie

Plik `asset_grid_model.py` jest zbyt rozbudowany i zawiera wiele niezależnych klas, które powinny znajdować się w osobnych modułach. Obecna struktura utrudnia zrozumienie, testowanie i rozwijanie poszczególnych komponentów.

1.  **Naruszenie SRP:** Klasy `FolderTreeModel`, `FolderSystemModel`, `WorkspaceFoldersModel`, `AssetScannerWorker` i `AssetScannerModelMV` są zdefiniowane w tym samym pliku co `AssetGridModel`. Każda z tych klas ma odrębną odpowiedzialność i powinna być w osobnym pliku.
2.  **Redundancja:** Istnieje pewna redundancja między `FolderTreeModel` a `FolderSystemModel`, co wymaga dalszej analizy i potencjalnego połączenia.
3.  **Hardkodowane wartości:** W funkcji `_calculate_columns_cached` używane są stałe wartości (`16` dla marginesów i odstępów), które powinny być dynamiczne lub konfigurowalne.

## 🛠️ ZALECANE ZMIANY

### 1. Wydzielenie klas do osobnych plików

Należy wydzielić następujące klasy do nowych plików w katalogu `core/amv_models`:

-   `FolderTreeModel` -> `core/amv_models/folder_tree_model.py`
-   `FolderSystemModel` -> `core/amv_models/folder_system_model.py`
-   `WorkspaceFoldersModel` -> `core/amv_models/workspace_folders_model.py`
-   `AssetScannerWorker` i `AssetScannerModelMV` -> `core/amv_models/asset_scanner_model.py`

Po wydzieleniu, plik `asset_grid_model.py` powinien zawierać tylko klasę `AssetGridModel`.

### 2. Refaktoryzacja `_calculate_columns_cached`

Należy zastąpić hardkodowane wartości dynamicznymi parametrami lub odniesieniami do konfiguracji, aby poprawić elastyczność i czytelność.
