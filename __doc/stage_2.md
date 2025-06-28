📋 AUDYT LOGIKI BIZNESOWEJ CFAB_3DHUB

WAŻNE! Wszystkie pliki wynikowe audytu (np. business_logic_map.md, corrections.md, patch_code.md, pliki z analizami i poprawkami) MUSZĄ być zapisywane wyłącznie w katalogu AUDYT. Tylko tam należy ich szukać!

🎯 CEL
Kompleksowa analiza, optymalizacja i uproszczenie logiki biznesowej aplikacji z naciskiem na wydajność procesów, stabilność operacji i eliminację over-engineering w warstwie biznesowej. Szczególny fokus na modernizację architektury PyQt6 zgodnie z najnowszymi standardami 2025.
🏛️ CZTERY FILARY AUDYTU LOGIKI BIZNESOWEJ
Ten audyt opiera się na czterech kluczowych filarach, które stanowią najwyższe priorytety każdej analizy procesów biznesowych:
1️⃣ WYDAJNOŚĆ PROCESÓW ⚡

Async I/O Operations: Konwersja synchronicznych operacji na asynchroniczne
Memory Management: Optymalizacja zarządzania pamięcią i eliminacja memory leaks
Thread Pool Optimization: Efektywne wykorzystanie QThreadPool dla operacji batch
Cache Strategy: Implementacja LRU cache dla często używanych danych
Virtual Scrolling: Implementacja lazy loading dla dużych zbiorów danych
Database Connection Pooling: Optymalizacja połączeń z bazami danych
Batch Processing: Grupowanie operacji I/O dla lepszej wydajności

2️⃣ STABILNOŚĆ OPERACJI 🛡️

Error Recovery Mechanisms: Implementacja robust error handling
Thread Safety: Zabezpieczenie operacji wielowątkowych
Resource Cleanup: Prawidłowe zwalnianie zasobów UI i systemowych
Signal-Slot Safety: Weryfikacja bezpiecznych połączeń signal-slot
Memory Leak Prevention: Wykrywanie i eliminacja wycieków pamięci
Atomic Operations: Zapewnienie atomowości krytycznych operacji
Graceful Degradation: Płynne degradowanie funkcjonalności przy błędach

3️⃣ WYELIMINOWANIE OVER-ENGINEERING 🎯

Architecture Simplification: Uproszczenie nadmiernie złożonych wzorców
Code Deduplication: Eliminacja duplikacji kodu
Dependency Reduction: Zmniejszenie liczby zależności
Layer Consolidation: Konsolidacja niepotrzebnych warstw abstrakcji
Pattern Optimization: Zastąpienie złożonych wzorców prostszymi rozwiązaniami
API Simplification: Uproszczenie interfejsów programowych
Configuration Reduction: Zmniejszenie liczby parametrów konfiguracyjnych

4️⃣ MODERNIZACJA ARCHITEKTURY PyQt6 🚀

MVC Pattern Enhancement: Ulepszenie implementacji wzorca Model-View-Controller
ModelView Architecture: Optymalizacja Qt ModelView dla dużych zbiorów danych
Signal-Slot Optimization: Modernizacja mechanizmów komunikacji
Qt6 Features Adoption: Wykorzystanie nowych możliwości Qt6
Performance Profiling: Implementacja narzędzi do monitorowania wydajności
Modern Python Patterns: Zastosowanie nowoczesnych wzorców Python 3.9+
Threading Modernization: Wykorzystanie najnowszych mechanizmów wielowątkowości

🖼️ KRYTYCZNY PROCES PREZENTACJI DANYCH W INTERFEJSIE UŻYTKOWNIKA
WAŻNE: Proces prezentacji danych w interfejsie użytkownika jest RÓWNIE WAŻNY jak główne procesy biznesowe!
WAŻNE: Kod aplikacji znajduje się w folderze CORE/, plik startowy jest w głównym katalogu -> cfab_browser.py. Nie przeszukuj innych folderów, nie trać czasu!!!
⚠️ KRYTYCZNE: Część funkcji jest wyłączona z audytu - informacja jest zawarta w opisie funkcji!
🎯 Dlaczego UI to Logika Biznesowa

