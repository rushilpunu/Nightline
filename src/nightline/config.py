"""YAML-backed application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

DEFAULT_APP_NAME = "Nightline"
DEFAULT_WINDOW_WIDTH = 480
DEFAULT_WINDOW_HEIGHT = 320


def _positive_int(value: Any, default: int, name: str) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except (ValueError, TypeError) as error:
        raise ValueError(f"{name} must be an integer") from error
    if parsed <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return parsed


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Runtime values that are safe for UI and service consumers."""

    name: str = DEFAULT_APP_NAME
    log_directory: str = "/tmp/nightline"
    show_fps: bool = False

    window_width: int = DEFAULT_WINDOW_WIDTH
    window_height: int = DEFAULT_WINDOW_HEIGHT
    fullscreen: bool = False

    camera_source: int | str = 0
    camera_width: int = 640
    camera_height: int = 480
    camera_fps: int = 30
    camera_reconnect_timing_ms: int = 5000

    parking_provider: str = "simulated"
    parking_units: str = "cm"
    parking_update_hz: int = 10
    parking_freshness_timeout_ms: int = 750
    parking_caution_distance_cm: float = 80.0
    parking_critical_distance_cm: float = 35.0
    parking_hysteresis_cm: float = 5.0

    @classmethod
    def load(cls, config_path: str | Path | None = None) -> "AppConfig":
        """Load configuration from YAML file and arguments."""
        if config_path is None:
            config_path = os.environ.get("NIGHTLINE_CONFIG", "config/default.yaml")

        path = Path(config_path)
        if not path.is_file():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file {path}: {e}")

        if not isinstance(data, dict):
            data = {}

        app_data = data.get("app") or {}
        if not isinstance(app_data, dict):
            app_data = {}
        display_data = data.get("display") or {}
        if not isinstance(display_data, dict):
            display_data = {}
        camera_data = data.get("camera") or {}
        if not isinstance(camera_data, dict):
            camera_data = {}
        parking_data = data.get("parking") or {}
        if not isinstance(parking_data, dict):
            parking_data = {}

        name = str(app_data.get("name", DEFAULT_APP_NAME)).strip()
        if not name:
            raise ValueError("App name must not be empty")

        log_directory = str(app_data.get("log_directory", "/tmp/nightline"))
        show_fps = bool(app_data.get("show_fps", False))

        window_width = _positive_int(
            os.environ.get("NIGHTLINE_WINDOW_WIDTH", display_data.get("width")),
            DEFAULT_WINDOW_WIDTH, "Display width",
        )
        window_height = _positive_int(
            os.environ.get("NIGHTLINE_WINDOW_HEIGHT", display_data.get("height")),
            DEFAULT_WINDOW_HEIGHT, "Display height",
        )
        fullscreen_value = os.environ.get("NIGHTLINE_FULLSCREEN", display_data.get("fullscreen", False))
        if isinstance(fullscreen_value, str):
            fullscreen = fullscreen_value.strip().lower() in {"1", "true", "yes", "on"}
        else:
            fullscreen = bool(fullscreen_value)

        source = camera_data.get("source", 0)
        if not isinstance(source, (int, str)):
            raise ValueError("Camera source must be an integer index or device path string")

        camera_width = _positive_int(camera_data.get("width"), 640, "Camera width")
        camera_height = _positive_int(camera_data.get("height"), 480, "Camera height")
        camera_fps = _positive_int(camera_data.get("fps"), 30, "Camera FPS")
        camera_reconnect_timing_ms = _positive_int(camera_data.get("reconnect_timing_ms"), 5000, "Camera reconnect timing")

        parking_provider = str(parking_data.get("provider", "simulated")).strip().lower()
        if parking_provider != "simulated":
            raise ValueError("Parking provider must be 'simulated' until hardware is configured")
        parking_units = str(parking_data.get("units", "cm")).strip().lower()
        if parking_units != "cm":
            raise ValueError("Parking units must be 'cm'")
        parking_update_hz = _positive_int(parking_data.get("update_hz"), 10, "Parking update rate")
        parking_freshness_timeout_ms = _positive_int(
            parking_data.get("freshness_timeout_ms"), 750, "Parking freshness timeout"
        )
        try:
            caution = float(parking_data.get("caution_distance_cm", 80))
            critical = float(parking_data.get("critical_distance_cm", 35))
            hysteresis = float(parking_data.get("hysteresis_cm", 5))
        except (TypeError, ValueError) as error:
            raise ValueError("Parking distance thresholds must be numbers") from error
        if critical <= 0 or caution <= critical or hysteresis < 0:
            raise ValueError("Parking thresholds must satisfy 0 < critical < caution and hysteresis >= 0")

        return cls(
            name=name,
            log_directory=log_directory,
            show_fps=show_fps,
            window_width=window_width,
            window_height=window_height,
            fullscreen=fullscreen,
            camera_source=source,
            camera_width=camera_width,
            camera_height=camera_height,
            camera_fps=camera_fps,
            camera_reconnect_timing_ms=camera_reconnect_timing_ms,
            parking_provider=parking_provider,
            parking_units=parking_units,
            parking_update_hz=parking_update_hz,
            parking_freshness_timeout_ms=parking_freshness_timeout_ms,
            parking_caution_distance_cm=caution,
            parking_critical_distance_cm=critical,
            parking_hysteresis_cm=hysteresis,
        )

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> "AppConfig":
        """Legacy compatibility wrapper."""
        source = os.environ if environment is None else environment
        config_path = source.get("NIGHTLINE_CONFIG", "config/default.yaml")
        return cls.load(config_path)
