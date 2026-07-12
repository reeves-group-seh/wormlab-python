# std
from enum import Enum

# pip
import pygame

# local
from .screen import Screen

# public api
__all__ = [
    "Router",
]


class Router[T: Enum]:
    """
    Owns every screen and drives the one that is currently active.

    A `Router` holds a fixed set of `Screen`s keyed by a screen-id `Enum` and
    tracks which one is active. Each frame it forwards the render loop
    (`process_event`, `update`, `draw_ui`) to the active screen, and it honors
    the navigation requests those screens return: when `process_event` yields a
    screen id, the router switches to that screen.

    All screens are constructed up front and passed in at construction; these
    are owned by the `Router` and are destroyed when the `Router` is destroyed.

    The type parameter `T` is the screen-id `Enum` shared with `Screen`; the
    same members that key the screen map are what screens return to request a
    transition.
    """

    # instance vars
    _screens: dict[T, Screen[T]]
    _current: Screen[T]

    def __init__(
        self,
        screens: dict[T, Screen[T]],
        initial: T,
    ) -> None:
        """
        Create a router over a fixed set of screens and enter the first one.

        `Screen.on_enter` is called on the `initial` screen immediately.

        :param screens: Every screen, keyed by its screen id.
        :param initial: The id of the screen to start on. Must be a key of
            `screens`.
        """
        # initialize screens
        self._screens = screens

        # set current to start
        self._current = self._screens[initial]
        self._current.on_enter()

    def switch(self, id: T) -> None:
        """
        Make the screen with the given id active.

        Calls `Screen.on_exit` on the current screen, then `Screen.on_enter`
        on the new one.

        :param id: The id of the screen to switch to. Must be a key of the
            screen map given at construction.
        """

        # cleanup current screen
        self._current.on_exit()

        # enter initial screen
        self._current = self._screens[id]
        self._current.on_enter()

    def process_event(self, event: pygame.Event) -> None:
        """
        Forward an event to the active screen and act on its response.

        If the screen returns a screen id from `Screen.process_event`, the
        router switches to that screen; otherwise the active screen is
        unchanged.

        :param event: The `pygame` event to dispatch.
        """
        id = self._current.process_event(event)
        if id is not None:
            self.switch(id)

    def update(self, dt: float) -> None:
        """
        Advance the active screen one frame.

        :param dt: Seconds elapsed since the last frame.
        """
        self._current.update(dt)

    def draw_ui(self, window: pygame.Surface) -> None:
        """
        Draw the active screen's UI to its window surface.
        """
        self._current.draw_ui(window)

    def destroy(self) -> None:
        """
        Tear down every screen the router owns.

        Calls `Screen.on_exit` on the current screen and `Screen.destroy` on all
        screens (not just the active one), cascading cleanup through each
        screen's root component. Call this once when shutting the router down.
        """
        self._current.on_exit()
        for screen in self._screens.values():
            screen.destroy()
