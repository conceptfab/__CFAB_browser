# 📋 KOREKTA PLIKU: gallery_tab.py

**Data:** 2024-05-22

**Link do zasad refaktoryzacji:** [`refactoring_rules.md`](../../doc/refactoring_rules.md)

---

## 📊 WYNIKI ANALIZY

| Kategoria Błędu          | Opis Problemu                                                                                                                                                                                                             |       Priorytet        | Rekomendacja                                                                                                                                                                                                                 |
| :----------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :--------------------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Architektura**         | Plik `gallery_tab.py` ma ponad 2600 linii i zawiera wiele klas (menedżer konfiguracji, menedżer siatki, workery, widgety). Narusza to zasadę pojedynczej odpowiedzialności (SRP) i ekstremalnie utrudnia utrzymanie kodu. | ⚫⚫⚫⚫ **KRYTYCZNE** | Podzielić plik na mniejsze, spójne moduły. Każda główna klasa (`ConfigManager`, `GridManager`, `AssetScanner`, `CustomTreeView` etc.) powinna znajdować się w osobnym pliku w dedykowanym podkatalogu, np. `core/gallery/`.  |
| **Architektura**         | `ConfigManager` zaimplementowany jako singleton w tym pliku. Jest to antywzorzec tworzący globalny stan i ukryte zależności, uniemożliwiając łatwe testowanie i konfigurację.                                             | ⚫⚫⚫⚫ **KRYTYCZNE** | Usunąć lokalny `ConfigManager`. Zamiast tego `GalleryTab` powinien otrzymywać obiekt konfiguracyjny (stworzony w `main_window.py`) przez wstrzykiwanie zależności w konstruktorze.                                           |
| **Wydajność / UX**       | Operacje I/O (usuwanie, kopiowanie plików w `delete_selected_assets`, `_move_selected_assets_to_folder`) są wykonywane synchronicznie w głównym wątku UI. Blokuje to interfejs przy operacjach na dużych plikach.         |   🔴🔴🔴 **WYSOKI**    | Przenieść wszystkie długotrwałe operacje plikowe do dedykowanych wątków roboczych (`QThread`), podobnie jak zrobiono to dla `AssetScanner`. Wątek powinien emitować sygnały o postępie i zakończeniu.                        |
| **Logika Biznesowa**     | Logika biznesowa jest silnie wymieszana z logiką UI. Metody w `GalleryTab` bezpośrednio manipulują plikami, zamiast delegować te zadania do dedykowanych serwisów lub kontrolerów.                                        |   🔴🔴🔴 **WYSOKI**    | Stworzyć dedykowaną klasę "serwisową" (np. `AssetService`), która będzie odpowiedzialna za operacje na zasobach (CRUD). `GalleryTab` powinien wywoływać metody tego serwisu, a nie bezpośrednio operować na systemie plików. |
| **Duplikacja Kodu**      | Funkcja `_check_texture_folders_presence` jest zduplikowana (występuje również w `scanner.py`). Zmiana logiki w jednym miejscu wymaga pamiętania o aktualizacji w drugim.                                                 |    🟡🟡 **ŚREDNI**     | Usunąć zduplikowaną metodę. Stworzyć jedną, wspólną funkcję w module `core.utils` lub podobnym, która będzie używana w obu miejscach.                                                                                        |
| **Zarządzanie Pamięcią** | Ręczne wywoływanie `gc.collect()` w `_clear_gallery_safe` jest niezalecane i może maskować problemy z cyklem życia obiektów. Prawidłowe zarządzanie rodzicielstwem w Qt powinno wystarczyć.                               |    🟡🟡 **ŚREDNI**     | Usunąć wywołanie `gc.collect()`. Upewnić się, że wszystkie widgety mają poprawnie ustawionego rodzica, co pozwoli mechanizmom Qt na automatyczne zwolnienie pamięci.                                                         |
| **Jakość Kodu**          | Import `find_and_create_assets` wewnątrz metody `_run_scanner` jest niekonwencjonalny i może spowalniać wykonanie oraz utrudniać analizę zależności.                                                                      |      🟢 **NISKI**      | Przenieść import `find_and_create_assets` na górę pliku, zgodnie ze standardami PEP 8.                                                                                                                                       |

## 🎯 PODSUMOWANIE I REKOMENDACJE

`gallery_tab.py` to najważniejszy i jednocześnie najbardziej problematyczny komponent aplikacji. Jego monolityczna struktura i mieszanie odpowiedzialności są głównym źródłem długu technicznego. Audyt tego pliku jest absolutnie krytyczny dla przyszłego rozwoju i stabilności projektu.

**Kluczowe rekomendacje:**

1.  **Refaktoryzacja Strukturalna (Priorytet: KRYTYCZNY):**

    - **Podział pliku:** Natychmiast podzielić `gallery_tab.py` na mniejsze pliki. Proponowana struktura:
      - `core/gallery/gallery_tab.py` (tylko główna klasa `GalleryTab`)
      - `core/gallery/grid_manager.py` (klasa `GridManager`)
      - `core/gallery/workers.py` (klasy `AssetScanner`, `AssetRebuilderThread`)
      - `core/gallery/widgets.py` (klasy `CustomTreeView`, `DropHighlightDelegate`)
    - **Usunięcie `ConfigManager`:** Pozbyć się lokalnego singletonu i przekazywać konfigurację przez konstruktor `GalleryTab`.

2.  **Oddzielenie Logiki od UI (Priorytet: WYSOKI):**
    - Stworzyć nową warstwę serwisową (`AssetService`), która zajmie się logiką operacji na plikach.
    - Wszystkie operacje I/O przenieść do wątków roboczych, aby UI pozostało w pełni responsywne.

Te zmiany są fundamentalne. Bez ich wprowadzenia, dalszy rozwój aplikacji będzie bardzo trudny, a jej stabilność i wydajność będą stale zagrożone.

## 📈 PRZEWIDYWANY WPŁYW

- **Pozytywny:**
  - Drastyczna poprawa czytelności i łatwości utrzymania kodu.
  - Zwiększenie responsywności interfejsu użytkownika, eliminacja "zamrożeń" podczas operacji na plikach.
  - Ułatwione testowanie jednostkowe poszczególnych komponentów.
  - Zmniejszenie ryzyka regresji dzięki lepszemu odizolowaniu logiki.
- **Negatywny:**
  - Refaktoryzacja będzie wymagała znaczących zmian w strukturze projektu i może tymczasowo wprowadzić błędy, jeśli nie zostanie przeprowadzona ostrożnie.

---
