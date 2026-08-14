"""Root window composition."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget

from ..camera import CameraService
from ..config import AppConfig
from ..platform import PlatformInfo
from .widgets import HudButton, StatusPill
from .theme import Theme


class MainWindow(QMainWindow):
    """Minimal startup window; final product screens belong in later work."""

    def __init__(
        self,
        config: AppConfig,
        camera: CameraService,
        platform: PlatformInfo,
    ) -> None:
        super().__init__()
        self._camera = camera
        self._platform = platform

        self.setWindowTitle(config.name)
        self.resize(config.window_width, config.window_height)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(Theme.metrics.spacing_xl, Theme.metrics.spacing_xl, Theme.metrics.spacing_xl, Theme.metrics.spacing_xl)
        layout.setSpacing(Theme.metrics.spacing_lg)

        title = QLabel(f"{config.name} Widget Showcase")
        title.setFont(Theme.typography.h1)
        layout.addWidget(title)

        camera_status = "Available" if camera.available else "Not Configured"
        subtitle = QLabel(f"Platform: {platform.system} | Camera: {camera_status}")
        subtitle.setFont(Theme.typography.body)
        subtitle.setStyleSheet(f"color: {Theme.colors.muted_text.name()};")
        layout.addWidget(subtitle)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(Theme.metrics.spacing_md)
        
        btn_normal = HudButton("Normal Button")
        btn_layout.addWidget(btn_normal)

        btn_disabled = HudButton("Disabled Button")
        btn_disabled.setEnabled(False)
        btn_layout.addWidget(btn_disabled)

        layout.addLayout(btn_layout)

        # Status Pills
        pill_layout = QHBoxLayout()
        pill_layout.setSpacing(Theme.metrics.spacing_md)
        
        pill_normal = StatusPill("Normal", Theme.colors.accent)
        pill_layout.addWidget(pill_normal)

        pill_caution = StatusPill("Caution", Theme.colors.caution)
        pill_layout.addWidget(pill_caution)

        pill_critical = StatusPill("Critical", Theme.colors.critical)
        pill_layout.addWidget(pill_critical)

        pill_layout.addStretch()
        layout.addLayout(pill_layout)

        layout.addStretch()
        self.setCentralWidget(central_widget)
