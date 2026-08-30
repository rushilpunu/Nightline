"""Four-front-sensor parking destination."""

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ...sensors import ProviderHealth
from ..theme import Theme
from ..widgets import HudButton, ParkingCanvas, StatusPill


class ParkingScreen(QWidget):
    request_home_screen = Signal()

    def __init__(self, config, provider) -> None:
        super().__init__()
        self._provider = provider
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 7, 8, 7)
        root.setSpacing(4)
        header = QHBoxLayout()
        back = HudButton("‹ HOME", compact=True)
        back.setMaximumWidth(115)
        back.clicked.connect(self.request_home_screen.emit)
        title = QLabel("FRONT PARKING")
        title.setFont(Theme.typography.h2)
        self.status = StatusPill("INITIALIZING", Theme.colors.muted_text)
        header.addWidget(back)
        header.addStretch()
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.status)
        root.addLayout(header)
        self.canvas = ParkingCanvas(
            config.parking_caution_distance_cm,
            config.parking_critical_distance_cm,
            config.parking_hysteresis_cm,
        )
        root.addWidget(self.canvas, 1)
        self._timer = QTimer(self)
        self._timer.setInterval(max(50, 1000 // config.parking_update_hz))
        self._timer.timeout.connect(self.refresh)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._timer.start()
        self.refresh()

    def hideEvent(self, event) -> None:
        self._timer.stop()
        super().hideEvent(event)

    def refresh(self) -> None:
        readings = dict(self._provider.snapshot())
        self.canvas.set_readings(readings)
        health = self._provider.health
        if health is ProviderHealth.CONNECTED:
            bands = self.canvas.bands.values()
            if "critical" in bands:
                self.status.set_status("STOP", Theme.colors.critical)
            elif "caution" in bands:
                self.status.set_status("CAUTION", Theme.colors.caution)
            elif all(band == "safe" for band in bands):
                self.status.set_status("LIVE", Theme.colors.safe)
            else:
                self.status.set_status("CHECK", Theme.colors.caution)
        elif health is ProviderHealth.FAULT:
            self.status.set_status("FAULT", Theme.colors.critical)
        elif health is ProviderHealth.DISCONNECTED:
            self.status.set_status("OFFLINE", Theme.colors.critical)
        else:
            self.status.set_status("INITIALIZING", Theme.colors.muted_text)
