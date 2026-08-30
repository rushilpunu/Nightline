"""Parking sensor domain boundary and providers."""

from .model import ParkingReading, ProviderHealth, ReadingQuality, SensorPosition
from .simulated import SimulatedParkingProvider

__all__ = [
    "ParkingReading", "ProviderHealth", "ReadingQuality", "SensorPosition",
    "SimulatedParkingProvider",
]
