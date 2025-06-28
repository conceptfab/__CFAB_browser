📋 INSTRUKCJA WPROWADZENIA ARCHITEKTURY MODEL/VIEW W CFAB_3DHUB

WAŻNE! Wszystkie pliki wynikowe refaktoryzacji (np. business_logic_map.md, corrections.md, patch_code.md, pliki z analizami i poprawkami) MUSZĄ być zapisywane wyłącznie w katalogu AUDYT. Tylko tam należy ich szukać!

🎯 CEL REFAKTORYZACJI
Wprowadzenie architektury Model/View do aplikacji CFAB_3DHUB z zachowaniem 100% funkcjonalności kodu i UI, zgodnie z trzema filarami audytu logiki biznesowej: WYDAJNOŚĆ PROCESÓW, STABILNOŚĆ OPERACJI i WYELIMINOWANIE OVER-ENGINEERING.
🏛️ TRZY FILARY REFAKTORYZACJI MODEL/VIEW
1️⃣ WYDAJNOŚĆ PROCESÓW ⚡

Optymalizacja renderowania UI przez delegaty Model/View
Redukcja zużycia pamięci przy dużych zbiorach danych w galerii
Eliminacja niepotrzebnych odświeżeń całego UI
Usprawnienie cache'owania miniatur przez modele
Lazy loading danych w widokach

2️⃣ STABILNOŚĆ OPERACJI 🛡️

Thread safety w operacjach Model/View PyQt6
Proper error handling w kontrolerach
Eliminacja memory leaks w widgetach UI
Przewidywalność zachowania sygnałów/slotów
Atomowość operacji na modelach danych

3️⃣ WYELIMINOWANIE OVER-ENGINEERING 🎯

Zastąpienie skomplikowanych custom widgetów standardowymi Qt widokami
Eliminacja niepotrzebnych abstrakcji w UI
Konsolidacja rozproszonej logiki UI w kontrolerach
Uproszczenie zarządzania stanem UI

📋 ETAP 1: MAPOWANIE LOGIKI BIZNESOWEJ UI
🗺️ DYNAMICZNE GENEROWANIE MAPY PLIKÓW UI DO REFAKTORYZACJI
Model MUSI dynamicznie przeanalizować strukturę projektu i zidentyfikować pliki odpowiedzialne za:
📋 KLUCZOWE KOMPONENTY UI DO ANALIZY
Model MUSI przeanalizować każdy plik i określić czy zawiera:

Komponenty galerii - główny interfejs wyświetlania danych
Komponenty kafelków - elementy wizualizacji pojedynczych elementów
Zarządzanie danymi UI - modele danych, cache, metadane
Kontrolery UI - obsługa zdarzeń, koordynacja
Custom widgety - niestandardowe komponenty interfejsu
Renderowanie - logika wyświetlania, delegaty

🎯 PRIORYTETY REFAKTORYZACJI MODEL/VIEW
⚫⚫⚫⚫ KRYTYCZNE - Komponenty wymagające natychmiastowej refaktoryzacji:

Główne komponenty galerii (renderowanie, wydajność)
Zarządzanie danymi galerii (modele, cache)
Kontrolery głównego UI (stabilność, thread safety)

🔴🔴🔴 WYSOKIE - Komponenty ważne dla architektury:

Komponenty kafelków (delegaty, renderowanie)
Serwisy UI (cache, metadane)
Kontrolery zdarzeń (obsługa interakcji)

🟡🟡 ŚREDNIE - Komponenty pomocnicze:

Utility widgety (toolbar, statusbar)
Konfiguracja UI (settings, preferences)

🟢 NISKIE - Komponenty dodatkowe:

Debugging UI (narzędzia deweloperskie)
Optional components (dodatkowe funkcje)

📊 SZABLON MAPY UI DO WYPEŁNIENIA
markdown### 🗺️ MAPA PLIKÓW UI DO REFAKTORYZACJI MODEL/VIEW

