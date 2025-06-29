### 📄 core/scanner.py - Analiza Repository Pattern

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `core/scanner.py` zawiera kluczową logikę biznesową związaną z wykrywaniem, tworzeniem i ładowaniem assetów. Przekształcenie go w implementację wzorca Repository poprawi separację odpowiedzialności, ułatwi testowanie i umożliwi łatwiejszą zmianę sposobu przechowywania danych w przyszłości.
- **Performance impact:** NISKI. Implementacja wzorca Repository nie ma bezpośredniego wpływu na wydajność, ponieważ dotyczy głównie struktury kodu i separacji odpowiedzialności. Może pośrednio wpłynąć na wydajność poprzez ułatwienie optymalizacji warstwy dostępu do danych.
- **Modernization priority:** WYSOKIE - Jest to kluczowy krok w implementacji wzorca Repository dla assetów.
- **Bottlenecks found:**
  - **Brak formalnego wzorca Repository:** Funkcje takie jak `find_and_create_assets` i `load_existing_assets` są operacjami dostępu do danych, ale nie są zgrupowane w klasie implementującej interfejs repozytorium. To utrudnia zarządzanie zależnościami i testowanie.
  - **Bezpośrednie wywołania funkcji:** Funkcje są wywoływane bezpośrednio, zamiast poprzez instancję repozytorium, co zmniejsza elastyczność.
- **Modernization needed:**
  - **Stworzenie klasy `AssetRepository`:** Klasa ta powinna enkapsulować logikę skanowania, tworzenia i ładowania assetów. Powinna implementować abstrakcyjny interfejs `IAssetRepository` (zdefiniowany np. w `amv_model.py` lub osobnym module).
  - **Przeniesienie funkcji do klasy:** Funkcje takie jak `_get_files_by_extensions`, `_scan_folder_for_files`, `_check_texture_folders_presence`, `_scan_for_special_folders`, `_create_single_asset`, `get_file_size_mb`, `create_thumbnail_for_asset`, `create_unpair_files_json`, `find_and_create_assets`, `load_existing_assets` powinny stać się metodami klasy `AssetRepository` (lub pomocniczymi funkcjami/klasami używanymi przez repozytorium).
  - **Wstrzykiwanie zależności:** `AssetScannerModelMV` (który obecnie używa `find_and_create_assets` i `load_existing_assets`) powinien otrzymywać instancję `IAssetRepository` w konstruktorze.
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
