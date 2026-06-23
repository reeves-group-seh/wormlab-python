# std
from abc import ABC
from enum import Enum, auto

# pip
import pygame
from pygame import Event, Surface
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel

# local
from stage_ui.components import Component
from stage_ui.context import Context

# constants
_NO_MARGINS: dict[str, int] = {"top": 0, "right": 0, "bottom": 0, "left": 0}


class ScreenId(Enum):
    """
    All possible application screens.
    """

    START = auto()
    HOME = auto()
    TEST = auto()


class Screen(ABC):
    def __init__(self, ctx: Context) -> None:
        self.ctx: Context = ctx
        self.manager: UIManager = UIManager(
            ctx.cfg.WINDOW_SIZE,
            theme_path=ctx.cfg.THEME_FILE,
        )
        self._components: list[Component] = []

    def track[C: Component](self, component: C) -> C:
        """
        Register a given component.
        """
        self._components.append(component)
        return component

    def on_enter(self) -> None:
        """
        Called when the screen becomes active. This builds the UI for this
        screen.
        """
        self.bg = UIPanel(
            relative_rect=(0, 0, self.ctx.cfg.WINDOW_W, self.ctx.cfg.WINDOW_H),
            manager=self.manager,
            object_id="#background",
            margins=_NO_MARGINS,
        )

    def on_exit(self) -> None:
        """
        Called when switching away from this screen. This destroys the UI.
        """

        # clean up elements
        self.manager.clear_and_reset()  # type: ignore[no-untyped-call]

        # clean up components
        for component in self._components:
            component.kill()

    def process_event(self, event: Event) -> ScreenId | None:
        """
        Process a given event generated during the render loop. By default, this
        passes the event off to the `UIManager` and sub-components for them to
        handle.
        """

        # let ui manager handle events
        self.manager.process_events(event)

        # let sub-components handle events
        for component in self._components:
            component.process_event(event)

        return None

    def update(self, dt: float) -> None:
        """
        Update the screen after `dt` seconds since the last frame. By default
        this updates the `UIManager` and sub-components.
        """

        # update ui manager
        self.manager.update(dt)

        # update sub-components
        for component in self._components:
            component.update(dt)

    def draw_ui(self, surface: Surface) -> None:
        """
        Draw the `Screen`'s UI to the given surface (window).
        """
        self.manager.draw_ui(surface)

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
