# std
from typing import TYPE_CHECKING

# extern
import pygame_gui

# local
import axon
import axonkit
from shooter.components import Feed, PanelHeading

# relative
from ._layout import HomeLayout
from ._state import HomeState

# type-check only imports
if TYPE_CHECKING:
    from shooter.app import AppContext


class FeedPanel(axon.Widget):
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
            anchors={"top": "top", "top_target": heading.element},
        )

    @staticmethod
    def content_h(lt: HomeLayout) -> int:
        return HomeLayout.stack(
            lt.panel_heading_h,
            lt.video_h,
        )
