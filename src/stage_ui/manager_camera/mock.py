# module imports
import numpy as np


# constants
WIDTH = 720
HEIGHT = 480
LOG_PREFIX = "MockCameraManager"


class MockCameraManager:
    def __init__(self) -> None:
        self.is_open = False

    def open(self, index: int) -> None:
        self.is_open = True
        print(f"{LOG_PREFIX}: opened at index {index}")

    def close(self) -> None:
        self.is_open = False
        print(f"{LOG_PREFIX}: closed")

    def read_frame(self) -> np.ndarray | None:
        if not self.is_open:
            raise Exception("resource has not been opened")

        return np.random.randint(0, 256, (HEIGHT, WIDTH, 3), dtype=np.uint8)

    def width(self) -> int:
        if not self.is_open:
            raise Exception("resource has not been opened")

        return WIDTH

    def height(self) -> int:
        if not self.is_open:
            raise Exception("resource has not been opened")

        return HEIGHT
