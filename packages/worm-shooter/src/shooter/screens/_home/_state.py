# std
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

# local
import axon
from shooter.backend.arduino import ArduinoAction, ArduinoBackend
from shooter.types import CenterPlan, FilterNumber, LaserFire, RadiusColor

# type-check only imports
if TYPE_CHECKING:
    from shooter.app import AppConfig, AppState


@dataclass(kw_only=True)
class HomeState:
    arduino_status: axon.Atom[ArduinoAction]
    fire_duration: axon.Atom[float]
    step_duration: axon.Atom[float]
    move_speed: axon.Atom[float]
    grid_size: axon.Atom[int]
    marker_pos: axon.Atom[tuple[int, int]]
    hover_pos: axon.Atom[tuple[int, int] | None]
    centering: axon.Atom[CenterPlan | None]
    last_fire: axon.Atom[LaserFire | None]
    lock_fire: axon.Atom[LaserFire | None]
    data_needed: axon.Atom[bool]
    num_fires: axon.Atom[int]
    filter_number: axon.Atom[FilterNumber]
    radius_color: axon.Atom[RadiusColor]
    worm_strain: axon.Atom[str]
    worm_id: axon.Atom[str]
    fire_comment: axon.Atom[str]
    behavior_comment: axon.Atom[str]

    # these are references to global state with a narrowed type as we know that
    # they must not be non on this screen
    room_temp: axon.Atom[float]
    room_humidity: axon.Atom[float]

    @staticmethod
    def new(
        cfg: AppConfig,
        app_state: AppState,
        arduino: ArduinoBackend,
    ) -> HomeState:
        # cast types
        room_temp = cast(axon.Atom[float], app_state.room_temp)
        room_humidity = cast(axon.Atom[float], app_state.room_humidity)

        # create
        s = HomeState(
            arduino_status=arduino.action(),
            fire_duration=axon.Atom(cfg.DEFAULT_FIRE_DURATION),
            step_duration=axon.Atom(cfg.DEFAULT_MOVE_DURATION),
            move_speed=axon.Atom(cfg.DEFAULT_MOVE_SPEED),
            grid_size=axon.Atom(cfg.DEFAULT_GRID_SIZE),
            marker_pos=axon.Atom(cfg.DEFAULT_MARKER_POS),
            hover_pos=axon.Atom(None),
            centering=axon.Atom(None),
            last_fire=axon.Atom(None),
            lock_fire=axon.Atom(None),
            data_needed=axon.Atom(False),
            num_fires=axon.Atom(0),
            filter_number=axon.Atom(cfg.DEFAULT_FILTER_NUMBER),
            radius_color=axon.Atom(cfg.DEFAULT_RADIUS_COLOR),
            worm_strain=axon.Atom(cfg.DEFAULT_WORM_STRAIN),
            worm_id=axon.Atom("1"),
            fire_comment=axon.Atom(""),
            behavior_comment=axon.Atom(""),
            room_temp=room_temp,
            room_humidity=room_humidity,
        )

        # bind
        s.worm_id.subscribe(lambda: HomeState._reset_num_fires(s.num_fires))

        # return
        return s

    @staticmethod
    def _reset_num_fires(num_fires: axon.Atom[int]) -> None:
        num_fires.value = 0
