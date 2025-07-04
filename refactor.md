Zmiany w core/amv_views/amv_view.py
Popraw fragment tworzenia gwiazdek w panelu kontrolnym:
python# W funkcji _create_control_panel(), około linii 300, zamień:

# 5 gwiazdek po przycisku "Odznacz wszystkie"
self.star_checkboxes = []
for i in range(5):
    star_cb = StarCheckBoxBase("★")
    star_cb.setProperty("class", "star")
    self.star_checkboxes.append(star_cb)
na:
python# 5 gwiazdek po przycisku "Odznacz wszystkie"
self.star_checkboxes = []
for i in range(5):
    star_cb = StarCheckBoxBase("★")
    star_cb.setObjectName(f"ControlPanelStar_{i+1}")
    star_cb.setProperty("class", "star")
    # Ustaw identyczne właściwości jak w kafelku
    star_cb.setFixedSize(12, 12)
    star_cb.setText("★")
    self.star_checkboxes.append(star_cb)
Zmiany w core/resources/styles.qss
Dodaj nowe style dla gwiazdek w panelu kontrolnym, aby były identyczne z kafelkami:
css/* ===================== PANEL KONTROLNY - GWIAZDKI ===================== */
/* Styluje gwiazdki w panelu kontrolnym - identyczne jak w kafelkach */
#ControlPanelStar_1, #ControlPanelStar_2, #ControlPanelStar_3, #ControlPanelStar_4, #ControlPanelStar_5 {
    spacing: 0px;
    color: #848484;
    font-size: 10.8px;
    min-width: 12px;
    min-height: 12px;
    max-width: 12px;
    max-height: 12px;
    background: transparent;
    margin: 0px;
    padding: 0px;
    border: none;
}

#ControlPanelStar_1::indicator, #ControlPanelStar_2::indicator, #ControlPanelStar_3::indicator, #ControlPanelStar_4::indicator, #ControlPanelStar_5::indicator {
    width: 0px;
    height: 0px;
    border: none;
    background: transparent;
}

#ControlPanelStar_1:checked, #ControlPanelStar_2:checked, #ControlPanelStar_3:checked, #ControlPanelStar_4:checked, #ControlPanelStar_5:checked {
    color: #717bbc;
    font-weight: bold;
}

#ControlPanelStar_1:hover, #ControlPanelStar_2:hover, #ControlPanelStar_3:hover, #ControlPanelStar_4:hover, #ControlPanelStar_5:hover {
    color: #717bbc;
}
Opcjonalnie: Aktualizacja core/amv_controllers/handlers/signal_connector.py
Upewnij się, że połączenia sygnałów dla gwiazdek panelu kontrolnego są poprawne:
python# W funkcji connect_all(), około linii 85, upewnij się że jest:

# --- Sygnały gwiazdek z panelu kontrolnego ---
for i, star_cb in enumerate(self.view.star_checkboxes):
    star_cb.setAutoExclusive(False)
    # Upewnij się, że mamy właściwy objectName
    star_cb.setObjectName(f"ControlPanelStar_{i+1}")
    star_cb.clicked.connect(
        lambda checked, star_index=i: control_panel_controller.on_star_filter_clicked(
            star_index + 1
        )
    )
Podsumowanie zmian
Te zmiany sprawią, że gwiazdki w panelu kontrolnym będą:

Identycznie stylowane - ten sam rozmiar (12x12px), kolory i efekty hover
Poprawnie rozpoznawane przez CSS - dzięki unikalnym objectName
Spójne wizualnie - dokładnie takie same jak w kafelkach assetów

Główny problem polegał na tym, że gwiazdki w panelu kontrolnym używały ogólnego selektora CSS QCheckBox.star, podczas gdy gwiazdki w kafelkach miały specyficzne objectName z dedykowanymi stylami CSS.