# std
from typing import Any

# extern
import pygame_gui

# local
import axon
import axonkit


class PanelHeading(axon.Widget):
    """
    ...
    """

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
        text: str,
        anchors: dict[str, str | Any] | None = None,
    ) -> None:
        # init parent
        super().__init__(manager, container, rect, anchors)

        # convert rect
        rect = axon.as_rect(rect)

        # create
        panel = axonkit.Panel(
            manager=manager,
            container=self.element,
            rect=(0, 0, rect.width, rect.height),
            margins=axonkit.MarginOption.NONE,
            obj_id="#panel_heading_panel",
        )
        axonkit.Label(
            manager=manager,
            container=panel.element,
            rect=(10, 0, panel.content_width() - 20, panel.content_height()),
            text=text,
            obj_id="#panel_heading_label",
        )
