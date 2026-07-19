# std
from typing import ClassVar

# extern
import pygame
import pygame_gui

# local
import axon

# relative
from ._util import Value, as_atom


class Label(axon.Widget):
    """
    ...
    """

    # class variables
    HEIGHT: ClassVar[int] = 20
    """
    Minimum and reccommended height for this element.
    """

    # instance variables
    _text: axon.Atom[str]
    _label: pygame_gui.elements.UILabel

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: pygame.Rect,
        text: Value[str],
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
        class_id: str | None = None,
        obj_id: str | None = None,
    ) -> None:
        """
        ...
        """

        # init parent
        super().__init__(manager, container, rect, anchors)

        # derive inputs
        object_id = pygame_gui.core.ObjectID(
            object_id=obj_id,
            class_id=class_id,
        )

        # set values
        self._text = as_atom(text)

        # create
        self._label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, rect.width, rect.height),
            text=self._text.value,
            manager=manager,
            container=self.element,
            object_id=object_id,
            anchors={
                "left": "left",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
        )

        # bind
        self.bind(self._text, self._render)

    def _render(self) -> None:
        self._label.set_text(self._text.value)

    def set_text(self, text: str) -> None:
        self._text.value = text
