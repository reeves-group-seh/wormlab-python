# std
from typing import ClassVar, override

# extern
import pygame
import pygame_gui

# local
import axon
import axonkit

# relative
from ._state import HomeState


class StatusBarPanel(axon.Widget):
    # class vars
    _TEXT_PAD_X: ClassVar[int] = 5

    # instance vars
    _state: HomeState
    _left_is_stale: bool
    _left_text: axonkit.Text
    _right_text: axonkit.Text

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
        state: HomeState,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface],
    ) -> None:
        # init parent
        super().__init__(manager, container, rect, anchors)

        # set values
        self._state = state
        self._left_is_stale = False

        # convert rect
        rect = axon.as_rect(rect)

        # root
        panel = axonkit.Panel(
            manager=manager,
            container=self.element,
            rect=(0, 0, rect.width, rect.height),
            margins=axonkit.MarginOption.DEFAULT,
            obj_id="#status_bar_panel",
        )

        # values
        text_w = panel.content_width() - (2 * StatusBarPanel._TEXT_PAD_X)
        text_h = panel.content_height() - 2

        # left-aligned info
        self._left_text = axonkit.Text(
            manager=manager,
            container=panel.content,
            rect=(StatusBarPanel._TEXT_PAD_X, 0, text_w, text_h),
            text=self._format_left_text(),
            obj_id="#status_bar_text",
        )

        # right-aligned info
        right_text_rect = pygame.Rect(0, 0, text_w, text_h)
        right_text_rect.topright = (-StatusBarPanel._TEXT_PAD_X, 0)
        self._right_text = axonkit.Text(
            manager=manager,
            container=panel.content,
            rect=right_text_rect,
            text=self._format_right_text(),
            anchors={"right": "right"},
            obj_id="#status_bar_text_right",
        )

        # bind
        self.bind(state.room_temp, self._render_right_text)
        self.bind(state.room_humidity, self._render_right_text)
        self.bind(state.last_fire, self._invalidate_left_text)
        self.bind(state.hover_pos, self._invalidate_left_text)

    @override
    def on_update(self, dt: float) -> None:
        # only set text once per frame
        if self._left_is_stale:
            self._left_text.set_text(self._format_left_text())
            self._left_is_stale = False

    def _format_left_text(self) -> str:
        # last fire info
        last_fire = self._state.last_fire.value
        last_fire_txt = (
            "N/A"
            if last_fire is None
            else (
                f"{last_fire.time.strftime('%H:%M:%S')} "
                f"(fire {self._state.num_fires.value}) {last_fire.duration} ms"
            )
        )

        # mouse hover info
        hover = self._state.hover_pos.value
        hover_txt = "N/A" if hover is None else f"{hover[0]}, {hover[1]}"

        # text
        return f"<b>Last Fire</b>: {last_fire_txt} | <b>Cursor</b>: {hover_txt}"

    def _format_right_text(self) -> str:
        return (
            f"<b>Temp</b>: {self._state.room_temp.value} \u2103 | "
            f"<b>Humidity</b>: {self._state.room_humidity.value}%"
        )

    def _invalidate_left_text(self) -> None:
        self._left_is_stale = True

    def _render_right_text(self) -> None:
        self._right_text.set_text(self._format_right_text())
