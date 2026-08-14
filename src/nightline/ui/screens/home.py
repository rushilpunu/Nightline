from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from ..widgets import HudButton, StatusPill
from ..theme import Theme
from ...camera import CameraService, CameraState
from ...config import AppConfig

class HomeScreen(QWidget):
    request_camera_screen = Signal()

    def __init__(self, config: AppConfig, camera: CameraService) -> None:
        super().__init__()
        self._config = config
        self._camera = camera

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Theme.metrics.spacing_xl,
            Theme.metrics.spacing_xl,
            Theme.metrics.spacing_xl,
            Theme.metrics.spacing_xl,
        )
        layout.setSpacing(Theme.metrics.spacing_lg)

        title = QLabel("Nightline")
        title.setFont(Theme.typography.h1)
        layout.addWidget(title)

        # Dominant Front Camera Tile
        self.btn_camera = HudButton("Front Camera")
        self.btn_camera.setMinimumHeight(200)
        self.btn_camera.clicked.connect(self.request_camera_screen.emit)
        layout.addWidget(self.btn_camera)

        layout.addStretch()

        # Status strip
        status_layout = QHBoxLayout()
        status_layout.setSpacing(Theme.metrics.spacing_md)
        
        self.lbl_camera_status = StatusPill("Camera: Unknown", Theme.colors.muted_text)
        status_layout.addWidget(self.lbl_camera_status)
        
        lbl_resolution = StatusPill(f"Resolution: {config.camera_width}x{config.camera_height}", Theme.colors.muted_text)
        status_layout.addWidget(lbl_resolution)

        lbl_app_status = StatusPill("App: OK", Theme.colors.accent)
        status_layout.addWidget(lbl_app_status)
        
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Status poll timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_status)
        self._timer.start(500)
        self._update_status()

    def _update_status(self) -> None:
        state = self._camera.health_state
        if state == CameraState.CONNECTED:
            self.lbl_camera_status.set_status("Camera: Connected", Theme.colors.accent)
        elif state == CameraState.CONNECTING:
            self.lbl_camera_status.set_status("Camera: Connecting", Theme.colors.caution)
        elif state == CameraState.ERROR:
            self.lbl_camera_status.set_status("Camera: Error", Theme.colors.critical)
        else:
            self.lbl_camera_status.set_status("Camera: Disconnected", Theme.colors.muted_text)
