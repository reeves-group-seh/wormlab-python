# std

# pip
import pygame_gui
from pygame_gui import UIManager
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIButton, UIPanel, UITextEntryLine

# local
from stage_ui.atom import Atom
from stage_ui.components.base import Component


class CycleBoxComponent[T: str](Component):
    # constants
    H: int = 30

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
        self.value = value
        self.options = options
        self.idx = options.index(value.value)

        # bindings
        self.bind(self.value, self._render_text)

        # unpack values
        x, y = pos

        # calculate widths
        text_w = w - (2 * self.H)

        # create
        prev_button = self.track(
            UIButton(
                relative_rect=(x, y, self.H, self.H),
                text="<",
                manager=manager,
                container=container,
            )
        )
        prev_button.bind(pygame_gui.UI_BUTTON_PRESSED, self._handle_prev)

        self.text = self.track(
            UITextEntryLine(
                relative_rect=(x + self.H, y, text_w, self.H),
                manager=manager,
                container=container,
                object_id=ObjectID(class_id="@cycle_box_text"),
                initial_text=value.value,
            )
        )
        self.text.disable()  # type: ignore[no-untyped-call]

        next_button = self.track(
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
        next_button.bind(pygame_gui.UI_BUTTON_PRESSED, self._handle_next)

    def _handle_prev(self) -> None:
        # compute new idx
        new_idx = self.idx - 1
        if new_idx < 0:
            new_idx = len(self.options) - 1

        # update state
        self.value.value = self.options[new_idx]

    def _handle_next(self) -> None:
        # compute new idx
        new_idx = (self.idx + 1) % len(self.options)

        # update state
        self.value.value = self.options[new_idx]

    def _render_text(self) -> None:
        # sync with state update
        self.idx = self.options.index(self.value.value)
        self.text.set_text(self.value.value)
