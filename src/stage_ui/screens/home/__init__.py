# std
from typing import override

# pip
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel

# local
from stage_ui.components import Component
from stage_ui.context import Context
from stage_ui.screens import Screen

# relative
from .info_panel import InfoPanelComponent
from .side_panel import SidePanelComponent
from .state import HomeState
from .top_panel import TopPanelComponent
from .video_panel import VideoPanelComponent


class HomeScreen(Screen):
    def __init__(self, ctx: Context) -> None:
        # init parent
        super().__init__(ctx)

        # state
        self.state = HomeState.new(ctx.cfg, ctx.state)

    @override
    def on_enter(self) -> None:
        # create backround
        super().on_enter()

        # create
        self.track(
            HomeScreenComponent(
                manager=self.manager,
                bg=self.bg,
                ctx=self.ctx,
                home_state=self.state,
            )
        )


class HomeScreenComponent(Component):
    def __init__(
        self,
        manager: UIManager,
        bg: UIPanel,
        ctx: Context,
        home_state: HomeState,
    ) -> None:
        # init parent
        super().__init__()

        # set values

        # bindings

        # info panel
        self.track(
            InfoPanelComponent(
                manager=manager,
                container=bg,
                pos=(20, 20),
                datafile=ctx.cfg.DATA_FILE,
                status=home_state.status,
                room_temp=home_state.room_temp,
                room_humidity=home_state.room_humidity,
            )
        )

        # top panel
        self.track(
            TopPanelComponent(
                manager=manager,
                container=bg,
                pos=(435, 20),
                cfg=ctx.cfg,
                fire_duration=home_state.fire_duration,
                step_duration=home_state.step_duration,
                move_speed=home_state.move_speed,
                grid_size=home_state.grid_size,
            )
        )

        # side panel
        self.track(
            SidePanelComponent(
                manager=manager,
                container=bg,
                pos=(20, 260),
                last_fire=home_state.last_fire,
                num_fires=home_state.num_fires,
                filter=home_state.filter,
                strain=home_state.strain,
                worm_id=home_state.worm_id,
            )
        )

        # video panel
        self.track(
            VideoPanelComponent(
                manager=manager,
                container=bg,
                pos=(435, 260),
                camera_man=ctx.camera_man,
            )
        )
