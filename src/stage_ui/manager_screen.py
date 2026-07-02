# pip
import pygame

# local
from stage_ui.context import Context
from stage_ui.screens import HomeScreen, Screen, ScreenId, StartScreen


class ScreenManager:
    # instance vars
    _screens: dict[ScreenId, Screen]
    _current: Screen

    def __init__(self, ctx: Context) -> None:
        # initialize screens
        self._screens = {}
        self._screens[ScreenId.START] = StartScreen(ctx)
        self._screens[ScreenId.HOME] = HomeScreen(ctx)

        # set current to start
        self._current = self._screens[ScreenId.START]
        self._current.on_enter()

    def switch(self, name: ScreenId) -> None:
        """
        Switch to the given screen.
        """

        # cleanup current screen
        self._current.on_exit()

        # build new screen
        self._current = self._screens[name]
        self._current.on_enter()

    def process_event(self, event: pygame.Event) -> None:
        id = self._current.process_event(event)
        self.switch(id) if id else ...

    def update(self, dt: float) -> None:
        self._current.update(dt)

    def draw_ui(self, surface: pygame.Surface) -> None:
        self._current.draw_ui(surface)
