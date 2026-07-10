# pip
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel

# local
from stage_ui.atom import Atom

# relative
from .base import Component
from .control_label import ControlLabelComponent
from .cycle_box import CycleBoxComponent


class LabeledCycleBoxComponent[T: str](Component):
    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        w: int,
        label_text: str,
        value: Atom[T],
        options: list[T],
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

        CycleBoxComponent(
            manager=manager,
            container=container,
            pos=(x, y + label.H),
            w=w,
            value=value,
            options=options,
        )
