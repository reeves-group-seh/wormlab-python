# module imports
import cv2
import pygame

# item imports
from cv2 import VideoCapture
from dataclasses import dataclass
from pygame import Color, Font, Surface
from pygame_gui.elements import UIImage


@dataclass(kw_only=True)
class VideoManager:
    """
    Class for handling frame capture and other video-related logic.
    """

    _feed: VideoCapture
    """
    Video capture feed from the camera.
    """

    _width: int
    """
    The feed's width.
    """

    _height: int
    """
    The feed's height.
    """

    _aspect_ratio: float
    """
    The feed's aspect ratio (width / height).
    """

    @property
    def width(self) -> int:
        """
        The feed's width.
        """
        return self._width

    @property
    def height(self) -> int:
        """
        The feed's height.
        """
        return self._height

    @property
    def aspect_ratio(self) -> float:
        """
        The feed's aspect ratio (width/height).
        """
        return self._aspect_ratio

    @staticmethod
    def new(camera_index: int) -> VideoManager:
        """
        Initialize a new `VideoManager` with the given camera index.

        :param camera_index:
            The OpenCV camera index for video capture.
        """

        # create values
        feed = VideoCapture(camera_index)
        width = int(feed.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(feed.get(cv2.CAP_PROP_FRAME_HEIGHT))
        aspect_ratio = width / height

        return VideoManager(
            _feed=feed,
            _width=width,
            _height=height,
            _aspect_ratio=aspect_ratio,
        )

    #
    # render loop method
    #

    # TODO: properly document and vet code
    def update(
        self, video_frame: UIImage, marker_coords: tuple[float, float] | None
    ) -> None:
        # get frame from feed. this is blocking and might be bad to be in our UI
        # thread? this seems like an issue that can be addressed later
        read_success, feed_frame = self._feed.read()

        # break early on no frame
        if not read_success:
            return

        # rotate frame to correct orientation and convert from bgr to rgb due to
        # differences between cv2 format and pygame format
        feed_frame = cv2.rotate(feed_frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        feed_frame = cv2.cvtColor(feed_frame, cv2.COLOR_BGR2RGB)

        # create surface from frame and scale to 500 by 500
        frame_surface: Surface = pygame.surfarray.make_surface(feed_frame)
        frame_surface = pygame.transform.scale(frame_surface, (500, 500))

        # font
        label_font: Font = pygame.font.SysFont("Arial", 14)

        # config
        GRID_SPACING: int = 40
        GRID_COLOR: Color = pygame.Color(183, 53, 219)
        GRID_LINE_WDITH: int = 1
        GRID_LABEL_COLOR: Color = pygame.Color(245, 235, 44)

        # width and height of frame surface (isn't this just 500 and 500)
        frame_surface_w, frame_surface_h = frame_surface.get_size()

        # draw vertical lines with labels
        for x in range(0, frame_surface_w, GRID_SPACING):
            pygame.draw.line(
                frame_surface, GRID_COLOR, (x, 0), (x, frame_surface_h), GRID_LINE_WDITH
            )
            label = label_font.render(f"{x}", True, GRID_LABEL_COLOR)
            frame_surface.blit(label, (x + 2, 2))

        # draw horizontal lines
        for y in range(0, frame_surface_h, GRID_SPACING):
            pygame.draw.line(
                frame_surface, GRID_COLOR, (0, y), (frame_surface_w, y), GRID_LINE_WDITH
            )
            label = label_font.render(f"{y}", True, GRID_LABEL_COLOR)
            frame_surface.blit(label, (2, y + 2))

        # label for something? i have no idea what this means
        pixel_size = 10
        pixel_label = label_font.render(
            f"{GRID_SPACING * pixel_size}", True, GRID_LABEL_COLOR
        )
        frame_surface.blit(pixel_label, (frame_surface_w - 80, frame_surface_h - 20))

        # draw marker
        if marker_coords is not None:
            # red circle with radius 5
            pygame.draw.circle(
                surface=frame_surface,
                color=pygame.Color(255, 0, 0),
                center=marker_coords,
                radius=5,
                width=2,
            )
            # green circle with radius 25
            pygame.draw.circle(
                surface=frame_surface,
                color=pygame.Color(0, 255, 0),
                center=marker_coords,
                radius=25,
                width=1,
            )
            # blue circle with radius 45
            pygame.draw.circle(
                surface=frame_surface,
                color=pygame.Color(0, 0, 255),
                center=marker_coords,
                radius=45,
                width=1,
            )
            # yellow circle with radius 65
            pygame.draw.circle(
                surface=frame_surface,
                color=pygame.Color(255, 255, 0),
                center=marker_coords,
                radius=65,
                width=1,
            )

        # set image
        video_frame.set_image(frame_surface)
