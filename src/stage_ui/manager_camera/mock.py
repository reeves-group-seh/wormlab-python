# std
from typing import override

# pip
import numpy as np

# relative
from .base import CameraManager


class MockCameraManager(CameraManager):
    # constants
    WIDTH = 720
    HEIGHT = 480
    LOG_PREFIX = "MockCameraManager"

    def __init__(self) -> None:
        self._index: int | None = None

    @override
    def open(self, index: int) -> None:
        self._index = index
        print(f"{self.LOG_PREFIX}: opened at index {index}")

    @override
    def close(self) -> None:
        self._index = None
        print(f"{self.LOG_PREFIX}: closed")

    @override
    def read_frame(self) -> np.ndarray | None:
        if self._index is None:
            raise Exception("resource has not been opened")

        return np.random.randint(0, 256, (self.WIDTH, self.HEIGHT, 3), dtype=np.uint8)

    @override
    def width(self) -> int:
        if self._index is None:
            raise Exception("resource has not been opened")

        return self.WIDTH

    @override
    def height(self) -> int:
        if self._index is None:
            raise Exception("resource has not been opened")

        return self.HEIGHT
