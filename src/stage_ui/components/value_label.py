# std

# pip
from pygame_gui import UIManager
from pygame_gui.core import ObjectID
from pygame_gui.elements import UILabel, UIPanel

# local
from stage_ui.components.base import Component


class ValueLabelComponent(Component):
    # constants
    H: int = 30

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        w: int,
        text: str,
    ) -> None:
        # init parent
        super().__init__()

        # unpack values
        x, y = pos

        # create
        self.label = self.track(
            UILabel(
                relative_rect=(x, y, w, self.H),
                manager=manager,
                container=container,
                text=text,
                object_id=ObjectID(class_id="@value_label"),
            )
        )

    def set_text(self, text: str) -> None:
        self.label.set_text(text)
