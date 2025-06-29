### 🚀 core/amv_views/preview_gallery_view.py - Plan Modernizacji

**Plik:** `core/amv_views/preview_gallery_view.py`

#### **Obszary Modernizacji:**

1.  **Wprowadzenie Type Hints:**
    - **Cel:** Zwiększenie czytelności kodu, ułatwienie debugowania i wczesne wykrywanie błędów.
    - **Działania:** Dodanie pełnych adnotacji typów do wszystkich funkcji, metod i zmiennych, zwłaszcza w interfejsach publicznych.

2.  **Modernizacja Wzorców Architektonicznych (View):**
    - **Cel:** Ulepszenie implementacji wzorca View w kontekście PyQt6, aby lepiej wspierać duże zbiory danych i złożone interakcje.
    - **Działania:**
        - **Implementacja Object Pooling/Virtual Scrolling:** Jest to najważniejszy punkt modernizacji. Zamiast niszczyć i tworzyć `PreviewTile` przy każdej zmianie rozmiaru, należy zaimplementować mechanizm ponownego wykorzystania istniejących instancji (object pooling) lub renderowania tylko widocznych elementów (virtual scrolling). Może to wymagać stworzenia dedykowanego menedżera dla `PreviewTile`.
        - **Separacja odpowiedzialności:** Upewnienie się, że `PreviewGalleryView` jest odpowiedzialny tylko za układ i zarządzanie widokami, a ładowanie i cache'owanie obrazów jest delegowane do innych komponentów.

3.  **Optymalizacja Zarządzania Zasobami Graficznymi:**
    - **Cel:** Zminimalizowanie obciążenia związanego z tworzeniem i zarządzaniem obiektami `QPixmap`.
    - **Działania:** Centralizacja ładowania i cache'owania miniatur. `PreviewTile` powinien jedynie wyświetlać gotowe `QPixmap` dostarczone przez model lub dedykowany serwis, zamiast samodzielnie je ładować i skalować.

4.  **Ulepszone Zarządzanie Połączeniami Sygnał-Slot:**
    - **Cel:** Zapewnienie, że połączenia sygnał-slot są prawidłowo rozłączane, aby zapobiec wyciekom pamięci i niestabilności.
    - **Działania:** Weryfikacja cyklu życia `PreviewGalleryView` i jego połączeń. Upewnienie się, że połączenia z `PreviewTile` są prawidłowo zarządzane, zwłaszcza gdy `PreviewTile` są ponownie wykorzystywane z puli.

5.  **Testowanie Jednostkowe i Integracyjne:**
    - **Cel:** Zapewnienie stabilności i poprawności działania widoku po modernizacji.
    - **Działania:** Rozbudowa testów jednostkowych dla logiki widoku, w tym testów wydajnościowych dla scenariuszy z dużą liczbą podglądów i szybkim przewijaniem/zmianą rozmiaru.

#### **Kluczowe Działania Modernizacyjne:**

- **Refaktoryzacja `set_previews` i `resizeEvent`:** Zmiana logiki tych metod, aby wykorzystywały object pooling/virtual scrolling zamiast ciągłego tworzenia/niszczenia widżetów.
- **Weryfikacja cyklu życia obiektów:** Upewnienie się, że wszystkie obiekty są prawidłowo niszczone, aby zapobiec wyciekom pamięci, zwłaszcza w przypadku dynamicznie tworzonych elementów UI.
- **Dokumentacja:** Uzupełnienie dokumentacji kodu o szczegóły dotyczące zarządzania pamięcią i wydajności.
