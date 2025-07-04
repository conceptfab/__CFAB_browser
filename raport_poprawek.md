## Raport z analizy kodu w katalogu `@core/`

Poniżej przedstawiono listę plików wymagających poprawek, wraz z numerowanymi punktami opisującymi wykryte problemy.

### core/amv_controllers/handlers/asset_grid_controller.py
1.  **Zduplikowana i nieużywana funkcja:** Funkcja `_calculate_columns_cached` jest zduplikowana. Istnieje identyczna funkcja w `core/amv_models/asset_grid_model.py`, która jest faktycznie używana. Wersja w tym pliku (`asset_grid_controller.py`) jest nieużywana i powinna zostać usunięta.

### core/amv_controllers/handlers/folder_tree_controller.py
1.  **Nadmiarowe wywołanie sygnału/funkcji:** W metodzie `on_tree_item_clicked`, wywołanie `self.model.folder_system_model.on_folder_clicked(folder_path)` jest nadmiarowe. `folder_system_model.on_folder_clicked` emituje sygnał `folder_clicked`, który jest już podłączony do `folder_tree_controller.on_folder_clicked` (w `signal_connector.py`). Powoduje to podwójne wywołanie tej samej logiki. Należy usunąć bezpośrednie wywołanie `self.model.folder_system_model.on_folder_clicked` z `on_tree_item_clicked`.

### core/amv_models/folder_system_model.py
1.  **Zduplikowany i nieużywany plik:** Cały plik `core/amv_models/folder_system_model.py` zawiera klasę `FolderSystemModel`, która jest zduplikowana. Identyczna klasa `FolderSystemModel` znajduje się w `core/amv_models/asset_grid_model.py` i to ona jest używana w aplikacji. Ten plik (`core/amv_models/folder_system_model.py`) jest nieużywany i powinien zostać usunięty.

### core/amv_models/workspace_folders_model.py
1.  **Brakująca metoda `save_config`:** Metoda `_update_config` wywołuje `self._config_manager.save_config(config)`. Jednak klasa `ConfigManagerMV` (zdefiniowana w `core/amv_models/config_manager_model.py`) nie posiada metody `save_config`. Spowoduje to błąd `AttributeError`. Należy dodać metodę `save_config` do `ConfigManagerMV`.
2.  **Sztywno zakodowane klucze konfiguracji:** W metodzie `_load_folders_from_config` foldery robocze są ładowane poprzez iterację sztywno zakodowanych kluczy `work_folder1` do `work_folder9`. Lepszym rozwiązaniem byłoby przechowywanie folderów roboczych jako listy w konfiguracji, co zwiększyłoby elastyczność i ułatwiło zarządzanie.

### core/amv_models/config_manager_model.py
1.  **Brakująca metoda `save_config`:** Jak wspomniano powyżej, ta klasa wymaga dodania metody `save_config` do zapisu konfiguracji.

### core/amv_views/amv_view.py
1.  **Bezpośrednie stylowanie w kodzie Python:** Metoda `update_workspace_folder_buttons` ustawia style przycisków za pomocą `button.setStyleSheet()`. Jest to mniej elastyczne i trudniejsze w utrzymaniu niż definiowanie stylów w plikach QSS. Zaleca się przeniesienie tych stylów do `styles.qss` i używanie `setObjectName` lub `setProperty` do ich przypisywania.

### core/amv_views/preview_tile.py
1.  **Niespójne logowanie:** W metodach `load_thumbnail` i `_create_placeholder_thumbnail` używane jest `print()` zamiast standardowego loggera (`logger`). Należy zmienić `print()` na `logger.info()` lub `logger.warning()` dla spójności logowania.

### core/base_widgets.py
1.  **Nieużywany kod/Niespójny wzorzec:** Plik definiuje bazowe klasy widgetów (`BaseFrame`, `BaseLabel`, `BaseButton` itd.), ale w dostarczonym kodzie żadne z widoków (np. `AmvView`, `AssetTileView`) nie dziedziczą z tych klas. Sugeruje to nieużywany wzorzec projektowy lub niekompletną refaktoryzację. Jeśli te klasy nie są używane, powinny zostać usunięte. Jeśli mają być używane, należy zrefaktoryzować widoki, aby z nich dziedziczyły.

### core/folder_scanner_worker.py
1.  **Nieużywana funkcja/Martwy kod:** Metoda `handle_folder_click` jest zdefiniowana, ale nie jest wywoływana w dostarczonym kontekście. Dodatkowo, odwołuje się do `self.asset_scanner_model_mv`, który nie jest zdefiniowany w tej klasie ani w jej konstruktorze. Sugeruje to, że jest to martwy kod, który powinien zostać usunięty.

### core/pairing_tab.py
1.  **Niespójne logowanie:** W metodzie `_on_archive_clicked` używane jest `print()` zamiast standardowego loggera (`logger`). Należy zmienić `print()` na `logger.info()` lub `logger.warning()` dla spójności logowania.

### core/tools_tab.py
1.  **Niespójne logowanie:** W metodach `_on_archive_double_clicked` i `_on_preview_double_clicked` używane jest `print()` zamiast standardowego loggera (`logger`) w niektórych komunikatach. Należy zmienić `print()` na `logger.info()` lub `logger.warning()` dla spójności logowania.