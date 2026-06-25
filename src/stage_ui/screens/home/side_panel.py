# std
import datetime as dt
from typing import override

# pip
import pygame_gui
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
from stage_ui.manager_data import DataManager
from stage_ui.types import FilterNumber, LaserFire, RadiusColor, WormResponse

# relative
from .state import HomeState


class SidePanelComponent(Component):
    # constants
    W: int = 395
    H: int = 370

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        data_manager: DataManager,
        state: HomeState,
    ):
        # init parent
        super().__init__()

        # set values
        self._state = state

        # bindings
        self.bind(state.last_fire, self._render_last_fire_label)
        self.bind(state.data_needed, self._render_buttons)

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
                last_fire=state.last_fire,
            )
        )

        # filter
        LabeledCycleBoxComponent(
            manager=manager,
            container=panel,
            pos=(10, 80),
            w=375,
            label_text="Filter Number",
            value=state.filter_number,
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
                value=state.worm_strain,
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
                value=state.worm_id,
            )
        )

        # buttons
        self.f_res_button = UIButton(
            relative_rect=(10, 290, 87, 70),
            text="F",
            manager=manager,
            container=panel,
        )
        self.f_res_button.bind(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda: self._record_response(data_manager, state, WormResponse.FULL),
        )

        self.p_res_button = UIButton(
            relative_rect=(106, 290, 87, 70),
            text="P",
            manager=manager,
            container=panel,
        )
        self.p_res_button.bind(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda: self._record_response(data_manager, state, WormResponse.PARTIAL),
        )

        self.a_res_button = UIButton(
            relative_rect=(202, 290, 87, 70),
            text="A",
            manager=manager,
            container=panel,
        )
        self.a_res_button.bind(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda: self._record_response(
                data_manager, state, WormResponse.ACKNOWLEDGE
            ),
        )

        self.n_res_button = UIButton(
            relative_rect=(298, 290, 87, 70),
            text="N",
            manager=manager,
            container=panel,
        )
        self.n_res_button.bind(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda: self._record_response(
                data_manager, state, WormResponse.NO_RESPONSE
            ),
        )

        # do initial renders
        self._render_last_fire_label()
        self._render_buttons()

    def _render_last_fire_label(self) -> None:
        # grab last fire and check if none
        last_fire = self._state.last_fire.value
        if last_fire is None:
            self.last_fire_label.set_text("N/A")
            return

        # format values
        time_txt = last_fire.time.strftime("%H:%M:%S")
        full_txt = (
            f"{time_txt} (fire {self._state.num_fires.value}) {last_fire.duration} ms"
        )
        self.last_fire_label.set_text(full_txt)

    def _render_buttons(self) -> None:
        if self._state.data_needed.value:
            self.f_res_button.enable()
            self.p_res_button.enable()
            self.a_res_button.enable()
            self.n_res_button.enable()
        else:
            self.f_res_button.disable()
            self.p_res_button.disable()
            self.a_res_button.disable()
            self.n_res_button.disable()

    def _record_response(
        self,
        data_manager: DataManager,
        state: HomeState,
        response: WormResponse,
    ) -> None:
        # unwrap fire value (buttons are disabled when no last fire)
        fire = state.last_fire.value
        assert fire is not None

        # add data
        data_manager.add_data_entry(
            fire=fire,
            room_temp=state.room_temp.value,
            room_humidity=state.room_humidity.value,
            radius_color=RadiusColor.RED,  # TODO: implement
            filter_number=state.filter_number.value,
            worm_strain=state.worm_strain.value,
            worm_id=state.worm_id.value,
            response=response,
        )

        # update state
        state.data_needed.value = False


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

        elapsed = (dt.datetime.now().astimezone() - last_fire.time).total_seconds()
        seconds = max(0, int(elapsed))
        if seconds != self.displayed:
            self.displayed = seconds
            self.label.set_text(f"{seconds if seconds <= 300 else '300+'} s")
