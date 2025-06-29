### 🚀 core/scanner.py - Plan Modernizacji

**Plik:** `core/scanner.py`

#### **Obszary Modernizacji:**

1.  **Wprowadzenie Type Hints:**
    - **Cel:** Zwiększenie czytelności kodu, ułatwienie debugowania i wczesne wykrywanie błędów.
    - **Działania:** Dodanie pełnych adnotacji typów do wszystkich funkcji, metod i zmiennych, zwłaszcza w interfejsach publicznych.

2.  **Asynchroniczne Operacje I/O (dla generowania miniatur):**
    - **Cel:** Zapewnienie, że generowanie miniatur nie blokuje wątku skanującego, co poprawi ogólną responsywność aplikacji.
    - **Działania:** Refaktoryzacja `create_thumbnail_for_asset` w celu wykorzystania `QThreadPool` lub `asyncio` do asynchronicznego przetwarzania obrazów. Wymaga to odpowiedniego zarządzania sygnałami i slotami, aby aktualizować stan assetu po zakończeniu generowania miniatury.

3.  **Ulepszone Zarządzanie Zasobami (Context Managers):**
    - **Cel:** Zapewnienie prawidłowego zwalniania zasobów i unikanie wycieków.
    - **Działania:** Upewnienie się, że wszystkie operacje na plikach (np. otwieranie plików JSON) używają `with open(...)` dla bezpiecznego zarządzania zasobami.

4.  **Obsługa Błędów i Odporność:**
    - **Cel:** Zwiększenie odporności na błędy podczas skanowania i przetwarzania plików.
    - **Działania:** Upewnienie się, że wszystkie potencjalne błędy (np. uszkodzone pliki obrazów, brak uprawnień) są odpowiednio obsługiwane i komunikowane.

5.  **Testowanie Jednostkowe i Integracyjne:**
    - **Cel:** Zapewnienie stabilności i poprawności działania skanera po modernizacji.
    - **Działania:** Rozbudowa testów jednostkowych dla logiki skanowania, w tym testów wydajnościowych dla scenariuszy z dużą liczbą plików i obrazów.

#### **Kluczowe Działania Modernizacyjne:**

- **Refaktoryzacja `create_thumbnail_for_asset`:** Przeniesienie logiki generowania miniatur do asynchronicznego wykonania.
- **Wdrożenie cache'owania miniatur:** Aby uniknąć ponownego generowania dla już istniejących obrazów.
- **Dokumentacja:** Uzupełnienie dokumentacji kodu o szczegóły dotyczące zarządzania pamięcią i wydajności.
