"""Deterministic, non-blocking simulator used until sensor hardware is available."""

from __future__ import annotations

import math
import threading
import time
from collections.abc import Mapping

from .model import FRONT_POSITIONS, ParkingReading, ProviderHealth, ReadingQuality, SensorPosition


class SimulatedParkingProvider:
    """Latest-value provider with realistic independent approach/retreat sweeps."""

    def __init__(self, update_hz: int = 10, freshness_timeout_ms: int = 750) -> None:
        self.update_hz = update_hz
        self.freshness_timeout = freshness_timeout_ms / 1000
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._health = ProviderHealth.INITIALIZING
        self._readings: dict[SensorPosition, ParkingReading] = {}
        self._started_at = 0.0

    @property
    def health(self) -> ProviderHealth:
        with self._lock:
            return self._health

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._started_at = time.monotonic()
        with self._lock:
            self._health = ProviderHealth.INITIALIZING
            self._readings = {}
        self._thread = threading.Thread(target=self._run, name="parking-simulator", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=2)
        self._thread = None
        with self._lock:
            self._health = ProviderHealth.DISCONNECTED

    def snapshot(self) -> Mapping[SensorPosition, ParkingReading]:
        now = time.monotonic()
        with self._lock:
            health = self._health
            values = dict(self._readings)
        if health is ProviderHealth.DISCONNECTED:
            return {
                position: ParkingReading(position, None, now, ReadingQuality.DISCONNECTED)
                for position in FRONT_POSITIONS
            }
        if health is ProviderHealth.FAULT:
            return {
                position: ParkingReading(position, None, now, ReadingQuality.FAULT, fault="Provider fault")
                for position in FRONT_POSITIONS
            }
        return {
            position: values.get(
                position, ParkingReading(position, None, now, ReadingQuality.INITIALIZING)
            ).with_freshness(now, self.freshness_timeout)
            for position in FRONT_POSITIONS
        }

    def set_test_state(
        self,
        health: ProviderHealth,
        readings: Mapping[SensorPosition, ParkingReading] | None = None,
    ) -> None:
        """Deterministic adversarial-state hook for contract/UI tests."""
        with self._lock:
            self._health = health
            if readings is not None:
                self._readings = dict(readings)

    def _run(self) -> None:
        interval = 1 / self.update_hz
        while not self._stop.wait(interval):
            elapsed = time.monotonic() - self._started_at
            now = time.monotonic()
            values: dict[SensorPosition, ParkingReading] = {}
            phase_offsets = (0.0, 0.7, 1.3, 2.0)
            centers = (118.0, 91.0, 102.0, 132.0)
            amplitudes = (72.0, 58.0, 66.0, 76.0)
            for position, phase, center, amplitude in zip(FRONT_POSITIONS, phase_offsets, centers, amplitudes):
                distance = center + amplitude * math.sin(elapsed * 0.42 + phase)
                distance = max(18.0, min(210.0, distance))
                values[position] = ParkingReading(position, round(distance, 1), now, ReadingQuality.LIVE)
            with self._lock:
                if self._health in (ProviderHealth.INITIALIZING, ProviderHealth.CONNECTED):
                    self._readings = values
                    self._health = ProviderHealth.CONNECTED
