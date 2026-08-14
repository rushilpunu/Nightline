"""Nightline application entry point."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from .camera import NullCameraService
from .config import AppConfig
from .platform import PlatformInfo
from .ui import MainWindow


def create_application(
    argv: Sequence[str] | None = None,
    config: AppConfig | None = None,
) -> tuple[QApplication, MainWindow]:
    """Build the Qt application and its root window without starting the loop."""
    settings = config or AppConfig.load()
    application = QApplication.instance() or QApplication(list(argv or sys.argv))
    application.setApplicationName(settings.name)

    window = MainWindow(
        config=settings,
        camera=NullCameraService(),
        platform=PlatformInfo.current(),
    )
    return application, window


def main(argv: Sequence[str] | None = None) -> int:
    """Show the Nightline window and return Qt's process exit status."""
    command = argparse.ArgumentParser(description="Start the Nightline application")
    command.add_argument(
        "--quit-after-ms",
        type=int,
        help="close automatically after this many milliseconds (smoke tests)",
    )
    command.add_argument(
        "--config",
        type=str,
        help="path to YAML configuration file",
        default=None,
    )
    arguments, qt_arguments = command.parse_known_args(
        list(sys.argv[1:] if argv is None else argv)
    )
    if arguments.quit_after_ms is not None and arguments.quit_after_ms < 0:
        command.error("--quit-after-ms must be zero or greater")

    try:
        config = AppConfig.load(arguments.config)
    except (ValueError, FileNotFoundError) as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    application, window = create_application([sys.argv[0], *qt_arguments], config=config)
    window.show()
    if arguments.quit_after_ms is not None:
        QTimer.singleShot(arguments.quit_after_ms, window.close)
    return application.exec()


if __name__ == "__main__":
    sys.exit(main())
