### 📊 core/scanner.py - Analiza Wydajności

**Plik:** `core/scanner.py`

#### **Zidentyfikowane Bottlenecki Wydajnościowe:**

- **Krytyczne: `create_thumbnail_for_asset` (i `process_thumbnail`):**
  - **Opis:** Funkcja `create_thumbnail_for_asset` wywołuje `process_thumbnail` (z `core.thumbnail`), która jest odpowiedzialna za generowanie miniatur. Jest to operacja intensywna zarówno pod kątem I/O (odczyt dużych plików obrazów) jak i CPU (skalowanie, konwersja). Ta operacja jest wykonywana synchronicznie w pętli w `find_and_create_assets` dla każdego assetu.
  - **Wpływ:** Chociaż `find_and_create_assets` jest wywoływana w osobnym wątku (`AssetScannerWorker`), generowanie miniatur jest najbardziej czasochłonną częścią procesu skanowania. Może to znacznie wydłużyć całkowity czas skanowania folderów z dużą liczbą obrazów, a także obciążać procesor.
  - **Rekomendacja:** Przeniesienie generowania miniatur do puli wątków (np. `QThreadPool`) lub do osobnego procesu, aby mogło być wykonywane równolegle. Dodatkowo, implementacja cache'owania miniatur, aby unikać ponownego generowania dla już przetworzonych obrazów.

- **Operacje I/O w `_get_files_by_extensions` i `_scan_folder_for_files`:**
  - **Opis:** Funkcje te używają `os.listdir` i `os.path.splitext` do listowania plików i sprawdzania ich rozszerzeń. Dla folderów zawierających bardzo dużą liczbę plików, te operacje mogą być czasochłonne.
  - **Wpływ:** Wydłużony czas skanowania folderów z dużą liczbą plików.
  - **Rekomendacja:** W większości przypadków te operacje są wystarczająco szybkie. Jeśli jednak okażą się bottleneckiem, można rozważyć optymalizację poprzez buforowanie wyników lub bardziej zaawansowane techniki skanowania systemu plików.

- **Operacje na plikach JSON (`load_from_file`, `save_to_file`):**
  - **Opis:** Funkcje te są używane do odczytu i zapisu plików `.asset`. Chociaż dla pojedynczego pliku nie jest to duży problem, przy dużej liczbie assetów (tysiące), sumaryczny czas operacji I/O na plikach JSON może być znaczący.
  - **Wpływ:** Wydłużony czas skanowania.
  - **Rekomendacja:** Upewnienie się, że operacje te są efektywne. Można rozważyć użycie szybszych bibliotek do serializacji/deserializacji JSON, jeśli okaże się to problemem.

#### **Rekomendowane Działania Optymalizacyjne:**

1.  **Asynchroniczne Generowanie Miniatur:**
    - Zmodyfikować `create_thumbnail_for_asset` tak, aby delegowała zadanie generowania miniatur do `QThreadPool` lub innego mechanizmu asynchronicznego.
    - Zaimplementować mechanizm powiadamiania o zakończeniu generowania miniatury i aktualizacji pliku `.asset`.
2.  **Cache'owanie Miniatur:**
    - Wdrożyć system cache'owania miniatur, aby unikać ponownego generowania dla już istniejących obrazów.
3.  **Profilowanie I/O i CPU:**
    - Użycie narzędzi do profilowania (np. `cProfile`, `py-spy`) do dokładnego pomiaru czasu wykonywania poszczególnych funkcji, zwłaszcza tych związanych z I/O i przetwarzaniem obrazów.
