# pip
from typing import override

import pygame
from pygame import Color, Surface
from pygame_gui import UIManager
from pygame_gui.elements import UIImage, UIPanel

from stage_ui.atom import Atom

# local
from stage_ui.components import NO_MARGINS, Component
from stage_ui.manager_camera import CameraManager
from stage_ui.screens import Screen

# constants
_BLANK_SURFACE = Surface((525, 350))
_BLANK_SURFACE.fill(Color(26, 32, 36))


class VideoPanelComponent(Component):
    # constants
    W: int = 545
    H: int = 370

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        camera_man: CameraManager,
        camera_index: Atom[int],
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self.camera_man = camera_man
        self.camera_index = camera_index

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
            image_surface=_BLANK_SURFACE,
            manager=manager,
            container=video_panel,
        )

    @override
    def update(self, dt: float) -> None:
        # update children
        super().update(dt)

        # get frame, skip if none
        frame = self.camera_man.read_frame()
        if frame is None:
            return

        # build a surface from the frame
        surf = pygame.surfarray.make_surface(frame)
        self._video_frame.set_image(
            Screen.fit_surface(surf, self._video_frame.get_relative_rect().size)
        )

    def _change_camera(self) -> None:
        # re-open the feed at the new index
        self.camera_man.close()
        self.camera_man.open(self.camera_index.value)

        # reset the preview until the new camera yields a frame
        self._video_frame.set_image(_BLANK_SURFACE)
