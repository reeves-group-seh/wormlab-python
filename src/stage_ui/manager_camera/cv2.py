# std
from typing import override

# pip
import cv2
import numpy as np

# relative
from .base import CameraManager


# @dataclass(kw_only=True)
class CV2CameraManager(CameraManager):
    """
    Class for handling frame capture and other video-related logic.
    """

    # instance variables
    _feed: cv2.VideoCapture | None

    def __init__(self) -> None:
        self._feed = None

    @override
    def open(self, index: int) -> None:
        self._feed = cv2.VideoCapture(index)

    @override
    def close(self) -> None:
        if self._feed:
            self._feed.release()
            self._feed = None

    @override
    def read_frame(self) -> np.ndarray | None:
        # ensure open
        if not self._feed:
            raise Exception("resource has not been opened")

        # read frame from device
        success, frame = self._feed.read()
        if not success:
            return None

        # convert frame data before returning
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    @override
    def width(self) -> int:
        # ensure open
        if not self._feed:
            raise Exception("resource has not been opened")

        # query cv2
        return int(self._feed.get(cv2.CAP_PROP_FRAME_WIDTH))

    @override
    def height(self) -> int:
        # ensure open
        if not self._feed:
            raise Exception("resource has not been opened")

        # query cv2
        return int(self._feed.get(cv2.CAP_PROP_FRAME_HEIGHT))
