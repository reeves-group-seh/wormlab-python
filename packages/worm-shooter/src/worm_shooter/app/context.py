# std
import dataclasses
from dataclasses import dataclass

# local
from stage_ui.app.config import AppConfig
from stage_ui.app.state import AppState
from stage_ui.backend.arduino import ArduinoBackend
from stage_ui.backend.camera import CameraBackend
from stage_ui.backend.data import DataBackend


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

    # backends

    arduino: ArduinoBackend
    """
    Backend handling serial communication with the arduino.
    """

    camera: CameraBackend
    """
    Backend handling camera input.
    """

    data: DataBackend
    """
    Backend handling writing of data.
    """

    def destroy(self) -> None:
        """
        Cleanup all open resources.
        """
        self.camera.close()
        self.arduino.close()
