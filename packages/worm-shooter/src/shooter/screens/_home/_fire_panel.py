# std
import contextlib
from collections.abc import Callable
from typing import TYPE_CHECKING

# extern
import pygame
import pygame_gui

# local
import axon
import axonkit
from shooter.components import PanelHeading
from shooter.types import FilterNumber, RadiusColor, WormResponse

# relative
from ._layout import HomeLayout
from ._state import HomeState

# type-only
if TYPE_CHECKING:
    from shooter.app import AppContext


class FirePanel(axon.Widget):
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

        # width
        content_w = rect.w - (2 * lt.border_pad)
        column_w = (content_w - lt.column_pad_x) // 2
        fire_btn_h = rect.h - HomeLayout.stack(
            lt.panel_heading_h,
            lt.border_label_pad_y,
            lt.label_h,
            lt.label_input_pad_y,
            lt.input_h,
            lt.input_label_pad_y,
            lt.label_h,
            lt.label_input_pad_y,
            lt.input_h,
            lt.input_label_pad_y,
            lt.label_h,
            lt.label_input_pad_y,
            lt.input_h,
            lt.input_input_pad_y,
            lt.border_pad,
        )

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
            text="FIRE DATA [TIME OF FIRE]",
        )

        # left column
        filter_num_label = axonkit.Label(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.border_label_pad_y, column_w, lt.label_h),
            text="Filter Number",
            anchors={"top": "top", "top_target": heading.element},
        )
        filter_num_input = axonkit.CycleBox(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.label_input_pad_y, column_w, lt.input_h),
            value=state.filter_number,
            options=list(FilterNumber),
            anchors={"top": "top", "top_target": filter_num_label.element},
        )
        strain_label = axonkit.Label(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.input_label_pad_y, column_w, lt.label_h),
            text="Strain",
            anchors={"top": "top", "top_target": filter_num_input.element},
        )
        strain_input = axonkit.Input(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.label_input_pad_y, column_w, lt.input_h),
            value=state.worm_strain,
            parse=str,
            anchors={"top": "top", "top_target": strain_label.element},
        )

        # right column
        radius_label_rect = pygame.Rect(0, 0, column_w, lt.label_h)
        radius_label_rect.topright = (-lt.border_pad, lt.border_label_pad_y)
        radius_label = axonkit.Label(
            manager=manager,
            container=panel.content,
            rect=radius_label_rect,
            text="Radius",
            anchors={"top": "top", "top_target": heading.element, "right": "right"},
        )
        radius_input_rect = pygame.Rect(0, 0, column_w, lt.input_h)
        radius_input_rect.topright = (-lt.border_pad, lt.label_input_pad_y)
        radius_input = axonkit.CycleBox(
            manager=manager,
            container=panel.content,
            rect=radius_input_rect,
            value=state.radius_color,
            options=list(RadiusColor),
            anchors={
                "top": "top",
                "top_target": radius_label.element,
                "right": "right",
            },
        )
        id_label_rect = pygame.Rect(0, 0, column_w, lt.label_h)
        id_label_rect.topright = (-lt.border_pad, lt.input_label_pad_y)
        id_label = axonkit.Label(
            manager=manager,
            container=panel.content,
            rect=id_label_rect,
            text="ID",
            anchors={
                "top": "top",
                "top_target": radius_input.element,
                "right": "right",
            },
        )

        def handle_id_btn_click() -> None:
            with contextlib.suppress(ValueError):
                state.worm_id.value = str(int(state.worm_id.value) + 1)

        id_rect = pygame.Rect(0, 0, lt.input_h, lt.input_h)
        id_rect.topright = (-lt.border_pad, lt.label_input_pad_y)
        id_btn = axonkit.Button(
            manager=manager,
            container=panel.content,
            rect=id_rect,
            text="+",
            anchors={"top": "top", "top_target": id_label.element, "right": "right"},
            on_click=handle_id_btn_click,
        )

        id_input_rect = pygame.Rect(
            0, 0, column_w - (axonkit.CycleBox._PADDING + lt.input_h), lt.input_h
        )
        id_input_rect.topright = (-axonkit.CycleBox._PADDING, lt.label_input_pad_y)
        axonkit.Input(
            manager=manager,
            container=panel.content,
            rect=id_input_rect,
            value=state.worm_id,
            parse=str,
            anchors={
                "top": "top",
                "top_target": id_label.element,
                "right": "right",
                "right_target": id_btn.element,
            },
        )

        # comment
        comment_label = axonkit.Label(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.input_label_pad_y, content_w, lt.label_h),
            text="Comment",
            anchors={"top": "top", "top_target": strain_input.element},
        )
        comment_input = axonkit.Input(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.label_input_pad_y, content_w, lt.input_h),
            value=state.fire_comment,
            parse=str,
            anchors={"top": "top", "top_target": comment_label.element},
        )

        # buttons
        btn_x = lt.border_pad
        btn_w = lt.left_5_btn_w(rect.w)
        btn_dict: dict[str, Callable[[], None]] = {
            "FUL": lambda: handle_submit(WormResponse.FULL),
            "PAR": lambda: handle_submit(WormResponse.PARTIAL),
            "ACK": lambda: handle_submit(WormResponse.ACKNOWLEDGE),
            "PAU": lambda: handle_submit(WormResponse.PAUSE),
            "NOR": lambda: handle_submit(WormResponse.NO_RESPONSE),
        }
        response_btns: list[axonkit.Button] = []
        for k, v in btn_dict.items():
            btn = axonkit.Button(
                manager=manager,
                container=panel.content,
                rect=(
                    btn_x,
                    lt.input_input_pad_y,
                    btn_w,
                    fire_btn_h,
                ),
                text=k,
                anchors={"top": "top", "top_target": comment_input.element},
                on_click=v,
            )
            response_btns.append(btn)
            btn_x += btn_w + lt.left_5_btn_pad_x

        def refresh_btns() -> None:
            for btn in response_btns:
                if state.data_needed.value:
                    btn.enable()
                else:
                    btn.disable()

        self.bind(state.data_needed, refresh_btns)
        refresh_btns()

        def handle_submit(response: WormResponse) -> None:
            # assert values
            fire = state.last_fire.value
            assert fire is not None

            # record
            ctx.data.add_data_fire(
                fire=fire,
                radius_color=state.radius_color.value,
                filter_number=state.filter_number.value,
                worm_strain=state.worm_strain.value,
                worm_id=state.worm_id.value,
                response=response,
                comment=state.fire_comment.value,
                room_temp=state.room_temp.value,
                room_humidity=state.room_humidity.value,
            )

            # reset
            state.fire_comment.value = ""
            state.data_needed.value = False
