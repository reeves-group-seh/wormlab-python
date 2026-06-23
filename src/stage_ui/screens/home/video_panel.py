# std
from typing import override

# pip
import pygame
from pygame import Surface
from pygame_gui import UIManager
from pygame_gui.elements import UIImage, UIPanel

# local
from stage_ui.components import NO_MARGINS, Component
from stage_ui.manager_camera import CameraManager
from stage_ui.screens.base import Screen


class VideoPanelComponent(Component):
    # constants
    W: int = 545
    H: int = 370

    # logical plane the overlay grid is drawn on (matches the camera feed, with
    # the origin at the upper-left)
    _PLANE_W: int = 720
    _PLANE_H: int = 480
    _GRID_STEP: int = 80
    _GRID_COLOR: pygame.Color = pygame.Color(183, 53, 219)

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        camera_man: CameraManager,
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self.camera_man = camera_man

        # unpack values
        x, y = pos

        # create
        panel = self.track(
            UIPanel(
                relative_rect=(x, y, self.W, self.H),
                manager=manager,
                container=container,
                margins=NO_MARGINS,
            )
        )

        self.video_frame = self.track(
            UIImage(
                relative_rect=(10, 10, 525, 350),
                image_surface=pygame.Surface((525, 350)),
                manager=manager,
                container=panel,
            )
        )

    @override
    def update(self, dt: float) -> None:
        super().update(dt)
        self._render_frame()

    def _render_frame(self) -> None:
        # grab a frame, skip if none is available
        frame = self.camera_man.read_frame()
        if frame is None:
            return

        # fit the frame into the video box preserving the camera's aspect ratio,
        # then draw the grid and marker overlay on top
        raw: Surface = pygame.surfarray.make_surface(frame)
        surf: Surface = Screen.fit_surface(
            raw, self.video_frame.get_relative_rect().size
        )
        self._draw_overlay(surf)

        self.video_frame.set_image(surf)

    def _draw_overlay(self, surf: Surface) -> None:
        sw, sh = surf.get_size()

        # vertical lines at logical x = 0, 80, ... 720 (origin at the upper-left)
        for lx in range(0, self._PLANE_W + 1, self._GRID_STEP):
            px = min(round(lx / self._PLANE_W * sw), sw - 1)
            pygame.draw.line(surf, self._GRID_COLOR, (px, 0), (px, sh), 1)

        # horizontal lines at logical y = 0, 80, ... 480 (origin at the upper-left)
        for ly in range(0, self._PLANE_H + 1, self._GRID_STEP):
            py = min(round(ly / self._PLANE_H * sh), sh - 1)
            pygame.draw.line(surf, self._GRID_COLOR, (0, py), (sw, py), 1)

        # center the marker in the box for now
        marker = (sw // 2, sh // 2)
        pygame.draw.circle(surf, pygame.Color(255, 0, 0), marker, 5, 2)
        pygame.draw.circle(surf, pygame.Color(0, 255, 0), marker, 25, 1)
        pygame.draw.circle(surf, pygame.Color(0, 0, 255), marker, 45, 1)
        pygame.draw.circle(surf, pygame.Color(255, 255, 0), marker, 65, 1)
