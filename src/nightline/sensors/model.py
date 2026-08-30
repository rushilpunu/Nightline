"""Transport-neutral parking sensor domain types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SensorPosition(Enum):
    FRONT_LEFT_OUTER = "front_left_outer"
    FRONT_LEFT_INNER = "front_left_inner"
    FRONT_RIGHT_INNER = "front_right_inner"
    FRONT_RIGHT_OUTER = "front_right_outer"
    REAR_LEFT_OUTER = "rear_left_outer"
    REAR_LEFT_INNER = "rear_left_inner"
    REAR_RIGHT_INNER = "rear_right_inner"
    REAR_RIGHT_OUTER = "rear_right_outer"


FRONT_POSITIONS = (
    SensorPosition.FRONT_LEFT_OUTER,
    SensorPosition.FRONT_LEFT_INNER,
    SensorPosition.FRONT_RIGHT_INNER,
    SensorPosition.FRONT_RIGHT_OUTER,
)


class ReadingQuality(Enum):
    INITIALIZING = "initializing"
    LIVE = "live"
    STALE = "stale"
    INVALID = "invalid"
    FAULT = "fault"
    DISCONNECTED = "disconnected"


class ProviderHealth(Enum):
    INITIALIZING = "initializing"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    FAULT = "fault"


@dataclass(frozen=True, slots=True)
class ParkingReading:
    position: SensorPosition
    distance_cm: float | None
    monotonic_timestamp: float
    quality: ReadingQuality
    raw_value: object | None = None
    fault: str | None = None

    def with_freshness(self, now: float, timeout_seconds: float) -> "ParkingReading":
        if self.quality is ReadingQuality.LIVE and now - self.monotonic_timestamp > timeout_seconds:
            return ParkingReading(
                self.position, self.distance_cm, self.monotonic_timestamp,
                ReadingQuality.STALE, self.raw_value, self.fault,
            )
        return self
