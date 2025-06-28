# PATCH-CODE DLA: core/amv_models/file_operations_model.py

**Powiązany plik z analizą:** `../corrections/file_operations_model_correction.md`
**Zasady ogólne:** `../refactoring_rules.md`

---

### PATCH 1: Poprawa wywołań `_update_asset_file_after_rename` i `_mark_asset_as_duplicate`

**Problem:** W `_move_single_asset_with_conflict_resolution`, `_update_asset_file_after_rename` i `_mark_asset_as_duplicate` są wywoływane z nieprawidłowymi ścieżkami, co prowadzi do błędów w aktualizacji metadanych assetu.
**Rozwiązanie:** Zapewnienie, że do tych funkcji przekazywane są ścieżki do pliku `.asset`.

```python
# ... istniejący kod ...

    def _move_single_asset_with_conflict_resolution(
        self, asset_data: dict, original_name: str
    ) -> dict:
        """
        Przenosi pojedynczy asset z obsługą konfliktów nazw.
        Zwraca dict z kluczami: success (bool), message (str), final_name (str)
        """
        # Wygeneruj unikalną nazwę
        unique_name = self._generate_unique_asset_name(original_name)

        try:
            # Przygotuj mapowanie plików źródłowych na docelowe
            files_to_move = []

            # 1. Plik .asset
            source_asset = os.path.join(
                self.source_folder_path, f"{original_name}.asset"
            )
            target_asset = os.path.join(self.target_folder_path, f"{unique_name}.asset")
            if os.path.exists(source_asset):
                files_to_move.append((source_asset, target_asset))

            # 2. Plik archiwum
            archive_filename = asset_data.get("archive")
            if archive_filename:
                source_archive = os.path.join(self.source_folder_path, archive_filename)
                if os.path.exists(source_archive):
                    # Zachowaj oryginalne rozszerzenie
                    archive_ext = os.path.splitext(archive_filename)[1]
                    target_archive = os.path.join(
                        self.target_folder_path, f"{unique_name}{archive_ext}"
                    )
                    files_to_move.append((source_archive, target_archive))

            # 3. Plik podglądu
            preview_filename = asset_data.get("preview")
            if preview_filename:
                source_preview = os.path.join(self.source_folder_path, preview_filename)
                if os.path.exists(source_preview):
                    # Zachowaj oryginalne rozszerzenie
                    preview_ext = os.path.splitext(preview_filename)[1]
                    target_preview = os.path.join(
                        self.target_folder_path, f"{unique_name}{preview_ext}"
                    )
                    files_to_move.append((source_preview, target_preview))

            # 4. Plik .thumb w folderze .cache
            source_thumb = os.path.join(
                self.source_folder_path, ".cache", f"{original_name}.thumb"
            )
            if os.path.exists(source_thumb):
                target_cache_dir = os.path.join(self.target_folder_path, ".cache")
                os.makedirs(target_cache_dir, exist_ok=True)
                target_thumb = os.path.join(target_cache_dir, f"{unique_name}.thumb")
                files_to_move.append((source_thumb, target_thumb))

            # Przenieś wszystkie pliki
            moved_files = []
            for source_path, target_path in files_to_move:
                shutil.move(source_path, target_path)
                moved_files.append(target_path)
                logger.debug(f"Przeniesiono: {source_path} -> {target_path}")

            # Jeśli nazwa została zmieniona, zaktualizuj plik .asset
            if unique_name != original_name:
                # Przekaż ścieżki do plików .asset
                self._update_asset_file_after_rename(source_asset, target_asset)

                # Oznacz jako duplikat z informacją o oryginale
                if os.path.exists(source_asset): # Sprawdź czy oryginalny asset istnieje
                    self._mark_asset_as_duplicate(
                        target_asset, source_asset
                    )

            # Zwróć informację o sukcesie
            if unique_name != original_name:
                message = (
                    f"Przeniesiono asset: {original_name} -> {unique_name} "
                    f"(zmieniono nazwę z powodu konfliktu)"
                )
            else:
                message = f"Pomyślnie przeniesiono asset: {original_name}"

            return {"success": True, "message": message, "final_name": unique_name}

        except Exception as e:
            return {
                "success": False,
                "message": f"Błąd przenoszenia assetu {original_name}: {e}",
                "final_name": original_name,
            }

# ... reszta istniejącego kodu ...
```

---

### PATCH 2: Uściślenie logiki aktualizacji ścieżek w `_update_asset_file_after_rename`

**Problem:** Logika aktualizacji ścieżek w pliku `.asset` jest zbyt ogólna i może prowadzić do niepożądanych zmian.
**Rozwiązanie:** Celowanie w konkretne pola (`archive`, `preview`) w pliku `.asset`.

