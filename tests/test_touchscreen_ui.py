from __future__ import annotations

import threading
import time

from PySide6.QtCore import QPointF, Qt
from PySide6.QtTest import QTest

from nightline.camera import NullCameraService
from nightline.config import AppConfig
from nightline.platform import PlatformInfo
from nightline.sensors import ParkingReading, ProviderHealth, ReadingQuality, SensorPosition, SimulatedParkingProvider
from nightline.ui.main_window import MainWindow
from nightline.ui.screens import HomeScreen
from nightline.ui.screens import ParkingScreen
from nightline.ui.widgets import ParkingCanvas


def test_home_has_exactly_six_full_surface_tiles_and_paging(qapp) -> None:
    home = HomeScreen(AppConfig())
    home.resize(480, 320)
    home.show()
    qapp.processEvents()
    assert list(home.tiles) == ["parking", "cameras", "statistics", "settings", "diagnostics", "vehicle"]
    assert all(tile.width() >= 180 and tile.height() >= 60 for tile in home.tiles.values())
    assert home.pages.currentIndex() == 0
    QTest.mouseClick(home.next_button, Qt.MouseButton.LeftButton)
    assert home.pages.currentIndex() == 1
    home._touch_start = QPointF(400, 150)
    home._finish_swipe(QPointF(100, 150))
    assert home.pages.currentIndex() == 1
    home._touch_start = QPointF(100, 150)
    home._finish_swipe(QPointF(400, 150))
    assert home.pages.currentIndex() == 0
    home.close()


def test_parking_bands_apply_hysteresis_and_reject_non_live(qapp) -> None:
    canvas = ParkingCanvas(80, 35, 5)
    pos = SensorPosition.FRONT_LEFT_OUTER
    now = time.monotonic()
    def update(distance, quality=ReadingQuality.LIVE):
        canvas.set_readings({pos: ParkingReading(pos, distance, now, quality)})
        return canvas.bands[pos]
    assert update(34) == "critical"
    assert update(38) == "critical"
    assert update(41) == "caution"
    assert update(82) == "caution"
    assert update(86) == "safe"
    assert update(None, ReadingQuality.INVALID) == "invalid"
    assert update(float("nan")) == "invalid"
    assert update(-1) == "invalid"
    assert update("malformed") == "invalid"
    canvas.resize(480, 220)
    assert not canvas.grab().isNull()


def test_parking_screen_explains_adverse_provider_states(qapp) -> None:
    provider = SimulatedParkingProvider()
    screen = ParkingScreen(AppConfig(), provider)
    now = time.monotonic()
    safe = {
        position: ParkingReading(position, 150, now, ReadingQuality.LIVE)
        for position in (
            SensorPosition.FRONT_LEFT_OUTER,
            SensorPosition.FRONT_LEFT_INNER,
            SensorPosition.FRONT_RIGHT_INNER,
            SensorPosition.FRONT_RIGHT_OUTER,
        )
    }
    provider.set_test_state(ProviderHealth.CONNECTED, safe)
    screen.refresh()
    assert screen.status._text == "LIVE"
    provider.set_test_state(ProviderHealth.CONNECTED, {
        position: ParkingReading(position, None, now, ReadingQuality.INVALID)
        for position in safe
    })
    screen.refresh()
    assert screen.status._text == "CHECK"
    provider.set_test_state(ProviderHealth.DISCONNECTED)
    screen.refresh()
    assert screen.status._text == "OFFLINE"
    provider.set_test_state(ProviderHealth.FAULT)
    screen.refresh()
    assert screen.status._text == "FAULT"


def test_all_destinations_and_100_cycle_soak_are_stable(qapp) -> None:
    provider = SimulatedParkingProvider(update_hz=20)
    window = MainWindow(AppConfig(window_width=480, window_height=320), NullCameraService(), PlatformInfo.current(), provider)
    window.show()
    qapp.processEvents()
    baseline = threading.active_count()
    for destination in ("parking", "cameras", "statistics", "settings", "diagnostics", "vehicle"):
        window.navigate(destination)
        assert window.current_destination == destination
        window.show_home()
    for _ in range(100):
        window.navigate("parking")
        window.show_home()
    qapp.processEvents()
    assert window.size().width() == 480 and window.size().height() == 320
    assert threading.active_count() == baseline
    window.close()
