# 🔧 Raport Analizy Kodu - Problemy do Naprawienia

## 📋 Spis treści

1. [Pliki wymagające poprawek](#-pliki-wymagające-poprawek)
2. [Podsumowanie statystyk](#-podsumowanie-statystyk)
3. [Priorytet i czas naprawy](#-priorytet-i-czas-naprawy)





### 3. **core/main_window.py**

#### 🔍 **Zidentyfikowane problemy:**

- **Zbyt duża klasa** z wieloma odpowiedzialnościami
- **Duplikowane metody helper** dla zliczania zasobów
- **Nieużywane pola** w `default_config`

#### ✅ **Planowane akcje:**

1. Wydzielić `StatusBarManager` jako osobną klasę
2. Usunąć duplikaty w metodach `_calculate_asset_counts` i podobnych
3. Oczyścić `default_config` z nieużywanych kluczy

---

### 4. **core/amv_controllers/handlers/file_operation_controller.py**

#### 🔍 **Zidentyfikowane problemy:**

- **Duplikowane metody optymalizacji** (`_remove_moved_assets_optimized` i pomocnicze)
- **Zbyt skomplikowana logika** usuwania kafelków
- **Nieużywane `_tiles_mutex`** w niektórych miejscach

#### ✅ **Planowane akcje:**

1. Uprościć optymalizację usuwania kafelków do 2-3 metod
2. Usunąć nieużywane referencje do `_tiles_mutex`
3. Wydzielić `AssetRemovalOptimizer` jako osobną klasę

---


### 6. **core/tools_tab.py**

#### 🔍 **Zidentyfikowane problemy:**

- **Duplikowane metody obsługi workerów** (`_handle_worker_*`)
- **Redundantne połączenia sygnałów**
- **Nieużywane importy**

#### ✅ **Planowane akcje:**

1. Użyć `WorkerManager` konsekwentnie dla wszystkich workerów
2. Usunąć nieużywane importy (`QThread`, `pyqtSignal` w niektórych miejscach)
3. Uprościć `_start_operation_with_confirmation()` - zbyt skomplikowana

---

### 7. **core/amv_models/file_operations_model.py**

#### 🔍 **Zidentyfikowane problemy:**

- **Błędne przypisanie** w linii 245: `asset_file_path = new_asset_path`
- **Duplikowane sprawdzania** ścieżek plików
- **Nieużywana metoda** `_mark_asset_as_duplicate()`

#### ✅ **Planowane akcje:**

1. Naprawić błędne przypisanie w `_update_asset_file_after_rename()`
2. Usunąć nieużywaną metodę `_mark_asset_as_duplicate()`
3. Wydzielić wspólne sprawdzenia ścieżek do metody pomocniczej

---

### 8. **core/amv_controllers/handlers/asset_grid_controller.py**

#### 🔍 **Zidentyfikowane problemy:**

- **Nieużywany `_last_layout_hash`** w niektórych scenariuszach
- **Duplikowane logiki** w `_rebuild_asset_grid_immediate()`
- **Zbyt skomplikowana metoda** `on_assets_changed()`

#### ✅ **Planowane akcje:**

1. Uprościć `on_assets_changed()` - wydzielić części do metod pomocniczych
2. Usunąć nieużywane optymalizacje layoutu jeśli nie są potrzebne
3. Wydzielić logikę sortowania do osobnej metody

---

### 9. **core/workers/worker_manager.py**

#### 🔍 **Zidentyfikowane problemy:**

- **Nieużywane parametry** w niektórych metodach
- **Duplikowana logika** resetowania stanu przycisków

#### ✅ **Planowane akcje:**

1. Usunąć nieużywane parametry z metod statycznych
2. Dodać abstrakcyjną klasę `ManagedWorker` dla lepszej integracji

---

### 10. **Pliki **init**.py**

#### 🔍 **Zidentyfikowane problemy:**

- **Niektóre pliki `__init__.py` są puste** gdy powinny eksportować klasy
- **Brak konsystentnych eksportów**

#### ✅ **Planowane akcje:**

1. Dodać eksporty w pustych plikach `__init__.py` gdzie potrzebne
2. Ujednolicić style eksportów (`__all__`)

---

## 📊 Podsumowanie statystyk

| Kategoria problemów             | Liczba | Status     |
| ------------------------------- | ------ | ---------- |
| ❌ Duplikowane funkcje/metody   | 15+    | Do naprawy |
| ❌ Nieużywane zmienne/metody    | 8      | Do naprawy |
| ❌ Potencjalne błędy logiczne   | 3      | Do naprawy |
| ❌ Problemy z architekturą kodu | 5      | Do naprawy |

### 🔢 **Szczegółowe statystyki:**

- **Łączna liczba plików do refaktoryzacji:** 10
- **Liczba problemów krytycznych:** 3
- **Liczba problemów średnich:** 12
- **Liczba problemów niskich:** 8

---

## ⏱️ Priorytet i czas naprawy

### 🎯 **Priorytet:**

**Średni** - kod działa, ale wymaga refaktoryzacji

### ⏰ **Szacowany czas naprawy:**

**4-6 godzin**

### 📋 **Plan realizacji:**

1. **Faza 1 (1-2h):** Naprawa błędów krytycznych (linia 245 w file_operations_model.py)
2. **Faza 2 (2-3h):** Refaktoryzacja duplikowanych metod
3. **Faza 3 (1h):** Czyszczenie nieużywanego kodu
4. **Faza 4 (30min):** Poprawa plików **init**.py

---

## 🚀 **Następne kroki:**

1. ✅ Weryfikacja problemów (ZAKOŃCZONA)
2. 🔄 Planowanie refaktoryzacji
3. ⏳ Implementacja poprawek
4. 🧪 Testowanie po refaktoryzacji
5. 📝 Dokumentacja zmian
