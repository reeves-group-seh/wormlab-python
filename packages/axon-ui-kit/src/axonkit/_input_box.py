# std
from typing import ClassVar, override

# extern
import pygame
import pygame_gui

# local
import axon


class InputBox(axon.Widget):
    """
    ...
    """

    # class variables
    HEIGHT: ClassVar[int] = 28
    """
    Minimum height for this element.
    """

    # instance variables
    _value: axon.Atom[str]
    _text_entry: pygame_gui.elements.UITextEntryBox

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: axon.RectLike,
        value: axon.Atom[str],
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
            class_id=class_id,
            object_id=obj_id,
        )

        # set values
        self._value = value

        # create
        self._text_entry = pygame_gui.elements.UITextEntryBox(
            relative_rect=(0, 0, rect.width, rect.height),
            manager=manager,
            container=self.element,
            initial_text=self._value.value,
            object_id=object_id,
        )
        self._text_entry.rebuild_from_changed_theme_data()  # type: ignore[no-untyped-call]

        # bind
        self.bind(self._value, self._render)

    @override
    def on_process_event(self, event: pygame.Event) -> None:
        if (
            event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED
            and event.ui_element is self._text_entry
        ):
            self._value.value = event.text

    def enable(self) -> None:
        """
        ...
        """
        self._text_entry.enable()  # type: ignore[no-untyped-call]

    def disable(self) -> None:
        """
        ...
        """
        self._text_entry.disable()  # type: ignore[no-untyped-call]

    def _render(self) -> None:
        if not self._text_entry.is_focused:
            self._text_entry.set_text(self._value.value)
