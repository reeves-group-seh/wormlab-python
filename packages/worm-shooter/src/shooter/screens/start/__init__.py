# std
from importlib.resources import files
from typing import override

# pip
from pygame import Event
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel, UITextBox

# local
import shooter
from shooter.app.context import AppContext
from shooter.atom import Atom
from shooter.components import NO_MARGINS, Component
from shooter.screens import Screen, ScreenId
from shooter.screens.events import CT_GO_HOME

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
        self._serial_port = Atom(ctx.arduino.ports()[0])
        self._camera_index = Atom(ctx.cfg.DEFAULT_CAMERA_INDEX)

        # (try to) open default serial connection and camera
        self._ctx.arduino.open(self._serial_port.value)
        self._ctx.camera.open(self._camera_index.value)

        # build ui
        self._root = StartScreenComponent(
            manager=self._manager,
            bg=Screen.bg_panel(ctx, self._manager),
            ctx=ctx,
            serial_port=self._serial_port,
            camera_index=self._camera_index,
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
        ctx: AppContext,
        serial_port: Atom[str],
        camera_index: Atom[int],
    ) -> None:
        # init parent
        super().__init__()

        # top panel
        top_panel = UIPanel(
            relative_rect=(20, 20, 960, 220),
            manager=manager,
            margins=NO_MARGINS,
            container=bg,
        )
        ascii_art = (files("shooter.resources") / "title.txt").read_text()
        title = UITextBox(
            html_text=f"{ascii_art}\n\nVersion: {shooter.VERSION}",
            relative_rect=(0, 0, 960, 220),
            manager=manager,
            container=top_panel,
            object_id="#ascii_art",
            pre_parsing_enabled=True,
            plain_text_display_only=True,
        )
        title.disable()  # type: ignore[no-untyped-call]

        # side panel
        SidePanelComponent(
            manager=manager,
            container=bg,
            pos=(20, 260),
            arduino=ctx.arduino,
            serial_port=serial_port,
            camera_index=camera_index,
            room_temp=ctx.state.room_temp,
            room_humidity=ctx.state.room_humidity,
        )

        # video panel
        VideoPanelComponent(
            manager=manager,
            container=bg,
            pos=(435, 260),
            camera=ctx.camera,
            camera_index=camera_index,
        )
