# std
from dataclasses import dataclass
from typing import cast

# local
from stage_ui.atom import Atom
from stage_ui.config import Config
from stage_ui.context import GlobalState
from stage_ui.manager_arduino import ArduinoManager
from stage_ui.manager_arduino.base import ArduinoAction
from stage_ui.types import FilterNumber, LaserFire


@dataclass(kw_only=True)
class HomeState:
    arduino_status: Atom[ArduinoAction]
    fire_duration: Atom[float]
    step_duration: Atom[float]
    move_speed: Atom[float]
    grid_size: Atom[int]
    last_fire: Atom[LaserFire | None]
    num_fires: Atom[int]
    filter: Atom[FilterNumber]
    strain: Atom[str]
    worm_id: Atom[str]

    # these are references to global state with a narrowed type as we know that
    # they must not be non on this screen
    room_temp: Atom[float]
    room_humidity: Atom[float]

    @staticmethod
    def new(
        cfg: Config, arduino_manager: ArduinoManager, global_state: GlobalState
    ) -> HomeState:
        # cast types
        room_temp = cast(Atom[float], global_state.room_temp)
        room_humidity = cast(Atom[float], global_state.room_humidity)

        return HomeState(
            arduino_status=arduino_manager.action(),
            fire_duration=Atom(cfg.DEFAULT_FIRE_DURATION),
            step_duration=Atom(cfg.DEFAULT_STEP_DURATION),
            move_speed=Atom(cfg.DEFAULT_MOVE_SPEED),
            grid_size=Atom(cfg.DEFAULT_GRID_SIZE),
            last_fire=Atom(None),
            num_fires=Atom(0),
            filter=Atom(cfg.DEFAULT_FILTER_NUMBER),
            strain=Atom(cfg.DEFAULT_STRAIN),
            worm_id=Atom("1"),
            room_temp=room_temp,
            room_humidity=room_humidity,
        )
