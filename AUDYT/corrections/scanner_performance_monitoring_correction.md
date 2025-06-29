### 📄 core/scanner.py - Analiza Performance Monitoring

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `core/scanner.py` zawiera kluczową logikę skanowania i tworzenia assetów. Implementacja monitoringu wydajności pozwoli na identyfikację bottlenecków, optymalizację procesów i zapewnienie płynnego działania aplikacji.
- **Performance impact:** NISKI. Implementacja monitoringu wydajności nie ma bezpośredniego wpływu na wydajność, ale dostarcza danych do jej optymalizacji.
- **Modernization priority:** WYSOKIE - Jest to kluczowy krok w zapewnieniu ciągłej optymalizacji i utrzymania wysokiej wydajności aplikacji.
- **Bottlenecks found:**
  - **Brak wbudowanego monitoringu wydajności:** Obecnie funkcje nie zawierają żadnych jawnych mechanizmów do mierzenia czasu trwania operacji, zużycia pamięci czy innych metryk wydajności. Dostępne są jedynie logi tekstowe, które nie są łatwe do analizy ilościowej.
- **Modernization needed:**
  - **Pomiar czasu trwania operacji:** Użycie `time.perf_counter()` do mierzenia czasu trwania kluczowych funkcji i metod (np. `find_and_create_assets`, `load_existing_assets`, `_create_single_asset`, `create_thumbnail_for_asset`, `_get_files_by_extensions`). Logowanie tych czasów w ustrukturyzowany sposób (np. JSON, CSV) lub wysyłanie ich do dedykowanego systemu monitoringu.
  - **Monitorowanie zużycia pamięci:** Dla operacji, które mogą być pamięciożerne (np. `create_thumbnail_for_asset`), można użyć bibliotek takich jak `memory_profiler` (do użytku deweloperskiego) lub `psutil` (do monitoringu w czasie rzeczywistym) do śledzenia zużycia pamięci.
  - **Integracja z systemem raportowania:** W przyszłości, jeśli aplikacja będzie większa, można zintegrować te pomiary z dedykowanym systemem monitoringu (np. Prometheus, Grafana) lub po prostu zapisywać je do pliku logów w formacie, który łatwo parsować.
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
