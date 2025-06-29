### 📄 core/thumbnail.py - Analiza Korekcyjna

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `core/thumbnail.py` jest odpowiedzialny za generowanie i zarządzanie miniaturami, które są kluczowe dla wizualnej prezentacji assetów w galerii. Jego wydajność bezpośrednio wpływa na szybkość ładowania i odświeżania widoków zawierających miniatury.
- **Performance impact:** KRYTYCZNY. Główne operacje przetwarzania obrazów (otwieranie, skalowanie, zapisywanie) są bardzo intensywne pod kątem CPU i I/O. Chociaż `ThumbnailLoaderWorker` jest zaprojektowany do asynchronicznego ładowania, to sama logika generowania miniatur w `ThumbnailProcessor` jest synchroniczna i blokująca. Wywołanie `process_thumbnail` z `core/scanner.py` oznacza, że generowanie miniatur blokuje wątek skanujący, co znacznie wydłuża czas skanowania folderów z dużą liczbą obrazów.
- **Modernization priority:** KRYTYCZNE - Optymalizacja generowania miniatur jest jednym z najważniejszych zadań w celu poprawy ogólnej wydajności aplikacji.
- **Bottlenecks found:**
  - **Synchroniczne przetwarzanie obrazów w `ThumbnailProcessor`:** Metody takie jak `_process_and_save_thumbnail` (zawierające `Image.open()` i `img.save()`) są blokujące i mogą być bardzo czasochłonne dla dużych obrazów. Wywołanie `process_thumbnail` w `core/scanner.py` oznacza, że cały proces skanowania jest spowalniany przez generowanie miniatur.
  - **Brak asynchronicznego generowania miniatur w `process_thumbnail` i `process_thumbnails_batch`:** Chociaż `ThumbnailLoaderWorker` istnieje, nie jest on używany do *generowania* miniatur, a jedynie do ich *ładowania* po wygenerowaniu. Generowanie odbywa się synchronicznie.
  - **Operacje I/O w `ThumbnailCacheManager`:** Metody takie jak `ensure_cache_dir`, `is_thumbnail_current`, `cleanup_old_thumbnails` wykonują operacje na systemie plików (`Path.exists()`, `Path.mkdir()`, `Path.stat()`, `Path.unlink()`, `Image.open()`). Chociaż są one zazwyczaj szybkie, ich wielokrotne wywoływanie może sumarycznie wpływać na wydajność.
- **Modernization needed:**
  - **Asynchroniczne generowanie miniatur:** Przeniesienie logiki generowania miniatur z `ThumbnailProcessor` do puli wątków (np. `QThreadPool`) lub do osobnego procesu. `process_thumbnail` powinien delegować to zadanie i zwracać wynik asynchronicznie.
  - **Ulepszone cache'owanie miniatur:** Chociaż `ThumbnailCache` jest zaimplementowany, należy upewnić się, że jest on efektywnie wykorzystywany w całym cyklu życia miniatur (generowanie, ładowanie, wyświetlanie).
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
  - **Ulepszone Zarządzanie Zasobami (Context Managers):** Upewnienie się, że wszystkie operacje na plikach (np. `Image.open()`) używają `with` statement.
