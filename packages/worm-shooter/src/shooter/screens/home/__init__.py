# std
from typing import override

# pip
import pygame
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel, UITextEntryLine

# local
from shooter.app.context import AppContext
from shooter.components import Component
from shooter.screens import Screen, ScreenId
from shooter.types import KeyMapAction, LaserFire

# relative
from .info_panel import InfoPanelComponent
from .side_panel import SidePanelComponent
from .state import HomeState
from .top_panel import TopPanelComponent
from .video_panel import VideoPanelComponent


class HomeScreen(Screen):
    # instance vars
    _state: HomeState

    def __init__(self, ctx: AppContext) -> None:
        # init parent
        super().__init__(ctx)

        # state
        self._state = HomeState.new(
            ctx.cfg,
            ctx.state,
            ctx.arduino,
        )

        self._root = HomeScreenComponent(
            manager=self._manager,
            bg=Screen.bg_panel(ctx, self._manager),
            ctx=self._ctx,
            state=self._state,
        )

    @override
    def process_event(self, event: pygame.Event) -> ScreenId | None:
        # process child events
        super().process_event(event)

        if event.type == pygame.KEYDOWN and not self._is_typing():
            action = self._ctx.cfg.KEYMAP.get(event.key)
            match action:
                case KeyMapAction.STEP_LEFT:
                    self._ctx.arduino.step_left(
                        self._state.move_speed.value,
                        self._state.step_duration.value,
                    )
                case KeyMapAction.STEP_RIGHT:
                    self._ctx.arduino.step_right(
                        self._state.move_speed.value,
                        self._state.step_duration.value,
                    )
                case KeyMapAction.STEP_UP:
                    self._ctx.arduino.step_up(
                        self._state.move_speed.value,
                        self._state.step_duration.value,
                    )
                case KeyMapAction.STEP_DOWN:
                    self._ctx.arduino.step_down(
                        self._state.move_speed.value,
                        self._state.step_duration.value,
                    )
                case KeyMapAction.MOVE_LEFT:
                    self._ctx.arduino.move_left(
                        self._state.move_speed.value,
                        self._state.step_duration.value,
                    )
                case KeyMapAction.MOVE_RIGHT:
                    self._ctx.arduino.move_right(
                        self._state.move_speed.value,
                        self._state.step_duration.value,
                    )
                case KeyMapAction.MOVE_UP:
                    self._ctx.arduino.move_up(
                        self._state.move_speed.value,
                        self._state.step_duration.value,
                    )
                case KeyMapAction.MOVE_DOWN:
                    self._ctx.arduino.move_down(
                        self._state.move_speed.value,
                        self._state.step_duration.value,
                    )
                case KeyMapAction.FIRE:
                    if not self._state.data_needed.value:
                        fire = LaserFire(duration=self._state.fire_duration.value)
                        self._ctx.arduino.fire(fire.duration)
                        self._state.num_fires.value += 1
                        self._state.last_fire.value = fire
                        self._state.data_needed.value = True
                case KeyMapAction.DESTROY:
                    if not self._state.data_needed.value:
                        fire = LaserFire(duration=self._ctx.cfg.DESTROY_FIRE_DURATION)
                        self._ctx.arduino.fire(fire.duration)
                        self._ctx.data.add_non_data_fire(fire, "Destroy Fire")
                case KeyMapAction.GRID:
                    if not self._state.data_needed.value:
                        self._ctx.arduino.grid(
                            self._state.grid_size.value,
                            self._state.move_speed.value,
                            self._state.step_duration.value,
                            self._state.fire_duration.value,
                        )
                case KeyMapAction.SKIP_DATA:
                    if self._state.last_fire.value and self._state.data_needed.value:
                        self._ctx.data.add_non_data_fire(
                            self._state.last_fire.value, "Non-Data Fire"
                        )
                        self._state.data_needed.value = False

        if event.type == pygame.KEYUP and not self._is_typing():
            action = self._ctx.cfg.KEYMAP.get(event.key)
            match action:
                case KeyMapAction.MOVE_LEFT:
                    self._ctx.arduino.stop()
                case KeyMapAction.MOVE_RIGHT:
                    self._ctx.arduino.stop()
                case KeyMapAction.MOVE_UP:
                    self._ctx.arduino.stop()
                case KeyMapAction.MOVE_DOWN:
                    self._ctx.arduino.stop()

        return None

    def _is_typing(self) -> bool:
        focused = self._manager.get_focus_set()  # type: ignore[no-untyped-call]
        if not focused:
            return False
        return any(isinstance(el, UITextEntryLine) for el in focused)


class HomeScreenComponent(Component):
    def __init__(
        self,
        manager: UIManager,
        bg: UIPanel,
        ctx: AppContext,
        state: HomeState,
    ) -> None:
        # init parent
        super().__init__()

        # info panel
        InfoPanelComponent(
            manager=manager,
            container=bg,
            pos=(20, 20),
            data_file=ctx.cfg.DATA_FILE,
            countdown_length=ctx.cfg.COUNTDOWN_LENGTH,
            state=state,
        )

        # top panel
        TopPanelComponent(
            manager=manager,
            container=bg,
            pos=(435, 20),
            cfg=ctx.cfg,
            fire_duration=state.fire_duration,
            step_duration=state.step_duration,
            move_speed=state.move_speed,
            grid_size=state.grid_size,
            marker_pos=state.marker_pos,
        )

        # side panel
        SidePanelComponent(
            manager=manager,
            container=bg,
            pos=(20, 260),
            data=ctx.data,
            state=state,
        )

        # video panel
        VideoPanelComponent(
            manager=manager,
            container=bg,
            pos=(435, 260),
            camera=ctx.camera,
            marker_pos=state.marker_pos,
            radius_color=state.radius_color,
        )
