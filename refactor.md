Poprawka asymetrycznego rozmieszczenia miniaturki
Plik: core/amv_views/asset_tile_view.py
Zmiana w funkcji _setup_ui() - linie 334-342:
pythondef _setup_ui(self):
    # Najpierw utwórz miniaturkę!
    self.thumbnail_container = BaseLabel()
    thumb_size = self.thumbnail_size
    self.thumbnail_container.setFixedSize(thumb_size, thumb_size)
    self.thumbnail_container.setSizePolicy(
        QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
    )
    self.thumbnail_container.setCursor(Qt.CursorShape.PointingHandCursor)
    self.thumbnail_container.setAlignment(Qt.AlignmentFlag.AlignCenter)  # DODANE
    self.thumbnail_container.setContentsMargins(0, 0, 0, 0)  # DODANE
Zmiana w funkcji _setup_ui_without_styles() - marginesy kontenera miniaturki (linia ~403):
python# MINIATURKA - najważniejsza, 12px marginesów wokół (ujednolicenie z resztą)
thumb_container = QWidget()
thumb_layout = QVBoxLayout(thumb_container)
thumb_layout.setContentsMargins(12, 10, 12, 10)  # ZMIENIONE: z (10,10,10,10) na (12,10,12,10)
thumb_layout.setSpacing(0)
thumb_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # DODANE
self.thumbnail_container.setContentsMargins(0, 0, 0, 0)
self.thumbnail_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
thumb_layout.addWidget(self.thumbnail_container, 0, Qt.AlignmentFlag.AlignCenter)  # DODANE parametr wyrównania
layout.addWidget(thumb_container)
Te zmiany:

Wyśrodkowują miniaturkę w kontenerze
Ujednolicają marginesy (12px lewo/prawo jak w pozostałych sekcjach)
Dodają jawne wyrównanie na poziomie layoutu