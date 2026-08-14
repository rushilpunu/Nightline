from nightline.camera import CameraService, NullCameraService
from nightline.camera.service import CameraState

def test_null_camera_satisfies_service_contract() -> None:
    camera = NullCameraService()

    assert isinstance(camera, CameraService)
    assert camera.available is False
    assert camera.health_state == CameraState.DISCONNECTED
