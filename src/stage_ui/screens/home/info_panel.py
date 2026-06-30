# std
import datetime as dt
from pathlib import Path
from typing import override

# pip
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel

# local
from stage_ui.components import NO_MARGINS, Component
from stage_ui.components.static_kv_label import StaticKVLabelComponent
from stage_ui.screens.home.state import HomeState


class InfoPanelComponent(Component):
    # constants
    W: int = 395
    H: int = 220

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        data_file: Path,
        state: HomeState,
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self.state = state
        self.data_file = data_file
        self.countdown_seconds: int | None = None

        # bindings
        self.bind(state.arduino_status, self._render_arduino_status_label)
        self.bind(state.room_temp, self._render_room_temp_label)
        self.bind(state.room_humidity, self._render_room_humidity_label)
        self.bind(state.last_fire, self._render_last_fire_label)

        # unpack values
        x, y = pos

        # panel
        panel = self.track(
            UIPanel(
                relative_rect=(x, y, self.W, self.H),
                manager=manager,
                container=container,
                margins=NO_MARGINS,
            )
        )

        # top info
        self.track(
            StaticKVLabelComponent(
                manager=manager,
                container=panel,
                pos=(5, 10),
                w=(self.W - 10),
                key="Data File",
                value=data_file.name,
            )
        )
        self.room_temp_label = self.track(
            StaticKVLabelComponent(
                manager=manager,
                container=panel,
                pos=(5, 35),
                w=(self.W - 10),
                key="Temperature",
                value="",
            )
        )
        self.room_humidity_label = self.track(
            StaticKVLabelComponent(
                manager=manager,
                container=panel,
                pos=(5, 60),
                w=(self.W - 10),
                key="Humidity",
                value="",
            )
        )
        self.arduino_status_label = self.track(
            StaticKVLabelComponent(
                manager=manager,
                container=panel,
                pos=(5, 85),
                w=(self.W - 10),
                key="Status",
                value="",
            )
        )
        self.last_fire_label = self.track(
            StaticKVLabelComponent(
                manager=manager,
                container=panel,
                pos=(5, 110),
                w=(self.W - 10),
                key="Last Fire",
                value="",
            )
        )
        self.countdown_label = self.track(
            StaticKVLabelComponent(
                manager=manager,
                container=panel,
                pos=(5, 135),
                w=(self.W - 10),
                key="Time Since Fire",
                value="",
            )
        )

        # do initial renders
        self._render_arduino_status_label()
        self._render_room_temp_label()
        self._render_room_humidity_label()
        self._render_last_fire_label()

    @override
    def update(self, dt: float) -> None:
        super().update(dt)
        self._render_countdown_label()

    def _render_arduino_status_label(self) -> None:
        self.arduino_status_label.set_value(str(self.state.arduino_status.value))

    def _render_room_temp_label(self) -> None:
        self.room_temp_label.set_value(f"{self.state.room_temp.value} \u2103")

    def _render_room_humidity_label(self) -> None:
        self.room_humidity_label.set_value(f"{self.state.room_humidity.value}%")

    def _render_last_fire_label(self) -> None:
        # last fire
        last_fire = self.state.last_fire.value
        last_fire_txt = (
            "N/A"
            if last_fire is None
            else f"{last_fire.time.strftime('%H:%M:%S')} (fire {self.state.num_fires.value}) {last_fire.duration} ms"
        )
        self.last_fire_label.set_value(last_fire_txt)

    def _render_countdown_label(self) -> None:
        # last fire
        last_fire = self.state.last_fire.value
        if last_fire is None:
            self.countdown_label.set_value("N/A")
            return

        # calculate change
        elapsed = (dt.datetime.now().astimezone() - last_fire.time).total_seconds()
        seconds = max(0, int(elapsed))
        if seconds != self.countdown_seconds:
            self.countdown_seconds = seconds
            self.countdown_label.set_value(f"{seconds if seconds <= 300 else '300+'} s")
