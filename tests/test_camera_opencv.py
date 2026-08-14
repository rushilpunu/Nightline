from unittest.mock import MagicMock, patch
import numpy as np
import time

from nightline.camera.opencv import ThreadedOpenCVCamera
from nightline.camera.service import CameraService

def test_threaded_opencv_camera_satisfies_contract():
    camera = ThreadedOpenCVCamera("/dev/video0")
    assert isinstance(camera, CameraService)
    assert not camera.available

@patch("nightline.camera.opencv.cv2.VideoCapture")
def test_camera_start_success(mock_videocapture):
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    # Simulate a frame read
    mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    mock_cap.read.return_value = (True, mock_frame)
    mock_videocapture.return_value = mock_cap

    camera = ThreadedOpenCVCamera("/dev/video0", fps=30)
    assert not camera.available

    camera.start()
    assert camera.available

    # Let the thread read a frame
    time.sleep(0.1)

    frame = camera.read()
    assert frame is not None
    assert frame.shape == (480, 640, 3)

    camera.stop()
    assert not camera.available
    mock_cap.release.assert_called_once()

@patch("nightline.camera.opencv.cv2.VideoCapture")
def test_camera_start_failure(mock_videocapture):
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = False
    mock_videocapture.return_value = mock_cap

    camera = ThreadedOpenCVCamera("/dev/video0")
    
    camera.start()
    assert not camera.available
    assert camera._thread is None
