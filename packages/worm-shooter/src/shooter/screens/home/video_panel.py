# std
import math
from typing import ClassVar, override

# pip
import pygame
from pygame import Surface
from pygame.event import Event
from pygame_gui import UIManager
from pygame_gui.elements import UIImage, UIPanel

# local
from shooter.atom import Atom
from shooter.backend.camera import CameraBackend
from shooter.components import NO_MARGINS, Component
from shooter.screens.base import Screen
from shooter.types import RadiusColor


class VideoPanelComponent(Component):
    # public class constants
    W: ClassVar[int] = 545
    H: ClassVar[int] = 370

    # private class constants
    _IMAGE_W: ClassVar[int] = 525
    _IMAGE_H: ClassVar[int] = 350
    _PLANE_W: ClassVar[int] = 720
    _PLANE_H: ClassVar[int] = 480
    _GRID_STEP: ClassVar[int] = 60
    _GRID_COLOR: ClassVar[pygame.Color] = pygame.Color.from_hex("#B735DB")
    _RINGS: ClassVar[list[tuple[RadiusColor, pygame.Color, int]]] = [
        (RadiusColor.RED, pygame.Color(255, 0, 0), 5),
        (RadiusColor.GREEN, pygame.Color(0, 255, 0), 25),
        (RadiusColor.BLUE, pygame.Color(0, 0, 255), 45),
        (RadiusColor.YELLOW, pygame.Color(255, 255, 0), 65),
    ]

    # instance variables
    _camera: CameraBackend
    _marker_pos: Atom[tuple[int, int]]  # relative to logical 720x480 plane
    _marker_plane_pos: tuple[int, int]  # unwraped value of atom
    _marker_norm_pos: tuple[float, float]  # relative to 1x1 unit grid
    _marker_image_pos: tuple[int, int]  # relative to 525x350 image
    _radius_color: Atom[RadiusColor]

    # components
    _video_frame: UIImage

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        camera: CameraBackend,
        marker_pos: Atom[tuple[int, int]],
        radius_color: Atom[RadiusColor],
    ) -> None:
        # init parent
        super().__init__()

        # bind
        self.bind(marker_pos, self._update_marker_pos)

        # set values
        self._camera = camera
        self._marker_pos = marker_pos
        self._update_marker_pos()
        self._radius_color = radius_color

        # unpack values
        x, y = pos

        # create
        panel = UIPanel(
            relative_rect=(x, y, self.W, self.H),
            manager=manager,
            container=container,
            margins=NO_MARGINS,
        )

        self._video_frame = UIImage(
            relative_rect=(10, 10, self._IMAGE_W, self._IMAGE_H),
            image_surface=pygame.Surface((self._IMAGE_W, self._IMAGE_H)),
            manager=manager,
            container=panel,
        )

    @override
    def process_event(self, event: Event) -> None:
        # parent logic
        super().process_event(event)

        # hande events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # get event data
            mouse_x: int = event.pos[0]
            mouse_y: int = event.pos[1]

            # get absolute rect of video frame
            video_abs_rect = self._video_frame.get_abs_rect()

            # check if video frame was clicked
            if not video_abs_rect.collidepoint(event.pos):
                return

            # calc dist from marker center
            dx = mouse_x - video_abs_rect.x - self._marker_image_pos[0]
            dy = mouse_y - video_abs_rect.y - self._marker_image_pos[1]
            dist = math.hypot(dx, dy)

            # find closest ring
            color, _, radius = min(self._RINGS, key=lambda r: abs(dist - r[2]))
            if abs(dist - radius) <= 12:
                self._radius_color.value = color

    @override
    def update(self, dt: float) -> None:
        # parent logic
        super().update(dt)

        # update video
        self._render_frame()

    def _update_marker_pos(self) -> None:
        self._marker_plane_pos = self._marker_pos.value
        self._marker_norm_pos = (
            self._marker_plane_pos[0] / self._PLANE_W,
            self._marker_plane_pos[1] / self._PLANE_H,
        )
        self._marker_image_pos = (
            round(self._marker_norm_pos[0] * self._IMAGE_W),
            round(self._marker_norm_pos[1] * self._IMAGE_H),
        )

    def _render_frame(self) -> None:
        # grab a frame, skip if none is available
        frame = self._camera.read_frame()
        if frame is None:
            return

        # fit the frame into the video box
        raw: Surface = pygame.surfarray.make_surface(frame)
        surf: Surface = Screen.fit_surface(raw, (self._IMAGE_W, self._IMAGE_H))
        self._draw_overlay(surf)

        # update image
        self._video_frame.set_image(surf)

    def _draw_overlay(self, surf: Surface) -> None:
        # surface size
        sw, sh = surf.get_size()

        # draw vertical lines from upper-left
        for lx in range(0, self._PLANE_W + 1, self._GRID_STEP):
            px = min(round((lx / self._PLANE_W) * sw), sw - 1)
            pygame.draw.line(surf, self._GRID_COLOR, (px, 0), (px, sh), 1)

        # draw horizontal lines from upper-left
        for ly in range(0, self._PLANE_H + 1, self._GRID_STEP):
            py = min(round((ly / self._PLANE_H) * sh), sh - 1)
            pygame.draw.line(surf, self._GRID_COLOR, (0, py), (sw, py), 1)

        # draw marker
        selected = self._radius_color.value
        for color, draw_color, radius in self._RINGS:
            width = 2 if radius == 5 else 1
            shade = (
                draw_color
                if color == selected
                else draw_color.lerp(pygame.Color.from_hex("#000000"), 0.65)
            )
            pygame.draw.circle(surf, shade, self._marker_image_pos, radius, width)
