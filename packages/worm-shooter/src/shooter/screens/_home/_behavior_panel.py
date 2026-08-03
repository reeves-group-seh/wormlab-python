# std
from collections.abc import Callable
from typing import TYPE_CHECKING

# extern
import pygame_gui

# local
import axon
import axonkit
from shooter.components import PanelHeading
from shooter.types import WormBehavior

# relative
from ._layout import HomeLayout
from ._state import HomeState

# type-only
if TYPE_CHECKING:
    from shooter.app import AppContext


class BehaviorPanel(axon.Widget):
    # instance vars
    _ctx: AppContext
    _state: HomeState

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

        # save values
        self._ctx = ctx
        self._state = state

        # convert rect
        rect = axon.as_rect(rect)

        # width
        content_w = rect.w - (2 * lt.border_pad)
        comment_inner_pad_x = axonkit.SpinBox._PADDING
        comment_btn_w = lt.input_h
        comment_box_w = content_w - (comment_btn_w + comment_inner_pad_x)

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
            text="BEHAVIOR DATA [TIME OF PRESS]",
        )

        # label
        label = axonkit.Label(
            manager=manager,
            container=panel.content,
            rect=(lt.border_pad, lt.border_label_pad_y, content_w, lt.label_h),
            text="Comment",
            anchors={"top": "top", "top_target": heading.element},
        )

        # comment
        comment_box = axonkit.InputBox(
            manager=manager,
            container=panel.content,
            rect=(
                lt.border_pad,
                lt.label_input_pad_y,
                comment_box_w,
                lt.behavior_comment_box_h,
            ),
            value=state.behavior_comment,
            anchors={"top": "top", "top_target": label.element},
            obj_id="#comment_input_box",
        )
        axonkit.Button(
            manager=manager,
            container=panel.content,
            rect=(
                axonkit.SpinBox._PADDING,
                lt.label_input_pad_y,
                comment_btn_w,
                lt.behavior_comment_box_h,
            ),
            text="+",
            anchors={
                "left": "left",
                "left_target": comment_box.element,
                "top": "top",
                "top_target": label.element,
            },
            on_click=self.handle_comment,
        )

        # buttons
        x_val = lt.border_pad
        btn_w = lt.left_5_btn_w(rect.w)
        btn_dict: dict[str, Callable[[], None]] = {
            "OME": lambda: handle_behavior(WormBehavior.OMEGA),
            "PIR": lambda: handle_behavior(WormBehavior.PIROUETTE),
            "PAU": lambda: handle_behavior(WormBehavior.PAUSE),
            "FOR": lambda: handle_behavior(WormBehavior.FORWARD),
            "REV": lambda: handle_behavior(WormBehavior.REVERSAL),
        }
        for k, v in btn_dict.items():
            axonkit.Button(
                manager=manager,
                container=panel.content,
                rect=(
                    x_val,
                    lt.input_input_pad_y,
                    btn_w,
                    lt.behavior_btn_h,
                ),
                text=k,
                anchors={"top": "top", "top_target": comment_box.element},
                on_click=v,
            )
            x_val += btn_w + lt.left_5_btn_pad_x

        def handle_behavior(behavior: WormBehavior) -> None:
            ctx.data.add_behavior(
                behavior,
                room_temp=state.room_temp.value,
                room_humidity=state.room_humidity.value,
            )

    def handle_comment(self) -> None:
        self._ctx.data.add_comment(
            self._state.behavior_comment.value,
            room_temp=self._state.room_temp.value,
            room_humidity=self._state.room_humidity.value,
        )
        self._state.behavior_comment.value = ""

    @staticmethod
    def content_h(lt: HomeLayout) -> int:
        return HomeLayout.stack(
            lt.panel_heading_h,
            lt.border_label_pad_y,
            lt.label_h,
            lt.label_input_pad_y,
            lt.behavior_comment_box_h,
            lt.input_input_pad_y,
            lt.behavior_btn_h,
            lt.border_pad,
        )
