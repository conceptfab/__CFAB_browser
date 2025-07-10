Przeanalizowałem kod i znalazłem główny problem z odświeżaniem galerii. Problem leży w optymalizacji hash w metodzie _reorganize_layout() w pliku core/amv_controllers/handlers/asset_grid_controller.py.
Zmiana w pliku core/amv_controllers/handlers/asset_grid_controller.py
W funkcji _reorganize_layout(), linia 196-202:
python# OPTIMIZATION: Check if layout actually needs rebuilding using hash
new_layout_hash = hash(tuple(asset["name"] for asset in assets))

if hasattr(self, '_last_layout_hash') and self._last_layout_hash == new_layout_hash:
    logger.debug("Layout unchanged - skipping full rebuild")
    return
Problem: Gdy użytkownik odświeża folder, assety mogą mieć te same nazwy co poprzednio, ale ich zawartość (thumbnail, metadane, rozmiar itp.) mogła się zmienić. Optymalizacja hash sprawdza tylko nazwy plików i blokuje przebudowę layoutu.
Proponowana zmiana:
pythondef _reorganize_layout(self, assets, current_tile_map, force_rebuild=False):
    if not assets:
        self.view.update_gallery_placeholder("No assets in this folder.")
        self.view.stacked_layout.setCurrentIndex(1)  # Show placeholder
        return
        
    cols = self.model.asset_grid_model.get_columns()
    sorted_tiles = [
        current_tile_map[asset["name"]]
        for asset in assets
        if asset["name"] in current_tile_map
    ]
    
    # Check if we have any tiles to display
    if not sorted_tiles:
        self.view.update_gallery_placeholder("No assets in this folder.")
        self.view.stacked_layout.setCurrentIndex(1)  # Show placeholder
        return
    
    # OPTIMIZATION: Check if layout actually needs rebuilding using hash
    # Skip optimization during force rebuild (e.g., folder refresh)
    if not force_rebuild:
        new_layout_hash = hash(tuple(asset["name"] for asset in assets))
        
        if hasattr(self, '_last_layout_hash') and self._last_layout_hash == new_layout_hash:
            logger.debug("Layout unchanged - skipping full rebuild")
            return
        
        self._last_layout_hash = new_layout_hash
    else:
        # Force rebuild - update hash but don't skip rebuild
        new_layout_hash = hash(tuple(asset["name"] for asset in assets))
        self._last_layout_hash = new_layout_hash
        logger.debug("Force rebuild requested - performing full rebuild")
    
    # Clear placeholder and show gallery
    self.view.update_gallery_placeholder("")
    
    # Full rebuild only when necessary
    logger.debug("Layout changed - performing full rebuild")
    while self.view.gallery_layout.count():
        item = self.view.gallery_layout.takeAt(0)
        if item.widget():
            item.widget().hide()
    for i, tile in enumerate(sorted_tiles):
        row, col = divmod(i, cols)
        self.view.gallery_layout.addWidget(tile, row, col)
        tile.show()
    
    # Ensure gallery is shown after rebuild
    self.view.stacked_layout.setCurrentIndex(0)
W funkcji _rebuild_asset_grid_immediate(), linia 170:
pythonself._reorganize_layout(assets, current_tile_map)
Zmienić na:
python# Check if this is a forced refresh operation
force_rebuild = getattr(self, '_force_rebuild_requested', False)
self._reorganize_layout(assets, current_tile_map, force_rebuild)
# Reset force rebuild flag
if hasattr(self, '_force_rebuild_requested'):
    self._force_rebuild_requested = False
W funkcji rebuild_asset_grid(), dodać parametr force:
pythondef rebuild_asset_grid(self, assets: list, force_rebuild: bool = False):
    """
    Throttled version of asset grid rebuild to prevent excessive calls.
    """
    # OPTIMIZATION: Throttling - delay rebuild by 50ms
    self._pending_assets = assets
    if force_rebuild:
        self._force_rebuild_requested = True
    self._rebuild_timer.start(50)  # 50ms delay
Zmiana w pliku core/amv_controllers/handlers/folder_tree_controller.py
W funkcji on_folder_refresh_requested(), linia 130:
python# SET folder as current and refresh assets - FORCE_RESCAN=True for refresh
if self._scan_folder_safely(folder_path, force_rescan=True):
    self.controller.control_panel_controller.update_button_states()
    logger.info(f"FOLDER AND ASSETS REFRESHED: {folder_path}")
Zmienić na:
python# SET folder as current and refresh assets - FORCE_RESCAN=True for refresh
if self._scan_folder_safely(folder_path, force_rescan=True):
    # Mark that this is a forced rebuild for gallery
    self.controller.asset_grid_controller._force_rebuild_requested = True
    self.controller.control_panel_controller.update_button_states()
    logger.info(f"FOLDER AND ASSETS REFRESHED: {folder_path}")
Zmiana w pliku core/amv_controllers/handlers/asset_grid_controller.py
W funkcji on_assets_changed(), linia 66:
pythonself.rebuild_asset_grid(assets)
Zmienić na:
python# Check if force rebuild was requested
force_rebuild = getattr(self, '_force_rebuild_requested', False)
self.rebuild_asset_grid(assets, force_rebuild)
Te zmiany rozwiążą problem poprzez:

Dodanie parametru force_rebuild do kluczowych funkcji
Ominięcie optymalizacji hash podczas force rebuild
Propagację flagi force rebuild przez cały pipeline odświeżania
Zagwarantowanie przebudowy galerii nawet jeśli nazwy assetów się nie zmieniły

Po tych zmianach odświeżenie folderu z menu kontekstowego będzie zawsze odświeżać galerię, niezależnie od tego czy nazwy plików się zmieniły.