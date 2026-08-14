"""YAML-backed application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

DEFAULT_APP_NAME = "Nightline"
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 480


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

        name = str(app_data.get("name", DEFAULT_APP_NAME)).strip()
        if not name:
            raise ValueError("App name must not be empty")

        log_directory = str(app_data.get("log_directory", "/tmp/nightline"))
        show_fps = bool(app_data.get("show_fps", False))

        window_width = _positive_int(display_data.get("width"), DEFAULT_WINDOW_WIDTH, "Display width")
        window_height = _positive_int(display_data.get("height"), DEFAULT_WINDOW_HEIGHT, "Display height")
        fullscreen = bool(display_data.get("fullscreen", False))

        source = camera_data.get("source", 0)
        if not isinstance(source, (int, str)):
            raise ValueError("Camera source must be an integer index or device path string")

        camera_width = _positive_int(camera_data.get("width"), 640, "Camera width")
        camera_height = _positive_int(camera_data.get("height"), 480, "Camera height")
        camera_fps = _positive_int(camera_data.get("fps"), 30, "Camera FPS")
        camera_reconnect_timing_ms = _positive_int(camera_data.get("reconnect_timing_ms"), 5000, "Camera reconnect timing")

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
        )

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> "AppConfig":
        """Legacy compatibility wrapper."""
        source = os.environ if environment is None else environment
        config_path = source.get("NIGHTLINE_CONFIG", "config/default.yaml")
        return cls.load(config_path)
