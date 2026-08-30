"""Touch-first paged application launcher."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPointF, Signal, Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QStackedWidget, QVBoxLayout, QWidget

from ..theme import Theme
from ..widgets import AppTile, HudButton


class HomeScreen(QWidget):
    destination_requested = Signal(str)

    APPS = (
        ("parking", "Parking", "4 sensors live", "P", True),
        ("cameras", "Cameras", "Coming soon", "C", False),
        ("statistics", "Statistics", "Session overview", "S", False),
        ("settings", "Settings", "Display & system", "⚙", False),
        ("diagnostics", "Diagnostics", "System health", "D", False),
        ("vehicle", "Vehicle", "F-150 profile", "V", False),
    )

    def __init__(self, config, camera=None) -> None:
        super().__init__()
        self._touch_start: QPointF | None = None
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)
        root = QVBoxLayout(self)
        root.setContentsMargins(9, 7, 9, 7)
        root.setSpacing(5)
        header = QHBoxLayout()
        title = QLabel("NIGHTLINE")
        title.setFont(Theme.typography.h1)
        title.setStyleSheet(f"letter-spacing: 2px; color: {Theme.colors.text.name()};")
        header.addWidget(title)
        header.addStretch()
        vehicle = QLabel("FRONT  •  READY")
        vehicle.setFont(Theme.typography.small)
        vehicle.setStyleSheet(f"color: {Theme.colors.safe.name()};")
        header.addWidget(vehicle)
        root.addLayout(header)
        self.pages = QStackedWidget()
        apps_page = QWidget()
        grid = QGridLayout(apps_page)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(7)
        grid.setVerticalSpacing(5)
        self.tiles: dict[str, AppTile] = {}
        for index, (key, title_text, subtitle, glyph, primary) in enumerate(self.APPS):
            tile = AppTile(title_text, subtitle, glyph, primary=primary)
            tile.clicked.connect(lambda checked=False, destination=key: self.destination_requested.emit(destination))
            grid.addWidget(tile, index // 2, index % 2)
            self.tiles[key] = tile
        self.pages.addWidget(apps_page)
        future = QWidget()
        future_layout = QVBoxLayout(future)
        future_title = QLabel("READY FOR MORE")
        future_title.setFont(Theme.typography.h2)
        future_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        future_copy = QLabel("Future vehicle apps will appear here.\nNo hardware features are implied.")
        future_copy.setFont(Theme.typography.body)
        future_copy.setStyleSheet(f"color: {Theme.colors.muted_text.name()};")
        future_copy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        future_layout.addStretch()
        future_layout.addWidget(future_title)
        future_layout.addWidget(future_copy)
        future_layout.addStretch()
        self.pages.addWidget(future)
        root.addWidget(self.pages, 1)
        nav = QHBoxLayout()
        self.previous_button = HudButton("‹  PREV", compact=True)
        self.next_button = HudButton("NEXT  ›", compact=True)
        self.page_label = QLabel("1 / 2")
        self.page_label.setFont(Theme.typography.small)
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.previous_button.clicked.connect(lambda: self.set_page(self.pages.currentIndex() - 1))
        self.next_button.clicked.connect(lambda: self.set_page(self.pages.currentIndex() + 1))
        nav.addWidget(self.previous_button)
        nav.addStretch()
        nav.addWidget(self.page_label)
        nav.addStretch()
        nav.addWidget(self.next_button)
        root.addLayout(nav)
        self.set_page(0)

    def set_page(self, index: int) -> None:
        index = max(0, min(index, self.pages.count() - 1))
        self.pages.setCurrentIndex(index)
        self.page_label.setText(f"{index + 1} / {self.pages.count()}")
        self.previous_button.setEnabled(index > 0)
        self.next_button.setEnabled(index < self.pages.count() - 1)

    def event(self, event) -> bool:
        if event.type() == QEvent.Type.TouchBegin:
            self._touch_start = event.points()[0].position()
            event.accept()
            return True
        if event.type() == QEvent.Type.TouchEnd and self._touch_start is not None:
            self._finish_swipe(event.points()[0].position())
            event.accept()
            return True
        return super().event(event)

    def mousePressEvent(self, event) -> None:
        self._touch_start = event.position()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._finish_swipe(event.position())
        super().mouseReleaseEvent(event)

    def _finish_swipe(self, end: QPointF) -> None:
        if self._touch_start is None:
            return
        delta = end.x() - self._touch_start.x()
        self._touch_start = None
        if abs(delta) >= 65:
            self.set_page(self.pages.currentIndex() + (1 if delta < 0 else -1))
