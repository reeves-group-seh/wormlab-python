# pip
import cv2
import numpy as np
from cv2 import VideoCapture


# @dataclass(kw_only=True)
class CV2CameraManager:
    """
    Class for handling frame capture and other video-related logic.
    """

    def __init__(self) -> None:
        self._index: int | None = None
        self._feed: VideoCapture | None = None

    def open(self, index: int) -> None:
        """
        Open the camera with the given index.
        """
        self._index = index
        self._feed = VideoCapture(index)

    def close(self) -> None:
        """
        Release the camera resource. This makes future reads throw an exception.
        """
        if self._feed:
            self._feed.release()
            self._index = None
            self._feed = None

    def read_frame(self) -> np.ndarray | None:
        """
        Read a frame from the camera if one is available.
        """
        if not self._feed:
            raise Exception("resource has not been opened")

        # read frame from device
        res, frame = self._feed.read()
        if not res:
            return None

        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def index(self) -> int | None:
        return self._index

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