**Wygenerowano na podstawie analizy kodu: [DATA]**

#### **KOMPONENTY GALERII** ⚫⚫⚫⚫

[ŚCIEŻKA_KATALOGU]/
├── [plik_galerii].py ⚫⚫⚫⚫ - [OPIS ROLI W UI] -> GalleryView + GalleryModel
├── [plik_danych].py ⚫⚫⚫⚫ - [OPIS ZARZĄDZANIA DANYMI] -> GalleryModel + CacheModel
└── [plik_kontrolera].py ⚫⚫⚫⚫ - [OPIS KONTROLI] -> GalleryController

#### **KOMPONENTY KAFELKÓW** 🔴🔴🔴

[ŚCIEŻKA_KATALOGU]/
├── [plik_kafelka].py 🔴🔴🔴 - [OPIS KAFELKA] -> TileWidget + TileDelegate
├── [plik_metadanych].py 🔴🔴🔴 - [OPIS METADANYCH] -> MetadataModel
└── [plik_renderowania].py 🔴🔴🔴 - [OPIS RENDEROWANIA] -> TileDelegate

#### **KONTROLERY UI** 🔴🔴🔴

[ŚCIEŻKA_KATALOGU]/
├── [plik_main_controller].py 🔴🔴🔴 - [OPIS GŁÓWNEGO KONTROLERA] -> MainController
├── [plik_event_handler].py 🔴🔴🔴 - [OPIS OBSŁUGI ZDARZEŃ] -> EventController
└── [plik_state_manager].py 🔴🔴🔴 - [OPIS ZARZĄDZANIA STANEM] -> StateController

📁 STRUKTURA PLIKÓW WYNIKOWYCH REFAKTORYZACJI
Dla każdego analizowanego pliku UI [nazwa_pliku].py:

Skopiuj **doc/correction_template.md do AUDYT/corrections/[nazwa_pliku]\_mv_correction.md
Wypełnij zgodnie z analizą refaktoryzacji Model/View
Skopiuj **doc/patch_code_template.md do AUDYT/patches/[nazwa_pliku]\_mv_patch_code.md
Wypełnij fragmentami kodu refaktoryzacji Model/View

🚫 ZASADA INDYWIDUALNEGO GENEROWANIA DOKUMENTÓW REFAKTORYZACJI
OBOWIĄZKOWE ZASADY:

Jeden plik UI = jeden correction - Każdy plik .py ma SWÓJ plik [nazwa]_mv_correction.md
Jeden plik UI = jeden patch - Każdy plik .py ma SWÓJ plik [nazwa]\_mv_patch_code.md
Brak grupowania - NIGDY nie łącz refaktoryzacji wielu plików w jeden dokument
Prefiks MV - Każdy dokument ma prefiks \_mv_ dla odróżnienia od standardowego audytu

PRZYKŁADY POPRAWNEJ STRUKTURY:
AUDYT/corrections/
├── [plik_galerii]\_mv_correction.md ✅ Refaktoryzacja Model/View
├── [plik_kafelka]\_mv_correction.md ✅ Refaktoryzacja Model/View  
├── [plik_kontrolera]\_mv_correction.md ✅ Refaktoryzacja Model/View
└── [plik_danych]\_mv_correction.md ✅ Refaktoryzacja Model/View

AUDYT/patches/
├── [plik_galerii]\_mv_patch_code.md ✅ Kod refaktoryzacji
├── [plik_kafelka]\_mv_patch_code.md ✅ Kod refaktoryzacji
├── [plik_kontrolera]\_mv_patch_code.md ✅ Kod refaktoryzacji  
└── [plik_danych]\_mv_patch_code.md ✅ Kod refaktoryzacji
🔍 ZAKRES ANALIZY REFAKTORYZACJI MODEL/VIEW
🎯 ANALIZA KOMPONENTÓW UI
Dla każdego pliku UI przeanalizuj:
🖼️ KOMPONENTY WIDOKÓW

