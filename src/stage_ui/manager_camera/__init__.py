# std
from typing import Protocol

# pip
import numpy as np

# local
from stage_ui.manager_camera.cv2 import CV2CameraManager
from stage_ui.manager_camera.mock import MockCameraManager

# public api
__all__ = [
    "CV2CameraManager",
    "CameraManager",
    "MockCameraManager",
]


class CameraManager(Protocol):
    def open(self, index: int) -> None: ...
    def close(self) -> None: ...
    def read_frame(self) -> np.ndarray | None: ...
    def index(self) -> int | None: ...

    def width(self) -> int:
        """
        The feed's width.
        """

    def height(self) -> int:
        """
        The feed's height.
        """
