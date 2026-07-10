# std
from typing import ClassVar

# pip
import pygame_gui
from pygame_gui import UIManager
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIButton, UIPanel, UITextEntryLine

# local
from shooter.atom import Atom

# relative
from .base import Component


class CycleBoxComponent[T: str](Component):
    # public class constants
    H: ClassVar[int] = 30

    # instance vars
    _value: Atom[T]
    _options: list[T]
    _idx: int

    _text: UITextEntryLine

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        w: int,
        value: Atom[T],
        options: list[T],
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self._value = value
        self._options = options
        self._idx = options.index(value.value)

        # bindings
        self.bind(self._value, self._render_text)

        # unpack values
        x, y = pos

        # calculate widths
        text_w = w - (2 * self.H)

        # create
        prev_button = UIButton(
            relative_rect=(x, y, self.H, self.H),
            text="<",
            manager=manager,
            container=container,
        )
        prev_button.bind(pygame_gui.UI_BUTTON_PRESSED, self._handle_prev)

        self._text = UITextEntryLine(
            relative_rect=(x + self.H, y, text_w, self.H),
            manager=manager,
            container=container,
            object_id=ObjectID(class_id="@cycle_box_text"),
            initial_text=value.value,
        )
        self._text.disable()  # type: ignore[no-untyped-call]

        next_button = UIButton(
            relative_rect=(
                x + self.H + text_w,
                y,
                self.H,
                self.H,
            ),
            text=">",
            manager=manager,
            container=container,
        )

        next_button.bind(pygame_gui.UI_BUTTON_PRESSED, self._handle_next)

    def _handle_prev(self) -> None:
        # compute new idx
        new_idx = self._idx - 1
        if new_idx < 0:
            new_idx = len(self._options) - 1

        # update state
        self._value.value = self._options[new_idx]

    def _handle_next(self) -> None:
        # compute new idx
        new_idx = (self._idx + 1) % len(self._options)

        # update state
        self._value.value = self._options[new_idx]

    def _render_text(self) -> None:
        # sync with state update
        self._idx = self._options.index(self._value.value)
        self._text.set_text(self._value.value)
