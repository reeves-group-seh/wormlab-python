# std
import dataclasses
from dataclasses import dataclass

# local
from shooter.app.config import AppConfig
from shooter.app.state import AppState
from shooter.backend.arduino import ArduinoBackend
from shooter.backend.camera import CameraBackend
from shooter.backend.data import DataBackend


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
