# std
from typing import ClassVar, override

# pip
import numpy as np

# relative
from ._base import CameraBackend


class MockCameraBackend(CameraBackend):
    # class constants
    _WIDTH: ClassVar[int] = 720
    _HEIGHT: ClassVar[int] = 480
    _LOG_PREFIX: ClassVar[str] = "MockCameraBackend"

    # instance variables
    _index: int | None

    def __init__(self) -> None:
        self._index = None

    @override
    def open(self, index: int) -> None:
        self._index = index
        print(f"{self._LOG_PREFIX}: opened at index {index}")

    @override
    def close(self) -> None:
        # already closed
        if self._index is None:
            print(f"{self._LOG_PREFIX}: attempted to close non-open index")
            return

        # close
        print(f"{self._LOG_PREFIX}: closed at index {self._index}")
        self._index = None

    @override
    def read_frame(self) -> np.ndarray | None:
        if self._index is None:
            raise Exception("resource has not been opened")

        return np.random.randint(0, 256, (self._WIDTH, self._HEIGHT, 3), dtype=np.uint8)

    @override
    def width(self) -> int:
        if self._index is None:
            raise Exception("resource has not been opened")

        return self._WIDTH

    @override
    def height(self) -> int:
        if self._index is None:
            raise Exception("resource has not been opened")

        return self._HEIGHT