Główny interfejs użytkownika - większość czasu użytkownik spędza w interfejsie
Wydajność krytyczna - interfejs musi być responsywny nawet przy dużych zbiorach danych
Algorytmy biznesowe - zarządzanie danymi, cache'owanie, filtrowanie, sortowanie
User Experience - responsywność interfejsu decyduje o użyteczności aplikacji
Memory Efficiency - optymalne zarządzanie pamięcią w komponentach UI
Thread Safety - bezpieczne operacje UI w środowisku wielowątkowym

📊 Wymagania Wydajnościowe UI - Standardy 2025

Virtual Scrolling: Renderowanie tylko widocznych elementów dla list >1000 elementów
Lazy Loading: Progresywne ładowanie komponentów interfejsu
Debounced Events: Opóźnione przetwarzanie zdarzeń UI (resize, search, filter)
Progressive Enhancement: Stopniowe zwiększanie funkcjonalności UI
Memory Pooling: Reużywanie obiektów UI zamiast ciągłego tworzenia/niszczenia
Async UI Updates: Asynchroniczne aktualizacje interfejsu bez blokowania
GPU Acceleration: Wykorzystanie akceleracji sprzętowej gdzie możliwe

🔧 Kluczowe Komponenty Logiki Prezentacji - Analiza Priorytetowa
⚫⚫⚫⚫ KRYTYCZNE:

AssetTileView: Główny komponent renderowania - wymaga virtual scrolling
AmvController: Kontroler główny - wymaga async operations
AssetGridModel: Model danych - wymaga lazy loading i cache
FolderTreeView: Drzewo folderów - wymaga debounced expansion

🔴🔴🔴 WYSOKIE:

ThumbnailProcessor: Przetwarzanie miniaturek - wymaga background processing
FileOperationsModel: Operacje na plikach - wymaga progress tracking
SelectionModel: Zarządzanie zaznaczeniem - wymaga batch operations
DragDropModel: Przeciąganie elementów - wymaga feedback optimization

🟡🟡 ŚREDNIE:

ConfigManager: Zarządzanie konfiguracją - wymaga validation
PreviewWindow: Okno podglądu - wymaga memory optimization
ProgressBars: Wskaźniki postępu - wymaga smooth animations

🚨 Krytyczne Obszary Wymagające Modernizacji
ARCHITECTURE PATTERNS:

Repository Pattern: Implementacja dla operacji na danych
Observer Pattern: Modernizacja signal-slot connections
Command Pattern: Implementacja dla operacji undo/redo
Factory Pattern: Optymalizacja tworzenia komponentów UI

PERFORMANCE PATTERNS:

Object Pooling: Reużywanie obiektów UI
Lazy Initialization: Opóźnione tworzenie komponentów
Caching Strategy: Implementacja cache dla często używanych danych
Background Processing: Przeniesienie operacji I/O do background threads

MODERN PYTHON FEATURES:

Type Hints: Implementacja pełnych adnotacji typów
AsyncIO Integration: Integracja z pętlą zdarzeń asyncio
Context Managers: Wykorzystanie do zarządzania zasobami
Dataclasses: Modernizacja struktur danych

📜 ZASADY I PROCEDURY
Wszystkie szczegółowe zasady, procedury i checklisty zostały zebrane w pliku __doc/refactoring_rules.md. Należy się z nim zapoznać przed rozpoczęciem pracy.

