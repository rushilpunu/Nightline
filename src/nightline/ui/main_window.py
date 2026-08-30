"""Root window composition and deterministic shallow navigation."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from ..camera import CameraService
from ..config import AppConfig
from ..platform import PlatformInfo
from ..sensors import SimulatedParkingProvider
from .screens import HomeScreen, InfoScreen, ParkingScreen


class MainWindow(QMainWindow):
    def __init__(
        self,
        config: AppConfig,
        camera: CameraService,
        platform: PlatformInfo,
        parking_provider: SimulatedParkingProvider | None = None,
    ) -> None:
        super().__init__()
        self._camera = camera
        self._platform = platform
        self._app_name = config.name
        self._parking_provider = parking_provider or SimulatedParkingProvider(
            config.parking_update_hz, config.parking_freshness_timeout_ms
        )
        self.setWindowTitle(config.name)
        self.resize(config.window_width, config.window_height)
        self.setMinimumSize(config.window_width, config.window_height)
        if config.fullscreen:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)

        self._stack = QStackedWidget(self)
        self.setCentralWidget(self._stack)
        self._home_screen = HomeScreen(config=config, camera=camera)
        self._screens = {"home": self._home_screen}
        parking = ParkingScreen(config, self._parking_provider)
        self._screens["parking"] = parking
        self._stack.addWidget(self._home_screen)
        self._stack.addWidget(parking)
        parking.request_home_screen.connect(self.show_home)
        for destination in ("cameras", "statistics", "settings", "diagnostics", "vehicle"):
            screen = InfoScreen(destination)
            screen.request_home_screen.connect(self.show_home)
            self._screens[destination] = screen
            self._stack.addWidget(screen)
        self._home_screen.destination_requested.connect(self.navigate)
        self.show_home()
        self._parking_provider.start()

        self._quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self._quit_shortcut.activated.connect(self.close)
        self._esc_shortcut = QShortcut(QKeySequence("Esc"), self)
        self._esc_shortcut.activated.connect(self._handle_escape)
        self._fullscreen = config.fullscreen

    @property
    def current_destination(self) -> str:
        current = self._stack.currentWidget()
        return next(key for key, screen in self._screens.items() if screen is current)

    def navigate(self, destination: str) -> None:
        screen = self._screens.get(destination)
        if screen is not None:
            self._stack.setCurrentWidget(screen)
            self.setWindowTitle(f"{self._app_name} • {destination.title()}")

    def show_home(self) -> None:
        self._stack.setCurrentWidget(self._home_screen)
        self.setWindowTitle(f"{self._app_name} • Home")

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self._fullscreen and not self.isFullScreen():
            self.showFullScreen()

    def _handle_escape(self) -> None:
        if self.current_destination != "home":
            self.show_home()
        elif not self.isFullScreen():
            self.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        self._parking_provider.stop()
        self._camera.stop()
        super().closeEvent(event)
