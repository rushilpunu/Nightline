"""Polished shallow destinations for deferred and available information."""

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..theme import Theme
from ..widgets import HudButton, StatusPill


CONTENT = {
    "cameras": ("CAMERAS", "Hardware not selected", "Camera acquisition is planned after sensor-first V1.", "COMING SOON"),
    "statistics": ("STATISTICS", "Parking session", "Minimum distance and event history will populate from live sessions.", "NO SESSION DATA"),
    "settings": ("SETTINGS", "Display", "480 × 320  •  Fullscreen  •  Simulated sensors", "CONFIGURED"),
    "diagnostics": ("DIAGNOSTICS", "Nightline system", "UI and simulator are running. Hardware sensors are not connected.", "SIMULATION"),
    "vehicle": ("VEHICLE", "2025 F-150 STX", "Iconic Silver  •  Front sensor layout: 4  •  CAN/OBD unavailable", "PROFILE ONLY"),
}


class InfoScreen(QWidget):
    request_home_screen = Signal()

    def __init__(self, destination: str) -> None:
        super().__init__()
        title, heading, copy, badge = CONTENT[destination]
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 8, 10, 10)
        header = QHBoxLayout()
        back = HudButton("‹ HOME", compact=True)
        back.setMaximumWidth(115)
        back.clicked.connect(self.request_home_screen.emit)
        label = QLabel(title)
        label.setFont(Theme.typography.h2)
        header.addWidget(back)
        header.addStretch()
        header.addWidget(label)
        root.addLayout(header)
        root.addStretch()
        heading_label = QLabel(heading)
        heading_label.setFont(Theme.typography.h1)
        heading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copy_label = QLabel(copy)
        copy_label.setFont(Theme.typography.body)
        copy_label.setWordWrap(True)
        copy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copy_label.setStyleSheet(f"color: {Theme.colors.muted_text.name()};")
        pill_row = QHBoxLayout()
        pill_row.addStretch()
        pill_row.addWidget(StatusPill(badge, Theme.colors.caution if destination == "cameras" else Theme.colors.accent))
        pill_row.addStretch()
        root.addWidget(heading_label)
        root.addWidget(copy_label)
        root.addLayout(pill_row)
        root.addStretch()
