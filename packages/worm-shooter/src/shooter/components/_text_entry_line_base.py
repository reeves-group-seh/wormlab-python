# std
from abc import abstractmethod
from collections.abc import Callable
from typing import ClassVar, override

# pip
import pygame_gui
from pygame import Event
from pygame_gui import UIManager
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UITextEntryLine

# local
from shooter.atom import Atom

# relative
from .base import Component


class BaseTextEntryLineComponent[T](Component):
    # public class constants
    H: ClassVar[int] = 30

    # instance variables
    _value: Atom[T]
    _parse: Callable[[str], T]
    _format: Callable[[T], str]
    _valid_class_id: str | None
    _invalid_class_id: str
    _is_valid: bool

    _text_entry: UITextEntryLine

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        w: int,
        value: Atom[T],
        parse: Callable[[str], T],
        format: Callable[[T], str] = str,
        valid_class_id: str | None = None,
        invalid_class_id: str = "@text_entry_line_invalid",
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self._value = value
        self._parse = parse
        self._format = format
        self._valid_class_id = valid_class_id
        self._invalid_class_id = invalid_class_id
        self._is_valid = True

        # bindings
        self.bind(self._value, self._render_text_entry)

        # unpack values
        x, y = pos

        # create
        self._text_entry = UITextEntryLine(
            relative_rect=(x, y, w, self.H),
            manager=manager,
            container=container,
            initial_text=self._format(value.value),
            object_id=ObjectID(class_id=valid_class_id),
        )

    @override
    def process_event(self, event: Event) -> None:
        super().process_event(event)
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

    def _set_valid(self, valid: bool) -> None:
        # do nothing if already in correct state
        if valid == self._is_valid:
            return

        # flip state and class
        self._is_valid = valid
        class_id = self._valid_class_id if valid else self._invalid_class_id
        self._text_entry.change_object_id(ObjectID(class_id=class_id))

    def _render_text_entry(self) -> None:
        if not self._text_entry.is_focused:
            self._text_entry.set_text(self._format(self._value.value))
            self._set_valid(True)

    @abstractmethod
    def _on_parse_error(self) -> None:
        """
        Hook for when entered text fails to parse.
        """
        raise NotImplementedError
