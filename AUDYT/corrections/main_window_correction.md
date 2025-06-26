# 📋 KOREKTA LOGIKI BIZNESOWEJ: `core/main_window.py`

- **Data analizy:** `2024-07-27`
- **Analizowany plik:** `core/main_window.py`
- **Priorytet:** `⚫⚫⚫⚫ KRYTYCZNE`

---

## 🎯 GŁÓWNY CEL KOREKTY

Celem tej korekty jest naprawa krytycznych błędów uniemożliwiających uruchomienie aplikacji oraz poprawa architektury w celu zapewnienia prawidłowego przekazywania zależności i zwiększenia stabilności. Główne okno jest fundamentem aplikacji, a jego nieprawidłowe działanie blokuje całą funkcjonalność.

## 📊 WYNIKI ANALIZY

| Kategoria Błędu                           | Opis Problemu                                                                                                                                                                                                                      |       Priorytet        | Rekomendacja                                                                                                                                                                                                                 |
| :---------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Błąd Krytyczny / Import**               | W pliku `main_window.py` klasa `QAction` jest importowana z `PyQt6.QtWidgets` zamiast z `PyQt6.QtGui`, co jest niezgodne z wersją PyQt6 i powoduje `ImportError` przy uruchamianiu aplikacji.                                      | ⚫⚫⚫⚫ **KRYTYCZNE** | Przenieść import `QAction` z `PyQt6.QtWidgets` do `PyQt6.QtGui`. To natychmiast naprawi błąd uniemożliwiający start aplikacji.                                                                                               |
| **Architektura / DI**                     | Instancja `GalleryTab` jest tworzona bez przekazania jej wymaganego obiektu konfiguracji. Po refaktoryzacji `GalleryTab` oczekuje na wstrzyknięcie zależności (DI), a jego brak powoduje błędy w działaniu tej kluczowej zakładki. |   🔴🔴🔴 **WYSOKI**    | Zmodyfikować tworzenie instancji `GalleryTab` w `_createTabs`, przekazując do jej konstruktora obiekt konfiguracji za pomocą `self.get_config()`.                                                                            |
| **Architektura / Ładowanie Konfiguracji** | Klasa `AppConfig` próbuje rzutować typy w locie, co jest niebezpieczne i może prowadzić do nieoczekiwanych błędów. Brakuje również bardziej szczegółowego logowania w przypadku problemów.                                         |    🟡🟡 **ŚREDNI**     | Uprościć logikę ładowania konfiguracji, unikając dynamicznego rzutowania typów. Dodać bardziej szczegółowe logi, aby ułatwić diagnozowanie problemów z plikiem `config.json`.                                                |
| **Odporność na Błędy**                    | Metoda `_createTabs` ma podstawową obsługę błędów, ale mogłaby być bardziej odporna na problemy z tworzeniem poszczególnych zakładek, zwłaszcza tych niekrytycznych.                                                               |      🟢 **NISKI**      | Rozbudować logikę w `_createTabs`, aby aplikacja mogła kontynuować działanie nawet jeśli jedna z niekrytycznych zakładek (`PairingTab`, `ToolsTab`) nie zostanie utworzona poprawnie, informując o tym użytkownika w logach. |

## 🎯 PODSUMOWANIE I REKOMENDACJE

1.  **Naprawa Błędu Importu (Priorytet: KRYTYCZNY):**

    - Natychmiastowa zmiana importu `QAction` na `from PyQt6.QtGui import QAction`. Jest to krok niezbędny do uruchomienia aplikacji.

2.  **Implementacja Wstrzykiwania Zależności (Priorytet: WYSOKI):**

    - Przekazanie konfiguracji do `GalleryTab` poprzez `GalleryTab(self.get_config())` w celu zapewnienia jej prawidłowego działania.

3.  **Refaktoryzacja Ładowania Konfiguracji (Priorytet: ŚREDNI):**
    - Poprawa metody `AppConfig.load`, aby była bardziej bezpieczna i zapewniała lepsze logowanie błędów konfiguracyjnych.

Te zmiany są kluczowe dla stabilności i dalszego rozwoju aplikacji. Usunięcie błędu krytycznego jest absolutnym priorytetem, a wdrożenie wstrzykiwania zależności naprawia fundamentalny problem architektoniczny wprowadzony w poprzednich krokach.
