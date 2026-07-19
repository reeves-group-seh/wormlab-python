# std
from collections.abc import Callable
from typing import override

# extern
import pygame
import pygame_gui

# local
import axon


class Input[T](axon.Widget):
    """
    ...
    """

    # instance variables
    _value: axon.Atom[T]
    _parse: Callable[[str], T]
    _format: Callable[[T], str]
    _valid_class_id: str | None
    _invalid_class_id: str | None
    _valid: bool
    _enabled: bool
    _text_entry: pygame_gui.elements.UITextEntryLine

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: pygame.Rect,
        value: axon.Atom[T],
        parse: Callable[[str], T],
        format: Callable[[T], str] = str,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
        valid_class_id: str | None = None,
        invalid_class_id: str | None = "@axonkit_input_invalid",
        obj_id: str | None = None,
    ) -> None:
        """
        ...
        """

        # init parent
        super().__init__(manager, container, rect, anchors)

        # set values
        self._value = value
        self._parse = parse
        self._format = format
        self._valid_class_id = valid_class_id
        self._invalid_class_id = invalid_class_id
        self._obj_id = obj_id
        self._valid = True
        self._enabled = True

        # create
        self._text_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=(0, 0, rect.width, rect.height),
            manager=manager,
            container=self.element,
            initial_text=self._format(self._value.value),
            object_id=self._create_object_id(),
        )

        # bind
        self.bind(self._value, self._render)

    @override
    def on_process_event(self, event: pygame.Event) -> None:
        if (
            event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED
            and event.ui_element is self._text_entry
        ):
            try:
                self._value.value = self._parse(event.text)
                self._set_valid(True)
            except ValueError:
                self._on_parse_error()
                self._set_valid(False)

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

    def _create_object_id(self) -> pygame_gui.core.ObjectID:
        if self._valid:
            return pygame_gui.core.ObjectID(
                class_id=self._valid_class_id, object_id=self._obj_id
            )
        else:
            return pygame_gui.core.ObjectID(
                class_id=self._invalid_class_id, object_id=self._obj_id
            )

    def _set_valid(self, valid: bool) -> None:
        # do nothing if already in correct state
        if valid == self._valid:
            return

        # flip state and class
        self._valid = valid
        object_id = self._create_object_id()
        self._text_entry.change_object_id(object_id)

    def _render(self) -> None:
        if not self._text_entry.is_focused:
            self._text_entry.set_text(self._format(self._value.value))
            self._set_valid(True)

    def _on_parse_error(self) -> None:
        # keep the last valid value on a parse error
        pass


class InputStrict[T](Input[T | None]):
    """
    ...
    """

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        container: pygame_gui.core.IContainerLikeInterface | None,
        rect: pygame.Rect,
        value: axon.Atom[T | None],
        parse: Callable[[str], T],
        format: Callable[[T], str] = str,
        anchors: dict[str, str | pygame_gui.core.interfaces.IUIElementInterface]
        | None = None,
        valid_class_id: str | None = "@axonkit_input_valid",
        invalid_class_id: str | None = "@axonkit_input_invalid",
        obj_id: str | None = None,
    ) -> None:
        super().__init__(
            manager=manager,
            container=container,
            rect=rect,
            value=value,
            parse=parse,
            format=lambda v: "" if v is None else format(v),
            anchors=anchors,
            valid_class_id=valid_class_id,
            invalid_class_id=invalid_class_id,
            obj_id=obj_id,
        )

    @override
    def _on_parse_error(self) -> None:
        self._value.value = None
