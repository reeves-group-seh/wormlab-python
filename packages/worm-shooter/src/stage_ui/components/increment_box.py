# std
import contextlib
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


class IncrementBoxComponent(Component):
    # public class constants
    H: ClassVar[int] = 30

    # instance vars
    _value: Atom[str]

    _text_entry: TextEntryLineComponent[str]

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        w: int,
        value: Atom[str],
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self._value = value

        # unpack values
        x, y = pos

        # calculate widths
        text_w = w - self.H

        # create
        self._text_entry = TextEntryLineComponent(
            manager=manager,
            container=container,
            pos=(x, y),
            w=text_w,
            value=value,
            parse=str,
        )

        inc_button = UIButton(
            relative_rect=(
                x + text_w,
                y,
                self.H,
                self.H,
            ),
            text="+",
            manager=manager,
            container=container,
        )
        inc_button.bind(pygame_gui.UI_BUTTON_PRESSED, self._handle_inc)

    def _handle_inc(self) -> None:
        with contextlib.suppress(ValueError):
            int_val = int(self._value.value)
            self._value.value = str(int_val + 1)
