# std
from abc import ABC, abstractmethod

# pip
import numpy as np


class CameraManager(ABC):
    @abstractmethod
    def open(self, index: int) -> None:
        """
        Open the camera at the given index. Open failures should not raise an
        exception.
        """
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """
        Close the camera if open, otherwise a no-op.
        """
        raise NotImplementedError

    @abstractmethod
    def read_frame(self) -> np.ndarray | None:
        """
        Read a frame from the camera, if one is available, otherwise `None`.
        """
        raise NotImplementedError

    @abstractmethod
    def width(self) -> int:
        """
        The opened feed's width.
        """
        raise NotImplementedError

    @abstractmethod
    def height(self) -> int:
        """
        The opened feed's height.
        """
