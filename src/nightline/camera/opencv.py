from __future__ import annotations

import logging
import threading
import time
from typing import Optional

import cv2

from .service import CameraState

logger = logging.getLogger(__name__)


class ThreadedOpenCVCamera:
    """Threaded OpenCV camera service that continuously reads frames."""

    def __init__(self, device_path: str | int, fps: int = 30) -> None:
        self.device_path = device_path
        self.target_fps = fps
        self._capture: Optional[cv2.VideoCapture] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._latest_frame = None
        self._health_state = CameraState.DISCONNECTED
        self._consecutive_failures = 0
        self._max_failures = 5

    def start(self) -> None:
        """Start the camera capture thread."""
        if self._thread is not None and self._thread.is_alive():
            logger.warning("Camera service already running.")
            return

        self._stop_event.clear()
        self._health_state = CameraState.CONNECTING
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def _connect(self) -> bool:
        """Attempt to connect or reconnect to the camera."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None
            
        self._capture = cv2.VideoCapture(self.device_path)
        if self._capture.isOpened():
            self._health_state = CameraState.CONNECTED
            self._consecutive_failures = 0
            logger.info("Camera connected: %s", self.device_path)
            return True
        else:
            self._health_state = CameraState.ERROR
            logger.error("Failed to open camera: %s", self.device_path)
            if self._capture is not None:
                self._capture.release()
                self._capture = None
            return False

    def _capture_loop(self) -> None:
        """Continuously read frames from the camera, reconnecting on failure."""
        frame_time = 1.0 / self.target_fps
        while not self._stop_event.is_set():
            start_time = time.time()
            
            if self._health_state != CameraState.CONNECTED:
                self._health_state = CameraState.CONNECTING
                if not self._connect():
                    # Wait before retrying connection
                    time.sleep(1.0)
                    continue
            
            if self._capture is not None:
                ret, frame = self._capture.read()
                if ret:
                    self._consecutive_failures = 0
                    with self._lock:
                        self._latest_frame = frame
                else:
                    self._consecutive_failures += 1
                    logger.warning("Failed to read frame. Consecutive failures: %d", self._consecutive_failures)
                    if self._consecutive_failures >= self._max_failures:
                        logger.error("Too many read failures. Reconnecting...")
                        self._health_state = CameraState.ERROR
                        if self._capture is not None:
                            self._capture.release()
                            self._capture = None
            
            elapsed = time.time() - start_time
            sleep_time = max(0.0, frame_time - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stop(self) -> None:
        """Stop the camera capture thread."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

        if self._capture is not None:
            self._capture.release()
            self._capture = None
            
        self._health_state = CameraState.DISCONNECTED

    @property
    def available(self) -> bool:
        """Return whether the camera is ready for use."""
        return self._health_state == CameraState.CONNECTED

    @property
    def health_state(self) -> CameraState:
        """Return the current health state of the camera."""
        return self._health_state

    def read(self):
        """Get the latest frame from the camera."""
        with self._lock:
            if self._latest_frame is not None:
                return self._latest_frame.copy()
            return None
