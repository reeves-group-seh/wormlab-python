# std
from typing import TYPE_CHECKING, override

# extern
import pygame
import pygame_gui

# local
import axon
import axonkit
from shooter.screens import ScreenId
from shooter.types import (
    KeyMapAction,
    LaserFire,
    LaserLockPhase,
    StepDirection,
    laser_lock,
)

# relative
from .._util import create_manager
from ._behavior_panel import BehaviorPanel
from ._feed_panel import FeedPanel
from ._fire_panel import FirePanel
from ._layout import HomeLayout
from ._marker_panel import MarkerPanel
from ._stage_panel import StagePanel
from ._state import HomeState
from ._status_bar_panel import StatusBarPanel
from ._status_panel import StatusPanel

# type-check only imports
if TYPE_CHECKING:
    from shooter.app import AppConfig, AppContext


__all__ = ["HomeScreen"]


_CANCELS_CENTERING: frozenset[KeyMapAction] = frozenset(
    {
        KeyMapAction.STEP_LEFT,
        KeyMapAction.STEP_RIGHT,
        KeyMapAction.STEP_UP,
        KeyMapAction.STEP_DOWN,
        KeyMapAction.MOVE_LEFT,
        KeyMapAction.MOVE_RIGHT,
        KeyMapAction.MOVE_UP,
        KeyMapAction.MOVE_DOWN,
        KeyMapAction.FIRE,
        KeyMapAction.DESTROY,
        KeyMapAction.GRID,
    }
)
"""
Actions that take over from an in-progress centering sequence. Moving by hand
makes the plan wrong, and firing part-way through a sequence would hit the wrong
spot. Escape cancels too, and is handled separately as it is not in the keymap.
"""


class HomeScreen(axon.Screen[ScreenId]):
    # instance vars
    _ctx: AppContext
    _state: HomeState

    def __init__(self, ctx: AppContext) -> None:
        # instance vars
        self._ctx = ctx
        self._state = HomeState.new(
            ctx.cfg,
            ctx.state,
            ctx.arduino,
        )

        # create
        manager = create_manager(self._ctx)
        root = _HomeScreenRoot(manager, self._ctx, self._state)

        # init parent
        super().__init__(manager, root)

    @override
    def on_process_event(self, event: pygame.Event) -> ScreenId | None:
        if event.type == pygame.KEYDOWN and not self._is_typing():
            action = self._ctx.cfg.KEYMAP.get(event.key)

            # the user takes the stage back off an in-progress centering
            # sequence. dropping the plan is enough to stop it: at most one of
            # its commands is outstanding, and whatever this key does next
            # replaces it
            if event.key == pygame.K_ESCAPE or action in _CANCELS_CENTERING:
                self._state.centering.value = None

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
                    if self._laser_unlocked():
                        fire = LaserFire(duration=self._state.fire_duration.value)
                        self._ctx.arduino.fire(fire.duration)
                        self._state.num_fires.value += 1
                        self._state.last_fire.value = fire
                        self._state.lock_fire.value = fire
                        self._state.data_needed.value = True
                case KeyMapAction.DESTROY:
                    if not self._state.data_needed.value:
                        fire = LaserFire(duration=self._ctx.cfg.DESTROY_FIRE_DURATION)
                        self._ctx.arduino.fire(fire.duration)
                        self._ctx.data.add_destroy_fire(
                            fire,
                            room_temp=self._state.room_temp.value,
                            room_humidity=self._state.room_humidity.value,
                        )
                case KeyMapAction.GRID:
                    ...
                    # if self._laser_unlocked():
                    #     self._ctx.arduino.grid(
                    #         self._state.grid_size.value,
                    #         self._state.move_speed.value,
                    #         self._state.step_duration.value,
                    #         self._state.fire_duration.value,
                    #     )
                case KeyMapAction.SKIP_DATA:
                    if self._state.last_fire.value and self._state.data_needed.value:
                        self._ctx.data.add_skipped_fire(
                            self._state.last_fire.value,
                            room_temp=self._state.room_temp.value,
                            room_humidity=self._state.room_humidity.value,
                        )
                        self._state.data_needed.value = False
                        self._state.lock_fire.value = None

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

    @override
    def on_update(self, dt: float) -> None:
        self._drive_centering()

    def _drive_centering(self) -> None:
        """
        Send the next command of an in-progress centering sequence.

        One command is issued per idle stage, so the plan is only ever one
        command deep and can be abandoned between any two of them.
        """

        # nothing to center
        plan = self._state.centering.value
        if plan is None:
            return

        # wait for the stage: a command that is pending, queued, or in flight
        # all read as busy, so this cannot run ahead of it
        if self._ctx.arduino.busy():
            return

        # take the next move, keeping the rest for later frames
        direction, rest = plan.pop()
        speed = self._state.move_speed.value
        duration = self._state.step_duration.value
        match direction:
            case StepDirection.LEFT:
                self._ctx.arduino.step_left(speed, duration)
            case StepDirection.RIGHT:
                self._ctx.arduino.step_right(speed, duration)
            case StepDirection.UP:
                self._ctx.arduino.step_up(speed, duration)
            case StepDirection.DOWN:
                self._ctx.arduino.step_down(speed, duration)
        self._state.centering.value = rest

    def _laser_unlocked(self) -> bool:
        lock = laser_lock(
            self._state.lock_fire.value,
            flash_duration=self._ctx.cfg.FLASH_DURATION,
            lock_duration=self._ctx.cfg.COUNTDOWN_LENGTH,
            data_needed=self._state.data_needed.value,
        )
        return lock.phase is LaserLockPhase.UNLOCKED

    def _is_typing(self) -> bool:
        focused = self._manager.get_focus_set()  # type: ignore[no-untyped-call]
        if not focused:
            return False
        return any(
            isinstance(
                el,
                (
                    pygame_gui.elements.UITextEntryLine,
                    pygame_gui.elements.UITextEntryBox,
                ),
            )
            for el in focused
        )


