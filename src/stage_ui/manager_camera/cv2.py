# module imports
import cv2
import numpy as np

# item imports
from cv2 import VideoCapture


# @dataclass(kw_only=True)
class CV2CameraManager:
    """
    Class for handling frame capture and other video-related logic.
    """

    def __init__(self) -> None:
        self._feed: VideoCapture | None

    def open(self, index: int) -> None:
        """
        Open the camera with the given index.
        """
        self._feed = VideoCapture(index)

    def close(self) -> None:
        """
        Release the camera resource. This makes future reads throw an exception.
        """
        if self._feed:
            self._feed.release()
            self._feed = None

    def read_frame(self) -> np.ndarray | None:
        """
        Read a frame from the camera if one is available.
        """
        if not self._feed:
            raise Exception("resource has not been opened")

        # read frame from device
        res, frame = self._feed.read()
        return frame if res else None

    def width(self) -> int:
        """
        The feed's width.
        """
        if not self._feed:
            raise Exception("resource has not been opened")

        return int(self._feed.get(cv2.CAP_PROP_FRAME_WIDTH))

    def height(self) -> int:
        """
        The feed's height.
        """
        if not self._feed:
            raise Exception("resource has not been opened")

        return int(self._feed.get(cv2.CAP_PROP_FRAME_HEIGHT))
