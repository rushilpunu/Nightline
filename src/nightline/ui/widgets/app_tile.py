"""Full-surface home destination tile."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPaintEvent, QPainter, QPen
from PySide6.QtWidgets import QPushButton

from ..theme import Theme


class AppTile(QPushButton):
    def __init__(self, title: str, subtitle: str, glyph: str, *, primary: bool = False) -> None:
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self.glyph = glyph
        self.primary = primary
        self.setMinimumSize(180, 60)
        self.setAccessibleName(title)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        if self.isDown():
            fill, border = QColor("#2A6090"), Theme.colors.accent.lighter(135)
        elif self.primary:
            fill, border = QColor("#173047"), Theme.colors.accent
        else:
            fill, border = Theme.colors.panel, Theme.colors.panel2.lighter(125)
        painter.setBrush(fill)
        painter.setPen(QPen(border, 2 if self.primary else 1))
        painter.drawRoundedRect(rect, Theme.metrics.radius_md, Theme.metrics.radius_md)

        glyph_rect = rect.adjusted(11, 7, -rect.width() + 46, -7)
        painter.setFont(Theme.typography.h2)
        painter.setPen(Theme.colors.accent if self.primary else Theme.colors.silver)
        painter.drawText(glyph_rect, Qt.AlignmentFlag.AlignCenter, self.glyph)
        text_rect = rect.adjusted(49, 7, -7, -7)
        painter.setFont(Theme.typography.body_bold)
        painter.setPen(Theme.colors.text)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft, self.title)
        painter.setFont(Theme.typography.small)
        painter.setPen(Theme.colors.muted_text)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft, self.subtitle)
