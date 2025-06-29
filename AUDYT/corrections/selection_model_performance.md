### ⚡ selection_model.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Główne Problemy Wydajnościowe:

1.  **Brak Obsługi Operacji Wsadowych (WYSOKI PRIORYTET):**
    -   **Problem:** To główny problem wydajnościowy tego modelu, wskazany w `stage_2.md` jako potrzeba "batch operations". Każde wywołanie `add_selection` lub `remove_selection` powoduje natychmiastową emisję sygnału `selection_changed`. W przypadku operacji masowych, takich jak "Zaznacz wszystko" na 10 000 assetów, spowoduje to wyemitowanie 10 000 sygnałów. Każdy taki sygnał może uruchamiać sloty w kontrolerze i widoku, które aktualizują stan przycisków, liczniki itp., co prowadzi do katastrofalnej wydajności i potencjalnego zamrożenia aplikacji.
    -   **Rekomendacja (WYSOKA):** Należy zaimplementować mechanizm do obsługi operacji wsadowych. Można to zrobić na dwa sposoby:
        1.  **Jawne Metody Wsadowe:** Dodać metody `add_multiple(ids)`, `remove_multiple(ids)`, `set_selection(ids)`. Metody te powinny modyfikować wewnętrzny zbiór, a następnie wyemitować sygnał `selection_changed` **tylko raz**, na samym końcu operacji.
        2.  **Transakcyjność:** Dodać metody `begin_update()` i `end_update()`. Przed serią zmian kontroler wywołuje `begin_update()`, co ustawia flagę blokującą emisję sygnałów. Po wykonaniu wszystkich operacji `add/remove`, kontroler wywołuje `end_update()`, która emituje jeden, zbiorczy sygnał `selection_changed`.

2.  **Niepotrzebna Konwersja `set` na `list`:**
    -   **Problem:** Metody `_emit_selection_changed` i `get_selected_asset_ids` konwertują zbiór na listę (`list(self._selected_asset_ids)`). Dla bardzo dużych zbiorów zaznaczeń (dziesiątki tysięcy elementów) ta konwersja nie jest darmowa – wymaga alokacji nowej pamięci i iteracji po całym zbiorze.
    -   **Rekomendacja (ŚREDNIA):** Należy zmodyfikować API modelu, aby zwracało i emitowało zbiory (`set`). Zbiory są naturalną strukturą dla przechowywania unikalnych ID. Uniknie się w ten sposób niepotrzebnych konwersji. Komponenty korzystające z tego modelu mogą w razie potrzeby same dokonać konwersji.

#### Pozytywne Aspekty:

-   **Użycie `set`:** Wybór zbioru (`set`) jako wewnętrznej struktury danych do przechowywania ID jest bardzo dobrym rozwiązaniem z punktu widzenia wydajności. Zapewnia on średni czas dostępu, dodawania i usuwania na poziomie O(1).
