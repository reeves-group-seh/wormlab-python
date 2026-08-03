# extern
import pygame_gui

# local
import axon

# relative
from ._util import Value, as_atom


class Text(axon.Widget):
    """
    ...
    """

    # instance variables
    _text: axon.Atom[str]
    _text_box: pygame_gui.elements.UITextBox

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
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
        rect = axon.as_rect(rect)
        object_id = pygame_gui.core.ObjectID(
            object_id=obj_id,
            class_id=class_id,
        )

        # set values
        self._text = as_atom(text)

        # create
        self._text_box = pygame_gui.elements.UITextBox(
            html_text=self._text.value,
            relative_rect=(0, 0, rect.width, rect.height),
            manager=manager,
            container=self.element,
            object_id=object_id,
        )

        # bind
        self.bind(self._text, self._render)

    def _render(self) -> None:
        self._text_box.set_text(self._text.value)

    def set_text(self, text: str) -> None:
        self._text.value = text
