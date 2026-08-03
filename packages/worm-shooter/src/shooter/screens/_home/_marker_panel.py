# extern
import pygame
import pygame_gui

# local
import axon
import axonkit
from shooter.components import PanelHeading

# relative
from ._layout import HomeLayout
from ._state import HomeState


class MarkerPanel(axon.Widget):
    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
        lt: HomeLayout,
        state: HomeState,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
    ) -> None:
        # parent init
        super().__init__(manager, container, rect, anchors)

        # convert rect
        rect = axon.as_rect(rect)

        # per-axis atoms kept in sync with the shared marker position, since
        # SpinBox edits one axis at a time
        marker_x = axon.Atom(state.marker_pos.value[0])
        marker_y = axon.Atom(state.marker_pos.value[1])

        def sync_from_marker_pos() -> None:
            marker_x.value = state.marker_pos.value[0]
            marker_y.value = state.marker_pos.value[1]

        def sync_to_marker_pos() -> None:
            state.marker_pos.value = (marker_x.value, marker_y.value)

        self.bind(state.marker_pos, sync_from_marker_pos)
        self.bind(marker_x, sync_to_marker_pos)
        self.bind(marker_y, sync_to_marker_pos)

        # width
        content_w = rect.w - (2 * lt.border_pad)
        column_w = (content_w - lt.column_pad_x) // 2

        # panel
        panel = axonkit.Panel(
            manager=manager,
            container=self.element,
            rect=(0, 0, rect.w, rect.h),
            margins=axonkit.MarginOption.DEFAULT,
        )

        # header
        heading = PanelHeading(
            manager=manager,
            container=panel.content,
            rect=(0, 0, panel.content_width(), lt.panel_heading_h),
            text="MARKER",
        )

        # label
        label = axonkit.Label(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.border_label_pad_y, content_w, lt.label_h),
            text="Position",
            anchors={"top": "top", "top_target": heading.element},
        )

        # left column
        axonkit.SpinBox(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.label_input_pad_y, column_w, lt.input_h),
            value=marker_x,
            inc=lambda x: x + 1,
            dec=lambda x: x - 1,
            parse=int,
            anchors={"top": "top", "top_target": label.element},
        )

        # right column
        y_input_rect = pygame.Rect(0, 0, column_w, lt.input_h)
        y_input_rect.topright = (-lt.border_pad, lt.label_input_pad_y)
        axonkit.SpinBox(
            manager=manager,
            container=panel.content,
            rect=y_input_rect,
            value=marker_y,
            inc=lambda x: x + 1,
            dec=lambda x: x - 1,
            parse=int,
            anchors={"top": "top", "top_target": label.element, "right": "right"},
        )

    @staticmethod
    def content_h(lt: HomeLayout) -> int:
        return HomeLayout.stack(
            lt.panel_heading_h,
            lt.border_label_pad_y,
            lt.label_h,
            lt.label_input_pad_y,
            lt.input_h,
            lt.border_pad,
        )
