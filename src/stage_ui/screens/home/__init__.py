# std
from typing import override

# pip
import pygame
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel, UITextEntryLine

# local
from stage_ui.components import Component
from stage_ui.context import Context
from stage_ui.screens import Screen, ScreenId
from stage_ui.types import KeyMapAction, LaserFire

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
                state=self.state,
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
                    if not self.state.data_needed.value:
                        fire = LaserFire.new(self.state.fire_duration.value)
                        self.ctx.arduino_man.fire(fire.duration)
                        self.state.num_fires.value += 1
                        self.state.last_fire.value = fire
                        self.state.data_needed.value = True
                case KeyMapAction.DESTROY:
                    if not self.state.data_needed.value:
                        fire = LaserFire.new(self.ctx.cfg.DESTROY_FIRE_DURATION)
                        self.ctx.arduino_man.fire(fire.duration)
                        self.ctx.data_man.add_non_data_fire(fire, "Destroy Fire")
                case KeyMapAction.GRID:
                    if not self.state.data_needed.value:
                        self.ctx.arduino_man.grid(
                            self.state.grid_size.value,
                            self.state.move_speed.value,
                            self.state.step_duration.value,
                            self.state.fire_duration.value,
                        )
                case KeyMapAction.SKIP_DATA:
                    if self.state.last_fire.value and self.state.data_needed.value:
                        self.ctx.data_man.add_non_data_fire(
                            self.state.last_fire.value, "Non-Data Fire"
                        )
                        self.state.data_needed.value = False

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
        state: HomeState,
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
                arduino_status=state.arduino_status,
                room_temp=state.room_temp,
                room_humidity=state.room_humidity,
            )
        )

        # top panel
        self.track(
            TopPanelComponent(
                manager=manager,
                container=bg,
                pos=(435, 20),
                cfg=ctx.cfg,
                fire_duration=state.fire_duration,
                step_duration=state.step_duration,
                move_speed=state.move_speed,
                grid_size=state.grid_size,
            )
        )

        # side panel
        self.track(
            SidePanelComponent(
                manager=manager,
                container=bg,
                pos=(20, 260),
                data_manager=ctx.data_man,
                state=state,
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
