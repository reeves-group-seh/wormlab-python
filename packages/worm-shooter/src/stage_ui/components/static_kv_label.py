# std
from typing import ClassVar

# pip
from pygame_gui import UIManager
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UITextBox

# relative
from .base import Component


class StaticKVLabelComponent(Component):
    # class constants
    H: ClassVar[int] = 25

    # params
    _key: str
    _text_box: UITextBox

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        w: int,
        key: str,
        value: str,
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self._key = key

        # unpack values
        x, y = pos

        # create
        self._text_box = UITextBox(
            html_text=self._format(value),
            relative_rect=(x, y, w, self.H),
            manager=manager,
            container=container,
            object_id=ObjectID(class_id="@static_kv_label"),
        )
        self._text_box.disable()  # type: ignore[no-untyped-call]

    def _format(self, value: str) -> str:
        return f"<b>{self._key}</b>: {value}"

    def set_value(self, text: str) -> None:
        self._text_box.set_text(self._format(text))
