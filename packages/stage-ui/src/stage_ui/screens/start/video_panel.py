# std
from typing import ClassVar, override

# pip
import pygame
from pygame import Color, Surface
from pygame_gui import UIManager
from pygame_gui.elements import UIImage, UIPanel

# local
from stage_ui.atom import Atom
from stage_ui.backend.camera import CameraBackend
from stage_ui.components import NO_MARGINS, Component
from stage_ui.screens import Screen

# constants
_BLANK_SURFACE = Surface((525, 350))
_BLANK_SURFACE.fill(Color(26, 32, 36))


class VideoPanelComponent(Component):
    # public class constants
    W: ClassVar[int] = 545
    H: ClassVar[int] = 370

    # private class constants
    _BLANK_SURFACE: ClassVar[Surface] = _BLANK_SURFACE

    # instance vars
    _camera: CameraBackend
    _camera_index: Atom[int]

    _video_frame: UIImage

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        camera: CameraBackend,
        camera_index: Atom[int],
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self._camera = camera
        self._camera_index = camera_index

        # bindings
        self.bind(camera_index, self._change_camera)

        # unpack values
        x, y = pos

        # create
        video_panel = UIPanel(
            relative_rect=(x, y, self.W, self.H),
            manager=manager,
            margins=NO_MARGINS,
            container=container,
        )
        self._video_frame = UIImage(
            relative_rect=(10, 10, 525, 350),
            image_surface=self._BLANK_SURFACE,
            manager=manager,
            container=video_panel,
        )

    @override
    def update(self, dt: float) -> None:
        # update children
        super().update(dt)

        # get frame, skip if none
        frame = self._camera.read_frame()
        if frame is None:
            return

        # build a surface from the frame
        surf = pygame.surfarray.make_surface(frame)
        self._video_frame.set_image(
            Screen.fit_surface(surf, self._video_frame.get_relative_rect().size)
        )

    def _change_camera(self) -> None:
        # re-open the feed at the new index
        self._camera.close()
        self._camera.open(self._camera_index.value)

        # reset the preview until the new camera yields a frame
        self._video_frame.set_image(self._BLANK_SURFACE)