class _HomeScreenRoot(axon.Component):
    def __init__(
        self,
        manager: pygame_gui.UIManager,
        ctx: AppContext,
        state: HomeState,
    ) -> None:
        # layout metrics
        lt = HomeLayout(window_w=ctx.cfg.WINDOW_W, window_h=ctx.cfg.WINDOW_H)

        # background
        bg = axonkit.Background(
            manager=manager,
            size=ctx.cfg.WINDOW_SIZE,
        )

        # widths
        right_panels_w = lt.video_w
        left_panels_w = lt.window_w - (lt.video_w + lt.border)

        # heights
        top_panels_h = lt.window_h - (lt.status_bar_h + lt.border)

        # status bar
        status_bar_panel_rect = pygame.Rect(0, 0, lt.window_w, lt.status_bar_h)
        status_bar_panel_rect.bottomleft = (0, 0)
        StatusBarPanel(
            manager=manager,
            container=bg.element,
            rect=status_bar_panel_rect,
            state=state,
            anchors={"bottom": "bottom"},
        )

        # left column
        _LeftPanels(
            manager=manager,
            container=bg.element,
            rect=(0, 0, left_panels_w, top_panels_h),
            ctx=ctx,
            lt=lt,
            state=state,
        )

        # right column
        right_panels_rect = pygame.Rect(0, 0, right_panels_w, top_panels_h)
        right_panels_rect.topright = (0, 0)
        _RightPanels(
            manager=manager,
            container=bg.element,
            rect=right_panels_rect,
            lt=lt,
            ctx=ctx,
            state=state,
            anchors={"right": "right"},
        )


class _LeftPanels(axon.Widget):
    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
        ctx: AppContext,
        lt: HomeLayout,
        state: HomeState,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
    ) -> None:
        # parent init
        super().__init__(manager, container, rect, anchors)

        # convert rect
        rect = axon.as_rect(rect)

        # heights
        marker_panel_h = MarkerPanel.content_h(lt)
        behavior_panel_h = BehaviorPanel.content_h(lt)
        fire_panel_h = rect.h - (marker_panel_h + behavior_panel_h + (2 * lt.border))

        marker_panel = MarkerPanel(
            manager=manager,
            container=self.element,
            rect=(0, 0, rect.w, marker_panel_h),
            lt=lt,
            state=state,
        )

        behavior_panel = BehaviorPanel(
            manager=manager,
            container=self.element,
            rect=(0, lt.border, rect.w, behavior_panel_h),
            ctx=ctx,
            lt=lt,
            state=state,
            anchors={"top": "top", "top_target": marker_panel.element},
        )

        FirePanel(
            manager=manager,
            container=self.element,
            rect=(0, lt.border, rect.w, fire_panel_h),
            ctx=ctx,
            lt=lt,
            state=state,
            anchors={"top": "top", "top_target": behavior_panel.element},
        )


class _RightPanels(axon.Widget):
    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
        lt: HomeLayout,
        ctx: AppContext,
        state: HomeState,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
    ) -> None:
        # parent init
        super().__init__(manager, container, rect, anchors)

        # convert rect
        rect = axon.as_rect(rect)

        # heights
        top_panels_h = rect.h - (FeedPanel.content_h(lt) + lt.border)

        # top panels
        top_panels = _TopPanels(
            manager=manager,
            container=self.element,
            rect=(0, 0, rect.w, top_panels_h),
            lt=lt,
            cfg=ctx.cfg,
            state=state,
        )

        # feed panel
        FeedPanel(
            manager=manager,
            container=self.element,
            rect=(0, lt.border, rect.w, FeedPanel.content_h(lt)),
            lt=lt,
            ctx=ctx,
            state=state,
            anchors={"top": "top", "top_target": top_panels.element},
        )


class _TopPanels(axon.Widget):
    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
        lt: HomeLayout,
        cfg: AppConfig,
        state: HomeState,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
    ) -> None:
        # parent init
        super().__init__(manager, container, rect, anchors)

        # convert rect
        rect = axon.as_rect(rect)

        # widths
        status_panel_w = rect.w - (lt.stage_panel_w + lt.border)

        # stage panel
        stage_panel = StagePanel(
            manager=manager,
            container=self.element,
            rect=(0, 0, lt.stage_panel_w, rect.h),
            lt=lt,
            cfg=cfg,
            state=state,
        )

        # status panel
        StatusPanel(
            manager=manager,
            container=self.element,
            rect=(lt.border, 0, status_panel_w, rect.h),
            lt=lt,
            cfg=cfg,
            state=state,
            anchors={"left": "left", "left_target": stage_panel.element},
        )
