# std
from abc import ABC
from enum import Enum, auto

# pip
import pygame
from pygame import Event, Surface
from pygame_gui import UIManager
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel

# local
from stage_ui.app_context import AppContext
from stage_ui.components import NO_MARGINS, Component


class ScreenId(Enum):
    """
    All possible application screens.
    """

    START = auto()
    HOME = auto()


class Screen(ABC):
    # instance variables
    _ctx: AppContext
    _manager: UIManager
    _root: Component

    def __init__(self, ctx: AppContext) -> None:
        """
        Child classes must set `self._root` in their own init functions.
        """
        # set attributes
        self._ctx = ctx
        self._manager = UIManager(
            ctx.cfg.WINDOW_SIZE,
            theme_path=ctx.cfg.THEME_FILE,
        )

    def on_enter(self) -> None:
        """
        Called when the screen becomes active.
        """
        pass

    def on_exit(self) -> None:
        """
        Called when switching away from this screen.
        """
        pass

    def process_event(self, event: Event) -> ScreenId | None:
        """
        Process a given event generated during the render loop. By default, this
        passes the event off to the `UIManager` and the root component for them
        to handle.
        """

        # let ui manager handle events
        self._manager.process_events(event)

        # let root component handle events
        self._root.process_event(event)

        # don't switch
        return None

    def update(self, dt: float) -> None:
        """
        Update the screen after `dt` seconds since the last frame. By default
        this updates the `UIManager` and the root component.
        """

        # update ui manager
        self._manager.update(dt)

        # update root component
        self._root.update(dt)

    def draw_ui(self, surface: Surface) -> None:
        """
        Draw the `Screen`'s UI to the given window surface.
        """
        self._manager.draw_ui(surface)

    @staticmethod
    def bg_panel(ctx: AppContext, manager: UIManager) -> UIPanel:
        return UIPanel(
            relative_rect=(0, 0, ctx.cfg.WINDOW_W, ctx.cfg.WINDOW_H),
            manager=manager,
            margins=NO_MARGINS,
            object_id=ObjectID(class_id="@background"),
        )

    @staticmethod
    def fit_surface(surface: Surface, size: tuple[float, float]) -> Surface:
        """
        Scale `surface` to fit within `size` while preserving its aspect ratio,
        centered on a black background (letterboxing the remainder).
        """
        box_w, box_h = int(size[0]), int(size[1])
        src_w, src_h = surface.get_size()

        # scale by the limiting dimension so the whole surface fits in the box
        scale = min(box_w / src_w, box_h / src_h)
        new_w = max(1, int(src_w * scale))
        new_h = max(1, int(src_h * scale))
        scaled = pygame.transform.scale(surface, (new_w, new_h))

        # center the scaled surface on a black canvas the size of the box
        canvas: Surface = pygame.Surface((box_w, box_h))
        canvas.fill(pygame.Color(26, 32, 36))
        canvas.blit(scaled, ((box_w - new_w) // 2, (box_h - new_h) // 2))
        return canvas
