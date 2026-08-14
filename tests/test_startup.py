from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QTimer

from nightline.app import create_application
from nightline.config import AppConfig


def test_application_starts_and_exits_cleanly() -> None:
    application, window = create_application(
        ["nightline-test"],
        AppConfig(window_width=320, window_height=240),
    )
    window.show()
    QTimer.singleShot(0, application.quit)

    assert application.exec() == 0
    window.close()