📊 ETAP 1: MAPOWANIE LOGIKI BIZNESOWEJ Z PRIORYTETAMI MODERNIZACJI
🗺️ DYNAMICZNE GENEROWANIE MAPY PLIKÓW LOGIKI BIZNESOWEJ
WAŻNE: Mapa NIE jest statyczna! Musi być generowana na podstawie aktualnego kodu za każdym razem z uwzględnieniem priorytetów modernizacji.
📋 PROCEDURA GENEROWANIA MAPY Z ANALIZĄ WYDAJNOŚCI
KROK 1: DYNAMICZNE ODKRYWANIE STRUKTURY PROJEKTU
Model MUSI dynamicznie przeanalizować strukturę projektu z fokusem na komponenty wydajnościowe:
bash# Model MUSI wykonać te komendy aby odkryć aktualną strukturę:
find core/ -type f -name "*.py" | head -30  # Znajdź pliki .py
ls -la core/                                # Sprawdź główne katalogi
tree core/ -I "__pycache__|*.pyc"           # Pełna struktura (jeśli dostępna)
KROK 2: IDENTYFIKACJA KATALOGÓW Z LOGIKĄ BIZNESOWĄ - PRIORYTETY WYDAJNOŚCI
Model MUSI przeanalizować każdy katalog i określić czy zawiera logikę biznesową z klasyfikacją wydajnościową:
KRYTERIA KLASYFIKACJI WYDAJNOŚCIOWEJ:

🚀 PERFORMANCE CRITICAL: Komponenty wpływające na responsywność UI
🧠 MEMORY INTENSIVE: Komponenty zarządzające dużymi zbiorami danych
🔄 I/O OPERATIONS: Komponenty wykonujące operacje dyskowe/sieciowe
🎨 UI RENDERING: Komponenty odpowiedzialne za renderowanie interfejsu
⚡ ASYNC CANDIDATES: Komponenty wymagające asynchronizacji

KROK 3: ANALIZA BOTTLENECKÓW W KODZIE
Dla każdego odkrytego pliku, model MUSI zidentyfikować:
WYDAJNOŚCIOWE ANTI-PATTERNS:

Synchronous I/O w głównym wątku: file.read(), os.listdir() w UI thread
Memory leaks w UI: Brak deleteLater() dla widgets
Inefficient loops: Nested loops w _rebuild_asset_grid()
Blocking operations: Długie operacje bez progress indicators
Resource leaks: Niedomykane pliki, connections, timers

THREAD SAFETY ISSUES:

UI operations poza głównym wątkiem: widget.update() w worker threads
Shared mutable state: Współdzielone zmienne bez synchronizacji
Signal connections: Nieprawidłowe połączenia signal-slot między wątkami
Race conditions: Konkurencyjny dostęp do zasobów

ARCHITECTURE SMELLS:

God classes: Klasy z >500 linii kodu
Long methods: Metody z >50 linii kodu
Deep inheritance: Hierarchie >4 poziomów
Circular dependencies: Cykliczne importy między modułami

🔍 METODA ANALIZY FUNKCJI LOGIKI BIZNESOWEJ Z FOKUSEM NA WYDAJNOŚĆ
Dla każdego pliku .py model MUSI przeanalizować:
1. ANALIZA WYDAJNOŚCIOWA:
python# Przykład analizy wydajnościowej:
def sync_file_operation():        # 🚨 KRYTYCZNE - blocking I/O
def heavy_computation():          # ⚡ WYSOKIE - CPU intensive  
def ui_update_method():          # 🎨 ŚREDNIE - UI thread safety
def helper_function():           # 🟢 NISKIE - utility function
2. KRYTERIA LOGIKI BIZNESOWEJ - ROZSZERZONE:

Performance Bottlenecks - Funkcje spowalniające aplikację
Memory Management - Zarządzanie zasobami pamięci
Thread Safety - Bezpieczeństwo operacji wielowątkowych
UI Responsiveness - Responsywność interfejsu użytkownika
Resource Management - Zarządzanie zasobami systemowymi
Error Recovery - Mechanizmy odzyskiwania po błędach
Cache Efficiency - Efektywność mechanizmów cache'owania

3. PYTANIA WERYFIKACYJNE - ROZSZERZONE:

Czy ta funkcja/klasa może powodować blocking głównego wątku?
Czy zarządza pamięcią w sposób efektywny?
Czy jest thread-safe w kontekście PyQt6?
Czy może powodować memory leaks?
Czy wymaga modernizacji do async/await?
Czy implementuje proper error handling?
Czy wykorzystuje najnowsze funkcje Python 3.9+?

