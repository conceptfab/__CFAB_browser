# Analiza parametrów do config.json

Na podstawie analizy kodu w katalogu `core/` zidentyfikowałem parametry i zmienne, które są hardcoded, ale mogłyby być przeniesione do `config.json`.

## Proponowana lista parametrów:

1. **cache_ttl**

   - Bieżąca wartość: 300 (sekund)
   - Lokalizacja: `core/rules.py` (CACHE_TTL)
   - Opis: Czas życia cache dla analizy folderów.

2. **max_cache_size_mb**

   - Bieżąca wartość: 600 (MB)
   - Lokalizacja: `core/thumbnail_cache.py`
   - Opis: Maksymalny rozmiar cache thumbnaili.

3. **max_scan_depth**

   - Bieżąca wartość: 50
   - Lokalizacja: `core/amv_models/folder_system_model.py`
   - Opis: Maksymalna głębokość skanowania folderów.

4. **asset_extensions**

   - Bieżąca wartość: [".asset"]
   - Lokalizacja: `core/rules.py`
   - Opis: Rozszerzenia assetów.

5. **archive_extensions**

   - Bieżąca wartość: [".rar", ".zip", ".sbsar", ".7z"]
   - Lokalizacja: `core/rules.py`
   - Opis: Rozszerzenia archiwów.

6. **preview_extensions**

   - Bieżąca wartość: [".jpg", ".jpeg", ".png", ".webp", ".gif"]
   - Lokalizacja: `core/rules.py`
   - Opis: Rozszerzenia preview.

7. **grid_min_columns**

   - Bieżąca wartość: 1
   - Lokalizacja: `core/amv_models/asset_grid_model.py`
   - Opis: Minimalna liczba kolumn w gridzie.

8. **grid_max_columns**

   - Bieżąca wartość: 10
   - Lokalizacja: `core/amv_models/asset_grid_model.py`
   - Opis: Maksymalna liczba kolumn w gridzie.

9. **thumbnail_size_options**

   - Bieżąca wartość: [128, 256, 512]
   - Lokalizacja: `core/amv_views/amv_view.py`
   - Opis: Dostępne rozmiary thumbnaili.

10. **cache_folder_name**
    - Bieżąca wartość: ".cache"
    - Lokalizacja: `core/rules.py`
    - Opis: Nazwa folderu cache.
