Zmiany w pliku core/amv_views/amv_view.py
1. Funkcja _create_edge_button() - linia 299
pythondef _create_edge_button(self):
    """Tworzy przycisk przyklejony do lewej krawędzi do otwierania panelu"""
    self.edge_button = QPushButton()
    self.edge_button.setObjectName("edgePanelButton")
    self.edge_button.setFixedSize(18, 18)  # Taki sam rozmiar jak przycisk zamykania
    self.edge_button.setToolTip("Otwórz panel")
    self.edge_button.setIcon(QIcon("core/resources/img/open_panel.png"))
    self.edge_button.setIconSize(QSize(16, 16))
    self.edge_button.setFlat(True)
    self.edge_button.clicked.connect(lambda: self.toggle_panel_requested.emit())

    # Stylowanie przycisku podobne do przycisku zamykania
    self.edge_button.setStyleSheet(
        """
        QPushButton#edgePanelButton {
            background-color: #2D2D30;
            border: 1px solid #3F3F46;
            border-right: none;
            border-radius: 4px 0px 0px 4px;
            color: #CCCCCC;
            font-size: 12px;
            font-weight: bold;
        }
        QPushButton#edgePanelButton:hover {
            background-color: #3F3F46;
            border-color: #007ACC;
        }
        QPushButton#edgePanelButton:pressed {
            background-color: #007ACC;
            color: #FFFFFF;
        }
    """
    )
2. Funkcja _setup_ui() - linia 51
pythondef _setup_ui(self):
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    
    # Utwórz przycisk krawędzi PRZED splitterem
    self._create_edge_button()
    
    self.splitter = QSplitter(Qt.Orientation.Horizontal)
    self.splitter.setSizes([200, 800])
    self.splitter.splitterMoved.connect(self._on_splitter_moved)
    self._create_left_panel()
    self._create_gallery_panel()
    
    # Dodaj przycisk krawędzi na początku layoutu
    layout.addWidget(self.edge_button)
    layout.addWidget(self.splitter)
    self.setLayout(layout)

    # Domyślnie ukryj przycisk krawędzi (panel jest otwarty)
    self.edge_button.hide()
3. Funkcja _create_left_panel_header() - linia 91
pythondef _create_left_panel_header(self, layout):
    header_frame = QFrame()
    header_frame.setFixedHeight(40)
    header_layout = QHBoxLayout()
    header_layout.setContentsMargins(12, 8, 12, 8)

    # Przyciski Zwiń i Rozwiń - szersze o 80%, bardzo niskie
    self.collapse_button = PanelButtonBase("Zwiń")
    self.collapse_button.setObjectName("collapseButton")
    self.collapse_button.setFixedWidth(35)  # Identyczna szerokość
    self.collapse_button.clicked.connect(self._on_collapse_tree_clicked)

    self.expand_button = PanelButtonBase("Rozwiń")
    self.expand_button.setObjectName("expandButton")
    self.expand_button.setFixedWidth(35)  # Identyczna szerokość
    self.expand_button.clicked.connect(self._on_expand_tree_clicked)

    self.toggle_button = QPushButton()
    self.toggle_button.setObjectName("panelToggleButton")  # ID dla QSS
    self.toggle_button.setFixedSize(18, 18)
    self.toggle_button.setToolTip("Zamknij panel")
    self.toggle_button.setIcon(self.collapse_icon)
    self.toggle_button.setIconSize(QSize(16, 16))
    self.toggle_button.setFlat(True)
    # POPRAWKA: Podłącz do toggle_panel_requested zamiast window().close
    self.toggle_button.clicked.connect(lambda: self.toggle_panel_requested.emit())

    # Centrowanie przycisków Zwiń i Rozwiń
    header_layout.addStretch(1)
    header_layout.addWidget(self.collapse_button)
    header_layout.addWidget(self.expand_button)
    header_layout.addStretch(1)
    header_layout.addWidget(self.toggle_button)
    header_frame.setLayout(header_layout)
    layout.addWidget(header_frame)
4. Funkcja update_toggle_button_text() - linia 444
pythondef update_toggle_button_text(self, is_panel_open: bool):
    if hasattr(self, "toggle_button"):
        icon = self.collapse_icon if is_panel_open else self.expand_icon
        self.toggle_button.setIcon(icon)
        self.toggle_button.setToolTip(
            "Zamknij panel" if is_panel_open else "Otwórz panel"
        )

    # POPRAWKA: Obsługa przycisku krawędzi
    if hasattr(self, "edge_button"):
        if is_panel_open:
            self.edge_button.hide()  # Ukryj przycisk krawędzi gdy panel jest otwarty
        else:
            self.edge_button.show()  # Pokaż przycisk krawędzi gdy panel jest zamknięty
Zmiany w pliku core/resources/styles.qss
Dodaj style dla przycisku krawędzi - po linii 612
css/* ===================== PRZYCISK KRAWĘDZI PANELU ===================== */
#edgePanelButton {
    background-color: #2D2D30;
    border: 1px solid #3F3F46;
    border-right: none;
    border-radius: 4px 0px 0px 4px;
    color: #CCCCCC;
    font-size: 12px;
    font-weight: bold;
    min-width: 18px;
    max-width: 18px;
    min-height: 18px;
    max-height: 18px;
    padding: 0px;
    margin: 0px;
}

#edgePanelButton:hover {
    background-color: #3F3F46;
    border-color: #007ACC;
    color: #717bbc;
}

#edgePanelButton:pressed {
    background-color: #007ACC;
    color: #FFFFFF;
    border-color: #005A9E;
}
Główne poprawki:

Pozycjonowanie przycisku krawędzi - przycisk jest teraz dodawany na początku layoutu, przed splitterem
Logika widoczności - przycisk krawędzi jest widoczny tylko gdy panel jest zamknięty
Wysokość - przycisk ma taki sam rozmiar (18x18) jak przycisk zamykania panelu
Funkcjonalność - oba przyciski teraz prawidłowo emitują sygnał toggle_panel_requested
Style - dodano dedykowane style CSS dla przycisku krawędzi

Teraz przycisk otwierania panelu będzie:

Widoczny tylko gdy panel jest zamknięty
Przyklejony do lewej krawędzi
Na tej samej wysokości co przycisk zamykania (dzięki jednakowym rozmiarom i pozycjonowaniu w headerze)
Prawidłowo zintegrowany z logiką przełączania panelu