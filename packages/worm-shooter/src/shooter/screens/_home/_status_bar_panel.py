# std
from typing import ClassVar

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
            text=self._left_status_text(),
            obj_id="#status_bar_text",
        )

        # right-aligned info
        right_text_rect = pygame.Rect(0, 0, text_w, text_h)
        right_text_rect.topright = (-StatusBarPanel._TEXT_PAD_X, 0)
        self._right_text = axonkit.Text(
            manager=manager,
            container=panel.content,
            rect=right_text_rect,
            text=self._room_status_text(),
            anchors={"right": "right"},
            obj_id="#status_bar_text_right",
        )

        # bind
        self.bind(state.room_temp, self._render_room_status)
        self.bind(state.room_humidity, self._render_room_status)
        self.bind(state.last_fire, self._render_left_status)

    def _left_status_text(self) -> str:
        last_fire = self._state.last_fire.value
        last_fire_txt = (
            "N/A"
            if last_fire is None
            else (
                f"{last_fire.time.strftime('%H:%M:%S')} "
                f"(fire {self._state.num_fires.value}) {last_fire.duration} ms"
            )
        )
        return f"<b>Last Fire</b>: {last_fire_txt}"

    def _render_left_status(self) -> None:
        self._left_text.set_text(self._left_status_text())

    def _room_status_text(self) -> str:
        return (
            f"<b>Temp</b>: {self._state.room_temp.value} \u2103 | "
            f"<b>Humidity</b>: {self._state.room_humidity.value}%"
        )

    def _render_room_status(self) -> None:
        self._right_text.set_text(self._room_status_text())
