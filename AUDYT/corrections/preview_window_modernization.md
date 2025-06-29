### 🚀 core/preview_window.py - Plan Modernizacji

**Plik:** `core/preview_window.py`

#### **Obszary Modernizacji:**

1.  **Wprowadzenie Type Hints:**
    - **Cel:** Zwiększenie czytelności kodu, ułatwienie debugowania i wczesne wykrywanie błędów.
    - **Działania:** Dodanie pełnych adnotacji typów do wszystkich funkcji, metod i zmiennych, zwłaszcza w interfejsach publicznych.

2.  **Ulepszone Zarządzanie Zasobami (Context Managers):**
    - **Cel:** Zapewnienie prawidłowego zwalniania zasobów i unikanie wycieków.
    - **Działania:** Chociaż `QPixmap` nie jest zasobem, który wymaga `with` statement, ogólna zasada zarządzania zasobami powinna być przestrzegana. Upewnienie się, że `original_pixmap` jest jawnie zwalniany, gdy okno jest zamykane.

3.  **Modernizacja Wzorców Architektonicznych (View):**
    - **Cel:** Ulepszenie implementacji widoku w kontekście PyQt6.
    - **Działania:** `PreviewWindow` jest prostym oknem dialogowym. Modernizacja może obejmować:
        - **Separacja logiki:** Upewnienie się, że logika ładowania i skalowania obrazu jest oddzielona od logiki wyświetlania okna. Można to osiągnąć poprzez delegowanie tych zadań do dedykowanej klasy pomocniczej.
        - **Asynchroniczne ładowanie/skalowanie:** Dla bardzo dużych obrazów, rozważenie asynchronicznego ładowania i skalowania, aby nie blokować UI.

4.  **Testowanie Jednostkowe i Integracyjne:**
    - **Cel:** Zapewnienie stabilności i poprawności działania okna podglądu po modernizacji.
    - **Działania:** Rozbudowa testów jednostkowych dla logiki ładowania i skalowania obrazów, w tym testów wydajnościowych dla dużych plików.

#### **Kluczowe Działania Modernizacyjne:**

- **Refaktoryzacja `load_image_and_resize` i `load_image`:** Wprowadzenie optymalizacji skalowania obrazów, aby uniknąć kosztownych operacji w `resizeEvent`.
- **Weryfikacja cyklu życia `QPixmap`:** Upewnienie się, że `original_pixmap` jest prawidłowo zwalniany, gdy okno jest zamykane.
- **Dokumentacja:** Uzupełnienie dokumentacji kodu o szczegóły dotyczące zarządzania pamięcią i wydajności.
