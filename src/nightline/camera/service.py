"""Camera boundary used by UI code."""

from __future__ import annotations

from enum import Enum
from typing import Protocol, runtime_checkable


class CameraState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@runtime_checkable
class CameraService(Protocol):
    """Minimal service contract for future camera implementations."""

    @property
    def available(self) -> bool:
        """Return whether a camera is ready for use."""
        ...

    @property
    def health_state(self) -> CameraState:
        """Return the current health state of the camera."""
        ...

    def stop(self) -> None:
        """Stop the camera service and clean up resources."""
        ...


class NullCameraService:
    """Safe placeholder used until camera discovery is implemented."""

    @property
    def available(self) -> bool:
        return False

    @property
    def health_state(self) -> CameraState:
        return CameraState.DISCONNECTED

    def stop(self) -> None:
        pass
