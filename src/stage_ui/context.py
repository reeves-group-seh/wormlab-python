# item imports
from dataclasses import dataclass

# local item imports
from stage_ui.config import Config
from stage_ui.manager_camera import CameraManager
from stage_ui.manager_data import DataManager
from stage_ui.manager_serial import SerialManager


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

    serial_man: SerialManager
    """
    Manager handling communication with the arduino.
    """
