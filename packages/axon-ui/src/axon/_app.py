# std
import signal
import sys
from abc import ABC
from collections.abc import Callable
from enum import Enum
from typing import final

# extern
import pygame

# relative
from ._screen import Screen
from .router import Router


class App[T: Enum](ABC):
    """
    Top-level application: owns the window and runs the render loop.

    `App` is the entry point of an `axon` program. It initializes `pygame`,
    opens the window, builds an `axon.router.Router` over the given screens, and
    (when `run` is called) drives the render loop forever: pump events, update,
    draw, flip, capped at a target frame rate. Ctrl-C is turned into a
    `pygame.QUIT` event so shutdown always flows through the same teardown path.

    Each frame is delegated to the router (and through it, the active screen)
    via `process_event`, `update`, and `draw_ui`. These are `final` and must not
    be overridden. For app-wide behavior that runs on every frame regardless of
    the active screen, override the hooks (`on_process_event`, `on_update`,
    `on_destroy`). Hooks default to no-ops and do not need a `super()` call.

    The type parameter `T` is the screen-id `Enum` shared with `Screen` and
    `Router`.

    ## Usage

    ```python
    class MyApp(App[ScreenId]):
        ...

    app = MyApp(
        app_name="Worm Watcher",
        window_size=(1280, 720),
        screens={ScreenId.HOME: HomeScreen(...)},
        initial_screen=ScreenId.HOME,
        fps=60,
    )
    app.run()  # blocks until the window is closed
    ```
    """

    # instance variables
    _window: pygame.Surface
    _router: Router[T]
    _fps: int
    _clock: pygame.Clock

    def __init__(
        self,
        app_name: str,
        window_size: tuple[int, int],
        screen_factories: dict[T, Callable[[], Screen[T]]],
        initial_screen: T,
        fps: int,
    ) -> None:
        """
        Initialize pygame, open the window, and build the router.

        :param app_name: Window caption / title.
        :param window_size: Window size in pixels as `(width, height)`.
        :param screens: Every screen, keyed by its screen id.
        :param initial_screen: The id of the screen to start on. Must be a key
            of `screens`.
        :param fps: Target frame rate the render loop is capped at.
        """
        # pygame setup
        pygame.init()
        pygame.display.set_caption(app_name)
        self._window = pygame.display.set_mode(window_size)

        # create screens
        screens: dict[T, Screen[T]] = {}
        for id, factory in screen_factories.items():
            screens[id] = factory()

        # init values
        self._router = Router(screens, initial_screen)
        self._fps = fps
        self._clock = pygame.Clock()

    @final
    def run(self) -> None:
        """
        Run the render loop until the app quits. Blocks the caller.

        Registers Ctrl-C (`SIGINT`) as a `pygame.QUIT` event, then loops
        forever: compute the frame delta, dispatch pending events, update, draw,
        and flip the display, capped at the target frame rate. The loop exits
        only when a `pygame.QUIT` event is handled (see `process_event`), which
        tears down and terminates the process.
        """
        # register ctrl-c as a quit event
        signal.signal(
            signal.SIGINT,
            lambda _s, _f: pygame.event.post(pygame.Event(pygame.QUIT)),
        )

        # render loop
        while True:
            # update time delta
            dt = self._clock.tick(self._fps) / 1000.0

            # handle events
            for event in pygame.event.get():
                self.process_event(event)

            # update
            self.update(dt)

            # draw ui
            self.draw_ui()

            # update display
            pygame.display.flip()

    @final
    def process_event(self, event: pygame.Event) -> None:
        """
        Run `on_process_event`, then handle and forward the event.

        Runs `on_process_event` first (which sees every event). On `pygame.QUIT`
        the app tears down via `destroy`, shuts down pygame, and exits the
        process; all other events are passed to the active screen via the
        router.

        :param event: The `pygame` event to handle.
        """

        # pass to hook
        self.on_process_event(event)

        # check for quit
        if event.type == pygame.QUIT:
            self.destroy()
            pygame.quit()
            sys.exit(0)

        # pass to router
        self._router.process_event(event)

    def on_process_event(self, event: pygame.Event) -> None:
        """
        Hook for handling an event at the app level.

        Called by `process_event` before the quit check and before the event is
        forwarded to the router, so it sees every event. Override for app-wide
        input handling; the default implementation does nothing.

        :param event: The `pygame` event to handle.
        """
        pass

    @final
    def update(self, dt: float) -> None:
        """
        Run `on_update`, then advance the active screen via the router.

        :param dt: Seconds elapsed since the last frame.
        """

        # pass to hook
        self.on_update(dt)

        # pass to router
        self._router.update(dt)

    def on_update(self, dt: float) -> None:
        """
        Hook for running app-level per-frame logic.

        Called by `update` before the active screen is stepped. Override for
        app-wide per-frame work; the default implementation does nothing.

        :param dt: Seconds elapsed since the last frame.
        """
        pass

    @final
    def draw_ui(self) -> None:
        """
        Draw the active screen's UI to the window, via the router.
        """
        # pass to router
        self._router.draw_ui(self._window)

    @final
    def destroy(self) -> None:
        """
        Tear down the app, then run `on_destroy`.

        Destroys every screen via the router, then calls `on_destroy`. Invoked
        during `pygame.QUIT` handling before the process exits.
        """
        # pass to router
        self._router.destroy()

        # pass to hook
        self.on_destroy()

    def on_destroy(self) -> None:
        """
        Hook for performing app-level teardown.

        Called by `destroy` after every screen has been destroyed, just before
        the process exits. Override to release app-owned resources; the default
        implementation does nothing.
        """
        pass