```python
# ... istniejący kod ...

    def _update_asset_file_after_rename(self, original_asset_path, new_asset_path):
        """Aktualizuje plik .asset po zmianie nazwy"""
        try:
            # asset_file_path = new_path.replace(os.path.splitext(new_path)[1], ".asset") # USUNIĘTO
            asset_file_path = new_asset_path # Użyj bezpośrednio nowej ścieżki do assetu

            if os.path.exists(asset_file_path):
                # Wczytaj JSON z pliku .asset
                with open(asset_file_path, "r", encoding="utf-8") as f:
                    asset_data = json.load(f)

                # Zaktualizuj ścieżki w asset_data
                original_basename = os.path.splitext(os.path.basename(original_asset_path))[0]
                new_basename = os.path.splitext(os.path.basename(new_asset_path))[0]

                # Aktualizuj tylko pola 'archive' i 'preview' jeśli zawierają oryginalną nazwę
                if "archive" in asset_data and isinstance(asset_data["archive"], str):
                    if original_basename in asset_data["archive"]:
                        asset_data["archive"] = asset_data["archive"].replace(original_basename, new_basename)

                if "preview" in asset_data and isinstance(asset_data["preview"], str):
                    if original_basename in asset_data["preview"]:
                        asset_data["preview"] = asset_data["preview"].replace(original_basename, new_basename)

                # Zapisz zaktualizowany JSON
                with open(asset_file_path, "w", encoding="utf-8") as f:
                    json.dump(asset_data, f, ensure_ascii=False, indent=2)

                logger.debug(f"Zaktualizowano plik .asset: {asset_file_path}")
        except Exception as e:
            logger.error(f"Błąd aktualizacji pliku .asset: {e}")

# ... reszta istniejącego kodu ...
```

---

### PATCH 3: Zmiana sygnału `operation_completed` w `FileOperationsWorker`

**Problem:** Sygnał `operation_completed` emituje listy komunikatów, co jest kruche i utrudnia dalsze przetwarzanie.
**Rozwiązanie:** Zmiana sygnału na emitowanie list nazw assetów, które zostały pomyślnie przetworzone.

```python
# ... istniejący kod ...

class FileOperationsWorker(QThread):
    """Worker do wykonywania operacji na plikach w osobnym wątku"""

    operation_progress = pyqtSignal(int, int, str)  # current, total, message
    operation_completed = pyqtSignal(list, list)  # success_asset_names, error_messages # Zmieniono sygnał
    operation_error = pyqtSignal(str)

    # ... istniejący kod ...

    def _move_assets(self):
        """Przenosi zaznaczone assety do nowego folderu."""
        if not self.assets_data:
            self.operation_completed.emit([], [])
            return

        success_asset_names = [] # Zmieniono na listę nazw assetów
        error_messages = []
        total_assets = len(self.assets_data)

        # ... istniejący kod ...

        for i, asset_data in enumerate(self.assets_data):
            asset_name = asset_data.get("name", "Unknown Asset")
            self.operation_progress.emit(
                i + 1, total_assets, f"Przenoszenie: {asset_name}"
            )
            try:
                # Użyj nowej metody z obsługą konfliktów nazw
                result = self._move_single_asset_with_conflict_resolution(
                    asset_data, asset_name
                )
                if result["success"]:
                    success_asset_names.append(result["final_name"]) # Dodano nazwę assetu
                    logger.debug(result["message"])
                else:
                    error_messages.append(result["message"])
                    logger.error(result["message"])
            except Exception as e:
                error_msg = f"Błąd przenoszenia assetu {asset_name}: {e}"
                error_messages.append(error_msg)
                logger.error(error_msg)

        # ... istniejący kod ...

        self.operation_completed.emit(success_asset_names, error_messages) # Zmieniono emitowanie

    # ... istniejący kod ...

    def _delete_assets(self):
        """Usuwa zaznaczone assety (wszystkie 4 pliki)."""
        if not self.assets_data:
            self.operation_completed.emit([], [])
            return

        success_asset_names = [] # Zmieniono na listę nazw assetów
        error_messages = []
        total_assets = len(self.assets_data)

        for i, asset_data in enumerate(self.assets_data):
            asset_name = asset_data.get("name", "Unknown Asset")
            self.operation_progress.emit(i + 1, total_assets, f"Usuwanie: {asset_name}")
            try:
                files_to_delete = self._get_asset_files_paths(
                    asset_data, self.source_folder_path
                )
                for file_path in files_to_delete:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.debug(f"Usunięto plik: {file_path}")
                success_asset_names.append(asset_name) # Dodano nazwę assetu
                logger.debug(f"Usunięto asset: {asset_name}")
            except Exception as e:
                error_messages.append(f"Błąd usuwania assetu {asset_name}: {e}")
                logger.error(f"Błąd usuwania assetu {asset_name}: {e}")

        # ... istniejący kod ...

        self.operation_completed.emit(success_asset_names, error_messages) # Zmieniono emitowanie

# ... reszta istniejącego kodu ...
```

---

### PATCH 4: Dostosowanie `_on_file_operation_completed` w `AmvController`

**Problem:** `_on_file_operation_completed` w `AmvController` parsuje komunikaty, co jest kruche.
**Rozwiązanie:** Dostosowanie metody do nowej struktury sygnału `operation_completed`, która emituje nazwy assetów.