4. OKREŚLANIE PRIORYTETU - Z FOKUSEM NA WYDAJNOŚĆ:
⚫⚫⚫⚫ KRYTYCZNE - PERFORMANCE BLOCKING:

Funkcje blokujące główny wątek UI
Memory leaks w komponentach UI
Thread safety violations
Operacje I/O w synchronous mode

🔴🔴🔴 WYSOKIE - PERFORMANCE IMPACT:

Nieefektywne algorytmy w hot paths
Brak cache'owania często używanych danych
Nadmierne zużycie pamięci
Brak progress indicators dla długich operacji

🟡🟡 ŚREDNIE - OPTIMIZATION CANDIDATES:

Funkcje pomocnicze wymagające optymalizacji
Konfiguracje wymagające walidacji
Algorytmy do refaktoryzacji

🟢 NISKIE - MAINTENANCE:

Funkcje utility nie wpływające na wydajność
Logowanie i debugging
Dokumentacja i komentarze

📊 SZABLON MAPY DO WYPEŁNIENIA - Z ANALIZĄ WYDAJNOŚCI
markdown### 🗺️ MAPA PLIKÓW FUNKCJONALNOŚCI BIZNESOWEJ - ANALIZA WYDAJNOŚCI

**Wygenerowano na podstawie aktualnego kodu: [DATA]**

**Odkryte katalogi z logiką biznesową:**

- [KATALOG_1] - [OPIS ROLI W LOGICE BIZNESOWEJ] - [PRIORYTET WYDAJNOŚCI]
- [KATALOG_2] - [OPIS ROLI W LOGICE BIZNESOWEJ] - [PRIORYTET WYDAJNOŚCI]
- [KATALOG_3] - [OPIS ROLI W LOGICE BIZNESOWEJ] - [PRIORYTET WYDAJNOŚCI]

#### **[NAZWA_KATALOGU_1]** ([ŚCIEŻKA_KATALOGU]) - 🚀 PERFORMANCE CRITICAL
[ŚCIEŻKA_KATALOGU]/
├── [nazwa_pliku].py [PRIORYTET] - [OPIS] - 🚨 BLOCKING I/O DETECTED
├── [nazwa_pliku].py [PRIORYTET] - [OPIS] - ⚡ MEMORY INTENSIVE
└── [nazwa_pliku].py [PRIORYTET] - [OPIS] - 🎨 UI THREAD SAFETY

**Zidentyfikowane bottlenecki:**
- [BOTTLENECK_1]: [OPIS PROBLEMU WYDAJNOŚCI]
- [BOTTLENECK_2]: [OPIS PROBLEMU WYDAJNOŚCI]

**Rekomendowane modernizacje:**
- [MODERNIZATION_1]: [OPIS POTRZEBNEJ MODERNIZACJI]
- [MODERNIZATION_2]: [OPIS POTRZEBNEJ MODERNIZACJI]
📋 ZAKRES ANALIZY LOGIKI BIZNESOWEJ - ROZSZERZONY
Przeanalizuj WSZYSTKIE pliki logiki biznesowej pod kątem modernizacji i wydajności:
🔍 Szukaj - Rozszerzone Kryteria

❌ Performance Bottlenecks - Synchronous I/O, blocking operations, memory leaks
❌ Thread Safety Issues - UI operations w background threads, race conditions
❌ Architecture Anti-patterns - God classes, circular dependencies, tight coupling
❌ Memory Management Issues - Wycieki pamięci, nadmierne zużycie, brak cleanup
❌ Outdated Patterns - Stare wzorce wymagające modernizacji do Python 3.9+

🎯 Podstawowa Funkcjonalność Biznesowa - Modernizacja

Async/Await Integration - Konwersja blocking operations na async
Type Safety - Implementacja pełnych type hints
Error Handling - Robust exception handling i recovery
Resource Management - Context managers i proper cleanup
Performance Monitoring - Metryki wydajności i profiling

