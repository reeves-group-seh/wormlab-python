# std
from importlib.resources import files
from typing import override

# pip
from pygame import Event
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel, UITextBox

# local
import stage_ui
from stage_ui.app_context import AppContext
from stage_ui.atom import Atom
from stage_ui.components import NO_MARGINS, Component
from stage_ui.screens import Screen, ScreenId
from stage_ui.screens.events import CT_GO_HOME

# relative
from .side_panel import SidePanelComponent
from .video_panel import VideoPanelComponent


class StartScreen(Screen):
    # instance vars
    _serial_port: Atom[str]
    _camera_index: Atom[int]

    def __init__(self, ctx: AppContext) -> None:
        # init parent
        super().__init__(ctx)

        # initial state
        self._serial_port = Atom(ctx.arduino_man.ports()[0])
        self._camera_index = Atom(ctx.cfg.DEFAULT_CAMERA_INDEX)

        # (try to) open default serial connection and camera
        self._ctx.arduino_man.open(self._serial_port.value)
        self._ctx.camera_man.open(self._camera_index.value)

    @override
    def on_enter(self) -> None:
        # create backround
        super().on_enter()

        # create
        self.track(
            StartScreenComponent(
                manager=self._manager,
                bg=self.bg,
                ctx=self._ctx,
                serial_port=self._serial_port,
                camera_index=self._camera_index,
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
    # instance vars
    _ctx: AppContext
    _serial_port: Atom[str]
    _camera_index: Atom[int]

    def __init__(
        self,
        manager: UIManager,
        bg: UIPanel,
        ctx: AppContext,
        serial_port: Atom[str],
        camera_index: Atom[int],
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self._ctx = ctx
        self._serial_port = serial_port
        self._camera_index = camera_index

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
                html_text=f"{ascii_art}\n\nVersion: {stage_ui.VERSION}",
                relative_rect=(0, 0, 960, 220),
                manager=manager,
                container=top_panel,
                object_id="#ascii_art",
                pre_parsing_enabled=True,
                plain_text_display_only=True,
            )
        )
        title.disable()  # type: ignore[no-untyped-call]

        # side panel
        self.track(
            SidePanelComponent(
                manager=manager,
                container=bg,
                pos=(20, 260),
                arduino_man=ctx.arduino_man,
                serial_port=self._serial_port,
                camera_index=self._camera_index,
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
                camera_index=self._camera_index,
            )
        )
