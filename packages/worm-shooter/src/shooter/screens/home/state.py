# std
from dataclasses import dataclass
from typing import cast

# local
from shooter.app.config import AppConfig
from shooter.app.state import AppState
from shooter.atom import Atom
from shooter.backend.arduino import ArduinoAction, ArduinoBackend
from shooter.types import FilterNumber, LaserFire, RadiusColor


@dataclass(kw_only=True)
class HomeState:
    arduino_status: Atom[ArduinoAction]
    fire_duration: Atom[float]
    step_duration: Atom[float]
    move_speed: Atom[float]
    grid_size: Atom[int]
    marker_pos: Atom[tuple[int, int]]
    last_fire: Atom[LaserFire | None]
    data_needed: Atom[bool]
    num_fires: Atom[int]
    filter_number: Atom[FilterNumber]
    radius_color: Atom[RadiusColor]
    worm_strain: Atom[str]
    worm_id: Atom[str]

    # these are references to global state with a narrowed type as we know that
    # they must not be non on this screen
    room_temp: Atom[float]
    room_humidity: Atom[float]

    @staticmethod
    def new(
        cfg: AppConfig,
        app_state: AppState,
        arduino: ArduinoBackend,
    ) -> HomeState:
        # cast types
        room_temp = cast(Atom[float], app_state.room_temp)
        room_humidity = cast(Atom[float], app_state.room_humidity)

        # create
        s = HomeState(
            arduino_status=arduino.action(),
            fire_duration=Atom(cfg.DEFAULT_FIRE_DURATION),
            step_duration=Atom(cfg.DEFAULT_MOVE_DURATION),
            move_speed=Atom(cfg.DEFAULT_MOVE_SPEED),
            grid_size=Atom(cfg.DEFAULT_GRID_SIZE),
            marker_pos=Atom(cfg.DEFAULT_MARKER_POS),
            last_fire=Atom(None),
            data_needed=Atom(False),
            num_fires=Atom(0),
            filter_number=Atom(cfg.DEFAULT_FILTER_NUMBER),
            radius_color=Atom(cfg.DEFAULT_RADIUS_COLOR),
            worm_strain=Atom(cfg.DEFAULT_WORM_STRAIN),
            worm_id=Atom("1"),
            room_temp=room_temp,
            room_humidity=room_humidity,
        )

        # bind
        s.worm_id.subscribe(lambda: HomeState._reset_num_fires(s.num_fires))

        # return
        return s

    @staticmethod
    def _reset_num_fires(num_fires: Atom[int]) -> None:
        num_fires.value = 0
