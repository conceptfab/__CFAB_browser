### 🚀 control_panel_model.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

Model `ControlPanelModel` jest prosty i funkcjonalny. Poniższe propozycje modernizacji mają na celu głównie poprawę jakości kodu, jego czytelności i przygotowanie na przyszły rozwój, a nie naprawę istniejących problemów.

1.  **Wprowadzenie `dataclass` dla Stanu Modelu:**
    -   **Cel:** Hermetyzacja stanu modelu w jednej, typowanej strukturze danych, co zwiększy czytelność i ułatwi zarządzanie.
    -   **Plan Działania:**
        1.  Zdefiniować `ControlPanelState` jako `dataclass`:
            ```python
            from dataclasses import dataclass

            @dataclass
            class ControlPanelState:
                progress: int = 0
                thumbnail_size: int = 256
                has_selection: bool = False
            ```
        2.  Model `ControlPanelModel` będzie przechowywał jedną instancję `self._state: ControlPanelState`.
        3.  Metody `set_*` będą modyfikować odpowiednie pola w `self._state`.
        4.  Dodać jeden sygnał `state_changed = pyqtSignal(ControlPanelState)`, który będzie emitowany po każdej zmianie stanu. Pozwoli to na bardziej elastyczne reagowanie na zmiany w widoku.

2.  **Pełne Adnotacje Typów:**
    -   **Cel:** Poprawa czytelności i umożliwienie statycznej analizy kodu.
    -   **Plan Działania:**
        1.  Upewnić się, że wszystkie metody i atrybuty mają precyzyjne adnotacje typów.

3.  **Ujednolicenie API (Opcjonalnie):**
    -   **Cel:** Zapewnienie spójnego sposobu dostępu do danych.
    -   **Plan Działania:**
        1.  Jeśli zostanie wprowadzony `ControlPanelState`, metody `get_progress`, `get_thumbnail_size`, `get_has_selection` mogą zostać zastąpione przez bezpośredni dostęp do pól obiektu stanu (np. `model.state.progress`).
        2.  Alternatywnie, można zaimplementować właściwości (`@property`) dla tych atrybutów, aby zachować spójny interfejs.
