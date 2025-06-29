### 🚀 file_operations_model.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Implementacja Bezpiecznego Anulowania (Cooperative Cancellation):**
    -   **Cel:** Zastąpienie niebezpiecznego `terminate()` mechanizmem bezpiecznego przerywania pracy wątku.
    -   **Plan Działania:**
        1.  Dodać atrybut `self._is_cancellation_requested = False` do `FileOperationsWorker`.
        2.  Dodać publiczną metodę `request_cancellation()`, która ustawia tę flagę na `True`.
        3.  W metodzie `run()` wątka, w pętli iterującej po assetach, sprawdzać `if self._is_cancellation_requested: return`.
        4.  Przepisać operacje kopiowania plików, aby odbywały się w mniejszych porcjach (chunks), i sprawdzać flagę anulowania po każdej porcji.
        5.  Metoda `stop_operation()` w modelu powinna teraz wywoływać `request_cancellation()` i ewentualnie czekać na zakończenie wątku za pomocą `wait()`.

2.  **Refaktoryzacja do Klas Usługowych (Service Classes):**
    -   **Cel:** Rozbicie monolitycznego wątku na mniejsze, testowalne komponenty.
    -   **Plan Działania:**
        1.  Stworzyć klasę `AssetCopier` z metodą `copy(asset_data, src_dir, dest_dir)`, która implementuje kopiowanie w porcjach z obsługą anulowania.
        2.  Stworzyć klasę `ConflictResolver` z metodą `resolve(original_name, dest_dir)`, która zwraca unikalną nazwę pliku.
        3.  `FileOperationsWorker` będzie używał instancji tych klas do orkiestracji całego procesu, ale jego własna logika będzie znacznie prostsza.

3.  **Modernizacja do `pathlib` i `dataclasses`:**
    -   **Cel:** Uczynienie kodu bardziej czytelnym, obiektowym i bezpiecznym pod względem typów.
    -   **Plan Działania:**
        1.  Wszystkie zmienne i parametry przechowujące ścieżki zamienić na obiekty `pathlib.Path`.
        2.  Zamiast `list[dict]` używać `list[AssetData]`, gdzie `AssetData` to `dataclass`.
        3.  Przepisać logikę operacji na plikach z użyciem metod `pathlib`, np. `target_path.exists()`, `target_path.write_text()`, `source_path.rename(target_path)`.

4.  **Integracja z `asyncio` (Opcjonalnie, ale Rekomendowane):**
    -   **Cel:** Ujednolicenie modelu asynchroniczności w całej aplikacji.
    -   **Plan Działania:**
        1.  Zamiast `QThread`, operacje na plikach mogą być uruchamiane jako zadania `asyncio` za pomocą `asyncio.to_thread`.
        2.  Pozwoli to na łatwiejszą integrację z innymi asynchronicznymi częściami aplikacji i potencjalnie uprości zarządzanie cyklem życia operacji.
        3.  Raportowanie postępu może być realizowane przez przekazanie asynchronicznej kolejki (`asyncio.Queue`) lub funkcji zwrotnej (`callback`) do zadania.
