import os
from pathlib import Path

import pytest
import yaml

from nightline.config import AppConfig


def test_config_loads_yaml(tmp_path: Path) -> None:
    config_file = tmp_path / "test.yaml"
    config_file.write_text("app:\n  name: Test Config\n")
    config = AppConfig.load(config_file)
    assert config.name == "Test Config"
    assert config.window_width == 800


def test_config_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        AppConfig.load("missing_file_that_does_not_exist.yaml")


def test_config_invalid_yaml(tmp_path: Path) -> None:
    config_file = tmp_path / "invalid.yaml"
    config_file.write_text("app: [this is not\nvalid yaml")
    with pytest.raises(ValueError, match="Invalid YAML"):
        AppConfig.load(config_file)


def test_config_rejects_invalid_dimensions(tmp_path: Path) -> None:
    config_file = tmp_path / "invalid.yaml"
    config_file.write_text("display:\n  width: -100\n")
    with pytest.raises(ValueError, match="Display width"):
        AppConfig.load(config_file)


def test_config_camera_settings(tmp_path: Path) -> None:
    config_file = tmp_path / "camera.yaml"
    config_file.write_text("camera:\n  source: /dev/video1\n  fps: 60\n")
    config = AppConfig.load(config_file)
    assert config.camera_source == "/dev/video1"
    assert config.camera_fps == 60


def test_config_from_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_file = tmp_path / "env.yaml"
    config_file.write_text("app:\n  name: EnvApp\n")
    monkeypatch.setenv("NIGHTLINE_CONFIG", str(config_file))
    config = AppConfig.from_environment()
    assert config.name == "EnvApp"
