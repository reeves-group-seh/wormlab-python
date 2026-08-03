# std
import enum
from enum import Enum
from typing import TypedDict, cast

# extern
import pygame_gui

# local
import axon


class _MarginsDict(TypedDict):
    top: int
    bottom: int
    left: int
    right: int


class MarginOption(Enum):
    NONE = enum.auto()
    DEFAULT = enum.auto()


class Panel(axon.Widget):
    """
    ...
    """

    # instance variables
    _panel: pygame_gui.elements.UIPanel
    _obj_id: str | None

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
        margins: _MarginsDict | MarginOption = MarginOption.NONE,
        class_id: str | None = "@axonkit_panel",
        obj_id: str | None = None,
    ) -> None:
        """
        ...
        """

        # init parent
        super().__init__(manager, container, rect, anchors)

        # derive inputs
        rect = axon.as_rect(rect)
        object_id = pygame_gui.core.ObjectID(
            object_id=obj_id,
            class_id=class_id,
        )
        self._obj_id = obj_id
        margins_dict: dict[str, int] | None
        match margins:
            case MarginOption.NONE:
                margins_dict = {"top": 0, "right": 0, "bottom": 0, "left": 0}
            case MarginOption.DEFAULT:
                margins_dict = None
            case d:
                margins_dict = cast(dict[str, int], d)

        # create
        self._panel = pygame_gui.elements.UIPanel(
            relative_rect=(0, 0, rect.width, rect.height),
            manager=manager,
            margins=margins_dict,
            container=self.element,
            object_id=object_id,
        )

    def set_class_id(self, class_id: str | None) -> None:
        """
        Re-theme this panel by swapping its class id, without rebuilding the
        underlying `pygame_gui` element.
        """
        object_id = pygame_gui.core.ObjectID(object_id=self._obj_id, class_id=class_id)
        self._panel.change_object_id(object_id)

    @property
    def content(self) -> pygame_gui.elements.UIPanel:
        """
        This panel's container for children.

        Pass it as the `container` of any element the widget builds and they
        will be placed with consideration of the margins. Do not use this for
        `*_target` anchors, use `axon.Widget.element`.
        """
        return self._panel

    def content_width(self) -> int:
        """
        ...
        """
        return self._panel.get_container().get_rect().width

    def content_height(self) -> int:
        """
        ...
        """
        return self._panel.get_container().get_rect().height