⚡ Wydajność Procesów - Szczegółowa Analiza
MEMORY OPTIMIZATION:

Object Pooling - Reużywanie objects zamiast create/destroy
Lazy Loading - Opóźnione ładowanie komponentów UI
Cache Strategy - LRU cache dla często używanych danych
Memory Profiling - Identyfikacja memory leaks

I/O OPTIMIZATION:

Async File Operations - Konwersja sync I/O na async
Batch Processing - Grupowanie operacji I/O
Connection Pooling - Reużywanie połączeń
Progress Tracking - Feedback dla długich operacji

UI PERFORMANCE:

Virtual Scrolling - Renderowanie tylko widocznych elementów
Debounced Events - Opóźnione przetwarzanie zdarzeń UI
Progressive Enhancement - Stopniowe ładowanie funkcjonalności
GPU Acceleration - Wykorzystanie akceleracji sprzętowej

🏗️ Architektura Logiki - Modernizacja Wzorców
MODERN PATTERNS:

Repository Pattern - Abstrakcja dostępu do danych
Observer Pattern - Modernizacja signal-slot
Command Pattern - Implementacja undo/redo
Factory Pattern - Optymalizacja tworzenia obiektów

DEPENDENCY INJECTION:

Service Container - Centralne zarządzanie zależnościami
Interface Segregation - Podział dużych interfejsów
Inversion of Control - Odwrócenie kontroli zależności

🔒 Bezpieczeństwo i Stabilność - Rozszerzone
THREAD SAFETY:

QMutex Usage - Synchronizacja dostępu do zasobów
Signal-Slot Safety - Bezpieczne połączenia między wątkami
Atomic Operations - Operacje atomowe dla krytycznych danych
Resource Locking - Proper locking mechanisms

ERROR RECOVERY:

Circuit Breaker - Ochrona przed cascading failures
Retry Mechanisms - Automatyczne ponawianie operacji
Graceful Degradation - Płynne degradowanie funkcjonalności
Health Checks - Monitorowanie stanu komponentów

📊 Monitoring i Profiling - Nowe Wymagania
PERFORMANCE METRICS:

Response Time Tracking - Czas odpowiedzi operacji
Memory Usage Monitoring - Śledzenie zużycia pamięci
CPU Utilization - Wykorzystanie CPU przez komponenty
I/O Performance - Wydajność operacji wejścia/wyjścia

PROFILING TOOLS:

cProfile Integration - Profiling wydajności
memory_profiler - Analiza użycia pamięci
py-spy - Live profiling w production
Scalene - Combined CPU/memory profiling

🧪 Testowanie Logiki - Modernizacja
PERFORMANCE TESTING:

Load Testing - Testy obciążeniowe komponentów
Memory Testing - Testy memory leaks
UI Performance Tests - Testy responsywności interfejsu
Benchmark Tests - Pomiary wydajności algorytmów

MODERN TESTING PATTERNS:

Property-based Testing - Testy z hypothesis
Mutation Testing - Testy jakości testów
Integration Testing - Testy pełnych workflow'ów
Visual Regression Testing - Testy regresji UI

📋 Stan i Działania - Priorytety Modernizacji
KRYTYCZNE MODERNIZACJE:

Async I/O Conversion - Konwersja blocking operations
Memory Leak Fixes - Naprawa wycieków pamięci
Thread Safety Implementation - Zabezpieczenie wielowątkowości
UI Responsiveness - Poprawa responsywności interfejsu

WYSOKIE MODERNIZACJE:

Type Hints Implementation - Pełne adnotacje typów
Error Handling Enhancement - Robust exception handling
Cache Implementation - Implementacja cache'owania
Progress Tracking - Feedback dla użytkownika

🚫 UNIKAJ - Rozszerzone

❌ Synchronous I/O w głównym wątku UI
❌ Memory leaks w komponentach UI
❌ Thread safety violations
❌ Blocking operations bez progress indicators
❌ Outdated Python patterns (pre-3.9)
❌ God classes i long methods
❌ Circular dependencies
❌ Tight coupling between components

