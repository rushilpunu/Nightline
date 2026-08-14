import pytest
from PySide6.QtGui import QColor
from nightline.ui.widgets import HudButton, StatusPill
from nightline.ui.theme import Theme

def test_hud_button_initialization(qapp):
    btn = HudButton("Test")
    assert btn.text() == "Test"
    
    # Check minimum height for touch target
    assert btn.minimumHeight() >= Theme.metrics.touch_target_min
    
    # Check size hint
    hint = btn.sizeHint()
    assert hint.height() >= Theme.metrics.touch_target_min
    assert hint.width() >= Theme.metrics.touch_target_min * 2

def test_status_pill_initialization(qapp):
    color = QColor("#FF0000")
    pill = StatusPill("Warning", color)
    assert pill._text == "Warning"
    assert pill._color == color
    
    # Minimum height check
    assert pill.minimumHeight() >= Theme.metrics.spacing_xl

def test_status_pill_update(qapp):
    pill = StatusPill("OK", QColor("#00FF00"))
    pill.set_status("Error", QColor("#FF0000"))
    assert pill._text == "Error"
    assert pill._color.name().upper() == "#FF0000"
