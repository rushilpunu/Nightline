from dataclasses import dataclass
from typing import ClassVar
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QApplication

@dataclass(frozen=True)
class ThemeColors:
    background: ClassVar[QColor] = QColor("#12161D")
    panel: ClassVar[QColor] = QColor("#1B222C")
    panel2: ClassVar[QColor] = QColor("#242C38")
    text: ClassVar[QColor] = QColor("#E6E8EC")
    muted_text: ClassVar[QColor] = QColor("#9AA4B2")
    accent: ClassVar[QColor] = QColor("#4DA3FF")
    caution: ClassVar[QColor] = QColor("#F2A93B")
    critical: ClassVar[QColor] = QColor("#E25555")

@dataclass(frozen=True)
class ThemeTypography:
    @staticmethod
    def _font(size_pt: int, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
        font = QFont("Helvetica Neue", size_pt)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        font.setWeight(weight)
        return font

    h1: ClassVar[QFont] = _font(32, QFont.Weight.Bold)
    h2: ClassVar[QFont] = _font(24, QFont.Weight.Bold)
    body: ClassVar[QFont] = _font(16, QFont.Weight.Normal)
    body_bold: ClassVar[QFont] = _font(16, QFont.Weight.Bold)
    small: ClassVar[QFont] = _font(12, QFont.Weight.Medium)

@dataclass(frozen=True)
class ThemeMetrics:
    spacing_xs: ClassVar[int] = 4
    spacing_sm: ClassVar[int] = 8
    spacing_md: ClassVar[int] = 16
    spacing_lg: ClassVar[int] = 24
    spacing_xl: ClassVar[int] = 32

    radius_sm: ClassVar[int] = 4
    radius_md: ClassVar[int] = 8
    radius_lg: ClassVar[int] = 16
    radius_pill: ClassVar[int] = 9999

    border_width: ClassVar[int] = 2
    touch_target_min: ClassVar[int] = 64
    icon_size: ClassVar[int] = 24

class Theme:
    colors = ThemeColors
    typography = ThemeTypography
    metrics = ThemeMetrics

    @classmethod
    def apply(cls, app: QApplication) -> None:
        style = f"""
            QWidget {{
                background-color: {cls.colors.background.name()};
                color: {cls.colors.text.name()};
                font-family: "Helvetica Neue", sans-serif;
                font-size: 16pt;
            }}
            QLabel {{
                background-color: transparent;
            }}
        """
        app.setStyleSheet(style)
