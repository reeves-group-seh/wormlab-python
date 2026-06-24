# std
from typing import override

import pygame

# pip
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel, UITextEntryLine

# local
from stage_ui.components import Component
from stage_ui.context import Context
from stage_ui.screens import Screen, ScreenId
from stage_ui.types import KeyMapAction

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
        self.state = HomeState.new(ctx.cfg, ctx.arduino_man, ctx.state)

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
                marker_pos=self.ctx.cfg.MARKER_POS,
            )
        )

    @override
    def process_event(self, event: pygame.Event) -> ScreenId | None:
        if event.type == pygame.KEYDOWN and not self._is_typing():
            action = self.ctx.cfg.KEYMAP.get(event.key)
            match action:
                case KeyMapAction.STEP_LEFT:
                    self.ctx.arduino_man.step_left(
                        self.state.move_speed.value,
                        self.state.step_duration.value,
                    )
                case KeyMapAction.STEP_RIGHT:
                    self.ctx.arduino_man.step_right(
                        self.state.move_speed.value,
                        self.state.step_duration.value,
                    )
                case KeyMapAction.STEP_UP:
                    self.ctx.arduino_man.step_up(
                        self.state.move_speed.value,
                        self.state.step_duration.value,
                    )
                case KeyMapAction.STEP_DOWN:
                    self.ctx.arduino_man.step_down(
                        self.state.move_speed.value,
                        self.state.step_duration.value,
                    )
                case KeyMapAction.MOVE_LEFT:
                    self.ctx.arduino_man.move_left(
                        self.state.move_speed.value,
                        self.state.step_duration.value,
                    )
                case KeyMapAction.MOVE_RIGHT:
                    self.ctx.arduino_man.move_right(
                        self.state.move_speed.value,
                        self.state.step_duration.value,
                    )
                case KeyMapAction.MOVE_UP:
                    self.ctx.arduino_man.move_up(
                        self.state.move_speed.value,
                        self.state.step_duration.value,
                    )
                case KeyMapAction.MOVE_DOWN:
                    self.ctx.arduino_man.move_down(
                        self.state.move_speed.value,
                        self.state.step_duration.value,
                    )
                case KeyMapAction.FIRE:
                    self.ctx.arduino_man.fire(
                        self.state.fire_duration.value,
                    )
                case KeyMapAction.DESTROY:
                    self.ctx.arduino_man.fire(
                        self.ctx.cfg.DESTROY_FIRE_DURATION,
                    )
                case KeyMapAction.GRID:
                    self.ctx.arduino_man.grid(
                        self.state.grid_size.value,
                        self.state.move_speed.value,
                        self.state.step_duration.value,
                        self.state.fire_duration.value,
                    )
                case KeyMapAction.SKIP_DATA:
                    ...

        if event.type == pygame.KEYUP and not self._is_typing():
            action = self.ctx.cfg.KEYMAP.get(event.key)
            match action:
                case KeyMapAction.MOVE_LEFT:
                    self.ctx.arduino_man.stop()
                case KeyMapAction.MOVE_RIGHT:
                    self.ctx.arduino_man.stop()
                case KeyMapAction.MOVE_UP:
                    self.ctx.arduino_man.stop()
                case KeyMapAction.MOVE_DOWN:
                    self.ctx.arduino_man.stop()

        # process child events
        super().process_event(event)
        return None

    def _is_typing(self) -> bool:
        focused = self.manager.get_focus_set()
        if not focused:
            return False
        return any(isinstance(el, UITextEntryLine) for el in focused)


class HomeScreenComponent(Component):
    def __init__(
        self,
        manager: UIManager,
        bg: UIPanel,
        ctx: Context,
        home_state: HomeState,
        marker_pos: tuple[int, int],
    ) -> None:
        # init parent
        super().__init__()

        # info panel
        self.track(
            InfoPanelComponent(
                manager=manager,
                container=bg,
                pos=(20, 20),
                datafile=ctx.cfg.DATA_FILE,
                arduino_status=home_state.arduino_status,
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
                marker_pos=marker_pos,
            )
        )
