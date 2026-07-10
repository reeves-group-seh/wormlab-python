# std
import datetime as dt
from pathlib import Path
from typing import ClassVar, override

# pip
from pygame_gui import UIManager
from pygame_gui.elements import UIPanel

# local
from worm_shooter.components import NO_MARGINS, Component, StaticKVLabelComponent

# relative
from .state import HomeState


class InfoPanelComponent(Component):
    # public class constants
    W: ClassVar[int] = 395
    H: ClassVar[int] = 220

    # instance vars
    _state: HomeState
    _data_file: Path
    _countdown_length: int
    _countdown_seconds: int | None

    _room_temp_label: StaticKVLabelComponent
    _room_humidity_label: StaticKVLabelComponent
    _arduino_status_label: StaticKVLabelComponent
    _last_fire_label: StaticKVLabelComponent
    _countdown_label: StaticKVLabelComponent

    def __init__(
        self,
        manager: UIManager,
        container: UIPanel,
        pos: tuple[int, int],
        data_file: Path,
        countdown_length: int,
        state: HomeState,
    ) -> None:
        # init parent
        super().__init__()

        # set values
        self._state = state
        self._data_file = data_file
        self._countdown_length = countdown_length
        self._countdown_seconds: int | None = None

        # bindings
        self.bind(state.arduino_status, self._render_arduino_status_label)
        self.bind(state.room_temp, self._render_room_temp_label)
        self.bind(state.room_humidity, self._render_room_humidity_label)
        self.bind(state.last_fire, self._render_last_fire_label)

        # unpack values
        x, y = pos

        # panel
        panel = UIPanel(
            relative_rect=(x, y, self.W, self.H),
            manager=manager,
            container=container,
            margins=NO_MARGINS,
        )

        # top info
        StaticKVLabelComponent(
            manager=manager,
            container=panel,
            pos=(5, 10),
            w=(self.W - 10),
            key="Data File",
            value=data_file.name,
        )
        self._room_temp_label = StaticKVLabelComponent(
            manager=manager,
            container=panel,
            pos=(5, 35),
            w=(self.W - 10),
            key="Temperature",
            value="",
        )
        self._room_humidity_label = StaticKVLabelComponent(
            manager=manager,
            container=panel,
            pos=(5, 60),
            w=(self.W - 10),
            key="Humidity",
            value="",
        )
        self._arduino_status_label = StaticKVLabelComponent(
            manager=manager,
            container=panel,
            pos=(5, 85),
            w=(self.W - 10),
            key="Status",
            value="",
        )
        self._last_fire_label = StaticKVLabelComponent(
            manager=manager,
            container=panel,
            pos=(5, 110),
            w=(self.W - 10),
            key="Last Fire",
            value="",
        )
        self._countdown_label = StaticKVLabelComponent(
            manager=manager,
            container=panel,
            pos=(5, 135),
            w=(self.W - 10),
            key="Countdown",
            value="",
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
        self._arduino_status_label.set_value(str(self._state.arduino_status.value))

    def _render_room_temp_label(self) -> None:
        self._room_temp_label.set_value(f"{self._state.room_temp.value} \u2103")

    def _render_room_humidity_label(self) -> None:
        self._room_humidity_label.set_value(f"{self._state.room_humidity.value}%")

    def _render_last_fire_label(self) -> None:
        # last fire
        last_fire = self._state.last_fire.value
        last_fire_txt = (
            "N/A"
            if last_fire is None
            else f"{last_fire.time.strftime('%H:%M:%S')} (fire {self._state.num_fires.value}) {last_fire.duration} ms"
        )
        self._last_fire_label.set_value(last_fire_txt)

    def _render_countdown_label(self) -> None:
        # last fire
        last_fire = self._state.last_fire.value
        if last_fire is None:
            self._countdown_label.set_value("N/A")
            return

        # calculate change
        elapsed = max(
            0, int((dt.datetime.now().astimezone() - last_fire.time).total_seconds())
        )
        seconds = max(0, 15 - elapsed)
        if seconds != self._countdown_seconds:
            self._countdown_seconds = seconds
            self._countdown_label.set_value(f"{seconds} s")
