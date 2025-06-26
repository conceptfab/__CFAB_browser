# 📋 KOREKTA PLIKU: main_window.py

**Data:** 2024-05-22

**Link do zasad refaktoryzacji:** [`refactoring_rules.md`](../../doc/refactoring_rules.md)

---

## 📊 WYNIKI ANALIZY

| Kategoria Błędu      | Opis Problemu                                                                                                                                            |     Priorytet     | Rekomendacja                                                                                                                                                                                         |
| :------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Logika Biznesowa** | Brak walidacji typów dla wartości w konfiguracji. Błędny typ (np. string zamiast int dla `thumbnail`) może powodować błędy w innych częściach aplikacji. | 🔴🔴🔴 **WYSOKI** | Wprowadzić walidację typów dla każdego klucza w `_load_config_safe` lub użyć dedykowanej klasy/struktury do zarządzania konfiguracją.                                                                |
| **Architektura**     | Silne powiązanie (tight coupling) `MainWindow` z konkretnymi klasami zakładek (`GalleryTab`, `PairingTab`). Utrudnia to testowanie i rozszerzalność.     |  🟡🟡 **ŚREDNI**  | Zastosować wstrzykiwanie zależności (Dependency Injection) do przekazywania klas lub instancji zakładek do `MainWindow`.                                                                             |
| **Logowanie**        | Komunikaty o błędach w `_load_config_safe` używają `print()` zamiast `logging`. Uniemożliwia to centralne zarządzanie logami i spójność.                 |  🟡🟡 **ŚREDNI**  | Zastąpić wszystkie wywołania `print()` w `_load_config_safe` odpowiednimi wywołaniami `self.logger.warning()` lub `self.logger.error()`. Logger musi być zainicjowany przed wczytaniem konfiguracji. |
| **Jakość Kodu**      | Konfiguracja jest zarządzana jako słownik. Prowadzi to do "stringly-typed" API i braku podpowiedzi typów, co utrudnia rozwój i refaktoryzację.           |  🟡🟡 **ŚREDNI**  | Stworzyć dedykowaną klasę (np. `dataclass` lub Pydantic model) do przechowywania konfiguracji, co zapewni bezpieczeństwo typów i lepszą organizację kodu.                                            |
| **Obsługa Błędów**   | W metodzie `_setup_logger` blok `except Exception` jest zbyt szeroki i może maskować błędy programistyczne.                                              |   🟢 **NISKI**    | Zamiast łapać ogólny `Exception`, należy łapać bardziej specyficzne wyjątki, które mogą wystąpić podczas konfiguracji loggera.                                                                       |

## 🎯 PODSUMOWANIE I REKOMENDACJE

`MainWindow` jest solidnie napisanym komponentem, pełniącym rolę orkiestratora aplikacji. Główne obszary do poprawy to **zarządzanie konfiguracją** i **redukcja powiązań między komponentami**.

**Kluczowe rekomendacje:**

1.  **Refaktoryzacja Konfiguracji (Priorytet: WYSOKI):**

    - Stworzyć dedykowaną klasę `AppConfig` (np. przy użyciu `dataclasses`) do zarządzania konfiguracją.
    - Przenieść logikę ładowania i walidacji do tej klasy. Zapewni to bezpieczeństwo typów i centralizację.
    - W `_load_config_safe` używać loggera zamiast `print`. Wymaga to wczesnej, podstawowej inicjalizacji loggera.

2.  **Wprowadzenie Wstrzykiwania Zależności (Priorytet: ŚREDNI):**
    - Zmodyfikować konstruktor `MainWindow`, aby przyjmował listę klas zakładek do utworzenia. Zmniejszy to powiązania i ułatwi dodawanie nowych zakładek oraz testowanie.

Zmiany te znacząco poprawią elastyczność, testowalność i bezpieczeństwo kodu, nie wpływając negatywnie na obecną funkcjonalność.

## 📈 PRZEWIDYWANY WPŁYW

- **Pozytywny:**
  - Zwiększona odporność na błędy w pliku konfiguracyjnym.
  - Ułatwione testowanie jednostkowe `MainWindow` dzięki mniejszym powiązaniom.
  - Lepsza czytelność i łatwość w utrzymaniu kodu dzięki obiektowi konfiguracyjnemu.
  - Spójne logowanie w całej aplikacji.
- **Negatywny:**
  - Brak. Zmiany są wewnętrzne i nie powinny wpłynąć na zachowanie aplikacji z perspektywy użytkownika.

---
