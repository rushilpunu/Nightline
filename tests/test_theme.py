import pytest
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QApplication, QWidget
from nightline.ui.theme import Theme, ThemeColors, ThemeTypography, ThemeMetrics

def test_theme_colors_exist():
    assert isinstance(ThemeColors.background, QColor)
    assert isinstance(ThemeColors.accent, QColor)
    assert ThemeColors.background.name().upper() == "#0D1117"

def test_theme_typography():
    assert isinstance(ThemeTypography.h1, QFont)
    assert ThemeTypography.h1.pointSize() == 21
    assert ThemeTypography.h1.weight() == QFont.Weight.Bold

def test_theme_metrics():
    assert ThemeMetrics.touch_target_min >= 48
    assert ThemeMetrics.spacing_md == 10

def test_theme_application(qapp):
    # qapp fixture is provided by pytest-qt or we can use a QApplication instance if running manually.
    # Since we are using standard PySide6 testing, we'll verify the stylesheet is set.
    app = QApplication.instance()
    Theme.apply(app)
    stylesheet = app.styleSheet()
    assert "background-color: #0d1117" in stylesheet.lower()
    assert "font-family: \"helvetica neue\"" in stylesheet.lower()
