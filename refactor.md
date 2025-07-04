Alternatywne rozwiązanie przez QSS
Jeśli wolisz zachować style w pliku CSS, dodaj to do core/resources/styles.qss:
css/* ===================== PRZYCISK TOGGLE PANELU ===================== */
#panelToggleButton {
    border: none;
    background: transparent;
    padding: 0px;
    margin: 0px;
}

#panelToggleButton:hover {
    background-color: rgba(113, 123, 188, 0.3);
    border-radius: 2px;
}

#panelToggleButton:pressed {
    background-color: rgba(113, 123, 188, 0.5);
    border-radius: 2px;
}
I wtedy w kodzie Python wystarczy dodać tylko setFlat(True):
pythonself.toggle_button.setFlat(True)  # Dodaj tylko tę linię