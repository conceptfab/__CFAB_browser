### 📊 core/thumbnail.py - Analiza Wydajności

**Plik:** `core/thumbnail.py`

#### **Zidentyfikowane Bottlenecki Wydajnościowe:**

- **Krytyczne: Synchroniczne przetwarzanie obrazów w `ThumbnailProcessor`:**
  - **Opis:** Metoda `_process_and_save_thumbnail` (wywoływana przez `process_image`) wykonuje operacje otwierania, przetwarzania (skalowanie, przycinanie) i zapisywania obrazów (`Image.open()`, `img.resize()`, `img.crop()`, `img.save()`). Wszystkie te operacje są blokujące i intensywne pod kątem CPU i I/O.
  - **Wpływ:** Gdy `process_thumbnail` jest wywoływana z `core/scanner.py` (lub w innych miejscach, gdzie wiele miniatur jest generowanych), każda operacja generowania miniatury blokuje wątek wywołujący. To znacznie wydłuża całkowity czas skanowania/przetwarzania i może prowadzić do zacięć UI, jeśli nie jest odpowiednio zarządzane w osobnym wątku.
  - **Rekomendacja:** Przeniesienie logiki generowania miniatur do puli wątków (np. `QThreadPool`) lub do osobnego procesu. `process_thumbnail` powinien delegować to zadanie i zwracać wynik asynchronicznie. To pozwoli na równoległe przetwarzanie wielu miniatur, znacznie skracając całkowity czas.

- **`ThumbnailLoaderWorker` - Ładowanie `QPixmap`:**
  - **Opis:** `ThumbnailLoaderWorker` ładuje `QPixmap` z pliku i skaluje go. Chociaż działa w osobnym wątku, operacje `QPixmap(path)` i `pixmap.scaled()` mogą być kosztowne dla dużych obrazów. Jeśli wiele miniatur jest ładowanych jednocześnie, może to obciążać system.
  - **Wpływ:** Potencjalne, chwilowe obciążenie CPU i pamięci podczas ładowania wielu miniatur do wyświetlenia.
  - **Rekomendacja:** Upewnienie się, że `ThumbnailCache` jest efektywnie wykorzystywany, aby unikać wielokrotnego ładowania tych samych miniatur. Rozważenie, czy `ThumbnailLoaderWorker` powinien również korzystać z `QThreadPool` dla lepszego zarządzania zasobami.

- **Operacje I/O w `ThumbnailCacheManager`:**
  - **Opis:** Metody takie jak `is_thumbnail_current`, `cleanup_old_thumbnails`, `get_thumbnail_cache_stats`, `clear_thumbnail_cache`, `validate_thumbnail_integrity` wykonują operacje na systemie plików (`Path.exists()`, `Path.stat()`, `Path.unlink()`, `Image.open()`). Chociaż są one zazwyczaj szybkie, ich wielokrotne wywoływanie (np. podczas czyszczenia cache) może sumarycznie wpływać na wydajność.
  - **Wpływ:** Potencjalne, krótkotrwałe spowolnienia podczas operacji na cache miniatur.
  - **Rekomendacja:** Monitorowanie tych operacji. Jeśli okażą się problematyczne, rozważenie ich asynchronicznego wykonania lub optymalizacji poprzez buforowanie wyników.

#### **Rekomendowane Działania Optymalizacyjne:**

1.  **Asynchroniczne Generowanie Miniatur (Priorytet):**
    - Zmodyfikować `process_thumbnail` tak, aby delegowała zadanie generowania miniatur do `QThreadPool`.
    - Zaimplementować mechanizm powiadamiania o zakończeniu generowania miniatury i aktualizacji pliku `.asset`.
2.  **Ulepszone Cache'owanie Miniatur:**
    - Zapewnić, że `_thumbnail_cache` jest efektywnie wykorzystywany w całym cyklu życia miniatur.
    - Rozważyć cache'owanie `QPixmap` w `ThumbnailLoaderWorker`.
3.  **Profilowanie I/O i CPU:**
    - Użycie narzędzi do profilowania (np. `cProfile`, `py-spy`) do dokładnego pomiaru czasu wykonywania poszczególnych funkcji, zwłaszcza tych związanych z I/O i przetwarzaniem obrazów.
