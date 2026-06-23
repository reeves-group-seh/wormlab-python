# std
import datetime as dt
from typing import override

# pip
from pygame_gui import UIManager
from pygame_gui.elements import UIButton, UIPanel

# local
from stage_ui.atom import Atom
from stage_ui.components import NO_MARGINS, Component
from stage_ui.components.control_label import ControlLabelComponent
from stage_ui.components.increment_box import IncrementBoxComponent
from stage_ui.components.labeled_cycle_box import LabeledCycleBoxComponent
from stage_ui.components.text_entry_line import TextEntryLineComponent
from stage_ui.components.value_label import ValueLabelComponent
from stage_ui.types import FilterNumber, LaserFire


class SidePanelComponent(Component):
    # constants
    W: int = 395
    H: int = 370

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        last_fire: Atom[LaserFire | None],
        num_fires: Atom[int],
        filter: Atom[FilterNumber],
        strain: Atom[str],
        worm_id: Atom[str],
    ):
        # init parent
        super().__init__()

        # unpack values
        x, y = pos

        # set values
        self.last_fire = last_fire
        self.num_fires = num_fires

        # bindings
        self.bind(last_fire, self._render_last_fire_label)
        self.bind(num_fires, self._render_last_fire_label)

        # unpack values
        x, y = pos

        # create
        panel = self.track(
            UIPanel(
                relative_rect=(x, y, self.W, self.H),
                manager=manager,
                container=container,
                margins=NO_MARGINS,
            )
        )

        # last fire
        self.track(
            ControlLabelComponent(
                manager=manager,
                container=panel,
                pos=(10, 10),
                w=183,
                text="Last Fire",
            )
        )
        self.last_fire_label = self.track(
            ValueLabelComponent(
                manager=manager,
                container=panel,
                pos=(10, 40),
                w=183,
                text="",
            )
        )

        # time since fire
        self.track(
            ControlLabelComponent(
                manager=manager,
                container=panel,
                pos=(202, 10),
                w=183,
                text="Time Since Fire",
            )
        )
        self.track(
            CountdownComponent(
                manager=manager,
                container=panel,
                pos=(202, 40),
                w=183,
                last_fire=last_fire,
            )
        )

        # filter
        LabeledCycleBoxComponent(
            manager=manager,
            container=panel,
            pos=(10, 80),
            w=375,
            label_text="Filter Number",
            value=filter,
            options=[
                FilterNumber.ONE,
                FilterNumber.TWO,
                FilterNumber.THREE,
                FilterNumber.FOUR,
                FilterNumber.FIVE,
                FilterNumber.SIX,
            ],
        )

        # strain
        self.track(
            ControlLabelComponent(
                manager=manager,
                container=panel,
                pos=(10, 150),
                w=375,
                text="Strain",
            )
        )
        self.track(
            TextEntryLineComponent(
                manager=manager,
                container=panel,
                pos=(10, 180),
                w=375,
                value=strain,
                parse=str,
            )
        )

        # worm id
        self.track(
            ControlLabelComponent(
                manager=manager,
                container=panel,
                pos=(10, 220),
                w=375,
                text="ID",
            )
        )
        self.track(
            IncrementBoxComponent(
                manager=manager,
                container=panel,
                pos=(10, 250),
                w=375,
                value=worm_id,
            )
        )

        # buttons
        f_res_button = UIButton(
            relative_rect=(10, 290, 87, 70),
            text="F",
            manager=manager,
            container=panel,
        )
        f_res_button.disable()
        p_res_button = UIButton(
            relative_rect=(106, 290, 87, 70),
            text="P",
            manager=manager,
            container=panel,
        )
        p_res_button.disable()
        a_res_button = UIButton(
            relative_rect=(202, 290, 87, 70),
            text="A",
            manager=manager,
            container=panel,
        )
        a_res_button.disable()
        n_res_button = UIButton(
            relative_rect=(298, 290, 87, 70),
            text="N",
            manager=manager,
            container=panel,
        )
        n_res_button.disable()

        # do initial renders
        self._render_last_fire_label()

    def _render_last_fire_label(self) -> None:
        # grab last fire and check if none
        last_fire = self.last_fire.value
        if last_fire is None:
            self.last_fire_label.set_text("N/A")
            return

        # format values
        time_txt = last_fire.time.strftime("%H:%M:%S")
        full_txt = f"{time_txt} (fire {self.num_fires.value}) {last_fire.duration} ms"
        self.last_fire_label.set_text(full_txt)


class CountdownComponent(Component):
    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        w: int,
        last_fire: Atom[LaserFire | None],
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self.last_fire = last_fire
        self.displayed: int | None = None

        # bindings
        self.bind(last_fire, self._render_label)

        # unpack values
        x, y = pos

        # create
        self.label = self.track(
            ValueLabelComponent(
                manager=manager,
                container=container,
                pos=(x, y),
                w=w,
                text="",
            )
        )

    @override
    def update(self, dt: float) -> None:
        super().update(dt)
        self._render_label()

    def _render_label(self) -> None:
        last_fire = self.last_fire.value
        if last_fire is None:
            self.label.set_text("N/A")
            return

        elapsed = (dt.datetime.now() - last_fire.time).total_seconds()
        seconds = max(0, int(elapsed))
        if seconds != self.displayed:
            self.displayed = seconds
            self.label.set_text(f"{seconds if seconds <= 300 else '300+'} s")
