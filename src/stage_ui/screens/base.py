# item imports
from abc import ABC
from enum import Enum, auto
from pygame import Surface
from pygame import Event
from pygame_gui import UIManager

# local item imports
from stage_ui.context import Context


class ScreenId(Enum):
    """
    All possible application screens.
    """

    START = auto()
    HOME = auto()


class Screen(ABC):
    def __init__(self, ctx: Context) -> None:
        self.ctx: Context = ctx
        self.ui_man: UIManager = UIManager(ctx.cfg.WINDOW_SIZE, ctx.cfg.THEME_FILE)

    def on_enter(self) -> None:
        """
        Called when the screen becomes active. This builds the UI for this
        screen.
        """
        pass

    def on_exit(self) -> None:
        """
        Called when switching away from this screen. This destroys the UI.
        """
        self.ui_man.clear_and_reset()  # type: ignore[no-untyped-call]

    def handle_event(self, event: Event) -> ScreenId | None:
        """
        Handle a given event generated during the render loop.
        """
        self.ui_man.process_events(event)
        return None

    def update(self, dt: float) -> None:
        """
        Update the screen after `dt` seconds since the last frame.
        """
        self.ui_man.update(dt)

    def draw_ui(self, surface: Surface) -> None:
        """
        Draw the `Screen`'s UI to the given surface (window).
        """
        self.ui_man.draw_ui(surface)
