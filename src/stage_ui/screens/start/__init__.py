# std
from importlib.metadata import version
from importlib.resources import files
from typing import override

# pip
from pygame import Event
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel, UITextBox

from stage_ui.atom import Atom

# local
from stage_ui.components import NO_MARGINS, Component
from stage_ui.context import Context
from stage_ui.screens import Screen, ScreenId
from stage_ui.screens.events import CT_GO_HOME

from .side_panel import SidePanelComponent
from .video_panel import VideoPanelComponent


class StartScreen(Screen):
    def __init__(self, ctx: Context) -> None:
        # init parent
        super().__init__(ctx)

        # (try to) open default camera
        self.ctx.camera_man.open(ctx.cfg.CAMERA_INDEX)

    @override
    def on_enter(self) -> None:
        # create backround
        super().on_enter()

        # create
        self.track(
            StartScreenComponent(
                manager=self.manager,
                bg=self.bg,
                ctx=self.ctx,
            )
        )

    @override
    def process_event(self, event: Event) -> ScreenId | None:
        # subcomponent events
        super().process_event(event)

        # handle
        if event.type == CT_GO_HOME:
            return ScreenId.HOME

        return None


class StartScreenComponent(Component):
    def __init__(
        self,
        manager: UIManager,
        bg: UIPanel,
        ctx: Context,
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self.ctx = ctx
        self.serial_port = Atom(ctx.cfg.SERIAL_PORT)
        self.camera_index = Atom(ctx.cfg.CAMERA_INDEX)

        # top panel
        top_panel = self.track(
            UIPanel(
                relative_rect=(20, 20, 960, 220),
                manager=manager,
                margins=NO_MARGINS,
                container=bg,
            )
        )
        ascii_art = (files("stage_ui.resources") / "title.txt").read_text()
        title = self.track(
            UITextBox(
                html_text=f"{ascii_art}\n\nVersion: {version('stage-ui')}",
                relative_rect=(0, 0, 960, 220),
                manager=manager,
                container=top_panel,
                object_id="#ascii_art",
                pre_parsing_enabled=True,
                plain_text_display_only=True,
            )
        )
        title.disable()

        # side panel
        self.track(
            SidePanelComponent(
                manager=manager,
                container=bg,
                pos=(20, 260),
                serial_port=self.serial_port,
                camera_index=self.camera_index,
                room_temp=ctx.state.room_temp,
                room_humidity=ctx.state.room_humidity,
            )
        )

        # video panel
        self.track(
            VideoPanelComponent(
                manager=manager,
                container=bg,
                pos=(435, 260),
                camera_man=ctx.camera_man,
                camera_index=self.camera_index,
            )
        )
