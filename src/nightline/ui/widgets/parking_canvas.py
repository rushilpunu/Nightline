"""Vehicle-relative four-front-sensor visualization."""

from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPaintEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget

from ...sensors.model import FRONT_POSITIONS, ParkingReading, ReadingQuality, SensorPosition
from ..theme import Theme


class ParkingCanvas(QWidget):
    def __init__(self, caution_cm: float, critical_cm: float, hysteresis_cm: float) -> None:
        super().__init__()
        self._caution = caution_cm
        self._critical = critical_cm
        self._hysteresis = hysteresis_cm
        self._readings: dict[SensorPosition, ParkingReading] = {}
        self._bands: dict[SensorPosition, str] = {}
        asset = Path(__file__).resolve().parent.parent / "assets" / "parking_truck_front-v3.png"
        self._vehicle_pixmap = QPixmap(str(asset))
        self.setMinimumHeight(190)

    @property
    def bands(self) -> dict[SensorPosition, str]:
        return dict(self._bands)

    def set_readings(self, readings: dict[SensorPosition, ParkingReading]) -> None:
        self._readings = dict(readings)
        for position in FRONT_POSITIONS:
            reading = readings.get(position)
            self._bands[position] = self._classify(position, reading)
        self.update()

    def _classify(self, position: SensorPosition, reading: ParkingReading | None) -> str:
        if reading is None or reading.quality is not ReadingQuality.LIVE or reading.distance_cm is None:
            return reading.quality.value if reading else ReadingQuality.INITIALIZING.value
        distance = reading.distance_cm
        if not isinstance(distance, (int, float)) or not math.isfinite(distance) or distance <= 0:
            return "invalid"
        previous = self._bands.get(position)
        if previous == "critical" and distance < self._critical + self._hysteresis:
            return "critical"
        if previous == "caution" and distance < self._caution + self._hysteresis and distance >= self._critical:
            return "caution"
        if distance <= self._critical:
            return "critical"
        if distance <= self._caution:
            return "caution"
        return "safe"

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Theme.colors.background)
        width, height = self.width(), self.height()

        center = width / 2
        sensor_layout = (
            (width * .30, -34, width * .12),
            (width * .445, -8, width * .36),
            (width * .555, 8, width * .64),
            (width * .70, 34, width * .88),
        )
        for position, (base_x, angle, value_x) in zip(FRONT_POSITIONS, sensor_layout):
            reading = self._readings.get(position)
            band = self._bands.get(position, "initializing")
            color = {
                "safe": Theme.colors.safe, "caution": Theme.colors.caution,
                "critical": Theme.colors.critical, "fault": Theme.colors.critical,
                "invalid": Theme.colors.critical,
            }.get(band, Theme.colors.muted_text)
            value = (
                f"{reading.distance_cm:.1f} cm"
                if reading and band in {"safe", "caution", "critical"}
                else "—"
            )
            painter.setPen(color)
            painter.setFont(Theme.typography.body_bold)
            painter.drawText(QRectF(value_x - 52, 0, 104, 22), Qt.AlignmentFlag.AlignCenter, value)

            active_segments = 0
            if reading and band in {"safe", "caution", "critical"}:
                proximity = max(0.0, min(1.0, (210.0 - reading.distance_cm) / 192.0))
                active_segments = 1 + round(proximity * 4)
            painter.save()
            painter.translate(base_x, 151)
            painter.rotate(angle)
            for segment in range(5):
                segment_rect = QRectF(-20, -17 - segment * 16, 40, 10)
                active = segment < active_segments
                fill = QColor(color)
                fill.setAlpha(220 if active else 22)
                outline = QColor(color)
                outline.setAlpha(235 if active else 75)
                painter.setBrush(fill)
                painter.setPen(QPen(outline, 1))
                painter.drawRoundedRect(segment_rect, 4, 4)
            painter.setPen(QPen(color, 2))
            painter.drawLine(0, -4, 0, 3)
            painter.restore()
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(base_x - 3.5, 147.5, 7, 7))

        # The supplied PhotoRoom cutout has genuine alpha and is cropped from
        # the mirrors forward, so no synthetic mask or background is needed.
        if self._vehicle_pixmap.isNull():
            painter.setBrush(QColor("#39434E"))
            painter.setPen(QPen(Theme.colors.silver, 2))
            painter.drawRoundedRect(QRectF(center - 82, 144, 164, height), 24, 24)
        else:
            source = QRectF(180, 0, 700, 700)
            target = QRectF(center - 105, 132, 210, 210)
            painter.drawPixmap(target, self._vehicle_pixmap, source)
