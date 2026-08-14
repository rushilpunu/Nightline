from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def get_camera_devices(sys_path: str = "/sys/class/video4linux") -> Dict[str, str]:
    """
    Discover all V4L2 video devices and return a mapping of device paths to their names.
    
    Args:
        sys_path: The sysfs path to search for video devices.
        
    Returns:
        Dict[str, str]: A dictionary where keys are device paths (e.g., '/dev/video0')
                        and values are the device names (e.g., 'Dell UltraSharp Webcam').
    """
    cameras: Dict[str, str] = {}
    v4l_dir = Path(sys_path)
    
    if not v4l_dir.exists():
        logger.debug("V4L2 directory %s does not exist.", v4l_dir)
        return cameras

    for device_dir in v4l_dir.iterdir():
        if not device_dir.is_dir():
            continue
            
        name_file = device_dir / "name"
        if name_file.exists():
            try:
                name = name_file.read_text().strip()
                dev_path = f"/dev/{device_dir.name}"
                cameras[dev_path] = name
            except Exception as e:
                logger.warning("Failed to read name for %s: %s", device_dir.name, e)
                
    return cameras


def find_dell_ultrasharp(sys_path: str = "/sys/class/video4linux") -> Optional[str]:
    """
    Probe the system for a Dell UltraSharp camera.
    
    Args:
        sys_path: The sysfs path to search for video devices.
        
    Returns:
        Optional[str]: The device path of the first Dell UltraSharp camera found,
                       or None if not found.
    """
    cameras = get_camera_devices(sys_path)
    for path, name in cameras.items():
        if "Dell UltraSharp" in name:
            logger.info("Found Dell UltraSharp at %s", path)
            return path
            
    logger.debug("Dell UltraSharp camera not found among devices: %s", cameras)
    return None
