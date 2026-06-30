# pip
import pygame
import pygame_gui
from pygame import Event
from pygame_gui import UIManager
from pygame_gui.elements import UIButton, UIPanel

# local
from stage_ui.atom import Atom
from stage_ui.components import NO_MARGINS, Component
from stage_ui.components.control_label import ControlLabelComponent
from stage_ui.components.cycle_box import CycleBoxComponent
from stage_ui.components.spin_box import SpinBoxComponent
from stage_ui.components.text_entry_line_eager import EagerTextEntryLineComponent
from stage_ui.manager_arduino import ArduinoManager
from stage_ui.screens.events import CT_GO_HOME


class SidePanelComponent(Component):
    # constants
    W: int = 395
    H: int = 370

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        arduino_man: ArduinoManager,
        serial_port: Atom[str],
        camera_index: Atom[int],
        room_temp: Atom[float | None],
        room_humidity: Atom[float | None],
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self.arduino_man = arduino_man
        self.serial_port = serial_port
        self.room_temp = room_temp
        self.room_humidity = room_humidity
        self._valid = True

        # bindings
        self.bind(room_temp, self._render_buttons)
        self.bind(room_humidity, self._render_buttons)
        self.bind(serial_port, self._change_port)

        # unpack values
        x, y = pos

        # panel
        panel = self.track(
            UIPanel(
                relative_rect=(x, y, self.W, self.H),
                manager=manager,
                margins=NO_MARGINS,
                container=container,
            )
        )

        # serial select
        self.track(
            ControlLabelComponent(
                manager=manager,
                container=panel,
                pos=(10, 20),
                w=375,
                text="Serial",
            )
        )
        self.track(
            CycleBoxComponent(
                manager=manager,
                container=panel,
                pos=(10, 50),
                w=375,
                value=serial_port,
                options=arduino_man.ports(),
            )
        )

        # camera select
        self.track(
            ControlLabelComponent(
                manager=manager,
                container=panel,
                pos=(10, 90),
                w=375,
                text="Camera",
            )
        )
        self.track(
            SpinBoxComponent(
                manager=manager,
                container=panel,
                pos=(10, 120),
                w=375,
                value=camera_index,
                inc=lambda v: v + 1,
                dec=lambda v: max(0, v - 1),
                parse=int,
            )
        )

        # temp input
        self.track(
            ControlLabelComponent(
                manager=manager,
                container=panel,
                pos=(10, 160),
                w=375,
                text="TI Temperature (\u2103)",
            )
        )
        self.track(
            EagerTextEntryLineComponent(
                manager=manager,
                container=panel,
                pos=(10, 190),
                w=375,
                value=room_temp,
                parse=float,
            )
        )

        # humidity input
        self.track(
            ControlLabelComponent(
                manager=manager,
                container=panel,
                pos=(10, 230),
                w=375,
                text="Relative Humidity (%)",
            )
        )
        self.track(
            EagerTextEntryLineComponent(
                manager=manager,
                container=panel,
                pos=(10, 260),
                w=375,
                value=room_humidity,
                parse=float,
            )
        )

        # buttons
        test_serial_button = self.track(
            UIButton(
                relative_rect=(10, 320, 184, 40),
                text="Test Serial",
                manager=manager,
                container=panel,
            )
        )
        test_serial_button.disable()  # type: ignore[no-untyped-call]
        self._start_button = self.track(
            UIButton(
                relative_rect=(201, 320, 184, 40),
                text="Start",
                manager=manager,
                container=panel,
            )
        )
        self._start_button.bind(
            pygame_gui.UI_BUTTON_PRESSED, lambda: pygame.event.post(Event(CT_GO_HOME))
        )
        self._start_button.disable()  # type: ignore[no-untyped-call]

    def _set_valid(self, valid: bool) -> None:
        # skip if correct
        if valid == self._valid:
            return

        # flip state and enable / disable
        self._valid = valid
        if valid:
            self._start_button.enable()  # type: ignore[no-untyped-call]
        else:
            self._start_button.disable()  # type: ignore[no-untyped-call]

    def _render_buttons(self) -> None:
        if self.room_temp.value is not None and self.room_humidity.value is not None:
            self._set_valid(True)
        else:
            self._set_valid(False)

    def _change_port(self) -> None:
        # re-open the connection at the new index
        self.arduino_man.close()
        self.arduino_man.open(self.serial_port.value)
