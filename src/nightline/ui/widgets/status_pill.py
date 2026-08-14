from typing import Optional
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QPaintEvent, QColor
from PySide6.QtWidgets import QWidget

from ..theme import Theme

class StatusPill(QWidget):
    """A pill-shaped status indicator."""

    def __init__(self, text: str, color: QColor, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._text = text
        self._color = color
        self.setFont(Theme.typography.small)
        self.setMinimumHeight(Theme.metrics.spacing_xl)

    def set_status(self, text: str, color: QColor) -> None:
        self._text = text
        self._color = color
        self.update()

    def sizeHint(self) -> QSize:
        metrics = self.fontMetrics()
        width = metrics.horizontalAdvance(self._text) + Theme.metrics.spacing_lg * 2
        return QSize(width, max(Theme.metrics.spacing_xl, metrics.height() + Theme.metrics.spacing_sm * 2))

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(1, 1, -1, -1)
        
        # Draw background (tinted with color)
        bg_color = QColor(self._color)
        bg_color.setAlpha(40) # 15% opacity
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(rect, rect.height() / 2, rect.height() / 2)

        # Draw border
        painter.setPen(self._color)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, rect.height() / 2, rect.height() / 2)

        # Draw text
        painter.setPen(self._color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._text)
