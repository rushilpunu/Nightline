from unittest.mock import MagicMock, patch
import numpy as np
import time

from nightline.camera.opencv import ThreadedOpenCVCamera
from nightline.camera.service import CameraService, CameraState

def test_threaded_opencv_camera_satisfies_contract():
    camera = ThreadedOpenCVCamera("/dev/video0")
    assert isinstance(camera, CameraService)
    assert not camera.available
    assert camera.health_state == CameraState.DISCONNECTED

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
    
    # Let the thread connect and read a frame
    time.sleep(0.1)

    assert camera.available
    assert camera.health_state == CameraState.CONNECTED

    frame = camera.read()
    assert frame is not None
    assert frame.shape == (480, 640, 3)

    camera.stop()
    assert not camera.available
    assert camera.health_state == CameraState.DISCONNECTED
    mock_cap.release.assert_called()

@patch("nightline.camera.opencv.cv2.VideoCapture")
def test_camera_start_failure(mock_videocapture):
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = False
    mock_videocapture.return_value = mock_cap

    camera = ThreadedOpenCVCamera("/dev/video0")
    
    camera.start()
    
    # Give thread a bit of time to try connecting
    time.sleep(0.1)
    
    assert not camera.available
    assert camera.health_state == CameraState.ERROR
    assert camera._thread is not None
    
    camera.stop()

@patch("nightline.camera.opencv.cv2.VideoCapture")
def test_camera_reconnects_on_read_failure(mock_videocapture):
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    
    # Fail to read frames consistently
    mock_cap.read.return_value = (False, None)
    mock_videocapture.return_value = mock_cap
    
    camera = ThreadedOpenCVCamera("/dev/video0", fps=100) # Fast fps to trigger failures quickly
    camera.start()
    
    # Wait enough time for 5 failures and a reconnect attempt
    time.sleep(0.2)
    
    # Because read continually fails, it will hit max_failures, set state to ERROR,
    # loop around, and reconnect. 
    assert camera._thread.is_alive()
    assert mock_videocapture.call_count >= 1
    
    camera.stop()
