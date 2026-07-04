# std
import dataclasses
from dataclasses import dataclass

# local
from stage_ui.app_config import AppConfig
from stage_ui.app_state import AppState
from stage_ui.manager_arduino import ArduinoManager
from stage_ui.manager_camera import CameraManager
from stage_ui.manager_data import DataManager


@dataclass(kw_only=True)
class AppContext:
    """
    All shared application context. Any data used beteen multiple components
    should be stored here.
    """

    cfg: AppConfig
    """
    Application configuration defined at app start and not changed throughout
    the application lifecycle.
    """

    state: AppState = dataclasses.field(default_factory=lambda: AppState())
    """
    State shared across screens.
    """

    # managers

    arduino_man: ArduinoManager
    """
    Manager handling serial communication with the arduino.
    """

    camera_man: CameraManager
    """
    Manager handling camera input.
    """

    data_man: DataManager
    """
    Manager handling writing of data.
    """

    def destroy(self) -> None:
        """
        Cleanup all open resources.
        """
        self.camera_man.close()
        self.arduino_man.close()
