# module imports
import dataclasses
import pygame

# item imports
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# local item imports
from app_types import FilterNumber, KeyMapAction, RadiusColor


@dataclass(kw_only=True, frozen=True)
class AppConfig:
    """
    Configuration defined at application start and not changed throughout the
    app lifecycle.
    """

    MARKER_POS: tuple[float, float] = (200.0, 311.0)
    """
    Position of the the marker relative to the video grid.
    """

    TESTING: bool
    """
    Whether the app should be run in "testing" mode.
    """

    APP_NAME: str = "Stage Controller"
    """
    Application name.
    """

    DATA_FILE: Path
    """
    Name of the CSV datafile to create & write to.
    """

    FPS: int = 60
    """
    Max number of frames per second to render at.
    """

    CAMERA_INDEX: int = 3
    """
    OpenCV video capture camera index.
    """

    WINDOW_W: int = 1000
    """
    Width of the display.
    """

    WINDOW_H: int = 650
    """
    Height of the display.
    """

    PACKAGE_NAME: str = "stage_ui"
    """
    Name of this package.
    """

    #
    # speed
    #

    SPEED_STEP: float = 10.0
    """
    Value to increment and decrement speed by in steps per second.
    """

    MIN_SPEED: float = 10.0
    """
    Minimum stage movement speed in steps per second.
    """

    MAX_SPEED: float = 1000.0
    """
    Maximum stage movement speed in steps per second.
    """

    DEFAULT_SPEED: float = 100.0
    """
    Default stage movement speed in steps per second.
    """

    #
    # move duration
    #

    MIN_MOVE_DURATION: float = 1.0
    """
    Mimimum stage move duration in milliseconds.
    """

    MAX_MOVE_DURATION: float = 5000.0
    """
    Maximum stage move duration in milliseconds.
    """

    DEFAULT_MOVE_DURATION: float = 100.0
    """
    Default stage move duration in milliseconds.
    """

    #
    # fire duration
    #

    MIN_FIRE_DURATION: float = 1.0
    """
    Mimimum laser fire duration in milliseconds.
    """

    MAX_FIRE_DURATION: float = 10000.0
    """
    Maximum laser fire duration in milliseconds.
    """

    DEFAULT_FIRE_DURATION: float = 200.0
    """
    Default laser fire duration in milliseconds.
    """

    #
    # grid
    #

    MIN_GRID_SIZE: int = 1
    """
    Minumum size of the square test grid.
    """

    MAX_GRID_SIZE: int = 20
    """
    Maximum size of the square test grid.
    """

    DEFAULT_GRID_SIZE: int = 3
    """
    Default size of the square test grid.
    """

    DEFAULT_GRID_SPEED: float = 100.0
    """
    Default speed when running the step-and-shoot.
    """

    DEFAULT_GRID_MOVE_DURATION: float = 10.0
    """
    Default duration of moves during step-and-shoot.
    """

    DEFAULT_GRID_FIRE_DURATION: float = 200.0
    """
    Default duration of fires during step-and-shoot.
    """

    #
    # other defaults
    #

    DEFAULT_FILTER_NUMBER: FilterNumber = FilterNumber.FOUR
    """
    Default selected filter number.
    """

    DEFAULT_RADIUS_COLOR: RadiusColor = RadiusColor.YELLOW
    """
    Default selected radius color.
    """

    #
    # serial
    #

    SERIAL_PORT: str = "COM4"
    """
    Port to connect to the arduino on.
    """

    SERIAL_BAUDRATE: int = 115200
    """
    Baude rate to communicate with arduino at.
    """

    SERIAL_TIMEOUT: float = 0.1
    """
    Time in seconds to timeout the connection to the arduino.
    """

    SERIAL_SLEEP_FACTOR: float = 1.5
    """
    A factor determining how long to wait between writes to the arduino. A value
    of 1.0 indicates the program will wait for exactly the theroretical
    execution time of a command before sending another. A value of 2.0 indicates
    the program will wait for double this theroretical execution time, 0.5 will
    wait half, etc. To be safe, this value should be set to a value > 1.0.
    """

    #
    # keymaps
    #

    KEYMAP: dict[int, KeyMapAction] = field(
        default_factory=lambda: {
            # steps
            pygame.K_h: KeyMapAction.STEP_LEFT,
            pygame.K_k: KeyMapAction.STEP_RIGHT,
            pygame.K_u: KeyMapAction.STEP_UP,
            pygame.K_j: KeyMapAction.STEP_DOWN,
            # movement
            pygame.K_LEFT: KeyMapAction.MOVE_LEFT,
            pygame.K_RIGHT: KeyMapAction.MOVE_RIGHT,
            pygame.K_UP: KeyMapAction.MOVE_UP,
            pygame.K_DOWN: KeyMapAction.MOVE_UP,
            # speed
            pygame.K_w: KeyMapAction.INC_SPEED,
            pygame.K_s: KeyMapAction.DEC_SPEED,
            # other
            pygame.K_ESCAPE: KeyMapAction.QUIT,
            pygame.K_f: KeyMapAction.FIRE,
            pygame.K_d: KeyMapAction.DESTROY,
            pygame.K_m: KeyMapAction.GRID,
            pygame.K_p: KeyMapAction.SKIP_DATA,
        }
    )
    """
    Main application keymap.
    """

    #
    # methods
    #

    @staticmethod
    def new(
        data_dir: Path,
        testing: bool = False,
        camera_index: int | None = None,
    ) -> AppConfig:
        # generated config
        data_file = data_dir / f"{datetime.now().strftime('%Y-%m-%dT%H%M%S')}_data.csv"

        # override default if given
        camera_index = (
            camera_index
            if camera_index is not None
            else _get_default(AppConfig, "CAMERA_INDEX")
        )

        # construct
        return AppConfig(
            TESTING=testing,
            CAMERA_INDEX=camera_index,
            DATA_FILE=data_file,
        )


def _get_default(cls: type, field_name: str) -> Any:
    for f in dataclasses.fields(cls):
        if f.name == field_name:
            if f.default is dataclasses.MISSING:
                raise Exception("no default for given field")
            return f.default
    raise Exception("no field matches givn name")
