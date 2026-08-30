from __future__ import annotations

import threading
import time

from nightline.sensors import (
    ParkingReading, ProviderHealth, ReadingQuality, SensorPosition,
    SimulatedParkingProvider,
)
from nightline.sensors.model import FRONT_POSITIONS


def test_simulator_maps_all_four_positions_and_stops_cleanly() -> None:
    baseline = threading.active_count()
    provider = SimulatedParkingProvider(update_hz=50)
    provider.start()
    time.sleep(.05)
    snapshot = provider.snapshot()
    assert tuple(snapshot) == FRONT_POSITIONS
    assert provider.health is ProviderHealth.CONNECTED
    assert all(reading.quality is ReadingQuality.LIVE for reading in snapshot.values())
    provider.stop()
    assert provider.health is ProviderHealth.DISCONNECTED
    assert threading.active_count() <= baseline


def test_stale_missing_disconnected_and_fault_states_are_explicit() -> None:
    provider = SimulatedParkingProvider(freshness_timeout_ms=10)
    now = time.monotonic()
    position = SensorPosition.FRONT_LEFT_OUTER
    provider.set_test_state(ProviderHealth.CONNECTED, {
        position: ParkingReading(position, 120, now - 1, ReadingQuality.LIVE),
    })
    snapshot = provider.snapshot()
    assert snapshot[position].quality is ReadingQuality.STALE
    assert snapshot[SensorPosition.FRONT_LEFT_INNER].quality is ReadingQuality.INITIALIZING
    provider.set_test_state(ProviderHealth.DISCONNECTED)
    assert all(value.quality is ReadingQuality.DISCONNECTED for value in provider.snapshot().values())
    provider.set_test_state(ProviderHealth.FAULT)
    assert all(value.quality is ReadingQuality.FAULT for value in provider.snapshot().values())
