# Raport audytu kodu `core/` (do poprawy)

## 1. Duplikaty i powielona logika

1. **`core/tools/file_renamer_worker.py` oraz `core/tools/file_shortener_worker.py`**
   - Oba pliki mają bardzo podobną strukturę i powielają logikę analizy plików, obsługi par, potwierdzeń użytkownika oraz obsługi błędów.
   - Zalecenie: Wydziel wspólną logikę do klasy bazowej lub funkcji pomocniczych, aby uniknąć duplikacji kodu.

## 2. Nieużywane lub zbędne funkcje

2. **`core/tools/duplicate_finder_worker.py`**
   - Funkcja `_move_related_files` jest zaimplementowana, ale jej wywołanie jest zakomentowane w `_move_duplicates_to_folder`.
   - Zalecenie: Usuń nieużywaną funkcję lub przywróć jej użycie, jeśli jest potrzebna.

## 3. Błędy i nieoptymalne fragmenty

3. **`core/tools/base_worker.py`**

   - W metodzie `stop` po wywołaniu `terminate()` następuje ponowne `wait(2000)`, co może prowadzić do niepotrzebnego blokowania wątku.
   - Zalecenie: Zweryfikuj, czy podwójne oczekiwanie jest konieczne, lub uprość logikę zatrzymywania wątku.

4. **`core/file_utils.py`**
   - Funkcja `handle_file_action` nie sprawdza, czy `parent_widget` jest przekazany przed próbą wywołania `_show_error_message`, co może prowadzić do błędów w przypadku braku widgetu.
   - Zalecenie: Dodaj warunek sprawdzający obecność `parent_widget` przed wywołaniem funkcji pokazującej komunikat.

## 4. Potencjalnie nieużywane pliki

5. **`core/tools/__init__.py`**
   - Importuje `BaseToolWorker`, który nie jest zdefiniowany w `base_worker.py` (tam jest tylko `BaseWorker`). Może to prowadzić do błędów importu.
   - Zalecenie: Zweryfikuj, czy `BaseToolWorker` jest potrzebny i popraw importy.

## 5. Inne drobne uwagi

6. **`core/scanner.py`**
   - W przypadku niepowodzenia importu Rust-backendu, kod przywraca oryginalną ścieżkę, ale nie zawsze loguje szczegóły błędu.
   - Zalecenie: Upewnij się, że wszystkie wyjątki są odpowiednio logowane.

---

## Podsumowanie: Lista działań dla modelu AI

1. Zrefaktoryzuj `file_renamer_worker.py` i `file_shortener_worker.py`, wydzielając wspólne fragmenty do klasy bazowej lub funkcji pomocniczych.
2. Usuń nieużywaną funkcję `_move_related_files` z `duplicate_finder_worker.py` lub przywróć jej użycie.
3. Uprość logikę zatrzymywania wątku w `base_worker.py`.
4. Popraw obsługę `parent_widget` w `handle_file_action` w `file_utils.py`.
5. Zweryfikuj i popraw importy w `tools/__init__.py` (dotyczy `BaseToolWorker`).
6. Upewnij się, że wszystkie wyjątki w `scanner.py` są logowane.

---

Pliki wymagające poprawek:

- `core/tools/file_renamer_worker.py`
- `core/tools/file_shortener_worker.py`
- `core/tools/duplicate_finder_worker.py`
- `core/tools/base_worker.py`
- `core/file_utils.py`
- `core/tools/__init__.py`
- `core/scanner.py`
