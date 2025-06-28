Prompt dla implementacji zakładki Parowanie w aplikacji
Zaimplementuj nową zakładkę "Parowanie" w aplikacji wykorzystując architekturę Model/View. Zakładka ma służyć do łączenia plików archiwów z podglądami w pary i tworzenia assetów.
Wymagania layoutu:

Podziel zakładkę na 3 kolumny w układzie poziomym
Kolumna lewa (200px): Lista plików archiwów z checkboxami
Kolumna środkowa (75px): 3 przyciski ułożone jeden pod drugim
Kolumna prawa (pozostała przestrzeń): Galeria podglądów z kafelkami

Szczegółowe wymagania funkcjonalne:
Kolumna lewa - Lista plików:

Wczytaj zawartość pliku unpair_files.json z folderu roboczego
Wyświetl listę z sekcji unpaired_archives
Każdy element listy ma zawierać:

Checkbox do zaznaczania
Nazwę pliku


Ograniczenie: Tylko jeden plik może być zaznaczony jednocześnie
Po kliknięciu w nazwę pliku uruchom zewnętrzny program do obsługi archiwum

Kolumna środkowa - Przyciski:

Umieść 3 przyciski (placeholdery) jeden pod drugim
Główny przycisk "Utwórz asset" z funkcjonalnością:

Aktywny tylko gdy zaznaczony jest jeden plik (lewa) i jeden podgląd (prawa)
Po kliknięciu:

Zmień nazwę pliku podglądu na odpowiadającą nazwie archiwum
Uruchom scanner dla tej pary plików
Utwórz odpowiedni plik asset
Wygeneruj plik thumb w folderze .cache
Zaktualizuj plik unpair_files.json
Odśwież zawartość obu list (lewa i prawa kolumna)





Kolumna prawa - Galeria podglądów:

Wyświetl podglądy z sekcji unpaired_previews w formie kafelków
Każdy kafelek zawiera:

Miniaturkę (docelowy plik, bez cache)
Nazwę pliku
Checkbox do zaznaczania


Ograniczenie: Tylko jeden kafelek może być zaznaczony jednocześnie
Dodaj suwak do powiększania widoku (podobnie jak w galerii głównej)
Po kliknięciu w miniaturkę wyświetl plik podglądu w osobnym oknie

Wymagania techniczne:
Model/View:

Utwórz odpowiednie klasy Model dla zarządzania danymi
Zaimplementuj View dla każdej kolumny
Zapewnij synchronizację między Model a View

Scanner:

Rozważ stworzenie dodatkowej klasy Scanner dla pojedynczych plików
Scanner ma generować pliki asset i thumb dla spaarowanych elementów

Zarządzanie stanem:

Implementuj obsługę radio-button behavior dla checkboxów (tylko jeden zaznaczony)
Zarządzaj stanem aktywności przycisku "Utwórz asset"
Zapewnij odświeżanie zawartości po wykonaniu operacji

Struktura danych:

Obsługuj format pliku unpair_files.json
Zaktualizuj strukturę po utworzeniu pary

Zaimplementuj tę funkcjonalność zachowując spójność z istniejącą architekturą aplikacji i stylem kodowania.
