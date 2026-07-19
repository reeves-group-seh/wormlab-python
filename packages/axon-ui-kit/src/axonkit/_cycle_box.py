# std
from collections.abc import Callable
from typing import ClassVar

# extern
import pygame
import pygame_gui

# local
import axon

# relative
from ._button import Button


class CycleBox[T](axon.Widget):
    """
    ...
    """

    # public class variables
    HEIGHT: ClassVar[int] = 28
    """
    Minimum and reccommended height for this element.
    """

    # private class variables
    _PADDING: ClassVar[int] = 2

    # instance variables
    _value: axon.Atom[T]
    _options: list[T]
    _idx: int
    _format: Callable[[T], str]

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: pygame.Rect,
        value: axon.Atom[T],
        options: list[T],
        format: Callable[[T], str] = str,
        prev_text: str = "<",
        next_text: str = ">",
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
        input_class_id: str | None = "@axonkit_cycle_box_input",
        input_obj_id: str | None = None,
        buttons_class_id: str | None = None,
        buttons_obj_id: str | None = None,
    ) -> None:
        """
        ...
        """

        # init parent
        super().__init__(manager, container, rect, anchors)

        # derive inputs
        cycle_box_object_id = pygame_gui.core.ObjectID(
            object_id=input_obj_id,
            class_id=input_class_id,
        )

        # set values
        self._value = value
        self._options = options
        self._idx = options.index(value.value)
        self._format = format

        # calculate
        input_width = rect.width - ((2 * rect.height) + (2 * self._PADDING))

        # create
        self._text_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=(0, 0, input_width, rect.height),
            manager=manager,
            container=self.element,
            initial_text=self._format(self._value.value),
            object_id=cycle_box_object_id,
        )
        self._text_entry.disable()  # type: ignore[no-untyped-call]
        prev_button = Button(
            manager=manager,
            container=self.element,
            rect=pygame.Rect(self._PADDING, 0, rect.height, rect.height),
            text=prev_text,
            anchors={"left": "left", "left_target": self._text_entry},
            on_click=self._prev,
            class_id=buttons_class_id,
            obj_id=buttons_obj_id,
        )
        Button(
            manager=manager,
            container=self.element,
            rect=pygame.Rect(self._PADDING, 0, rect.height, rect.height),
            text=next_text,
            anchors={"left": "left", "left_target": prev_button.element},
            on_click=self._next,
            class_id=buttons_class_id,
            obj_id=buttons_obj_id,
        )

        # bind
        self.bind(self._value, self._render)

    def _render(self) -> None:
        # sync with state update
        self._idx = self._options.index(self._value.value)
        self._text_entry.set_text(self._format(self._value.value))

    def _prev(self) -> None:
        # compute new idx and update value
        new_idx = self._idx - 1
        if new_idx < 0:
            new_idx = len(self._options) - 1
        self._value.value = self._options[new_idx]

    def _next(self) -> None:
        # compute new idx and update value
        new_idx = (self._idx + 1) % len(self._options)
        self._value.value = self._options[new_idx]
