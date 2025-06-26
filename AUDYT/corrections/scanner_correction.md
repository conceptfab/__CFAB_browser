# 📋 KOREKTA PLIKU: scanner.py

**Data:** 2024-05-22

**Link do zasad refaktoryzacji:** [`refactoring_rules.md`](../../doc/refactoring_rules.md)

---

## 📊 WYNIKI ANALIZY

| Kategoria Błędu      | Opis Problemu                                                                                                                                                                                                                 |     Priorytet     | Rekomendacja                                                                                                                                                                                       |
| :------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Wydajność**        | Funkcja `_get_files_by_extensions` wielokrotnie skanuje ten sam katalog dla każdego rozszerzenia (raz dla małych, raz dla dużych liter). Przy dużej liczbie plików i rozszerzeń prowadzi to do niepotrzebnego obciążenia I/O. | 🔴🔴🔴 **WYSOKI** | Zrefaktoryzować `_get_files_by_extensions`, aby skanowała katalog tylko raz (`os.listdir`) i filtrowała pliki w pamięci na podstawie rozszerzeń, ignorując wielkość liter.                         |
| **Logika Biznesowa** | Porównywanie nazw plików za pomocą `.lower()` jest niewystarczające. Systemy plików różnie traktują wielkość liter. Może to prowadzić do błędów w parowaniu na systemach, gdzie nazwy plików są case-sensitive.               | 🔴🔴🔴 **WYSOKI** | Używać `os.path.normcase()` do normalizacji ścieżek i nazw plików. Zapewni to spójne zachowanie niezależnie od systemu operacyjnego i jego ustawień dotyczących wielkości liter.                   |
| **Wydajność / I/O**  | Tworzenie zasobu (`.asset` i miniaturki) powoduje wielokrotne operacje I/O. `_create_single_asset` zapisuje plik, a `create_thumbnail_for_asset` ponownie go odczytuje i zapisuje.                                            |  🟡🟡 **ŚREDNI**  | Połączyć logikę. `_create_single_asset` powinna wywoływać logikę tworzenia miniaturki i ustawiać flagę `thumbnail: true` przed pierwszym zapisem pliku `.asset`.                                   |
| **Architektura**     | Moduł `scanner` jest silnie powiązany z modułem `thumbnail` przez bezpośredni import `process_thumbnail`. Utrudnia to testowanie jednostkowe i ewentualną wymianę implementacji.                                              |  🟡🟡 **ŚREDNI**  | Zastosować wstrzykiwanie zależności. Funkcja `find_and_create_assets` powinna przyjmować jako argument funkcję odpowiedzialną za tworzenie miniaturek (np. `thumbnail_processor`).                 |
| **Obsługa Błędów**   | Proces tworzenia zasobu nie jest atomowy. Jeśli tworzenie miniaturki (`process_thumbnail`) zawiedzie, plik `.asset` pozostaje w systemie z flagą `thumbnail: null`, co stanowi niespójny stan.                                |  🟡🟡 **ŚREDNI**  | Wprowadzić mechanizm transakcyjny. Zapisywać plik `.asset` do tymczasowej lokalizacji, a po pomyślnym utworzeniu miniaturki przenieść go do docelowej nazwy. W razie błędu usuwać plik tymczasowy. |
| **Jakość Kodu**      | Stała `FILE_EXTENSIONS` jest zdefiniowana na poziomie modułu. Przeniesienie jej do centralnej konfiguracji (np. `AppConfig`) zwiększyłoby elastyczność i ułatwiło zarządzanie.                                                |   🟢 **NISKI**    | Przenieść definicję `FILE_EXTENSIONS` do centralnego obiektu konfiguracyjnego, który byłby przekazywany do funkcji skanujących.                                                                    |

## 🎯 PODSUMOWANIE I REKOMENDACJE

Moduł `scanner.py` jest sercem aplikacji, ale jego obecna implementacja ma wady wydajnościowe i architektoniczne, które mogą stać się problematyczne przy pracy z dużymi zbiorami danych.

**Kluczowe rekomendacje:**

1.  **Optymalizacja Skanowania (Priorytet: WYSOKI):**

    - Zmienić implementację `_get_files_by_extensions` na jednokrotne listowanie katalogu i filtrowanie w pamięci.
    - Używać `os.path.normcase` do wszystkich porównań nazw plików, aby zapewnić niezawodność międzyplatformową.

2.  **Poprawa Procesu Tworzenia Zasobów (Priorytet: ŚREDNI):**

    - Połączyć tworzenie pliku `.asset` i miniaturki w jedną operację, aby zredukować operacje I/O.
    - Zaimplementować podstawową transakcyjność (np. zapis do pliku tymczasowego), aby uniknąć niespójnych stanów w przypadku błędów.

3.  **Wprowadzenie Wstrzykiwania Zależności (Priorytet: ŚREDNI):**
    - Przekazywać funkcję `thumbnail_processor` jako argument, aby oddzielić `scanner` od konkretnej implementacji tworzenia miniaturek.

Wprowadzenie tych zmian sprawi, że proces skanowania będzie znacznie szybszy, bardziej niezawodny i łatwiejszy w utrzymaniu oraz testowaniu.

## 📈 PRZEWIDYWANY WPŁYW

- **Pozytywny:**
  - Znaczące przyspieszenie skanowania folderów z dużą liczbą plików.
  - Zwiększona niezawodność parowania plików na różnych systemach operacyjnych.
  - Zmniejszenie liczby operacji I/O, co dodatkowo poprawi wydajność.
  - Zwiększenie odporności na błędy i unikanie pozostawiania "osieroconych" plików `.asset`.
  - Ułatwione testowanie jednostkowe modułu `scanner`.
- **Negatywny:**
  - Brak. Zmiany są wewnętrzne i nie powinny negatywnie wpłynąć na funkcjonalność.

---
