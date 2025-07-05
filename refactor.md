RADYKALNE ROZWIĄZANIE - zmień QLabel na QWidget!
W pliku: core/amv_views/amv_view.py
ZNAJDŹ i ZASTĄP cały fragment tworzenia ikony:
python# STARY KOD (USUŃ TO WSZYSTKO):
# self.icon_placeholder = QLabel()
# self.icon_placeholder.setFixedSize(22, 22)
# self.icon_placeholder.setObjectName("ControlPanelIcon")
# self.icon_placeholder.setPixmap(QPixmap("core/resources/img/search.png").scaled(16, 16))
# self.icon_placeholder.setFocusPolicy(Qt.FocusPolicy.NoFocus)

# NOWY KOD - UŻYJ QWidget ZAMIAST QLabel:
self.icon_placeholder = QWidget()
self.icon_placeholder.setFixedSize(22, 22)
self.icon_placeholder.setFocusPolicy(Qt.FocusPolicy.NoFocus)
self.icon_placeholder.setStyleSheet("background: transparent; border: none;")

# Stwórz layout dla ikony
icon_layout = QVBoxLayout(self.icon_placeholder)
icon_layout.setContentsMargins(3, 3, 3, 3)
icon_layout.setSpacing(0)

# Stwórz QLabel TYLKO dla pixmap WEWNĄTRZ widget
icon_label = QLabel()
icon_label.setPixmap(QPixmap("core/resources/img/search.png").scaled(16, 16))
icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
icon_label.setStyleSheet("border: none; background: transparent;")
icon_layout.addWidget(icon_label)
Sprawdź czy masz import QVBoxLayout:
pythonfrom PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSlider,
    QSplitter,
    QStackedLayout,
    QTreeView,
    QVBoxLayout,    # <-- sprawdź czy to jest
    QWidget,
)
QWidget NIE dziedziczy stylów QLabel, więc nie będzie żadnej ramki!