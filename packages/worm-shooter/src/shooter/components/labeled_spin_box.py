# std
from collections.abc import Callable

# pip
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel

# local
from shooter.atom import Atom

# relative
from .base import Component
from .control_label import ControlLabelComponent
from .spin_box import SpinBoxComponent


class LabeledSpinBoxComponent[T](Component):
    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        w: int,
        label_text: str,
        value: Atom[T],
        inc: Callable[[T], T],
        dec: Callable[[T], T],
        parse: Callable[[str], T],
        format: Callable[[T], str] = str,
    ) -> None:
        # init parent
        super().__init__()

        # unpack values
        x, y = pos

        # create
        label = ControlLabelComponent(
            manager=manager,
            container=container,
            pos=pos,
            w=w,
            text=label_text,
        )

        SpinBoxComponent(
            manager=manager,
            container=container,
            pos=(x, y + label.H),
            w=w,
            value=value,
            inc=inc,
            dec=dec,
            parse=parse,
            format=format,
        )
