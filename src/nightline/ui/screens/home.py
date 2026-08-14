from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ..widgets import HudButton
from ..theme import Theme

class HomeScreen(QWidget):
    request_camera_screen = Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Theme.metrics.spacing_xl,
            Theme.metrics.spacing_xl,
            Theme.metrics.spacing_xl,
            Theme.metrics.spacing_xl,
        )
        layout.setSpacing(Theme.metrics.spacing_lg)

        title = QLabel("Home")
        title.setFont(Theme.typography.h1)
        layout.addWidget(title)

        btn = HudButton("Open Front Camera")
        btn.clicked.connect(self.request_camera_screen.emit)
        layout.addWidget(btn)
        layout.addStretch()
