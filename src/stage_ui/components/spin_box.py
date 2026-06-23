# std
from collections.abc import Callable

# pip
import pygame_gui
from pygame_gui import UIManager
from pygame_gui.elements import UIButton, UIPanel

# local
from stage_ui.atom import Atom
from stage_ui.components.base import Component
from stage_ui.components.text_entry_line import TextEntryLineComponent


class SpinBoxComponent[T](Component):
    # constants
    H: int = 30

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
        self.value = value
        self.inc = inc
        self.dec = dec
        self.parse = parse
        self.format = format

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

        self.text_entry = self.track(
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
        self.value.value = self.inc(self.value.value)

    def _handle_dec(self) -> None:
        self.value.value = self.dec(self.value.value)
