**⚠️ KRYTYCZNE: Przed rozpoczęciem pracy zapoznaj się z ogólnymi zasadami refaktoryzacji, poprawek i testowania opisanymi w pliku [refactoring_rules.md](refactoring_rules.md).**

---

# 🐞 ANALIZA PLIKU: amv_controller.py - KOREKTA

**Wersja: 1.0**

**Data: 2025-06-28**

**Autor: Gemini**

---

## 🎯 CEL KOREKTY

Poprawa struktury kodu, czytelności i zgodności z zasadą pojedynczej odpowiedzialności w pliku `amv_controller.py`.

## 📊 WYNIKI ANALIZY

- **Stan:** ✅ Plik przeanalizowany.
- **Wynik:** Zidentyfikowano problemy ze strukturą kodu i jego czytelnością.

### 📝 Podsumowanie

Kontroler `AmvController` jest centralnym punktem logiki interaktywnej aplikacji. Analiza wykazała następujące obszary do poprawy:

1.  **Lokalny import:** W metodzie `_on_tile_thumbnail_clicked` znajduje się lokalny import `from core.thumbnail_tile import PreviewWindow`. Należy go przenieść na początek pliku, aby zachować spójność i czytelność kodu.
2.  **Niewłaściwe umiejscowienie klasy:** Klasa `AssetRebuilderThread` jest zdefiniowana w pliku kontrolera. Narusza to zasadę pojedynczej odpowiedzialności. Powinna zostać wydzielona do osobnego pliku, np. `core/amv_controllers/rebuilder_thread.py`.
3.  **Złożona logika parsowania:** Metoda `_on_file_operation_completed` wykorzystuje parsowanie ciągów znaków do identyfikacji zmodyfikowanych zasobów. Jest to rozwiązanie nieelastyczne i podatne na błędy. W przyszłości należy rozważyć refaktoryzację, aby model `FileOperationsModel` emitował sygnały ze strukturalnymi danymi.

## 🛠️ ZALECANE ZMIANY

### 1. Przeniesienie importu

Należy przenieść import `PreviewWindow` na początek pliku `amv_controller.py`.

### 2. Wydzielenie klasy `AssetRebuilderThread`

Należy utworzyć nowy plik `core/amv_controllers/rebuilder_thread.py` i przenieść do niego definicję klasy `AssetRebuilderThread`. W kontrolerze należy zaktualizować import, aby wskazywał na nową lokalizację.
