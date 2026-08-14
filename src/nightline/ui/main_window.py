"""Root window composition."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence, QCloseEvent
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from ..camera import CameraService
from ..config import AppConfig
from ..platform import PlatformInfo
from .screens import HomeScreen, FrontCameraScreen
from .theme import Theme


class MainWindow(QMainWindow):
    """Stable fullscreen application container and navigation shell."""

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

        # Apply fullscreen if configured, removing window chrome.
        if config.fullscreen:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
            self.showFullScreen()

        # Setup stacked widget for screen navigation
        self._stack = QStackedWidget(self)
        self.setCentralWidget(self._stack)

        # Initialize screens
        self._home_screen = HomeScreen()
        self._front_camera_screen = FrontCameraScreen()

        self._stack.addWidget(self._home_screen)
        self._stack.addWidget(self._front_camera_screen)

        # Connect navigation
        self._home_screen.request_camera_screen.connect(
            lambda: self._stack.setCurrentWidget(self._front_camera_screen)
        )
        self._front_camera_screen.request_home_screen.connect(
            lambda: self._stack.setCurrentWidget(self._home_screen)
        )

        # Start at home screen
        self._stack.setCurrentWidget(self._home_screen)

        # Escape path for development (Ctrl+Q always works, Escape only works if not fullscreen kiosk)
        self._quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self._quit_shortcut.activated.connect(self.close)

        self._esc_shortcut = QShortcut(QKeySequence("Esc"), self)
        self._esc_shortcut.activated.connect(self._handle_escape)

    def _handle_escape(self) -> None:
        """Only allow Escape to quit in windowed mode."""
        if not self.isFullScreen():
            self.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Ensure clean application shutdown."""
        if hasattr(self._camera, "stop"):
            self._camera.stop()
        super().closeEvent(event)
