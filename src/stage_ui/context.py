# std
from dataclasses import dataclass

from stage_ui.atom import Atom

# local
from stage_ui.config import Config
from stage_ui.manager_arduino import ArduinoManager
from stage_ui.manager_camera import CameraManager
from stage_ui.manager_data import DataManager


@dataclass(kw_only=True)
class Context:
    """
    All shared application context. Any data used beteen multiple components
    should be stored here.
    """

    #
    # static config
    #

    cfg: Config
    """
    Application configuration defined at app start and not changed throughout
    the application lifecycle.
    """

    #
    # managers
    #

    camera_man: CameraManager
    """
    Manager handling camera input.
    """

    data_man: DataManager
    """
    Manager handling writing of data.
    """

    arduino_man: ArduinoManager
    """
    Manager handling serial communication with the arduino.
    """

    #
    # global state
    #

    state: GlobalState
    """
    State shared across screens.
    """

    def close(self) -> None:
        # cleanup logic
        self.camera_man.close()

        # TODO: implement fully


@dataclass(kw_only=True)
class GlobalState:
    """
    All "atomic" state shared across screens.
    """

    room_temp: Atom[float | None]
    """
    TI room temperature in degrees celsius, selected on the start screen.
    """

    room_humidity: Atom[float | None]
    """
    Relative room humidity as a percent, selected on the start screen.
    """

    @staticmethod
    def new() -> GlobalState:
        return GlobalState(
            room_humidity=Atom(None),
            room_temp=Atom(None),
        )
