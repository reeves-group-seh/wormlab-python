# std
from typing import TYPE_CHECKING

# extern
import pygame_gui

# local
import axon
import axonkit
from shooter.components import Feed, PanelHeading
from shooter.types import center_plan

# relative
from ._layout import HomeLayout
from ._state import HomeState

# type-check only imports
if TYPE_CHECKING:
    from shooter.app import AppContext


class FeedPanel(axon.Widget):
    # instance vars
    _ctx: AppContext
    _state: HomeState

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

        # set values
        self._ctx = ctx
        self._state = state

        # convert rect
        rect = axon.as_rect(rect)

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
            text="VIDEO FEED",
        )

        # video
        Feed(
            manager=manager,
            container=panel.content,
            rect=(0, 0, panel.content_width(), lt.video_h),
            camera=ctx.camera,
            marker_pos=state.marker_pos,
            radius_color=state.radius_color,
            hover_pos=state.hover_pos,
            on_left_click=self._center_on_plane,
            on_right_click=self._center_on_marker,
            anchors={"top": "top", "top_target": heading.element},
        )

    def _center_on_plane(self, pos: tuple[int, int]) -> None:
        """
        Bring a left-clicked point to the center of the frame.
        """
        self._start_centering(pos, Feed.PLANE_CENTER)

    def _center_on_marker(self, pos: tuple[int, int]) -> None:
        """
        Bring a right-clicked point to the marker, where the laser fires.
        """
        self._start_centering(pos, self._state.marker_pos.value)

    def _start_centering(self, pos: tuple[int, int], target: tuple[int, int]) -> None:
        """
        Replace the centering plan with one taking `pos` to `target`.

        A click always replaces the plan, so clicking again during a sequence
        re-aims it, and a click too far to plan cancels it.
        """

        # speed and duration are whatever the stage controls currently say, so
        # a command covers this much of the plane
        cfg = self._ctx.cfg
        px_per_command = (
            self._state.move_speed.value
            * (self._state.step_duration.value / 1000.0)
            * cfg.PX_PER_STEP
        )

        # plan the journey
        self._state.centering.value = center_plan(
            pos,
            target=target,
            px_per_command=px_per_command,
            invert_x=cfg.CENTER_INVERT_X,
            invert_y=cfg.CENTER_INVERT_Y,
            max_commands=cfg.MAX_CENTER_COMMANDS,
        )

    @staticmethod
    def content_h(lt: HomeLayout) -> int:
        return HomeLayout.stack(
            lt.panel_heading_h,
            lt.video_h,
        )