Obecna architektura - Jak obecnie zorganizowane są widoki
Custom widgety - Które można zastąpić standardowymi Qt
Data binding - Jak obecnie dane są bindowane do UI
Event handling - Jak obecnie obsługiwane są zdarzenia
Layout management - Jak zarządzane są układy

📊 KOMPONENTY DANYCH

Data structures - Jak obecnie przechowywane są dane
Cache mechanisms - Mechanizmy cache dla UI
Data updates - Jak aktualizowane są dane w UI
Memory management - Zarządzanie pamięcią dla UI
Thread safety - Bezpieczeństwo wątków w UI

🎮 KOMPONENTY KONTROLI

Business logic in UI - Logika biznesowa w widokach
State management - Zarządzanie stanem aplikacji
Component communication - Komunikacja między komponentami
Event coordination - Koordynacja zdarzeń
Error handling - Obsługa błędów w UI

✅ KRYTERIA REFAKTORYZACJI
Szukaj w każdym pliku:
❌ PROBLEMY DO NAPRAWIENIA

Tight coupling - Ścisłe powiązanie UI z danymi
Business logic in views - Logika biznesowa w widokach
Manual data synchronization - Ręczna synchronizacja danych
Custom implementations - Niestandardowe implementacje zamiast Qt
Thread safety issues - Problemy z bezpieczeństwem wątków
Memory leaks in UI - Wycieki pamięci w komponentach UI
Over-engineered solutions - Nadmiernie skomplikowane rozwiązania

✅ CELE REFAKTORYZACJI

Separation of concerns - Rozdzielenie odpowiedzialności
Standard Qt patterns - Użycie standardowych wzorców Qt
Automatic data binding - Automatyczne bindowanie danych
Signal/slot architecture - Architektura sygnałów/slotów
Model/View delegation - Delegacja renderowania
Thread safety - Bezpieczne operacje wielowątkowe
Memory efficiency - Efektywne zarządzanie pamięcią

📋 TEMPLATE ANALIZY PLIKU UI
markdown## 📄 ANALIZA REFAKTORYZACJI: [NAZWA_PLIKU].PY

### **🎯 OBECNA ARCHITEKTURA**

- **Typ komponentu:** [Widget/Controller/Model/Service]
- **Główne odpowiedzialności:** [LISTA ODPOWIEDZIALNOŚCI]
- **Zależności:** [LISTA ZALEŻNOŚCI]
- **Dane zarządzane:** [TYPY DANYCH]

### **❌ PROBLEMY DO NAPRAWIENIA**

- **Problem 1:** [OPIS] - [WPŁYW NA WYDAJNOŚĆ/STABILNOŚĆ]
- **Problem 2:** [OPIS] - [WPŁYW NA WYDAJNOŚĆ/STABILNOŚĆ]
- **Problem 3:** [OPIS] - [WPŁYW NA OVER-ENGINEERING]

### **✅ PLAN REFAKTORYZACJI MODEL/VIEW**

- **Docelowa architektura:** [Model/View/Controller/Delegate]
- **Klasy Qt do użycia:** [QAbstractListModel/QListView/QStyledItemDelegate]
- **Podział odpowiedzialności:** [MODEL: ... / VIEW: ... / CONTROLLER: ...]
- **Zachowanie funkcjonalności:** [LISTA FUNKCJI DO ZACHOWANIA]

### **🔧 ZMIANY TECHNICZNE**

- **Zmiana 1:** [OPIS ZMIANY] - [UZASADNIENIE]
- **Zmiana 2:** [OPIS ZMIANY] - [UZASADNIENIE]
- **Zmiana 3:** [OPIS ZMIANY] - [UZASADNIENIE]

### **⚡ WPŁYW NA WYDAJNOŚĆ**

- **Renderowanie:** [OPIS POPRAWY]
- **Pamięć:** [OPIS OPTYMALIZACJI]
- **Responsywność:** [OPIS POPRAWY]

### **🛡️ WPŁYW NA STABILNOŚĆ**