✅ SKUP SIĘ NA - Rozszerzone

✅ Async/await modernization - Konwersja na asynchroniczne operacje
✅ Memory optimization - Efektywne zarządzanie pamięcią
✅ Thread safety - Bezpieczeństwo operacji wielowątkowych
✅ UI responsiveness - Responsywność interfejsu użytkownika
✅ Type safety - Pełne adnotacje typów
✅ Error resilience - Odporność na błędy
✅ Performance monitoring - Monitorowanie wydajności
✅ Modern Python patterns - Najnowsze wzorce Python 3.9+

🎯 Pytania Kontrolne - Modernizacja

Czy można to przekonwertować na async/await? - Priorytet dla I/O operations
Czy jest thread-safe w kontekście PyQt6? - Krytyczne dla stabilności
Czy wykorzystuje najnowsze funkcje Python? - Modernizacja kodu
Czy ma proper type hints? - Type safety
Czy zarządza pamięcią efektywnie? - Memory optimization
Czy implementuje proper error handling? - Resilience
Czy można to zoptymalizować wydajnościowo? - Performance tuning
Czy interfejs pozostanie responsywny? - UX priority

📁 STRUKTURA PLIKÓW WYNIKOWYCH - ROZSZERZONA
Nowa struktura z analizą wydajności:
AUDYT/
├── business_logic_map.md              # Główna mapa z priorytetami wydajności
├── performance_analysis.md            # Szczegółowa analiza wydajności
├── modernization_roadmap.md           # Plan modernizacji architektury
├── corrections/
│   ├── [plik]_correction.md          # Standardowe poprawki
│   ├── [plik]_performance.md         # Analiza wydajności
│   └── [plik]_modernization.md       # Plan modernizacji
├── patches/
│   ├── [plik]_patch_code.md          # Poprawki kodu
│   ├── [plik]_async_patch.md         # Konwersja async/await
│   └── [plik]_optimization_patch.md  # Optymalizacje wydajności
└── monitoring/
    ├── performance_metrics.md         # Metryki wydajności
    ├── memory_analysis.md             # Analiza pamięci
    └── threading_analysis.md          # Analiza wielowątkowości
🚫 ZASADA INDYWIDUALNEGO GENEROWANIA DOKUMENTÓW - ROZSZERZONA
NOWE TYPY DOKUMENTÓW:

Performance Analysis - [nazwa]_performance.md - Analiza wydajności
Modernization Plan - [nazwa]_modernization.md - Plan modernizacji
Async Conversion - [nazwa]_async_patch.md - Konwersja async/await
Optimization Patches - [nazwa]_optimization_patch.md - Optymalizacje

📈 OBOWIĄZKOWA KONTROLA POSTĘPU - ROZSZERZONA
PRZYKŁAD ROZSZERZONEGO RAPORTU POSTĘPU:
📊 POSTĘP AUDYTU LOGIKI BIZNESOWEJ - MODERNIZACJA:
✅ Ukończone etapy: 3/15 (20%)
🔄 Aktualny etap: [NAZWA_PLIKU_LOGIKI_BIZNESOWEJ]
⏳ Pozostałe etapy: 12
💼 Business impact: [OPIS WPŁYWU NA PROCESY BIZNESOWE]
🚀 Performance impact: [OPIS WPŁYWU NA WYDAJNOŚĆ]
⚡ Modernization priority: [PRIORYTET MODERNIZACJI]
✅ UZUPEŁNIONO BUSINESS_LOGIC_MAP.MD: TAK
✅ UZUPEŁNIONO PERFORMANCE_ANALYSIS.MD: TAK
🚀 ROZPOCZĘCIE - ETAPOWANIE MODERNIZACJI
🚨 OBOWIĄZKOWE KROKI PRZED ROZPOCZĘCIEM:

Zapoznaj się z README.md - architektura, wymagania wydajnościowe, procesy biznesowe
Przeanalizuj strukturę projektu - dynamicznie odkryj katalogi i pliki
Wygeneruj mapę logiki biznesowej - z priorytetami wydajności i modernizacji
Stwórz plan modernizacji - roadmapa konwersji do nowoczesnych wzorców
Zidentyfikuj bottlenecki - krytyczne problemy wydajności do rozwiązania

