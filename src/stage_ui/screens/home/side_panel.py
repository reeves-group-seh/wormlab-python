# std

# pip
import pygame_gui
from pygame_gui import UIManager
from pygame_gui.elements import UIButton, UIPanel

# local
from stage_ui.components import NO_MARGINS, Component
from stage_ui.components.control_label import ControlLabelComponent
from stage_ui.components.increment_box import IncrementBoxComponent
from stage_ui.components.labeled_cycle_box import LabeledCycleBoxComponent
from stage_ui.components.text_entry_line import TextEntryLineComponent
from stage_ui.manager_data import DataManager
from stage_ui.types import FilterNumber, RadiusColor, WormResponse

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
        # self._render_last_fire_label()
        self._render_buttons()

    # def _render_last_fire_label(self) -> None:
    #     # grab last fire and check if none
    #     last_fire = self._state.last_fire.value
    #     if last_fire is None:
    #         self.last_fire_label.set_text("N/A")
    #         return

    #     # format values
    #     time_txt = last_fire.time.strftime("%H:%M:%S")
    #     full_txt = (
    #         f"{time_txt} (fire {self._state.num_fires.value}) {last_fire.duration} ms"
    #     )
    #     self.last_fire_label.set_text(full_txt)

    def _render_buttons(self) -> None:
        if self._state.data_needed.value:
            self.f_res_button.enable()  # type: ignore[no-untyped-call]
            self.p_res_button.enable()  # type: ignore[no-untyped-call]
            self.a_res_button.enable()  # type: ignore[no-untyped-call]
            self.n_res_button.enable()  # type: ignore[no-untyped-call]
        else:
            self.f_res_button.disable()  # type: ignore[no-untyped-call]
            self.p_res_button.disable()  # type: ignore[no-untyped-call]
            self.a_res_button.disable()  # type: ignore[no-untyped-call]
            self.n_res_button.disable()  # type: ignore[no-untyped-call]

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
            radius_color=state.radius_color.value,
            filter_number=state.filter_number.value,
            worm_strain=state.worm_strain.value,
            worm_id=state.worm_id.value,
            response=response,
        )

        # update state
        state.data_needed.value = False
