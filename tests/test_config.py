import pytest

from nightline.config import AppConfig


def test_config_uses_defaults() -> None:
    assert AppConfig.from_environment({}) == AppConfig()


def test_config_reads_environment() -> None:
    config = AppConfig.from_environment(
        {
            "NIGHTLINE_APP_NAME": "Bench Nightline",
            "NIGHTLINE_WINDOW_WIDTH": "1024",
            "NIGHTLINE_WINDOW_HEIGHT": "600",
        }
    )

    assert config == AppConfig("Bench Nightline", 1024, 600)


def test_config_rejects_invalid_dimensions() -> None:
    with pytest.raises(ValueError, match="NIGHTLINE_WINDOW_WIDTH"):
        AppConfig.from_environment({"NIGHTLINE_WINDOW_WIDTH": "0"})
