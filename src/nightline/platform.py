"""Platform discovery kept separate from application startup."""

from __future__ import annotations

import platform as system_platform
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlatformInfo:
    """Small, immutable snapshot of the host running Nightline."""

    system: str
    machine: str

    @classmethod
    def current(cls) -> "PlatformInfo":
        return cls(system=system_platform.system(), machine=system_platform.machine())