```python
# ... istniejący kod w AmvController ...

    def _on_file_operation_completed(
        self, success_asset_names: list, error_messages: list
    ):
        self.model.control_panel_model.set_progress(100)
        self.view.update_gallery_placeholder("")  # Clear placeholder

        # Usuń przeniesione/usunięte assety z listy bez ponownego skanowania
        if success_asset_names:
            # moved_asset_names = [] # USUNIĘTO
            # for msg in success_messages: # USUNIĘTO
            #     if "przeniesiono" in msg.lower(): # USUNIĘTO
            #         # Wyciągnij nazwę assetu z komunikatu "Pomyślnie przeniesiono asset: nazwa" # USUNIĘTO
            #         asset_name = msg.split("asset: ")[-1] if "asset: " in msg else None # USUNIĘTO
            #         if asset_name: # USUNIĘTO
            #             moved_asset_names.append(asset_name) # USUNIĘTO
            #     elif "usunięto" in msg.lower(): # USUNIĘTO
            #         # Wyciągnij nazwę assetu z komunikatu "Pomyślnie usunięto asset: nazwa" # USUNIĘTO
            #         asset_name = msg.split("asset: ")[-1] if "asset: " in msg else None # USUNIĘTO
            #         if asset_name: # USUNIĘTO
            #             moved_asset_names.append(asset_name) # USUNIĘTO

            # Użyj bezpośrednio success_asset_names
            if success_asset_names:
                current_assets = self.model.asset_grid_model.get_assets()
                updated_assets = [
                    asset
                    for asset in current_assets
                    if asset.get("name") not in success_asset_names # Użyj success_asset_names
                ]
                self.model.asset_grid_model._assets = updated_assets

                # Usuń kafelki z widoku
                tiles_to_remove = []
                for tile in self.asset_tiles:
                    if tile.model.get_name() in success_asset_names: # Użyj success_asset_names
                        tiles_to_remove.append(tile)

                for tile in tiles_to_remove:
                    self.view.gallery_layout.removeWidget(tile)
                    tile.deleteLater()
                    self.asset_tiles.remove(tile)

                logger.debug(
                    f"Removed {len(success_asset_names)} assets from list and view without rescanning" # Użyj success_asset_names
                )

        self.model.selection_model.clear_selection()  # Wyczyść zaznaczenie po operacji

# ... reszta istniejącego kodu ...
```

---

## ✅ CHECKLISTA WERYFIKACYJNA (DO WYPEŁNIENIA PRZED WDROŻENIEM)

#### **FUNKCJONALNOŚCI DO WERYFIKACJI:**

- [ ] **Funkcjonalność podstawowa** - czy plik nadal wykonuje swoją główną funkcję.
- [ ] **API kompatybilność** - czy wszystkie publiczne metody/klasy działają jak wcześniej.
- [ ] **Obsługa błędów** - czy mechanizmy obsługi błędów nadal działają.
- [ ] **Walidacja danych** - czy walidacja wejściowych danych działa poprawnie.
- [ ] **Logowanie** - czy system logowania działa bez spamowania.
- [ ] **Konfiguracja** - czy odczytywanie/zapisywanie konfiguracji działa.
- [ ] **Cache** - czy mechanizmy cache działają poprawnie.
- [ ] **Thread safety** - czy kod jest bezpieczny w środowisku wielowątkowym.
- [ ] **Memory management** - czy nie ma wycieków pamięci.
- [ ] **Performance** - czy wydajność nie została pogorszona.

#### **ZALEŻNOŚCI DO WERYFIKACJI:**

- [ ] **Importy** - czy wszystkie importy działają poprawnie.
- [ ] **Zależności zewnętrzne** - czy zewnętrzne biblioteki są używane prawidłowo.
- [ ] **Zależności wewnętrzne** - czy powiązania z innymi modułami działają.
- [ ] **Cykl zależności** - czy nie wprowadzono cyklicznych zależności.
- [ ] **Backward compatibility** - czy kod jest kompatybilny wstecz.
- [ ] **Interface contracts** - czy interfejsy są przestrzegane.
- [ ] **Event handling** - czy obsługa zdarzeń działa poprawnie.
- [ ] **Signal/slot connections** - czy połączenia Qt działają.
- [ ] **File I/O** - czy operacje na plikach działają.

#### **TESTY WERYFIKACYJNE:**

- [ ] **Test jednostkowy** - czy wszystkie funkcje działają w izolacji.
- [ ] **Test integracyjny** - czy integracja z innymi modułami działa.
- [ ] **Test regresyjny** - czy nie wprowadzono regresji.
- [ ] **Test wydajnościowy** - czy wydajność jest akceptowalna.

#### **KRYTERIA SUKCESU:**

- [ ] **WSZYSTKIE CHECKLISTY MUSZĄ BYĆ ZAZNACZONE** przed wdrożeniem.
- [ ] **BRAK FAILED TESTS** - wszystkie testy muszą przejść.
- [ ] **PERFORMANCE BUDGET** - wydajność nie pogorszona o więcej niż 5%.
- [ ] **CODE COVERAGE** - pokrycie kodu nie spadło poniżej 80%.
