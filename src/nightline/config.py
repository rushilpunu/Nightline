"""Environment-backed application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

DEFAULT_APP_NAME = "Nightline"
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 480


def _positive_int(value: str | None, default: int, variable: str) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError as error:
        raise ValueError(f"{variable} must be an integer") from error
    if parsed <= 0:
        raise ValueError(f"{variable} must be greater than zero")
    return parsed


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Runtime values that are safe for UI and service consumers."""

    name: str = DEFAULT_APP_NAME
    window_width: int = DEFAULT_WINDOW_WIDTH
    window_height: int = DEFAULT_WINDOW_HEIGHT

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> "AppConfig":
        source = os.environ if environment is None else environment
        name = source.get("NIGHTLINE_APP_NAME", DEFAULT_APP_NAME).strip()
        if not name:
            raise ValueError("NIGHTLINE_APP_NAME must not be empty")
        return cls(
            name=name,
            window_width=_positive_int(
                source.get("NIGHTLINE_WINDOW_WIDTH"),
                DEFAULT_WINDOW_WIDTH,
                "NIGHTLINE_WINDOW_WIDTH",
            ),
            window_height=_positive_int(
                source.get("NIGHTLINE_WINDOW_HEIGHT"),
                DEFAULT_WINDOW_HEIGHT,
                "NIGHTLINE_WINDOW_HEIGHT",
            ),
        )
