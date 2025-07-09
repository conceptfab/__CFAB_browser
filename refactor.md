Raport Analizy Kodu - Problemy do Naprawienia
📁 Pliki wymagające poprawek
1. core/amv_views/asset_tile_view.py
Problemy:

Duplikowane metody cleanup w sekcji końcowej (_cleanup_connections_and_resources, _reset_state_variables, _clear_ui_elements, _remove_from_parent)
Nieużywana zmienna _cached_pixmap wspomniana w komentarzach
Potencjalny problem z _drag_in_progress - może powodować deadlock

Akcje:

Usunąć duplikowane metody cleanup i pozostawić tylko release_resources()
Usunąć nieużywane zmienne i komentarze o nich
Dodać timeout do _drag_in_progress lub użyć context managera

2. core/tools/ (wszystkie pliki worker)
Problemy:

Duplikowane wzorce obsługi sygnałów w każdym workerze
Redundantne importy z komentarzami # pyright: ignore
Podobne metody walidacji ścieżek

Akcje:
4. Wydzielić wspólny BaseToolWorker z obsługą sygnałów
5. Usunąć duplikaty walidacji ścieżek - użyć metod z base_worker.py
6. Naprawić importy Rust bez używania # pyright: ignore
3. core/main_window.py
Problemy:

Zbyt duża klasa z wieloma odpowiedzialnościami
Duplikowane metody helper dla zliczania zasobów
Nieużywane pola w default_config

Akcje:
7. Wydzielić StatusBarManager jako osobną klasę
8. Usunąć duplikaty w metodach _calculate_asset_counts i podobnych
9. Oczyścić default_config z nieużywanych kluczy
4. core/amv_controllers/handlers/file_operation_controller.py
Problemy:

Duplikowane metody optymalizacji (_remove_moved_assets_optimized i pomocnicze)
Zbyt skomplikowana logika usuwania kafelków
Nieużywane _tiles_mutex w niektórych miejscach

Akcje:
10. Uprościć optymalizację usuwania kafelków do 2-3 metod
11. Usunąć nieużywane referencje do _tiles_mutex
12. Wydzielić AssetRemovalOptimizer jako osobną klasę
5. core/thumbnail_cache.py
Problemy:

Potencjalne problemy z thread safety w singleton pattern
Duplikowane sprawdzania rozmiaru cache

Akcje:
13. Przepisać singleton na thread-safe implementację
14. Usunąć duplikaty w _evict_oldest() i podobnych metodach
6. core/tools_tab.py
Problemy:

Duplikowane metody obsługi workerów (_handle_worker_*)
Redundantne połączenia sygnałów
Nieużywane importy

Akcje:
15. Użyć WorkerManager konsekwentnie dla wszystkich workerów
16. Usunąć nieużywane importy (QThread, pyqtSignal w niektórych miejscach)
17. Uprościć _start_operation_with_confirmation() - zbyt skomplikowana
7. core/amv_models/file_operations_model.py
Problemy:

Błędne przypisanie w linii 245: asset_file_path = new_asset_path
Duplikowane sprawdzania ścieżek plików
Nieużywana metoda _mark_asset_as_duplicate()

Akcje:
18. Naprawić błędne przypisanie w _update_asset_file_after_rename()
19. Usunąć nieużywaną metodę _mark_asset_as_duplicate()
20. Wydzielić wspólne sprawdzenia ścieżek do metody pomocniczej
8. core/amv_controllers/handlers/asset_grid_controller.py
Problemy:

Nieużywany _last_layout_hash w niektórych scenariuszach
Duplikowane logiki w _rebuild_asset_grid_immediate()
Zbyt skomplikowana metoda on_assets_changed()

Akcje:
21. Uprościć on_assets_changed() - wydzielić części do metod pomocniczych
22. Usunąć nieużywane optymalizacje layoutu jeśli nie są potrzebne
23. Wydzielić logikę sortowania do osobnej metody
9. core/workers/worker_manager.py
Problemy:

Nieużywane parametry w niektórych metodach
Duplikowana logika resetowania stanu przycisków

Akcje:
24. Usunąć nieużywane parametry z metod statycznych
25. Dodać abstrakcyjną klasę ManagedWorker dla lepszej integracji
10. Pliki init.py
Problemy:

Niektóre pliki __init__.py są puste gdy powinny eksportować klasy
Brak konsystentnych eksportów

Akcje:
26. Dodać eksporty w pustych plikach __init__.py gdzie potrzebne
27. Ujednolicić style eksportów (__all__)
📊 Podsumowanie
Znalezione problemy:

❌ 15+ duplikowanych funkcji/metod
❌ 8 nieużywanych zmiennych/metod
❌ 3 potencjalne błędy logiczne
❌ 5 problemów z architekturą kodu

Szacowany czas naprawy: 4-6 godzin
Priorytet: Średni (kod działa, ale wymaga refaktoryzacji)