ETAPY MODERNIZACJI:
ETAP 1: ANALIZA I MAPOWANIE (2-3 dni)

Mapowanie logiki biznesowej z priorytetami wydajności
Identyfikacja bottlenecków i anti-patterns
Stworzenie planu modernizacji

ETAP 2: KRYTYCZNE POPRAWKI WYDAJNOŚCI (3-5 dni)

Naprawa memory leaks w komponentach UI
Konwersja blocking I/O na async operations
Implementacja thread safety w krytycznych komponentach

ETAP 3: MODERNIZACJA ARCHITEKTURY (5-7 dni)

Implementacja Repository pattern
Modernizacja MVC do najnowszych standardów
Wprowadzenie dependency injection

ETAP 4: OPTYMALIZACJA WYDAJNOŚCI (3-5 dni)

Implementacja cache'owania i lazy loading
Virtual scrolling dla dużych zbiorów danych
Optymalizacja algorytmów w hot paths

ETAP 5: MONITORING I TESTOWANIE (2-3 dni)

Implementacja performance monitoring
Dodanie comprehensive test suite
Benchmark testing i profiling

Czekam na Twój pierwszy wynik: zawartość pliku business_logic_map.md z mapą plików logiki biznesowej oraz performance_analysis.md z analizą bottlenecków wydajności.
UWAGA: Mapa musi być wygenerowana na podstawie analizy aktualnego kodu z fokusem na wydajność oraz kontekstu biznesowego z README.md!
🚨 KRYTYCZNE ZASADY - MODEL MUSI PAMIĘTAĆ! - ROZSZERZONE
📋 OBOWIĄZKOWE UZUPEŁNIANIE DOKUMENTÓW MODERNIZACJI
🚨 MODEL MUSI PAMIĘTAĆ: Po każdej ukończonej analizie pliku logiki biznesowej OBOWIĄZKOWO uzupełnić wszystkie dokumenty modernizacji!
OBOWIĄZKOWE KROKI PO KAŻDEJ ANALIZIE:

✅ Ukończ analizę pliku - utwórz correction.md, performance.md, modernization.md
✅ OTWÓRZ business_logic_map.md - znajdź sekcję z analizowanym plikiem
✅ DODAJ status ukończenia - zaznacz że analiza została ukończona
✅ DODAJ performance impact - wpływ na wydajność aplikacji
✅ DODAJ modernization priority - priorytet modernizacji
✅ UZUPEŁNIJ performance_analysis.md - dodaj wykryte bottlenecki
✅ UZUPEŁNIJ modernization_roadmap.md - dodaj plan modernizacji

FORMAT UZUPEŁNIENIA - ROZSZERZONY:
markdown### 📄 [NAZWA_PLIKU].PY

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** [DATA]
- **Business impact:** [OPIS WPŁYWU NA PROCESY BIZNESOWE]
- **Performance impact:** [OPIS WPŁYWU NA WYDAJNOŚĆ]
- **Modernization priority:** [PRIORYTET MODERNIZACJI]
- **Bottlenecks found:** [LISTA WYKRYTYCH BOTTLENECKÓW]
- **Modernization needed:** [LISTA POTRZEBNYCH MODERNIZACJI]
- **Pliki wynikowe:**
  - `AUDYT/corrections/[nazwa_pliku]_correction.md`
  - `AUDYT/corrections/[nazwa_pliku]_performance.md`
  - `AUDYT/corrections/[nazwa_pliku]_modernization.md`
  - `AUDYT/patches/[nazwa_pliku]_patch_code.md`
  - `AUDYT/patches/[nazwa_pliku]_async_patch.md`
  - `AUDYT/patches/[nazwa_pliku]_optimization_patch.md`
🚨 MODEL NIE MOŻE ZAPOMNIEĆ O WSZYSTKICH KROKACH MODERNIZACJI!