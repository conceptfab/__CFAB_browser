### 📄 core/thumbnail.py - Analiza Cache'owania i Lazy Loading

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `core/thumbnail.py` jest odpowiedzialny za generowanie i zarządzanie miniaturami. Efektywne cache'owanie i lazy loading miniatur są kluczowe dla szybkiego ładowania galerii i płynności UI, zwłaszcza przy dużej liczbie assetów.
- **Performance impact:** KRYTYCZNY. Chociaż plik zawiera już zaawansowane mechanizmy cache'owania i asynchronicznego ładowania, to samo *generowanie* miniatur jest nadal synchroniczne i blokujące, co jest głównym bottleneckiem wydajnościowym.
- **Modernization priority:** KRYTYCZNE - Asynchroniczne generowanie miniatur jest niezbędne dla poprawy wydajności.
- **Bottlenecks found:**
  - **Synchroniczne generowanie miniatur w `ThumbnailProcessor`:** Metoda `_process_and_save_thumbnail` (wywoływana przez `process_image`) wykonuje operacje otwierania, przetwarzania i zapisywania obrazów synchronicznie. Jest to operacja intensywna pod kątem CPU i I/O, która blokuje wątek wywołujący.
  - **Brak asynchronicznego generowania miniatur w `process_thumbnail` i `process_thumbnails_batch`:** Chociaż `ThumbnailLoaderWorker` istnieje do asynchronicznego *ładowania*, nie jest on używany do asynchronicznego *generowania* miniatur. Generowanie odbywa się synchronicznie.
- **Modernization needed:**
  - **Asynchroniczne generowanie miniatur:** Przeniesienie logiki generowania miniatur z `ThumbnailProcessor` do puli wątków (np. `QThreadPool`) lub do osobnego procesu. `process_thumbnail` powinien delegować to zadanie i zwracać wynik asynchronicznie.
  - **Integracja z `AssetTileView` i `PreviewGalleryView`:** Upewnienie się, że te widoki efektywnie wykorzystują `_thumbnail_cache` i `ThumbnailLoaderWorker` do ładowania miniatur, a nie ładują ich bezpośrednio z dysku.
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
