# pip
import numpy as np

# constants
WIDTH = 720
HEIGHT = 480
LOG_PREFIX = "MockCameraManager"


class MockCameraManager:
    def __init__(self) -> None:
        self._index: int | None = None

    def open(self, index: int) -> None:
        self._index = index
        print(f"{LOG_PREFIX}: opened at index {index}")

    def close(self) -> None:
        self._index = None
        print(f"{LOG_PREFIX}: closed")

    def read_frame(self) -> np.ndarray | None:
        if self._index is None:
            raise Exception("resource has not been opened")

        return np.random.randint(0, 256, (WIDTH, HEIGHT, 3), dtype=np.uint8)

    def index(self) -> int | None:
        return self._index

    def width(self) -> int:
        if self._index is None:
            raise Exception("resource has not been opened")

        return WIDTH

    def height(self) -> int:
        if self._index is None:
            raise Exception("resource has not been opened")

        return HEIGHT
