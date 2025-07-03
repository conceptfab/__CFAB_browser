# 🎯 CEL ZADANIA

## 🎯 CEL zadania

Przeprowadź audyt i przygotuj plan refaktoryzacji kodu aplikacji, eliminując over-engineering przy zachowaniu funkcjonalności.
Obszary do audytu

1. Architektura i wzorce projektowe

Zidentyfikuj wszystkie implementacje Repository pattern i oceń ich konieczność
Sprawdź użycie abstrakcyjnych interfejsów - które można usunąć bez utraty funkcjonalności
Oceń dependency injection - gdzie można zastąpić prostymi importami
Przeanalizuj wzorzec MVC vs Model-View (PyQt preferuje Model-View)
Zidentyfikuj singleton patterns i global managers - które można uprościć

2. Struktura plików i modułów

Policzy pliki i klasy - zaproponuj konsolidację
Znajdź małe klasy (< 50 linii) które można scalić
Zidentyfikuj duplicate functionality między modułami
Oceń czy podział na foldery amv_models/, amv_views/, amv_controllers/ jest uzasadniony
Sprawdź "wrapper functions" zachowujące kompatybilność wsteczną

3. Nadmiarowe abstrakcje

Znajdź klasy które są tylko proxy/wrapper dla innych klas
Zidentyfikuj factory patterns używane tylko w jednym miejscu
Oceń performance monitoring - czy jest wszędzie potrzebny
Sprawdź object pooling i cache - czy to przedwczesna optymalizacja
Przeanalizuj async/threading - czy jest uzasadnione

4. Dependency injection i konstrukcja obiektów

Znajdź konstruktory z > 5 parametrami opcjonalnymi
Zidentyfikuj miejsca gdzie DI można zastąpić prostym importem
Oceń czy "fallback to default instances" jest potrzebne
Sprawdź chains of dependencies - gdzie można uprościć

5. Kod boilerplate i redundancja

Znajdź powtarzające się patterns w różnych klasach
Zidentyfikuj podobne metody które można zunifikować
Oceń ilość kodu związanego z setup/teardown
Sprawdź czy wszystkie property getters/setters są potrzebne

6. PyQt specific patterns

Oceń czy używanie zarówno Qt Model/View i własnego MVC jest sensowne
Sprawdź sygnały i sloty - czy nie ma over-connectingu
Zidentyfikuj custom widgets które powielają standard Qt functionality
Oceń threading patterns - czy QThread jest prawidłowo używany

Plan refaktoryzacji
Priorytet 1: Architektura

Usuń Repository interfaces - zastąp bezpośrednimi klasami
Uprość dependency injection - używaj tylko tam gdzie rzeczywiście potrzebne
Scal małe modele - połącz related functionality w jeden plik
Uprość Controller construction - maksymalnie 3 parametry

Priorytet 2: Struktura plików

Konsoliduj pliki - target: maksymalnie 15-20 plików zamiast 35
Usuń zbędne init.py importy
Scal views - połącz related widgets w jeden plik
Usuń wrapper functions - pozostaw tylko nowe API

Priorytet 3: Uproszczenia kodu

Usuń przedwczesne optymalizacje (object pooling, excessive caching)
Uprość error handling - usuń try/catch gdzie nie są potrzebne
Usuń global managers - zastąp lokalnymi instancjami
Uprość configuration loading - jeden centralny miejsce

Kryteria sukcesu

Redukcja o 30-40% linii kodu bez utraty funkcjonalności
Maksymalnie 20 plików w strukturze projektu
Eliminacja wszystkich abstract interfaces które mają tylko jedną implementację
Uproszczenie konstruktorów - maksymalnie 3 parametry obowiązkowe
Zachowanie wszystkich funkcji aplikacji

Rzeczy do zachowania

Logowanie i error handling - struktura jest dobra
Configuration management - ale uprościć ładowanie
Asset management core logic - tylko uprościć warstwy
PyQt widgets i layouts - działają dobrze
File operations - ale bez Repository pattern

Output format
Przedstaw wyniki jako:

Lista konkretnych plików do usunięcia/scalenia
Mapa refaktoryzacji klas (co gdzie przenieść)
Nowa struktura folderów (target state)
Priority list zmian (co najpierw)
Oszacowanie redukcji kodu (% i linie)
