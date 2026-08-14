import pytest
from nightline.camera.discovery import get_camera_devices, find_dell_ultrasharp

def test_get_camera_devices_empty(tmp_path):
    # Test with empty or non-existent sysfs directory
    assert get_camera_devices(str(tmp_path)) == {}

def test_get_camera_devices_with_devices(tmp_path):
    # Create mock sysfs structure
    video0 = tmp_path / "video0"
    video0.mkdir()
    (video0 / "name").write_text("Integrated Camera")

    video1 = tmp_path / "video1"
    video1.mkdir()
    (video1 / "name").write_text("Dell UltraSharp Webcam")
    
    # Add a file that is not a directory, should be ignored
    (tmp_path / "not_a_dir").write_text("ignore me")

    devices = get_camera_devices(str(tmp_path))
    
    assert devices == {
        "/dev/video0": "Integrated Camera",
        "/dev/video1": "Dell UltraSharp Webcam"
    }

def test_find_dell_ultrasharp_found(tmp_path):
    video0 = tmp_path / "video0"
    video0.mkdir()
    (video0 / "name").write_text("Some Other Camera")

    video1 = tmp_path / "video1"
    video1.mkdir()
    (video1 / "name").write_text("Dell UltraSharp Webcam WB7022")

    path = find_dell_ultrasharp(str(tmp_path))
    assert path == "/dev/video1"

def test_find_dell_ultrasharp_not_found(tmp_path):
    video0 = tmp_path / "video0"
    video0.mkdir()
    (video0 / "name").write_text("Integrated Camera")

    path = find_dell_ultrasharp(str(tmp_path))
    assert path is None
