"""Camera boundary used by UI code."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class CameraService(Protocol):
    """Minimal service contract for future camera implementations."""

    @property
    def available(self) -> bool:
        """Return whether a camera is ready for use."""
        ...


class NullCameraService:
    """Safe placeholder used until camera discovery is implemented."""

    @property
    def available(self) -> bool:
        return False
