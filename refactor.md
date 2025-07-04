Zmiany w pliku core/amv_views/amv_view.py
python# W metodzie _create_left_panel_header(), znajdź tę część:
self.toggle_button = QPushButton()
self.toggle_button.setObjectName("panelToggleButton")  # ID dla QSS
self.toggle_button.setFixedSize(18, 18)  # ZMIEŃ NA: (20, 20) dla kwadratowości
self.toggle_button.setToolTip("Zamknij panel")
self.toggle_button.setIcon(self.collapse_icon)
self.toggle_button.setIconSize(QSize(16, 16))  # ZMIEŃ NA: (18, 18) dla lepszych proporcji
self.toggle_button.setFlat(True)
self.toggle_button.clicked.connect(lambda: self.toggle_panel_requested.emit())
Zmień na:
pythonself.toggle_button = QPushButton()
self.toggle_button.setObjectName("panelToggleButton")  # ID dla QSS
self.toggle_button.setFixedSize(20, 20)  # Kwadratowy 20x20px
self.toggle_button.setToolTip("Zamknij panel")
self.toggle_button.setIcon(self.collapse_icon)
self.toggle_button.setIconSize(QSize(18, 18))  # Ikona 18x18px w przycisku 20x20px
self.toggle_button.setFlat(True)
self.toggle_button.clicked.connect(lambda: self.toggle_panel_requested.emit())
Zmiany w pliku core/resources/styles.qss
css/* Znajdź tę sekcję i ZASTĄP ją: */
/* ===================== PRZYCISK TOGGLE PANELU ===================== */
#panelToggleButton {
    border: none;
    background: transparent;
    padding: 0px;
    margin: 0px;
    opacity: 0.8;  /* 80% przeźroczystości domyślnie */
}

#panelToggleButton:hover {
    background-color: rgba(113, 123, 188, 0.15);  /* Subtelne tło na hover */
    border-radius: 3px;
    opacity: 1.0;  /* 100% przeźroczystości na hover */
}

#panelToggleButton:pressed {
    background-color: rgba(113, 123, 188, 0.3);
    border-radius: 3px;
    opacity: 1.0;
}
Dlaczego przycisk nie był kwadratowy?
Problem był w tej linii:
pythonself.toggle_button.setFixedSize(18, 18)
Prawdopodobnie CSS lub padding/margin wprowadzały dodatkowe piksele, przez co przycisk wyglądał na prostokątny. Zwiększenie do 20x20px z ikoną 18x18px da lepsze proporcje i zapewni kwadratowy kształt.
Główne zmiany:

Kwadratowy kształt: 20x20px zamiast 18x18px
Lepsze proporcje ikony: 18x18px ikona w 20x20px przycisku
Profesjonalna animacja opacity: 80% → 100% na hover
Subtelne tło na hover: rgba(113, 123, 188, 0.15)
Gładkie przejścia: CSS automatycznie animuje zmiany opacity

Te zmiany sprawią, że przycisk będzie wyglądał znacznie bardziej profesjonalnie z płynną animacją i kwadratowym kształtem.