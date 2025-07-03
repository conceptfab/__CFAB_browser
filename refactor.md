Rozwiązanie
Zmiana 1: W pliku core/amv_views/asset_tile_view.py
Usuń podwójne tworzenie thumbnail_container. W metodzie _setup_ui() zakomentuj lub usuń linie 134-142:
pythondef _setup_ui(self):
    # Usuń to:
    # self.thumbnail_container = BaseLabel()
    # thumb_size = self.thumbnail_size
    # self.thumbnail_container.setFixedSize(thumb_size, thumb_size)
    # self.thumbnail_container.setSizePolicy(
    #     QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
    # )
    # self.thumbnail_container.setCursor(Qt.CursorShape.PointingHandCursor)
    # self.thumbnail_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
    # self.thumbnail_container.setContentsMargins(0, 0, 0, 0)
Zmiana 2: W metodzie _setup_ui_without_styles(), uproszczenie struktury:
python# Zamiast linii 283-295, użyj:
# MINIATURKA - bezpośrednio w layoucie głównym
self.thumbnail_container.setContentsMargins(0, 0, 0, 0)
layout.addWidget(self.thumbnail_container, 0, Qt.AlignmentFlag.AlignCenter)
layout.addSpacing(4)  # Mały odstęp przed nazwą pliku
Zmiana 3: Dostosuj obliczanie rozmiaru kafelka (linia 271-273):
python# Bardziej precyzyjne obliczanie rozmiaru
tile_padding = 6  # z CSS
tile_border = 1   # z CSS
tile_width = self.thumbnail_size + (2 * tile_padding) + (2 * tile_border)
tile_height = self.thumbnail_size + 70 + (2 * tile_padding) + (2 * tile_border)
self.setFixedSize(tile_width, tile_height)
To powinno rozwiązać problem. Jeśli nadal nie działa, to możemy sprawdzić przez debugging - dodaj to tymczasowo do metody update_ui():
pythondef update_ui(self):
    # Debug info
    logger.info(f"Kafelek rozmiar: {self.size()}")
    logger.info(f"Miniaturka rozmiar: {self.thumbnail_container.size()}")
    logger.info(f"Miniaturka pozycja: {self.thumbnail_container.pos()}")
    
    # Reszta kodu...
To pokaże nam dokładne rozmiary i pozycje w logach.