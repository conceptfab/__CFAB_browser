# PATCH CODE: asset_grid_model.py

**Wersja: 1.0**

**Data: 2025-06-28**

**Autor: Gemini**

---

## 🎯 OPIS ZMIAN

1.  **Refaktoryzacja hardkodowanych wartości:** Zdefiniowano stałe w klasie `AssetGridModel` dla marginesów i odstępów, aby poprawić czytelność i ułatwić przyszłe modyfikacje.

## 💻 KOD

### Zmiana 1: Zdefiniowanie stałych i ich użycie w `_calculate_columns_cached`

```python
class AssetGridModel(QObject):
    """Model dla siatki assetów - architektura M/V"""

    assets_changed = pyqtSignal(list)
    grid_layout_changed = pyqtSignal(int)
    loading_state_changed = pyqtSignal(bool)
    recalculate_columns_requested = pyqtSignal(int, int)  # Sygnał do kontrolera

    # Constants for layout calculations
    TILE_MARGINS = 8  # 2 * 8px = 16px total for tile_width
    LAYOUT_MARGINS = 16 # From gallery_layout.setContentsMargins(8, 8, 8, 8)
    TILE_SPACING = 8 # Spacing between tiles

    def __init__(self):
        super().__init__()
        self._assets = []
        self._columns = 4
        self._is_loading = False
        self._current_folder_path = ""
        self._last_available_width = 0  # Nowy atrybut
        self._last_thumbnail_size = 0  # Nowy atrybut
        self._recalc_timer = QTimer(self)  # Timer do debouncingu
        self._recalc_timer.setSingleShot(True)
        self._recalc_timer.timeout.connect(self._perform_recalculate_columns)
        logger.info("AssetGridModel initialized")

    # ... (pozostałe metody bez zmian)

    def _calculate_columns_cached(
        self, available_width: int, thumbnail_size: int
    ) -> int:
        """Oblicza optymalną liczbą kolumn."""
        # Rzeczywisty rozmiar kafelka (thumbnail_size + (2 * TILE_MARGINS))
        tile_width = thumbnail_size + (2 * self.TILE_MARGINS)

        # Dostępna szerokość po odjęciu marginesów layoutu
        effective_width = available_width - self.LAYOUT_MARGINS

        # Oblicz liczbę kolumn z uwzględnieniem spacing
        if (tile_width + self.TILE_SPACING) > 0:
            columns_calc = (effective_width + self.TILE_SPACING) // (tile_width + self.TILE_SPACING)
        else:
            columns_calc = 1  # Zapobiegaj dzieleniu przez zero

        calculated_columns = max(1, columns_calc)

        self._last_available_width = available_width
        self._last_thumbnail_size = thumbnail_size
        return calculated_columns
```
