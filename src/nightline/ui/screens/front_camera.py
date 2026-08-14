from PySide6.QtCore import Signal, QTimer, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget
from PySide6.QtGui import QImage, QPixmap
import cv2

from ..widgets import HudButton, StatusPill
from ..theme import Theme
from ...camera import CameraService, CameraState
from ...config import AppConfig

class FrontCameraScreen(QWidget):
    request_home_screen = Signal()

    def __init__(self, config: AppConfig, camera: CameraService) -> None:
        super().__init__()
        self._config = config
        self._camera = camera
        self._fps_counter = 0
        self._last_state = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Theme.metrics.spacing_xl,
            Theme.metrics.spacing_xl,
            Theme.metrics.spacing_xl,
            Theme.metrics.spacing_xl,
        )
        layout.setSpacing(Theme.metrics.spacing_lg)

        # Top Bar
        top_bar = QHBoxLayout()
        self.btn_back = HudButton("Back")
        self.btn_back.clicked.connect(self.request_home_screen.emit)
        top_bar.addWidget(self.btn_back)

        top_bar.addStretch()

        self.lbl_status = StatusPill("Opening...", Theme.colors.caution)
        top_bar.addWidget(self.lbl_status)

        if self._config.show_fps:
            self.lbl_fps = StatusPill("0 FPS", Theme.colors.muted_text)
            top_bar.addWidget(self.lbl_fps)
        else:
            self.lbl_fps = None

        layout.addLayout(top_bar)

        # Content Stack
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        # Page 0: Video Feed
        self.video_page = QWidget()
        video_layout = QVBoxLayout(self.video_page)
        video_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_video = QLabel()
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_video.setStyleSheet(f"background-color: {Theme.colors.panel.name()}; border-radius: {Theme.metrics.radius_lg}px;")
        video_layout.addWidget(self.lbl_video)
        self.stack.addWidget(self.video_page)

        # Page 1: State/Error View
        self.state_page = QWidget()
        state_layout = QVBoxLayout(self.state_page)
        self.lbl_state_msg = QLabel("Camera Disconnected")
        self.lbl_state_msg.setFont(Theme.typography.h2)
        self.lbl_state_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        state_layout.addStretch()
        state_layout.addWidget(self.lbl_state_msg)
        
        self.btn_retry = HudButton("Retry Connection")
        self.btn_retry.clicked.connect(self._on_retry)
        retry_layout = QHBoxLayout()
        retry_layout.addStretch()
        retry_layout.addWidget(self.btn_retry)
        retry_layout.addStretch()
        state_layout.addLayout(retry_layout)
        state_layout.addStretch()
        self.stack.addWidget(self.state_page)

        # Timers
        self._frame_timer = QTimer(self)
        self._frame_timer.timeout.connect(self._update_frame)
        
        self._fps_timer = QTimer(self)
        self._fps_timer.timeout.connect(self._update_fps)

    def showEvent(self, event):
        super().showEvent(event)
        self._frame_timer.start(1000 // self._config.camera_fps)
        self._fps_timer.start(1000)
        self._fps_counter = 0

    def hideEvent(self, event):
        super().hideEvent(event)
        self._frame_timer.stop()
        self._fps_timer.stop()
        self.lbl_video.clear()

    def _on_retry(self):
        if hasattr(self._camera, "stop") and hasattr(self._camera, "start"):
            self._camera.stop()
            self._camera.start()
        self.lbl_status.set_status("Retrying...", Theme.colors.caution)

    def _update_frame(self):
        state = self._camera.health_state
        
        if state != self._last_state:
            self._last_state = state
            if state == CameraState.CONNECTED:
                self.lbl_status.set_status("Streaming", Theme.colors.accent)
                self.stack.setCurrentWidget(self.video_page)
            elif state == CameraState.CONNECTING:
                self.lbl_status.set_status("Opening...", Theme.colors.caution)
                self.lbl_state_msg.setText("Opening Camera...")
                self.lbl_state_msg.setStyleSheet(f"color: {Theme.colors.caution.name()};")
                self.btn_retry.hide()
                self.stack.setCurrentWidget(self.state_page)
            elif state == CameraState.ERROR:
                self.lbl_status.set_status("Failure", Theme.colors.critical)
                self.lbl_state_msg.setText("Camera Persistent Failure")
                self.lbl_state_msg.setStyleSheet(f"color: {Theme.colors.critical.name()};")
                self.btn_retry.show()
                self.stack.setCurrentWidget(self.state_page)
            else:
                self.lbl_status.set_status("Disconnected", Theme.colors.muted_text)
                self.lbl_state_msg.setText("Camera Unavailable")
                self.lbl_state_msg.setStyleSheet(f"color: {Theme.colors.muted_text.name()};")
                self.btn_retry.show()
                self.stack.setCurrentWidget(self.state_page)

        if state == CameraState.CONNECTED:
            frame = self._camera.read()
            if frame is not None:
                self._fps_counter += 1
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                pixmap = QPixmap.fromImage(q_image)
                lbl_size = self.lbl_video.size()
                if lbl_size.width() > 0 and lbl_size.height() > 0:
                    scaled_pixmap = pixmap.scaled(lbl_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.lbl_video.setPixmap(scaled_pixmap)

    def _update_fps(self):
        if self.lbl_fps:
            self.lbl_fps.set_status(f"{self._fps_counter} FPS", Theme.colors.muted_text)
        self._fps_counter = 0