- **Thread safety:** [OPIS POPRAWY]
- **Error handling:** [OPIS POPRAWY]
- **Memory management:** [OPIS POPRAWY]

### **🎯 ELIMINACJA OVER-ENGINEERING**

- **Uproszczenie 1:** [OPIS]
- **Uproszczenie 2:** [OPIS]
- **Konsolidacja:** [OPIS]
  📈 OBOWIĄZKOWA KONTROLA POSTĘPU REFAKTORYZACJI
  Po każdym ukończonym pliku UI model MUSI:
  markdown📊 POSTĘP REFAKTORYZACJI MODEL/VIEW:
  ✅ Ukończone pliki UI: X/Y (Z%)
  🔄 Aktualny plik: [NAZWA_PLIKU_UI]
  ⏳ Pozostałe pliki: [LICZBA]
  💼 Wpływ na architekturę: [OPIS WPŁYWU]
  ✅ UZUPEŁNIONO BUSINESS_LOGIC_MAP.MD: TAK/NIE
  ✅ ZAZNACZANIE UKOŃCZONYCH REFAKTORYZACJI
  Po każdej ukończonej refaktoryzacji pliku UI:
  markdown### 📄 [NAZWA_PLIKU].PY

- **Status:** ✅ UKOŃCZONA REFAKTORYZACJA MODEL/VIEW
- **Data ukończenia:** [DATA]
- **Typ refaktoryzacji:** [Model/View/Controller/Delegate]
- **Wpływ na architekturę:** [OPIS WPŁYWU NA ARCHITEKTURĘ]
- **Pliki wynikowe:**
  - `AUDYT/corrections/[nazwa_pliku]_mv_correction.md`
  - `AUDYT/patches/[nazwa_pliku]_mv_patch_code.md`
    🚀 ROZPOCZĘCIE REFAKTORYZACJI
    🚨 OBOWIĄZKOWE KROKI PRZED ROZPOCZĘCIEM:

Zapoznaj się z README.md - architektura UI, wymagania wydajnościowe
Przeanalizuj strukturę UI - dynamicznie odkryj komponenty galerii i kafli
Wygeneruj mapę UI - na podstawie analizy kodu i kontekstu z README.md
Zidentyfikuj priorytety - które komponenty wymagają natychmiastowej refaktoryzacji

Czekam na Twój pierwszy wynik: zawartość pliku business_logic_map.md z mapą plików UI do refaktoryzacji Model/View.
UWAGA: Mapa musi być wygenerowana na podstawie analizy aktualnego kodu oraz kontekstu UI z README.md!
🚨 KRYTYCZNE ZASADY REFAKTORYZACJI - MODEL MUSI PAMIĘTAĆ!
📋 OBOWIĄZKOWE UZUPEŁNIANIE BUSINESS_LOGIC_MAP.MD
🚨 Po każdej ukończonej refaktoryzacji pliku UI OBOWIĄZKOWO uzupełnić AUDYT/business_logic_map.md!
🎯 ZACHOWANIE WYGLĄDU GALERII I KAFLI
🚨 KRYTYCZNE: 100% zachowanie wyglądu galerii i kafli!

Identyczne rozmiary - dokładnie te same wymiary
Identyczne kolory - zachowanie palety kolorów
Identyczne fonty - rodzina i rozmiary fontów
Identyczne układy - pozycje i spacing elementów
Identyczne animacje - wszystkie przejścia i efekty
Identyczna responsywność - zachowanie przy zmianie rozmiaru

⚡ PRIORYTET WYDAJNOŚCI UI

Renderowanie - delegaty Model/View dla optymalnego renderowania
Pamięć - efektywne zarządzanie pamięcią w modelach
Cache - inteligentne cache'owanie w modelach danych
Threading - bezpieczne operacje wielowątkowe
Lazy loading - ładowanie danych na żądanie

Model musi sprawdzać każdy punkt przed przejściem do następnego pliku!
