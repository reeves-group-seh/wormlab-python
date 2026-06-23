# std

# pip
import contextlib

import pygame_gui
from pygame_gui import UIManager
from pygame_gui.elements import UIButton, UIPanel

# local
from stage_ui.atom import Atom
from stage_ui.components.base import Component
from stage_ui.components.text_entry_line import TextEntryLineComponent


class IncrementBoxComponent(Component):
    # constants
    H: int = 30

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
        self.value = value

        # unpack values
        x, y = pos

        # calculate widths
        text_w = w - self.H

        # create
        self.text_entry = self.track(
            TextEntryLineComponent(
                manager=manager,
                container=container,
                pos=(x, y),
                w=text_w,
                value=value,
                parse=str,
            )
        )

        inc_button = self.track(
            UIButton(
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
        )
        inc_button.bind(pygame_gui.UI_BUTTON_PRESSED, self._handle_inc)

    def _handle_inc(self) -> None:
        with contextlib.suppress(ValueError):
            int_val = int(self.value.value)
            self.value.value = str(int_val + 1)
