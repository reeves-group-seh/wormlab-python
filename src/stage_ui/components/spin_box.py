# std
from collections.abc import Callable
from typing import ClassVar

# pip
import pygame_gui
from pygame_gui import UIManager
from pygame_gui.elements import UIButton, UIPanel

# local
from stage_ui.atom import Atom

# relative
from .base import Component
from .text_entry_line import TextEntryLineComponent


class SpinBoxComponent[T](Component):
    # public class constants
    H: ClassVar[int] = 30

    # instance vars
    _value: Atom[T]
    _inc: Callable[[T], T]
    _dec: Callable[[T], T]
    _parse: Callable[[str], T]
    _format: Callable[[T], str]

    _text_entry: TextEntryLineComponent[T]

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        w: int,
        value: Atom[T],
        inc: Callable[[T], T],
        dec: Callable[[T], T],
        parse: Callable[[str], T],
        format: Callable[[T], str] = str,
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self._value = value
        self._inc = inc
        self._dec = dec
        self._parse = parse
        self._format = format

        # unpack values
        x, y = pos

        # calculate widths
        text_w = w - (2 * self.H)

        # create
        dec_button = self.track(
            UIButton(
                relative_rect=(x, y, self.H, self.H),
                text="<",
                manager=manager,
                container=container,
            )
        )
        dec_button.bind(pygame_gui.UI_BUTTON_PRESSED, self._handle_dec)

        self._text_entry = self.track(
            TextEntryLineComponent(
                manager=manager,
                container=container,
                pos=(x + self.H, y),
                w=text_w,
                value=value,
                parse=parse,
                format=format,
                valid_class_id="@spin_box_text_entry_valid",
                invalid_class_id="@spin_box_text_entry_invalid",
            )
        )

        inc_button = self.track(
            UIButton(
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
        )
        inc_button.bind(pygame_gui.UI_BUTTON_PRESSED, self._handle_inc)

    def _handle_inc(self) -> None:
        self._value.value = self._inc(self._value.value)

    def _handle_dec(self) -> None:
        self._value.value = self._dec(self._value.value)
