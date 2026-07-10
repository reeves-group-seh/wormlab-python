# std
from typing import ClassVar

# pip
import pygame_gui
from pygame_gui import UIManager
from pygame_gui.elements import UIButton, UIPanel

# local
from worm_shooter.backend.data import DataBackend
from worm_shooter.components import (
    NO_MARGINS,
    Component,
    ControlLabelComponent,
    IncrementBoxComponent,
    LabeledCycleBoxComponent,
    TextEntryLineComponent,
)
from worm_shooter.types import FilterNumber, RadiusColor, WormResponse

# relative
from .state import HomeState


class SidePanelComponent(Component):
    # public class constants
    W: ClassVar[int] = 395
    H: ClassVar[int] = 370

    # instance vars
    _data: DataBackend
    _state: HomeState

    _f_res_button: UIButton
    _p_res_button: UIButton
    _a_res_button: UIButton
    _n_res_button: UIButton

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        data: DataBackend,
        state: HomeState,
    ):
        # init parent
        super().__init__()

        # set values
        self._data = data
        self._state = state

        # bindings
        self.bind(state.data_needed, self._render_buttons)

        # unpack values
        x, y = pos

        # create
        panel = UIPanel(
            relative_rect=(x, y, self.W, self.H),
            manager=manager,
            container=container,
            margins=NO_MARGINS,
        )

        # filter
        LabeledCycleBoxComponent(
            manager=manager,
            container=panel,
            pos=(10, 10),
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

        # radius
        LabeledCycleBoxComponent(
            manager=manager,
            container=panel,
            pos=(10, 80),
            w=375,
            label_text="Radius Color",
            value=state.radius_color,
            options=[
                RadiusColor.RED,
                RadiusColor.GREEN,
                RadiusColor.BLUE,
                RadiusColor.YELLOW,
            ],
        )

        # strain
        ControlLabelComponent(
            manager=manager,
            container=panel,
            pos=(10, 150),
            w=375,
            text="Strain",
        )
        TextEntryLineComponent(
            manager=manager,
            container=panel,
            pos=(10, 180),
            w=375,
            value=state.worm_strain,
            parse=str,
        )

        # worm id
        ControlLabelComponent(
            manager=manager,
            container=panel,
            pos=(10, 220),
            w=375,
            text="ID",
        )
        IncrementBoxComponent(
            manager=manager,
            container=panel,
            pos=(10, 250),
            w=375,
            value=state.worm_id,
        )

        # buttons
        self._f_res_button = UIButton(
            relative_rect=(10, 290, 87, 70),
            text="F",
            manager=manager,
            container=panel,
        )
        self._f_res_button.bind(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda: self._record_response(WormResponse.FULL),
        )

        self._p_res_button = UIButton(
            relative_rect=(106, 290, 87, 70),
            text="P",
            manager=manager,
            container=panel,
        )
        self._p_res_button.bind(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda: self._record_response(WormResponse.PARTIAL),
        )

        self._a_res_button = UIButton(
            relative_rect=(202, 290, 87, 70),
            text="A",
            manager=manager,
            container=panel,
        )
        self._a_res_button.bind(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda: self._record_response(WormResponse.ACKNOWLEDGE),
        )

        self._n_res_button = UIButton(
            relative_rect=(298, 290, 87, 70),
            text="N",
            manager=manager,
            container=panel,
        )
        self._n_res_button.bind(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda: self._record_response(WormResponse.NO_RESPONSE),
        )

        # do initial renders
        self._render_buttons()

    def _render_buttons(self) -> None:
        if self._state.data_needed.value:
            self._f_res_button.enable()  # type: ignore[no-untyped-call]
            self._p_res_button.enable()  # type: ignore[no-untyped-call]
            self._a_res_button.enable()  # type: ignore[no-untyped-call]
            self._n_res_button.enable()  # type: ignore[no-untyped-call]
        else:
            self._f_res_button.disable()  # type: ignore[no-untyped-call]
            self._p_res_button.disable()  # type: ignore[no-untyped-call]
            self._a_res_button.disable()  # type: ignore[no-untyped-call]
            self._n_res_button.disable()  # type: ignore[no-untyped-call]

    def _record_response(
        self,
        response: WormResponse,
    ) -> None:
        # unwrap fire value (buttons are disabled when no last fire)
        fire = self._state.last_fire.value
        assert fire is not None

        # add data
        self._data.add_data_entry(
            fire=fire,
            room_temp=self._state.room_temp.value,
            room_humidity=self._state.room_humidity.value,
            radius_color=self._state.radius_color.value,
            filter_number=self._state.filter_number.value,
            worm_strain=self._state.worm_strain.value,
            worm_id=self._state.worm_id.value,
            response=response,
        )

        # update state
        self._state.data_needed.value = False
