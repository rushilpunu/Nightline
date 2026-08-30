from dataclasses import dataclass
from typing import ClassVar
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QApplication

@dataclass(frozen=True)
class ThemeColors:
    background: ClassVar[QColor] = QColor("#0D1117")
    panel: ClassVar[QColor] = QColor("#181E27")
    panel2: ClassVar[QColor] = QColor("#252D38")
    text: ClassVar[QColor] = QColor("#F1F3F5")
    muted_text: ClassVar[QColor] = QColor("#A5AFBA")
    accent: ClassVar[QColor] = QColor("#3B82C4")
    safe: ClassVar[QColor] = QColor("#6FA8B8")
    caution: ClassVar[QColor] = QColor("#D89A3A")
    critical: ClassVar[QColor] = QColor("#D74C4C")
    silver: ClassVar[QColor] = QColor("#B8C0C8")

@dataclass(frozen=True)
class ThemeTypography:
    @staticmethod
    def _font(size_pt: int, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
        font = QFont("Helvetica Neue", size_pt)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        font.setWeight(weight)
        return font

    h1: ClassVar[QFont] = _font(21, QFont.Weight.Bold)
    h2: ClassVar[QFont] = _font(17, QFont.Weight.Bold)
    body: ClassVar[QFont] = _font(13, QFont.Weight.Normal)
    body_bold: ClassVar[QFont] = _font(13, QFont.Weight.Bold)
    small: ClassVar[QFont] = _font(10, QFont.Weight.Medium)

@dataclass(frozen=True)
class ThemeMetrics:
    spacing_xs: ClassVar[int] = 4
    spacing_sm: ClassVar[int] = 8
    spacing_md: ClassVar[int] = 10
    spacing_lg: ClassVar[int] = 14
    spacing_xl: ClassVar[int] = 18

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
                font-size: 13pt;
            }}
            QLabel {{
                background-color: transparent;
            }}
        """
        app.setStyleSheet(style)
