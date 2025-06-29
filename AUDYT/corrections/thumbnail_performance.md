### ⚡ thumbnail.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Krytyczne Problemy Wydajnościowe:

1.  **Synchroniczne Przetwarzanie Obrazów (KRYTYCZNY PRIORYTET):**
    -   **Problem:** Największym problemem wydajnościowym jest to, że całe przetwarzanie obrazu (`Image.open`, `img.resize`, `img.save`) w metodzie `_process_and_save_thumbnail` jest synchroniczne. Oznacza to, że wątek, który wywołuje `process_thumbnail` (np. wątek UI, wątek skanera), jest całkowicie blokowany na czas generowania miniatury. Dla obrazów o wysokiej rozdzielczości lub przy generowaniu wielu miniatur, prowadzi to do długotrwałego zamrożenia interfejsu użytkownika lub spowolnienia innych operacji w tle.
    -   **Rekomendacja (KRYTYCZNA):** Generowanie miniatur musi odbywać się **asynchronicznie w puli wątków**. Należy wykorzystać `QThreadPool` (lub `asyncio.to_thread` w połączeniu z `qasync`). `ThumbnailProcessor` powinien delegować zadania generowania miniatur do workera (`QRunnable` lub `QObject` przeniesiony do `QThread` z `QThreadPool`). Worker po zakończeniu pracy powinien emitować sygnał z gotową miniaturą, a UI (lub inny komponent) powinien ją odebrać i wyświetlić.

2.  **Brak Właściwego Wykorzystania `ThumbnailLoaderWorker`:**
    -   **Problem:** Klasa `ThumbnailLoaderWorker` jest zdefiniowana, ale nie jest używana w głównym przepływie generowania miniatur. Zamiast tego, `process_thumbnail` bezpośrednio wywołuje synchroniczny `_thumbnail_processor.process_image`. `ThumbnailLoaderWorker` sam w sobie również używa `QPixmap(path)`, co jest blokujące.
    -   **Rekomendacja (WYSOKA):** `ThumbnailLoaderWorker` powinien zostać przeprojektowany tak, aby używał biblioteki PIL do ładowania i skalowania obrazów w tle, a następnie konwertował wynik do `QPixmap` i emitował go. Powinien być uruchamiany w `QThreadPool`.

3.  **Wielokrotne Odczytywanie Konfiguracji:**
    -   **Problem:** `ThumbnailConfigManager` używa cache'owania, ale `get_thumbnail_config` jest wywoływane przy każdym przetwarzaniu obrazu. Chociaż cache pomaga, nadal jest to dodatkowy narzut.
    -   **Rekomendacja (NISKA):** Konfiguracja powinna być ładowana raz na początku aplikacji i przekazywana do `ThumbnailProcessor` (np. przez wstrzykiwanie zależności). `ThumbnailProcessor` powinien przechowywać konfigurację wewnętrznie.

#### Pozytywne Aspekty:

-   **LRU Cache dla Miniatur:** Implementacja `ThumbnailCache` (LRU) jest bardzo dobrym rozwiązaniem dla wydajności, ponieważ zapobiega wielokrotnemu generowaniu tych samych miniatur i przyspiesza ich ładowanie z pamięci.
-   **Atomowy Zapis Miniatur:** Metoda `_save_thumbnail_atomic` jest kluczowa dla niezawodności. Zapis do pliku tymczasowego, a następnie atomowa zamiana, chroni przed uszkodzeniem plików w przypadku awarii systemu.
-   **Użycie `pathlib`:** Użycie `pathlib` jest nowoczesne i poprawia wydajność operacji na ścieżkach w porównaniu do `os.path`.
