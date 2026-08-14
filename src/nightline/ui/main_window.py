"""Root window composition."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow

from ..camera import CameraService
from ..config import AppConfig
from ..platform import PlatformInfo


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

        camera_status = "available" if camera.available else "not configured"
        label = QLabel(
            f"{config.name}\n\nCamera: {camera_status}\n"
            f"Platform: {platform.system} ({platform.machine})"
        )
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(label)
