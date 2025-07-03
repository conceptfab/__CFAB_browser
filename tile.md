Zmiany w core/amv_views/asset_tile_view.py

Responsive z minimalnym rozmiarem (zalecane)
pythondef _setup_ui(self):
    # ... istniejący kod ...
    
    # ZMIANA: Ustaw minimum size ale pozwól na ograniczone skalowanie
    self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
    
    # Ustaw minimalny i maksymalny rozmiar
    tile_width = self.thumbnail_size + (2 * self.margins_size)
    tile_height = self.thumbnail_size + 120
    
    self.setMinimumSize(tile_width, tile_height)
    self.setMaximumSize(tile_width + 50, tile_height + 30)  # Mały luz na skalowanie
    
    # ... reszta kodu bez zmian ...
Zmiany w core/amv_controllers/handlers/asset_grid_controller.py
Modyfikacja funkcji on_recalculate_columns_requested:
pythondef on_recalculate_columns_requested(
    self, available_width: int, thumbnail_size: int
):
    """Obsługuje żądanie przeliczenia kolumn z AssetGridModel"""
    # Model już przeliczył kolumny w _perform_recalculate_columns
    cols = self.model.asset_grid_model.get_columns()
    logger.debug(
        "Controller: Columns recalculated to %d (width: %d, thumb: %d)",
        cols,
        available_width,
        thumbnail_size,
    )

    # ZMIANA: Nie przebudowuj całej galerii - kafelki mają stały rozmiar
    # Tylko zaktualizuj układ jeśli potrzeba
    current_assets = self.model.asset_grid_model.get_assets()
    if current_assets:
        self.rebuild_asset_grid(current_assets, preserve_filter=True)

    # Aktualizuj stan przycisków po przeliczeniu kolumn
    self.controller.control_panel_controller.update_button_states()
Modyfikacje w core/amv_models/asset_grid_model.py
Usprawnienie kalkulacji kolumn:
pythondef _calculate_columns_cached(
    self, available_width: int, thumbnail_size: int
) -> int:
    """Oblicza optymalną liczbę kolumn dla stałych rozmiarów kafelków."""
    # ZMIANA: Używaj stałego rozmiaru kafelka
    tile_width = thumbnail_size + 16  # miniatury + marginesy
    tile_height = thumbnail_size + 120  # Wysokość nie wpływa na kolumny
    
    # Marginesy layoutu
    layout_margins = 16
    
    # Spacing między kafelkami (8px)
    spacing = 8
    
    # Dostępna szerokość po odjęciu marginesów
    effective_width = available_width - layout_margins
    
    # Oblicz liczbę kolumn - kafelki mają stały rozmiar
    if (tile_width + spacing) > 0:
        columns_calc = (effective_width + spacing) // (tile_width + spacing)
    else:
        columns_calc = 1
    
    calculated_columns = max(1, columns_calc)
    
    # DODAJ: Logowanie dla debugowania
    logger.debug(
        f"Kalkulacja kolumn: width={available_width}, tile_width={tile_width}, "
        f"columns={calculated_columns}"
    )
    
    return calculated_columns
Dodatkowe ulepszenia (opcjonalne)
W core/amv_views/amv_view.py możesz dodać:
pythondef _create_gallery_content_widget(self):
    # ... istniejący kod ...
    
    # DODAJ: Ustaw lepsze właściwości layoutu galerii
    self.gallery_layout.setSpacing(8)  # Stały spacing
    self.gallery_layout.setContentsMargins(8, 8, 8, 8)  # Stałe marginesy
    self.gallery_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    
    # ... reszta kodu ...
Efekt końcowy
Po tych zmianach:

Kafelki będą miały stały rozmiar bazujący na rozmiarze miniatury
Nie będą się skalować wraz ze zmianą rozmiaru okna
Układ będzie bardziej przewidywalny - tylko liczba kolumn będzie się zmieniać
Zachowane zostaną proporcje niezależnie od rozmiaru okna

Zalecam Opcję 2 (responsive z minimalnym rozmiarem), ponieważ daje lepsze doświadczenie użytkownika - kafelki pozostają czytelne ale mają trochę elastyczności.