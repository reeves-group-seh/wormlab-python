# item imports
from pygame import Event, Surface

# local item imports
from stage_ui.context import Context
from stage_ui.screens import Screen, ScreenId
from stage_ui.screens import HomeScreen, StartScreen


class ScreenManager:
    def __init__(self, ctx: Context) -> None:
        # declare members
        self.screens: dict[ScreenId, Screen]
        self.current: Screen

        # initialize screens
        self.screens = {}
        self.screens[ScreenId.START] = StartScreen(ctx)
        self.screens[ScreenId.HOME] = HomeScreen(ctx)

        # set current to start
        self.current = self.screens[ScreenId.START]
        self.current.on_enter()

    def switch(self, name: ScreenId) -> None:
        """
        Switch to the given screen.
        """

        # cleanup current screen
        self.current.on_exit()

        # build new screen
        self.current = self.screens[name]
        self.current.on_enter()

    def handle_event(self, event: Event) -> None:
        id = self.current.handle_event(event)
        self.switch(id) if id else ...

    def update(self, dt: float) -> None:
        self.current.update(dt)

    def draw_ui(self, surface: Surface) -> None:
        self.current.draw_ui(surface)
