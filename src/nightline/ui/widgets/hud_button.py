from typing import Optional
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QPaintEvent, QColor, QFontMetrics
from PySide6.QtWidgets import QPushButton, QWidget

from ..theme import Theme

class HudButton(QPushButton):
    """A large touch-friendly button designed for automotive displays."""

    def __init__(self, text: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setMinimumHeight(Theme.metrics.touch_target_min)
        self.setFont(Theme.typography.body_bold)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def sizeHint(self) -> QSize:
        hint = super().sizeHint()
        hint.setHeight(max(hint.height(), Theme.metrics.touch_target_min))
        hint.setWidth(max(hint.width(), Theme.metrics.touch_target_min * 2))
        return hint

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Determine state colors
        if not self.isEnabled():
            bg_color = Theme.colors.panel2
            text_color = Theme.colors.muted_text
            border_color = Theme.colors.panel2
        elif self.isDown():
            bg_color = Theme.colors.accent
            text_color = Theme.colors.background
            border_color = Theme.colors.accent
        else:
            bg_color = Theme.colors.panel
            text_color = Theme.colors.text
            border_color = Theme.colors.panel2

        rect = self.rect().adjusted(1, 1, -1, -1)
        
        # Draw background and border
        painter.setPen(border_color)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(rect, Theme.metrics.radius_md, Theme.metrics.radius_md)

        # Draw text
        painter.setPen(text_color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
