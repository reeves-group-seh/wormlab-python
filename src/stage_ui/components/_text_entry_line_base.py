# std
from abc import abstractmethod
from collections.abc import Callable
from typing import override

# pip
import pygame_gui
from pygame import Event
from pygame_gui import UIManager
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UITextEntryLine

# local
from stage_ui.atom import Atom
from stage_ui.components.base import Component


class BaseTextEntryLineComponent[T](Component):
    # constants
    H: int = 30

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
        self.value = value
        self.parse = parse
        self.format = format
        self.valid_class_id = valid_class_id
        self.invalid_class_id = invalid_class_id
        self._is_valid = True

        # bindings
        self.bind(self.value, self._render_text_entry)

        # unpack values
        x, y = pos

        # create
        self.text_entry = self.track(
            UITextEntryLine(
                relative_rect=(x, y, w, self.H),
                manager=manager,
                container=container,
                initial_text=self.format(value.value),
                object_id=ObjectID(class_id=valid_class_id),
            )
        )

    @override
    def process_event(self, event: Event) -> None:
        super().process_event(event)
        if (
            event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED
            and event.ui_element is self.text_entry
        ):
            try:
                self.value.value = self.parse(event.text)
                self._set_valid(True)
            except ValueError:
                self.on_parse_error()
                self._set_valid(False)

    def _set_valid(self, valid: bool) -> None:
        # do nothing if already in correct state
        if valid == self._is_valid:
            return

        # flip state and class
        self._is_valid = valid
        class_id = self.valid_class_id if valid else self.invalid_class_id
        self.text_entry.change_object_id(ObjectID(class_id=class_id))

    def _render_text_entry(self) -> None:
        if not self.text_entry.is_focused:
            self.text_entry.set_text(self.format(self.value.value))

    @abstractmethod
    def on_parse_error(self) -> None:
        """
        Hook for when entered text fails to parse.
        """
        raise NotImplementedError
