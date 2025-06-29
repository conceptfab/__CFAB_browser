### 📄 core/amv_models/asset_grid_model.py - Analiza Cache'owania i Lazy Loading

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `AssetGridModel` zarządza listą assetów wyświetlanych w galerii. Brak lazy loading i cache'owania prowadzi do wysokiego zużycia pamięci i spowolnienia aplikacji przy dużych zbiorach danych, co negatywnie wpływa na komfort użytkownika.
- **Performance impact:** KRYTYCZNY. Obecna implementacja ładuje wszystkie assety do pamięci, co jest nieefektywne dla dużych galerii. Brak cache'owania powoduje ponowne ładowanie i przetwarzanie tych samych danych.
- **Modernization priority:** KRYTYCZNE - Implementacja lazy loading i cache'owania jest niezbędna dla poprawy wydajności i skalowalności aplikacji.
- **Bottlenecks found:**
  - **Brak Lazy Loading:** Metoda `set_assets` ładuje całą listę assetów do pamięci (`_assets`), niezależnie od tego, ile z nich jest aktualnie widocznych w UI. Przy dużej liczbie assetów (np. tysiące), może to prowadzić do znacznego zużycia pamięci i opóźnień w ładowaniu.
  - **Brak Cache'owania:** Nie ma mechanizmu cache'owania dla często używanych danych assetów (np. miniatur, metadanych). Każde ponowne żądanie tych samych danych może prowadzić do ponownego ich przetwarzania lub odczytu z dysku.
- **Modernization needed:**
  - **Implementacja Lazy Loading:** Zamiast przechowywać pełne dane wszystkich assetów w `_assets`, można przechowywać tylko ich identyfikatory lub ścieżki. Dane assetów (np. miniatury, szczegółowe metadane) powinny być ładowane na żądanie, gdy kafelek staje się widoczny w widoku. Wymaga to ścisłej współpracy z `AssetTileView` i `AmvController`.
  - **Implementacja LRU Cache:** Wprowadzenie LRU (Least Recently Used) cache dla danych assetów (szczególnie miniatur i metadanych), aby zminimalizować ponowne ładowanie z dysku. Cache powinien być zarządzany centralnie (np. w `core/thumbnail.py` dla miniatur, lub w nowej klasie `AssetCacheManager`).
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
