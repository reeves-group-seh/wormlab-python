# std
import math
from typing import TYPE_CHECKING, override

# extern
import pygame_gui

# local
import axon
import axonkit
from shooter.components import PanelHeading
from shooter.types import LaserLockPhase, laser_lock

# relative
from ._layout import HomeLayout
from ._state import HomeState

# type-check only imports
if TYPE_CHECKING:
    from shooter.app import AppConfig


_CLASS_ID_BY_PHASE: dict[LaserLockPhase, str] = {
    LaserLockPhase.UNLOCKED: "@laser_unlocked",
    LaserLockPhase.FIRING: "@laser_flashing",
    LaserLockPhase.LOCKED: "@laser_locked",
}

_TEXT_BY_PHASE: dict[LaserLockPhase, str] = {
    LaserLockPhase.UNLOCKED: "UNLOCKED",
    LaserLockPhase.FIRING: "FIRING",
    LaserLockPhase.LOCKED: "LOCKED",
}


class StatusPanel(axon.Widget):
    # instance vars
    _cfg: AppConfig
    _state: HomeState
    _last_phase: LaserLockPhase | None
    _last_countdown: int | None

    _panel: axonkit.Panel
    _phase_label: axonkit.Label
    _countdown_label: axonkit.Label
    _data_needed_label: axonkit.Label

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

        # set values
        self._cfg = cfg
        self._state = state
        self._last_phase: LaserLockPhase | None = None
        self._last_countdown: int | None = None

        # convert rect
        rect = axon.as_rect(rect)

        # panel
        self._panel = axonkit.Panel(
            manager=manager,
            container=self.element,
            rect=(0, 0, rect.w, rect.h),
            margins=axonkit.MarginOption.DEFAULT,
            class_id=_CLASS_ID_BY_PHASE[LaserLockPhase.UNLOCKED],
        )

        # header
        heading = PanelHeading(
            manager=manager,
            container=self._panel.content,
            rect=(0, 0, self._panel.content_width(), lt.panel_heading_h),
            text="STATUS",
        )

        # content
        self._phase_label = axonkit.Label(
            manager=manager,
            container=self._panel.content,
            rect=(0, lt.border_label_pad_y, self._panel.content_width(), lt.label_h),
            text="",
            anchors={"top": "top", "top_target": heading.element},
            obj_id="#laser_phase_label",
        )
        self._countdown_label = axonkit.Label(
            manager=manager,
            container=self._panel.content,
            rect=(0, lt.label_label_pad_y, self._panel.content_width(), lt.label_h),
            text="",
            anchors={"top": "top", "top_target": self._phase_label.element},
            obj_id="#laser_countdown_label",
        )
        self._data_needed_label = axonkit.Label(
            manager=manager,
            container=self._panel.content,
            rect=(0, lt.label_label_pad_y, self._panel.content_width(), lt.label_h),
            text="",
            anchors={"top": "top", "top_target": self._countdown_label.element},
            obj_id="#laser_data_needed_label",
        )

        # bind
        self.bind(state.lock_fire, self._refresh)
        self.bind(state.data_needed, self._refresh)

        # render initial state
        self._refresh()

    @override
    def on_update(self, dt: float) -> None:
        self._refresh()

    def _refresh(self) -> None:
        lock = laser_lock(
            self._state.lock_fire.value,
            flash_duration=self._cfg.FLASH_DURATION,
            lock_duration=self._cfg.COUNTDOWN_LENGTH,
            data_needed=self._state.data_needed.value,
        )

        if self._state.data_needed.value and lock.phase is LaserLockPhase.LOCKED:
            self._data_needed_label.set_text("DATA")
        else:
            self._data_needed_label.set_text("")

        if lock.phase != self._last_phase:
            self._last_phase = lock.phase
            self._panel.set_class_id(_CLASS_ID_BY_PHASE[lock.phase])
            self._phase_label.set_text(_TEXT_BY_PHASE[lock.phase])

        if lock.phase is LaserLockPhase.LOCKED:
            countdown = math.ceil(lock.remaining)
            if countdown != self._last_countdown:
                self._last_countdown = countdown
                self._countdown_label.set_text(f"{countdown}s")
        elif self._last_countdown is not None:
            self._last_countdown = None
            self._countdown_label.set_text("")
